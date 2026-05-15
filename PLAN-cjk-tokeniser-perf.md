# CJK Tokeniser Performance — Investigation & Fix Plan

**Branch:** `perf/cjk-tokeniser` (created in `ldaca_wordflow`, `ldaca_wordflow/backend`, `ldaca_wordflow/polars-text`)
**Started:** 2026-05-15
**Base:** `v0.4` (Wordflow + backend) / `multilingual` (polars-text)

## Symptom

After the new CJK tokeniser (Jieba for zh, Lindera for ja/ko) was added in polars-text 0.2.0, the app became significantly slower and RAM consumption spiked, despite the LazyFrame architecture being intact.

## Root causes (ordered by impact)

### 1. O(N²) byte→char offset conversion — JA/KO specific

[`polars-text/src/tokenizer.rs:141-143`](ldaca_wordflow/polars-text/src/tokenizer.rs#L141-L143):

```rust
fn byte_to_char_idx(text: &str, byte_idx: usize) -> usize {
    text.char_indices().take_while(|(b, _)| *b < byte_idx).count()
}
```

Called twice per token from `tokenize_text_with_offsets` for the Lindera and HuggingFace branches. Each call re-walks `char_indices()` from byte 0 → token's byte offset. For an N-token document this is `Θ(N²·avg_token_chars)`. A 10 000-char Japanese article with ~5 000 morphemes ≈ 5×10⁷ char-iterations per document; over 10 000 docs ≈ 5×10¹¹ iterations.

The Jieba (zh) branch uses `t.start` / `t.end` directly from `jieba_rs::TokenizeMode::Default` — already char offsets, so zh is fast. **Only JA/KO regress.**

**Fix:** single forward sweep — accumulate char count by stepping through `char_indices()` once per document, and zip each Lindera/HF token's byte offsets against a running pointer. `O(C + N)`.

### 2. Unnecessary `to_lowercase()` for CJK

[`polars-text/src/tokenizer.rs:44-48`](ldaca_wordflow/polars-text/src/tokenizer.rs#L44-L48) unconditionally allocates a fresh `String` and walks the entire text doing Unicode case folding when `lowercase=true`. The Python wrapper defaults `lowercase=True` and the backend never overrides it.

CJK has no case. For Chinese/Japanese/Korean every row pays a full alloc + Unicode lowercase walk that does nothing useful.

**Fix:** in [`backend/src/ldaca_wordflow/core/derived_columns.py`](ldaca_wordflow/backend/src/ldaca_wordflow/core/derived_columns.py), pass `lowercase=False` when the model is `jieba` / `lindera-*` (or when `language in {"zh","ja","ko"}`). Also add a defensive short-circuit in the Rust `tokenize_text_with_offsets` so passing `lowercase=true` with `model_id ∈ {jieba, lindera-*}` is a no-op.

### 3. Per-row Series construction in the list builder

[`polars-text/src/expressions.rs:255-272`](ldaca_wordflow/polars-text/src/expressions.rs#L255-L272) calls `struct_series_from_tokens` once per input row, allocating three fresh `Series` + a `StructChunked` + validity metadata, then appending via `AnonymousOwnedListBuilder::append_series` which concats them. 10 k rows × ~1 k tokens ≈ 30 k throwaway allocations.

**Fix:** flat builder. Keep three growable `Vec<>`s (`tok`, `start`, `end`) plus one `Vec<i64>` of list-boundary offsets across the whole chunk, then construct one `ListChunked<StructChunked>` at the end. Standard idiom for plugin list-of-struct outputs.

### 4. Token frequencies fully collects + materialises to Python objects

[`backend/src/ldaca_wordflow/api/workspaces/analyses/token_frequencies.py:464-473`](ldaca_wordflow/backend/src/ldaca_wordflow/api/workspaces/analyses/token_frequencies.py#L464-L473):

```python
tokens_df = node_data.select(...).collect()
node_tokens[node_id] = [[str(tok) ...] for row in tokens_df[...].to_list()]
```

Full collect, then materialises every token as a Python `str` (~50 B overhead vs ~16 B Arrow), then pickles the list of lists to a worker. 10 k docs × ~1 k tokens ≈ 10 M PyObjects ≈ ~500 MB pure overhead.

**Fix:** ship the LazyFrame (or the cached tokens parquet path from §5 below) to the worker. Inside the worker, compute frequencies with `pl.col(...).list.eval(pl.element().struct.field("token")).explode().value_counts()` and sink to parquet. No Python materialisation.

### 5. Tokenisation re-runs on every page / probe / collect

[`backend/src/ldaca_wordflow/core/derived_columns.py:57-71`](ldaca_wordflow/backend/src/ldaca_wordflow/core/derived_columns.py#L57-L71) only appends the `tokenize_with_offsets` expression to the lazy plan — no materialisation. Every downstream `.collect()` re-executes the tokeniser. With `is_elementwise=True` the slice should push past `with_columns`, so per-page concordance only re-tokenises page rows; but:

- The page-size estimator probes the candidate ladder multiple times per request
- `_count_tokens_concordance_hits` does `base_lf.select(derived_column).slice(0, size).collect()`
- Token frequencies (§4) bypasses any laziness by collecting everything

**Fix: persistent tokens cache.** See dedicated section below.

### 6. Verify slice pushdown

Run `node.data.slice(0, 20).explain(optimized=True)` on a tokenised node to confirm the planner pushes the slice past `with_columns`. If not, every page collect tokenises the entire corpus regardless of fixes 1–5.

## Tokens cache — design

User-specified requirements:
1. Store outside the workspace garbage collector's reach.
2. Sharable by child data blocks with same/subset columns of the same source.
3. Sweep when no live data block references it.

### Cache location

`~/.ldaca/tokens-cache/` (mirrors `~/.cache/ldaca/lindera/` used by polars-text). **Outside per-user/per-workspace directories** so workspace deletion or workspace GC never touches it. Path is user-scoped (one cache per OS user), not workspace-scoped.

### Cache key & schema

Each cache entry is a parquet file with content-defined identity:

- **Filename:** `{model}__{params_hash}__{source_hash}.parquet`
  - `model`: e.g. `jieba`, `lindera-ja-ipadic`, `bert-base-uncased`
  - `params_hash`: sha256(json({lowercase, remove_punct}))[:12]
  - `source_hash`: sha256 of the source column's content fingerprint (see below)
- **Schema:** `{__content_hash: u64, tokens: List<Struct{token, start, end}>}`
  - The per-row `__content_hash` is `pl.col(source_column).hash()` — fast 64-bit xxhash
  - Storing the per-row hash lets child blocks share the cache via a hash-join even after filter / sort / column-select

The **source fingerprint** for the filename is computed once at tokenise time:

```python
source_hash = sha256(b"|".join(
    str(h).encode() for h in source_lf.select(pl.col(col).hash()).collect()[col].to_list()
))[:16]
```

This makes the cache identity content-defined: two corpora with the same text in the same order produce the same hash, hence one shared cache file. Different orderings still share *rows* via the per-row `__content_hash`.

### Lazy-plan integration

`tokenise_column` replaces the in-plan `tokenize_with_offsets` expression with a cached read:

```python
cache_path = ensure_tokens_cache(source_lf, source_column, model, params)

cache_lf = pl.scan_parquet(cache_path)
new_lf = (
    source_lf
    .with_columns(pl.col(source_column).hash().alias("__content_hash"))
    .join(cache_lf, on="__content_hash", how="left")
    .drop("__content_hash")
    .rename({"tokens": derived_name})
)
node.data = new_lf
```

**Sharing**: any child block derived from this node by filter / select / sort inherits the lazy plan including the join. Child blocks that retain a subset of rows automatically retrieve only their rows from the cache; child blocks that drop the tokens column never touch the cache parquet (projection pushdown).

**Missed rows**: if a child block was filtered before tokenisation and is tokenised later from the same source, the `__content_hash` matches the parent's rows → full reuse. New rows that don't match any cached hash get `tokens = null`; we compute those on the fly and append to the cache parquet (concat + dedup write).

### Reference tracking & sweep

A sidecar manifest `~/.ldaca/tokens-cache/manifest.json` maps each cache filename to a list of references:

```json
{
  "lindera-ja-ipadic__a1b2c3__deadbeef.parquet": {
    "size_bytes": 1234567,
    "created_at": "2026-05-15T10:00:00Z",
    "last_accessed_at": "2026-05-15T12:34:00Z",
    "references": [
      {"user_id": "u1", "workspace_id": "ws-abc", "node_id": "n-xyz"}
    ]
  }
}
```

- `tokenise_column` adds the `(user, workspace, node)` triple to the cache entry's `references`
- `delete_derived_column` and node-deletion paths remove the matching reference
- Workspace deletion drops all references under that workspace
- **Sweep** runs at backend startup and after any workspace delete: any cache file with `references == []` AND `last_accessed_at > 7 days ago` is deleted. The 7-day grace prevents thrashing when a user closes & reopens a workspace.
- Optional secondary cap: total cache size limit (e.g. 5 GiB), LRU-evict by `last_accessed_at` when exceeded.

### Concurrency

Cache writes are rare (only on tokenise) and idempotent. Use a per-cache-file `flock` (advisory file lock) to serialise writers. Reads via `scan_parquet` are safe under POSIX read-while-write on stable files; the write path is atomic write-to-temp + rename.

## Fix order & checkpoints

Each step ends with a commit on the perf branch.

| # | Step | Repo | Validation |
|---|------|------|------------|
| 1 | Branch creation | all three | `git branch --show-current` |
| 2 | Plan committed | master | this file |
| 3 | O(N²) byte→char fix | polars-text | `cargo test` (existing offset tests) |
| 4 | Lowercase short-circuit (Rust) + CJK skip (Python) | polars-text + backend | `cargo test` + `uv run pytest tests/` scoped |
| 5 | Flat list-of-struct builder | polars-text | `cargo test` — offset round-trip identical |
| 6 | Tokens cache module (read/write/manifest) | backend | new unit test |
| 7 | Wire cache into `tokenise_column` | backend | existing derived-columns tests |
| 8 | Cache reference add/drop hooks | backend | new unit test |
| 9 | Sweep routine + startup hook | backend | new unit test |
| 10 | Token frequencies — drop Python materialisation, use cache | backend | existing token-freq tests |
| 11 | Master submodule pointer bumps | master | `git submodule status` |

Per-commit rules:
- Build green (Rust: `cargo build`, Python: import smoke + scoped pytest)
- No `--no-verify`; respect pre-commit hooks
- Commit message: `perf(cjk): <what> — <why>` style
- Do **not** push until the user reviews

## Open questions for follow-up

- Should the source fingerprint include row order (`sha256` of concatenated hashes) or be order-invariant (`sha256` of sorted hashes)? Order-invariant maximises sharing but loses the "same hash = same parquet readable directly" property. Starting with order-sensitive; revisit if cache hit rate is poor.
- Cache size cap default — 5 GiB feels right for desktop / Tauri; cloud deploys may want different. Make it env-overridable.
- Cross-process safety on Windows: `flock` is POSIX-only. The Tauri build needs the `fcntl`-free equivalent (e.g. `fs2` crate or a simple lockfile-with-retry on Python side).

## Out of scope for this branch

- Streaming-engine opt-in (`collect(engine="streaming")`) — separate concern, can land later
- Materialised concordance parquet integration with tokens cache — Phase 2.6 already has a materialised path for regex mode; tokens mode currently doesn't materialise. Defer to a follow-up.
- POS / NER derived columns — same caching strategy applies but they're not the current pain point.
