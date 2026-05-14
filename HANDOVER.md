# Handover — what changed since 2026-04-25

For Alex (Senhui Guo) and his coding agent, on return from leave. This summarises the substantive work landed in the LDaCA text-analytics tools between Alex's last commit (parent `4087f05`, 2026-04-25) and the master-repo migration (today, 2026-05-15). The intent is to bridge the gap quickly — read this once, then trust the per-repo `AGENTS.md` files for working conventions.

> **Volume note.** ~415 commits across `ldaca_web_app` plus heavy work in `backend/`, `docworkspace/`, and `polars-text/`. This doc covers the load-bearing changes, not every fix. For full detail, the per-version `CHANGELOG.md` entries (currently 0.2.6 through 0.4.1) are the user-facing record; `git log v<prev>..v<next>` is the engineering record.

## TL;DR

1. **New active release line `v0.4` (multilingual)** — `main` is parked at v0.3.5; production now lives on the `v0.4` branch of `ldaca_web_app` and its docs counterpart. PyPI's `latest` is `0.4.1`.
2. **Multilingual support shipped end-to-end** — Japanese, Korean, Chinese (Simplified/Traditional), Vietnamese, and the major European languages now flow through concordance, token frequency, topic modelling, and AI annotation with language-appropriate tokenisation + stopwords.
3. **Docs + sample data became sibling repos** — `frontend/src/docs/*` was extracted into `ldaca-analytics-docs` (runtime-fetched at view time via a docs registry with bundled fallback). Sample datasets moved to `ldaca-analytics-sample-data` and are downloaded on demand.
4. **Major submodule version bumps:** `backend` v0.1.26 → v0.4.1, `docworkspace` v0.2.5 → v0.2.8, `polars-text` v0.1.4 → v0.2.0.
5. **The master repo (this one) is being promoted** to the primary working root so agent sessions can make atomic cross-repo commits — see [AGENTS.md](AGENTS.md) and [MIGRATION_PLAN.md](MIGRATION_PLAN.md).

## Submodule version moves

