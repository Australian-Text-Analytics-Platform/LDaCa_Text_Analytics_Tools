# CJK Tokeniser Performance — Investigation & Fix Plan

**Branch:** `perf/cjk-tokeniser` (in `ldaca_wordflow`, `ldaca_wordflow/backend`, `ldaca_wordflow/polars-text`)
**Base:** `v0.4` for `ldaca_wordflow` + `backend`; `multilingual` for `polars-text` (its release-line equivalent — `polars-text` has no `v0.4`).
**Started:** 2026-05-15

## Symptom

After Phase 5 of multilingual support (Jieba for Chinese, Lindera for Japanese/Korean) landed in `polars-text 0.2.0`, tokenised workspaces became dramatically slower and consumed much more RAM than the v0.3 (English-only) line — despite the lazy-frame architecture being intact.

Functional correctness is fine; the regression is purely performance.

## Root causes (in priority order)

### 1. `byte_to_char_idx` is O(N²) per document — the biggest offender

[`polars-text/src/tokenizer.rs:141-143`](ldaca_wordflow/polars-text/src/tokenizer.rs#L141-L143):

```rust
fn byte_to_char_idx(text: &str, byte_idx: usize) -> usize {
    text.char_indices().take_while(|(b, _)| *b < byte_idx).count()
}
```

Called **twice per token** from the Lindera and HuggingFace arms of `tokenize_text_with_offsets`. Each call walks `char_indices()` from byte 0. For `N` tokens in a `C`-character document, total cost is `Θ(N·C)`.

- Jieba (`zh`) is **unaffected** — its tokens come back with native char offsets (line 111), so the function is never called.
- Lindera (`ja`, `ko`) and any HuggingFace model are pathologically slow because their tokens emit byte offsets.

A 10 000-char JA article with ~5 000 Lindera morphemes → ~50 million char-iterations **per row**. Over 10 000 rows the work approaches 10¹² iterations. This alone explains most of the regression.

**Fix:** single forward sweep. Lindera and HF both emit tokens in document order, so accumulate char position by stepping through `text.char_indices()` once per document, zipping token byte offsets against it as we go. Replaces `Θ(N·C)` with `Θ(C + N)`.

### 2. Tokenisation re-runs on every collect (no materialisation)

[`backend/src/ldaca_wordflow/core/derived_columns.py:57-71`](ldaca_wordflow/backend/src/ldaca_wordflow/core/derived_columns.py#L57-L71) only appends the tokenise expression to the lazy plan. Each downstream `.collect()` re-executes the tokeniser. Hot paths:

- Page-size estimator [`concordance_core.py:560-573`](ldaca_wordflow/backend/src/ldaca_wordflow/api/workspaces/analyses/concordance_core.py#L560-L573) probes the candidate ladder, triggering multiple tokenisation passes per concordance request.
- Tokens-mode concordance [`concordance_tokens_mode.py:165-167`](ldaca_wordflow/backend/src/ldaca_wordflow/api/workspaces/analyses/concordance_tokens_mode.py#L165-L167) re-tokenises on every page navigation.
- Token frequencies (see issue 3) materialises the full column eagerly.

`is_elementwise=True` plus a `.slice()` should keep per-page cost bounded by the page size, but the estimator and token-frequencies path each undermine that.

**Fix:** see "Tokens cache" section below.

### 3. `calculate_token_frequencies` collects the full tokens column to Python

[`backend/src/ldaca_wordflow/api/workspaces/analyses/token_frequencies.py:464-473`](ldaca_wordflow/backend/src/ldaca_wordflow/api/workspaces/analyses/token_frequencies.py#L464-L473):

```python
tokens_df = node_data.select(
    pl.col(derived_tokens_col)
    .list.eval(pl.element().struct.field("token"))
    .alias("__tokens__")
).collect()
node_tokens[node_id] = [
    [str(tok) for tok in (row or []) if tok is not None]
    for row in tokens_df["__tokens__"].to_list()
]
```

Forces a full collect, materialises every token as a Python `str` (~50 B overhead each vs ~16 B in Arrow), then pickles the whole `list[list[str]]` to a worker via `task_args`. For 10 k docs × ~1 k tokens that's 10 M PyObjects ≈ ~500 MB of pure object overhead before any work happens.

**Fix:** keep it in Polars end-to-end. Pass the LazyFrame (or, post-cache, the cache parquet path) to the worker; compute frequencies inside the worker with `pl.col(...).list.eval(pl.element().struct.field("token")).explode().value_counts()` and sink the result to the existing token-frequencies parquet artifact.

### 4. Unconditional `text.to_lowercase()` for CJK

[`polars-text/src/tokenizer.rs:44-48`](ldaca_wordflow/polars-text/src/tokenizer.rs#L44-L48) always allocates a fresh `String` and Unicode-lowercases when `lowercase=true` (the wrapper default at [`functions.py:35`](ldaca_wordflow/polars-text/polars_text/functions.py#L35)). CJK has no case to fold, so this is wasted CPU and allocation per row.

**Fix:** in `tokenise_column` (backend), override `lowercase=False` when `language in {"zh","ja","ko"}` or `model in {"jieba","lindera-*"}`. Defence-in-depth in Rust: short-circuit the lowercase call when the backend is `Jieba` or `Lindera`.

### 5. Per-row Series construction in the list builder

[`polars-text/src/expressions.rs:281-308`](ldaca_wordflow/polars-text/src/expressions.rs#L281-L308) calls `struct_series_from_tokens` per input row, allocating three new `Series` and a `StructChunked` each time, then appending via `AnonymousOwnedListBuilder::append_series` which concatenates them. For 10 k rows × ~1 k tokens that's 10 k throwaway Series and ~30 k extra allocations.

**Fix:** flat builder. Maintain three growable `Vec<>`s (`tok_col`, `start_col`, `end_col`) plus a `Vec<i64>` of cumulative list offsets across the entire chunk. Build a single `ListChunked<StructChunked>` once at the end.

### 6. Slice-pushdown verification (resolved, with caveat)

Ran the manual check after the cache landed:

```python
print(node.data.slice(0, 5).explain(optimized=True))
```

Result: the optimised plan is **identical** to the full-data plan — Polars 1.40 does **not** push the slice past the `LEFT JOIN` to the cache parquet. So every paged query reads the **entire** cache parquet's `(hash, tokens)` columns and joins them against the (correctly-sliced) source rows.

That's a **partial** outcome:

- ✅ Re-tokenisation is gone — the dominant cost. Tokens are computed exactly once.
- ⚠️ Each page still reads the full cache parquet (~MB scale for a 10 k-row corpus, ~tens of ms). Much better than seconds-to-minutes of Jieba / Lindera work, but not free.

Possible follow-up optimisations (out of scope here, but worth recording):

- **Per-source bucketed cache parquets.** Partition the cache by hash prefix (e.g. 16 files keyed by `hash >> 60`) so a slice that touches only one bucket reads ~1/16th of the data. Adds write-side complexity.
- **Two-pass collect.** API endpoint could compute the slice's content hashes first, then `scan_parquet(cache).filter(pl.col("__hash__").is_in(hashes))` to read only the needed rows. Bypasses the join entirely; needs a small helper in `tokens_cache`.
- **Statistics-driven parquet pruning.** Polars + Arrow already read parquet page-level statistics; writing the cache sorted by `__content_hash__` would let the scanner skip pages whose hash range doesn't overlap the slice's hash set. Single-line `.sort()` before `sink_parquet`.

None of these are urgent given the structural win the cache already delivers, but they are the natural next moves if profiling shows the parquet read becoming the bottleneck after Fix #2.

The functional test `test_tokens_cache::test_tokenise_column_slice_collect_returns_correct_tokens` pins the correctness invariant: sliced collects must still return matching tokens for the surviving rows.

---

## Tokens cache design

The cache is the structural fix for issue 2. It turns tokenisation from "an expression that re-runs forever" into "a one-time write, then a join." Design constraints come straight from the request:

1. **Location outside workspace-GC reach** — must survive `clear_workspace_artifacts_dir` and workspace deletion.
2. **Sharable across child blocks** with same / subset of rows.
3. **Sweepable** when no live node references it.

### Storage location

```
~/.cache/ldaca_wordflow/tokens/
    {cache_key}.parquet         # token data
    {cache_key}.manifest.json   # references + metadata
```

Matches the existing `~/.cache/ldaca_wordflow/spacy/` convention from [`quotation_extractor.py:32`](ldaca_wordflow/backend/src/ldaca_wordflow/core/quotation_extractor.py#L32). Workspaces live at `~/Documents/ldaca/...` ([`settings.py:32`](ldaca_wordflow/backend/src/ldaca_wordflow/settings.py#L32)); workspace GC operates entirely within that tree, so `~/.cache/...` is untouched.

Override via env var `LDACA_TOKENS_CACHE_DIR` for tests / Tauri sandboxing.

### Cache schema

One parquet per `(model, params)` combination. Schema:

| Column | Type | Notes |
|---|---|---|
| `__content_hash__` | `UInt64` | xxhash64 of the source string (Polars default `pl.col(...).hash()`) |
| `tokens` | `List<Struct{token: String, start: Int64, end: Int64}>` | The persisted tokens column |

**Cache key** is `sha256(f"{model}|lowercase={lc}|remove_punct={rp}")[:16]` — a short hex string used as the filename stem.

Why hash-keyed (not row-index-keyed): the source node's row order can change as users filter / sort / sample. Hashing the source content makes the cache **position-independent** — a child block that retains a subset of parent rows still hits every cached entry through a hash join.

### Tokenisation flow

```python
def tokenise_column(node, *, source_column, model, language) -> str:
    cache_key = compute_cache_key(model, lowercase=..., remove_punct=...)
    cache_path = cache_dir() / f"{cache_key}.parquet"
    manifest_path = cache_dir() / f"{cache_key}.manifest.json"

    # 1. Identify which source values are already cached
    src_lf = node.data.select(
        pl.col(source_column).alias("__src__"),
        pl.col(source_column).hash().alias("__h__"),
    )
    if cache_path.exists():
        cached_hashes = pl.scan_parquet(cache_path).select("__content_hash__").collect()
        new_rows = src_lf.join(
            cached_hashes.lazy().with_columns(pl.lit(True).alias("__cached__")),
            left_on="__h__", right_on="__content_hash__", how="left",
        ).filter(pl.col("__cached__").is_null()).unique(subset=["__h__"])
    else:
        new_rows = src_lf.unique(subset=["__h__"])

    # 2. Tokenise only the new rows
    new_tokens_df = new_rows.select(
        pl.col("__h__").alias("__content_hash__"),
        pt.tokenize_with_offsets(pl.col("__src__"), model=model,
                                 lowercase=should_lowercase(language, model),
                                 remove_punct=...).alias("tokens"),
    ).collect()

    # 3. Append-merge into the cache parquet
    if cache_path.exists():
        existing = pl.scan_parquet(cache_path)
        combined = pl.concat([existing, new_tokens_df.lazy()]).unique(subset=["__content_hash__"])
        combined.sink_parquet(cache_path.with_suffix(".tmp.parquet"))
        cache_path.with_suffix(".tmp.parquet").replace(cache_path)
    else:
        new_tokens_df.write_parquet(cache_path)

    # 4. Replace node.data with a plan that joins the cache by content hash
    derived_name = derived_column_name(TOKENS_FORM, source_column, model)
    new_lf = (
        node.data
        .with_columns(pl.col(source_column).hash().alias("__h__"))
        .join(
            pl.scan_parquet(cache_path).rename({"__content_hash__": "__h__", "tokens": derived_name}),
            on="__h__", how="left",
        )
        .drop("__h__")
    )
    node.data = new_lf

    # 5. Register reference in manifest
    register_reference(manifest_path, user_id, workspace_id, node.id, source_column)

    node.register_derived_column(derived_name, {..., "cache_key": cache_key})
    return derived_name
```

### Sharing across child blocks

Falls out for free. When a user filters / sorts / sub-selects the parent node, the child node's `data` LazyFrame still contains the `with_columns(...).join(scan_parquet(...), on="__h__")` segment. The polars optimiser pushes filters past joins where it can, and the hash key carries through any operation that preserves rows. Result:

- **Filter** on parent → child reads only matching cached rows.
- **Sort / shuffle** on parent → child reads cache by hash, gets the same tokens.
- **Sample column subset** that still includes the source column → cache still joins.
- **Drop the source column** without re-deriving → child carries the tokens column directly (the `with_columns` step pre-joined them).

The only edge case where sharing breaks is if a transformation modifies the source column's *content* (e.g. lower-casing it before tokenising). Such transforms should be marked "tokens-invalidating" on the Node side and trigger a re-derive — captured in `register_derived_column` metadata.

### Manifest schema (`{cache_key}.manifest.json`)

```json
{
  "model": "lindera-ja-ipadic",
  "params": {"lowercase": false, "remove_punct": true},
  "created_at": "2026-05-15T07:00:00Z",
  "last_accessed": "2026-05-15T09:14:32Z",
  "references": [
    {"user_id": "u123", "workspace_id": "ws456", "node_id": "n789",
     "source_column": "text", "derived_column": "__derived__.tokens.text.lindera-ja-ipadic",
     "registered_at": "2026-05-15T07:00:00Z"}
  ]
}
```

References are added in `tokenise_column`, removed in `delete_derived_column` and on node / workspace deletion. The manifest is the source of truth for whether a cache file is live.

### Sweep / GC

Three layers, increasing strength:

1. **Per-reference removal** — surgical, synchronous. On `delete_derived_column`, `delete_node`, `delete_workspace`, walk the affected references and drop them from the manifest. If `references` is empty AND `last_accessed` is older than `LDACA_TOKENS_CACHE_TTL_DAYS` (default 7), delete both files in the same call. Keeps the cache responsive to user-driven cleanup.

2. **Startup sweep** — defensive. On backend boot, walk `~/.cache/ldaca_wordflow/tokens/`, for each `*.manifest.json` verify each referenced `(user, workspace, node)` still exists. Drop stale references. Delete files whose `references` end up empty AND `last_accessed` is past the TTL. Catches references stranded by crashes or out-of-band workspace deletion.

3. **Row-level compaction (deferred)** — not in MVP. If a cache parquet accumulates many rows from short-lived workspaces, a `lf.filter(__content_hash__.is_in(live_hashes)).sink_parquet(...)` rewrite can reclaim within-file space. Out of scope for this branch; revisit if cache parquets grow unmanageably.

The MVP ships layers 1 and 2.

### Concurrency

The cache parquet is rewritten via tmp-file-then-replace (atomic on POSIX). The manifest uses an exclusive `flock` (best-effort on Linux/macOS) around the read-modify-write. Concurrent tokenise calls on different `(model, params)` combinations are isolated by cache key. Concurrent calls on the *same* combination race on the cache file — the loser sees the winner's tokens on its next read and skips them.

---

## Execution order

Each step ends with `cargo test` (Rust) or `uv run pytest -q` (Python) and a commit. Commits stay in the submodule; pointer bumps in `ldaca_wordflow` and master are batched at the end.

1. **Branches** — `perf/cjk-tokeniser` in `polars-text` (off `multilingual`), `backend` (off `v0.4`), `ldaca_wordflow` (off `v0.4`).
2. **Fix #1** (Rust, polars-text) — rewrite `byte_to_char_idx` + call-site rework in `tokenize_text_with_offsets`. Verify with the existing `test_jieba_offsets_reconstruct_chinese` test and add a Lindera-path regression test.
3. **Fix #4** (Python, backend) — branch on language / model in `tokenise_column` to pass `lowercase=False` for CJK. (Defence-in-depth Rust change deferred unless a path that bypasses backend control appears.)
4. **Fix #5** (Rust, polars-text) — flat list-of-struct builder in `tokenize_with_offsets`. Verify with existing tests + benchmark before/after on a 1k-row CJK fixture.
5. **Fix #2** (Python, backend) — tokens cache: storage layout, cache key, write path, read-back join, reference manifest, sweep helper. New tests for cache hit/miss, sharing across child nodes, sweep behaviour.
6. **Fix #3** (Python, backend) — rewrite `calculate_token_frequencies` to pass a LazyFrame / cache path to the worker; rewrite the worker to compute frequencies in Polars. Existing token-frequency goldens should stay green.
7. **Fix #6** (manual) — run `.explain()` on a tokenised plan post-fix to confirm slice pushdown. Documented here; result captured in a follow-up note.
8. **Pointer bumps** — bump `polars-text` and `backend` SHAs in `ldaca_wordflow`; bump `ldaca_wordflow` SHA in master. Each bump is its own commit.

## What does NOT change

- Public Python API of `polars-text` (function signatures, kwargs). Internal Rust changes only.
- Tokens column schema (`List<Struct{token, start, end}>`). Backwards-compatible with persisted workspaces.
- Wordflow's frontend. No UI changes needed.
- The legacy English (BERT) path remains correct; it benefits from fixes 1 + 5 incidentally.

## Out of scope

- Row-level cache compaction (deferred).
- A Tauri-side cache path override (the env var is enough for now; Tauri builds can set it).
- Streaming engine flag (`engine="streaming"`) — separate investigation; current fixes don't require it.
- Caching for non-tokens derived columns. The cache module should be generic enough to extend later but only `TOKENS_FORM` ships here.

## Validation gates (per commit)

- Rust: `cargo build --release` + `cargo test` in `polars-text/`.
- Python: `uv run pytest -q tests/` in `backend/` (full suite, not just the touched module — `Verify between commits in multi-commit refactors` lesson from prior god-file work).
- Pointer bumps: `git submodule status --recursive` clean before and after.