| Submodule | At `4087f05` (Alex's last) | At v0.4.1 | Net change |
|---|---|---|---|
| `backend` | `c7e56aa` (v0.1.26) | `f656e2f` (v0.4.1) | Huge — new analyses, multilingual stack, MPS/ONNX embedders, CILogon auth, ui_state sidecar |
| `docworkspace` | `45f6318` (v0.2.5) | `3e6f0fa` (v0.2.8) | Derived-column registry (`Node.derived`), per-column metadata, propagation through all node ops |
| `polars-text` | `7fb74ed` (v0.1.4) | `e9664f9` (v0.2.0 + 1 CI fix) | Lindera (JA/KO) + Jieba (ZH) tokenisers, feature-gate broadening for full DslPlan coverage |
| `ldaca-tabulator` | n/a (was inline) | `ea1a4a7` | Now a proper submodule; provides the data-loader |

> The version-number jumps for `docworkspace` and `polars-text` look small relative to the backend's, but that's their natural cadence — they're foundational libraries that turn over less often. The numeric distance understates the content change; the "Net change" column is the better signal. Most of `docworkspace` v0.2.6, v0.2.7, and v0.2.8 are derived-registry work landed across multiple commits per release.

## Architectural changes

### 1. Docs moved out of the web app

Before: tutorials and reference pages lived under `ldaca_web_app/frontend/src/docs/` and were bundled into the JS app. Updating a tutorial required a frontend rebuild + release.

After: docs live in [`ldaca-analytics-docs`](https://github.com/Australian-Text-Analytics-Platform/ldaca-analytics-docs) with version branches mirroring the web app (`v0.3`, `v0.4`). The web app fetches them at runtime via a **docs registry** with a stale-while-revalidate cache and a bundled-fallback path — so users see the latest tutorial without redeploying the app, and offline users still get the bundled version. The registry also drives an end-of-life banner when a docs version is past its support window.

Frontend env var: `VITE_DOCS_BASE_URL=https://australian-text-analytics-platform.github.io/ldaca-analytics-docs/v0.4` (set in `frontend/.env`, committed). Updated per minor version, not per patch.

### 2. Sample data moved to its own repo

Before: Reddit sample datasets were bundled inside the Python wheel.

After: [`ldaca-analytics-sample-data`](https://github.com/Australian-Text-Analytics-Platform/ldaca-analytics-sample-data) hosts the catalogue. The web app's **Add Sample Data** panel is now a multi-collection picker driven by `/api/sample-data/catalogue` (a backend endpoint that proxies the remote `catalogue.json`). Datasets download on demand the first time a user selects them. Cut tens of MB off the install size.

### 3. New `v0.4` release line, parallel to `main`

`main` on every repo is parked at the v0.3.5 state for users who want the legacy stable line. All multilingual work lives on a `v0.4` branch (or `multilingual` upstream of v0.4 — see commit graph). PyPI's "latest" pointer resolves to v0.4.1. The Nectar VM deploy now targets `v0.4`.

This is non-traditional (tags usually live on `main`); the rationale is that multilingual is a substantial architectural shift and the team wanted v0.3 users protected from accidental upgrades during the transition. Expect `v0.4` (and future `v0.5`, etc.) to be the long-term pattern.

### 4. Persistent UI state per workspace

New backend endpoint: `GET / PUT /workspaces/{id}/ui-state` writing a free-form JSON sidecar at `<workspace_dir>/ui_state.json`. Deliberately separate from docworkspace's `metadata.json` so the data-model serialisation stays free of UI concerns. The frontend currently writes only the assigned node-colour map; future presentation prefs (column visibility, layout) land here without a backend release.

## Major feature areas

### Multilingual stack (Phases 0–5)

Tracked under `frontend/docs/pluggable-tokeniser/PLAN.md` (now archived; the plan is complete). Key shipped pieces:

- **Phase 0**: Test fixtures for EN/JA/ZH golden snapshots.
- **Phase 1**: `polars-text` v0.2.0 with Lindera (JA dict variants: `ipadic`, `unidic`, `jumandic`; KO: `ko-dic`) and Jieba (ZH) tokenisers. Dictionaries fetched on demand from a separate LDaCA-hosted registry (`SIH/lindera-dicts`).
- **Phase 2**: `docworkspace` Phase 2.x v2 — derived-column registry (`Node.derived` dict + per-column metadata), propagation through `clone`/`filter`/`slice`/`concat`/`join`/expression operations. Backend endpoints for `POST / DELETE` derived columns.
- **Phase 3**: Language-routed topic-modelling embedder. Language hint in AI-annotation prompt. Per-corpus stopword merging.
- **Phase 4**: Frontend integration — language selector at import, defaultLanguage/defaultTokenizerModel preferences, Tokenise action on graph node, derived-columns dialog, search-mode toggle (text/tokens) on concordance, English-only gate on quotation.
- **Phase 5**: Lindera dict selector UI + JA/KO defaults, dict hosting on `SIH/lindera-dicts`.

User-visible result: every analysis tool works correctly on CJK corpora, with substring matching auto-disabled where it's meaningless.

### Node-colour strategy (Phases A–C; D was attempted then reverted)

Frontend-only feature. Each workspace node now carries an X/Y shade pair from a 12-colour palette, persisted per workspace via the `ui_state.json` sidecar. Three visual states (Active / Focus / Unselected) plus a "fresh" outline for newly-created nodes. Manual picks preview via a per-tab temp layer before *Run* commits them.

Design doc: `frontend/docs/developer-guide/node-colour-strategy.md`. **Phase D** (re-roll auto temps on manual-pick conflicts) was implemented and reverted because it broke graph colouring — kept as a no-op pair in git history.

### Topic modelling overhauls

- **Topic-size modes**: Aim Topic No. (soft target) / Min Topic Size (exact min) / Exact Topic No. (post-fit re-aggregation with a slider 2..raw_count).
- **Per-corpus sampling** with auto-suggested fractions, RNG aligned with the preprocessing slice tool (`pl.int_range(N).sample(seed=...)`).
- **ONNX embedder** for Windows/Linux/Intel Mac (quantised, faster than the previous PyTorch path) + **MPS embedder** for Apple Silicon (~3× faster cold-runs).
- **SHA-256-keyed embedding disk cache**, configurable + clearable via UI (Clear Embedding Cache in sidebar's Edit-visible-views menu). Per-chunk progress during embedding (every 10 chunks of 512 docs).
- **Stop button** that cancels via SIGTERM (new `/tasks/cancel` endpoint).
- **Online pipeline** (IncrementalPCA + MiniBatchKMeans) via `force_mode="online"` for memory-bound corpora.
- **Post-fit stopword filter** + **Words-per-topic slider** scaling up to `max(50, 2×setting)`.
- **Detach exports renamed topic words** via `topic_meanings_override` (with per-corpus filtering on the v0.4 line — semantic difference vs main, see `backend/src/ldaca_web_app/api/workspaces/analyses/topic_modeling.py`).
- **Embedder revision pinning** to a specific HuggingFace revision (was tracking `main` implicitly). Optional `scripts/check_model_updates.py` for guided revision bumps.
- **MPS prefetch optimisation** — probe HuggingFace cache locally first, skip network HEAD when cached.

### Authentication

- **CILogon OIDC** (AAF-federated) added alongside Google OAuth. Configured via `CILOGON_CLIENT_ID` / `CILOGON_DISCOVERY_URL` / `CILOGON_REDIRECT_URI`. Currently in test config; awaiting production credentials from Moises (ARDC/AAF).

### Concordance

- **Search-mode toggle** (text / tokens). Text-mode is the existing substring matcher; tokens-mode joins against the derived tokens column and is required on CJK corpora.
- **Whole-word toggle suppressed** on CJK nodes per-node.
- **`CONC_extraction` column** on detached results.
- **Legend-filtered detach** when a chart legend filter is active.
- **Dispersion endpoint** `/bins` with 100-bucket histogram.
- **Per-document aggregated detach** + auto-materialise.
- **Per-source `model` picker** when N>1 derivations exist on the same source.
- **KWIC alignment**: left-context right-aligned, matched-text centred, so the keyword runs as a clean vertical band.

### Quotation

- **`QUOTE_extraction` column** + frontend rename.
- **English-only gate** with disabled-with-tooltip on non-English corpora.

### Token frequency

- **Apply Stop Words** uses corpus language (not a global default).
- **Multi-corpus stopword merging** when languages differ across the working set.
- **Cap selector to 2 corpora**; results pane labelled "Keyword Analysis".

### Sequential analysis

- **Linear-axis ticks denser**; missing time-group buckets zero-filled.

### Workspace graph

- **Batch Delete (N)** replaces the toolbar's Save button (workspaces autosave; Save was redundant).
- **Virtual super-source** for layout — multi-root workspaces left-anchor uniformly.
- **Tokenise** action via right-click on a node.
- **Per-node *Manage derived columns*** dialog.
- **Node-colour strategy** end-to-end (see above).

### Export

- **Workspace name** instead of UUID in the panel header.
- **Per-data-block UUID line dropped** — name + shape is enough context.
- **`__derived__.*` columns hidden** from exported files.

### Detach dialog

- **Analysis column highlighted** (bold).
- **Topic-modelling detach gated** until ≥1 metadata column picked.
- **`__derived__.*` columns hidden** in detach pickers + row-detail dialogs.

## Operational lessons (read these before similar work)

### docworkspace drift (resolved in v0.4.1)

The web app's `backend/pyproject.toml` carried `[tool.uv.sources] docworkspace = { path = "../docworkspace", editable = true }`. Local validation passed because uv resolved docworkspace from the sibling clone (which had unpublished commits past the v0.2.7 tag). The **published wheel** declared only `docworkspace>=0.2.7`, so PyPI users got the un-patched 0.2.7 and crashed on the tokenise / concordance-tokens-mode / CJK topic-modeling paths.

**Fix**: published `docworkspace==0.2.8` from its `multilingual` branch (commit `3e6f0fa`), bumped the web app to `docworkspace>=0.2.8`, and removed the path-source override.

**Lesson**: path-source overrides mask drift in local builds but not in published wheels. Before any release with a path source active, either bump+republish the dep or remove the override and verify the PyPI-resolved install. Validation command:

```bash
uvx --refresh --from ldaca-web-app==<version> python -c \
  "from importlib.metadata import version; print(version('docworkspace'))"
```

### Polars-text feature gates

Every new polars op may require a `polars-plan` Cargo feature in `polars-text`. Missing one breaks workspace save/load at deserialise time with `unknown variant 'XXX'`. The fix is always: enable the matching feature in `polars-text/Cargo.toml`, republish.

### Release branch strategy

Releases now happen from dedicated `v0.4` branches (web app, docs), not `main`. `main` stays parked at v0.3.5 for legacy consumers. This was an explicit user preference after seeing multilingual diverge from the stable line; expect it to continue. Tag the release on `v0.4`, push the tag — that's what triggers PyPI (backend repo) and Tauri desktop builds (parent repo) workflows.

### Frontend version is baked in at build time

`import.meta.env.VITE_APP_VERSION` (from `frontend/package.json`) is referenced by `DocumentView.tsx` (markdown placeholder substitution) and `FeedbackPanel.tsx` (feedback context). **Bump `package.json` BEFORE `npm run build`** — Vite tree-shakes the literal into the bundle and changes after the build are invisible.

Verification: `grep -c '"?X\.Y\.Z"?'` on the unpacked bundle; expect hits in `DocumentView-*.js` and `FeedbackPanel-*.js`. Zero hits means you built before bumping.

### Releases that shouldn't have shipped

- **v0.4.0 on PyPI is yanked.** Same-day hot-fix as v0.4.1 because of the docworkspace drift above. v0.4.0's GitHub release page is annotated with a "Superseded by v0.4.1" banner. Tauri desktop builds for v0.4.0 also went out (the desktop pipeline doesn't pin docworkspace per-platform — same content issue).

## Release timeline

| Tag | Date (AEST) | Theme |
|---|---|---|
| v0.2.1 → v0.2.5 | 2026-04-26 → 2026-05-03 | Foundational backend work; pre-CHANGELOG |
| v0.2.6 | 2026-05-04 | Xlsx export fix + feedback survey v2 |
| v0.2.7 | 2026-05-05 | Topic-modelling optimisation release (ONNX/MPS, sampling, online pipeline) |
| v0.2.8 | 2026-05-05 | Token-frequency UI overhaul; tutorials unified |
| v0.2.9 | 2026-05-06 | CILogon OIDC; embedding cache UX |
| v0.3.0 → v0.3.2 | 2026-05-07 → 2026-05-12 | Concordance extraction column; topic-meanings override; detach gating |
| v0.3.5 | 2026-05-14 | Sample-data catalogue; docs registry; workspace-graph polish |
| v0.4.0 | 2026-05-15 | Multilingual stack + node-colour strategy — **YANKED on PyPI** |
| v0.4.1 | 2026-05-15 | docworkspace>=0.2.8 hot-fix; functionally what v0.4.0 should have been |

## Open follow-ups

- **Nectar VM deploy of v0.4.1** is pending (manual step). The VM currently runs the v0.3.5 line; switching it over is a `git checkout v0.4 && git submodule update --init --recursive --checkout --force && sudo systemctl restart ldaca-web-app` on the deploy host.
- **CILogon prod credentials** — awaiting Moises (ARDC/AAF). The `cilogon` config is in the test config; flip `CILOGON_DISCOVERY_URL` once prod credentials land.
- **Pluggable-tokeniser PLAN.md** — Phase 5 is the last marked phase. If you have additional tokeniser dictionaries to host, follow the existing `SIH/lindera-dicts` pattern.
- **`ai_annotator/` at the master root** appears empty — confirm and remove.

## Where the agent context lives

- This master repo: [AGENTS.md](AGENTS.md), [MIGRATION_PLAN.md](MIGRATION_PLAN.md), this file.
- Web app: `ldaca_web_app/AGENTS.md`, `ldaca_web_app/DEPLOY.md`.
- Docs site: `ldaca-analytics-docs/` (its own README + branch-per-version layout).
- Sample data: `ldaca-analytics-sample-data/` (catalogue.json is the entry point).

Saved memory under `~/.claude/projects/...` carries operational lessons (release cadence, verify-between-commits, polars-text feature gates, etc.) and should travel with whichever working folder the agent opens.
