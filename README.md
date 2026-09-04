# LDaCa Text Analytics Tools

This repository publishes notebook-first Binder launches for pinned
[LDaCA Wordflow](https://pypi.org/project/ldaca-wordflow/) releases
(formerly `ldaca-web-app`), alongside versioned Tauri desktop downloads
for the same published versions. Use the latest section for the newest
published environment, or pick a specific historical version when you
need a stable, versioned setup.

> **Renamed at v0.4.2:** the PyPI package, Python module, GitHub repo, and
> Tauri product name all flipped from `ldaca-web-app` / "LDaCA Text Analytics"
> to `ldaca-wordflow` / "LDaCA Wordflow". `pip install ldaca-web-app==0.4.2`
> still works (one-shot shim depending on `ldaca-wordflow==0.4.2`); future
> 0.5+ releases ship only to `ldaca-wordflow`.

## Latest

- Published (AEST): 2026-09-03
- Package: `ldaca-wordflow@0.7.7` (ECharts word clouds, Liquid Glass desktop styling, and workspace schema versioning; see "What's new" below)
- ARDC BinderHub: [![Binder](https://mybinder.org/badge_logo.svg)](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/7364496?labpath=index.ipynb)
- Desktop app — bundled installers that include the backend runtime: [Windows](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.7/ldaca-wordflow_0.7.7_windows-x86_64.msi) · [macOS (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.7/ldaca-wordflow_0.7.7_darwin-aarch64.dmg)
  - The macOS app is Developer ID signed and notarized. On Windows you may see a security prompt — choose "More info" → "Run anyway".
- Run locally: `uvx --refresh ldaca-wordflow@0.7.7`

## Binder launch

The Binder image installs the pinned `ldaca-wordflow[deploy]` release, which
includes Jupyter Server Proxy support. Run `index.ipynb` to start the packaged
frontend and backend together on loopback port `8001`; the notebook displays
its authenticated `/proxy/8001/` link and includes a shutdown cell. Changing
the notebook's `PORT` to `3000` produces the corresponding `/proxy/3000/` URL.
The notebook computes that deployment path and passes it to Wordflow as a
generic ASGI `root_path`; Wordflow itself does not infer JupyterHub settings.
Binder storage is session-scoped unless the operator provides a persistent
mount and `DATA_ROOT` points into it.

## What's new in v0.7.7: ECharts word clouds, Liquid Glass desktop styling, and workspace schema versioning

- **Word clouds are now rendered with ECharts**, with native sizing and layouts that fit every configured term instead of dropping the largest ones.
- **A refreshed desktop identity:** the new Liquid Glass Wordflow icon, a macOS Liquid Glass backplane, and one shared application header across the browser and desktop builds.
- **Workspaces move to the vNext contracts with granular schema versioning**, and the native text packages advance to the polars-text 0.6 contracts.
- **Annotation uses provider-aware inference settings**, so temperature and related options follow what each AI provider actually accepts.
- **Fixes:** Data Block colours persist immediately, the app reloads after Data Root changes, chart interaction states are shared across analyses, Trends hover emphasis is softened, desktop exports use the native save dialog again, backend diagnostics now reach the frontend, and CILogon sign-in accepts accounts without a verified-email claim.

See the [v0.7.7 release](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/tag/v0.7.7) and [full changelog](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/compare/v0.7.6...v0.7.7) for details.

## What's new in v0.7.6 — unified updater, live Data Root switching, and desktop navigation

- **A unified desktop updater** checks for signed releases, shows Markdown release notes and download progress, and supports automatic checks, skip, later, and restart-to-install flows in one dedicated window.
- **Data Root changes now happen inside the running backend process**, with a coordinated drain and reinitialization instead of restarting the desktop backend.
- **The macOS desktop window has VS Code-style navigation and quick access**, including back/forward history and analysis-tab search in a seamless draggable title bar.

See the [v0.7.6 release](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/tag/v0.7.6) and [full changelog](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/compare/v0.7.5...v0.7.6) for details.

## What's new in v0.7.5: Trends filtering and selection blocks, unified Annotation comparisons, desktop hardening

Covers v0.7.3 to v0.7.5 (the three bug-fix releases shipped on 27 and 28 August 2026 ahead of the online workshop).

- **Trends:** result-level filtering, small-group filtering with a configurable "Other" legend, and chart selections that publish straight to the workspace as new Data Blocks; analysis charts migrated to ECharts.
- **Annotation:** comparison labels and filters unified across the Preview and Review surfaces (Compare To, difference and existence filters, value display).
- **Frequency and Topic Modelling:** result-wide token filtering, virtualised full vocabulary lists, and a shared Add to Workspace dialog for topic selections.
- **Workspaces and Data Blocks:** per-workspace backend ownership, unified data-root bootstrap and switching, row detail navigation, a sidebar clear-selection action, toned Data Block identity surfaces and correct colours for detached outputs.
- **Desktop:** hardened runtime and download boundaries, statically linked DuckDB JSON, a fixed application identifier, the theme contract audit running on Windows, and fixes for tokenizer option overlap and graph-node interactions.

See the [v0.7.5 release](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/tag/v0.7.5) and [full changelog](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/compare/v0.7.2...v0.7.5) for details.

## What's new in v0.7.2: Topic Modelling controls, Concordance totals, and folder-aware uploads

- **Topic Modelling gains adjustable topic counts and a Minimum topic size**, plus full-table "Top topics per document" projections (positive-share ranking with cutoff ties), reorganised result controls, topic filtering, bubble sizing and composition colouring, and steadier tooltips and graph interactions with compact expandable toolbars.
- **Concordance shows per-source totals and summaries**, with dispersion controls, review sorting and highlighting, and document publication.
- **Data workflows:** unified folder-aware uploads, synchronised multi-source column selection, per-source Data Block Creation controls, known-total page jumps, safer external-file handling, better schema inference, and clearer presentation (and preservation) of unavailable or incompatible workspaces.
- **Annotation and guidance:** focused example sampling and comparison-visibility controls, progressive contextual hints, clearer warnings for missing filter values, and filterable column pickers with wildcard search.
- **Under the hood:** the backend now lives in the Wordflow monorepo, and packaged-backend discovery, reload, zoom and CORS behaviour are fixed across desktop builds.

See the [v0.7.2 release](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/tag/v0.7.2) and [full changelog](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/compare/v0.7.1...v0.7.2) for details.

## What's new in v0.7.0 — Data Block colour, result ordering, and desktop release hardening

- **Data Block colouring** makes workspace items easier to distinguish visually.
- **Token-frequency result ordering** gives frequency results a consistent, useful order.
- **Double-click add** provides a quicker way to add a Data Block to an analysis.
- **Desktop distribution is simpler and more trustworthy:** each platform has one bundled installer, and the macOS app is Developer ID signed and notarized.

See the [v0.7.0 release](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/tag/v0.7.0) and [full changelog](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/compare/v0.5.6...v0.7.0) for details.

## What's new in v0.5.6 — Self-refreshing in-app docs + Trends grouping fix

- **In-app docs refresh themselves and work offline — identically everywhere.** The Tutorial, References and Information pages are now served by the backend, which quietly mirrors the version-matched docs site to a local cache on startup: the latest docs when online, the cached copy when offline, and the copy bundled in the build as a floor. Same behaviour in the desktop app, the `uvx` runner, and the web/Binder deployments — previously the desktop app could only show the documentation frozen into its build.
- **Case-insensitive Trends grouping now folds every group field.** Low-cardinality group columns stored as Categorical/Enum (party, stance, outlet, …) — not just plain text — now fold together too, so a multi-group key like "party · stance" no longer leaves values that differ only in case (e.g. "lnp · Yes" vs "lnp · yes") in separate buckets. The live tool and the snapshot viewer bucket identically.
- **Trends "Add to workspace"** is now enabled whenever your selection is a subset of the full result — including when every period is selected but a group/value filter narrows it.
- **Desktop fixes:** long names wrap inside confirmation dialogs instead of overflowing; dropping a file on empty space no longer navigates away from the app; and the bottom-left Tutorial button loads correctly.

Workspace compatibility: no serialization-layer change since v0.5.5; workspaces saved by prior 0.5.x versions open unchanged. See the [wordflow CHANGELOG](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/blob/v0.5.6/CHANGELOG.md) for the full v0.5.6 entry.

## What's new in v0.5.5 — Cross-platform update reminder + self-refreshing desktop runtime

- **"Update available" reminder on every platform.** When a newer release is on PyPI, a dismissible banner tells you the new version and where to get it (download for desktop, launch for web/Binder) — driven by a new backend `/api/version` endpoint, so it works in the desktop app, the `uvx` runner, and the web deployments alike. On a shared/hosted server you can request an update via the feedback form.
- **The desktop runtime refreshes itself on reinstall.** Installing a newer desktop build over an existing one reconciles the bundled Python runtime to the new version automatically on first launch — no manual reset.
- **Fixed: analysis no longer locks up after you cancel a task.** Stopping a running concordance used to break the shared worker pool so every later search failed until restart; the pool now rebuilds itself.
- **Plain-language filter hints** (no more "operator"/"value"/"condition") and a Zenodo concept DOI for citation.

Workspace compatibility: no serialization-layer change since v0.5.4; workspaces saved by prior 0.5.x versions open unchanged. See the [wordflow CHANGELOG](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/blob/v0.5.5/CHANGELOG.md) for the full v0.5.5 entry.

## What's new in v0.5.4 — Frequency Snapshot Display-Limit Fix + v0.5 line aligned with dev

**Frequency snapshot display-limit fix.** In v0.5.3 and earlier, the Cloud display limit and List display limit inputs in a loaded Frequency snapshot snapped back to the captured value on every edit — typing a new number, blurring, then watching it revert. The fix tracks the last `backendTokenLimit` we synced from so the resync effect only fires when the backend value itself changes (a new snapshot loads, or live results arrive), not on every override change. Live mode behaviour is unchanged.

**v0.5 release line fast-forwarded to dev.** The cherry-pick-only convention on the `v0.5` branch had quietly drifted ~34 patches behind `dev` over the v0.5.0–v0.5.3 window, and the v0.5.4 PyPI wheel was bundled from `dev` (so PyPI carried `dev` features while a v0.5-source rebuild would have shipped older code). To remove that risk going forward, `v0.5` and `main` were force-updated to `dev`'s tip and the cherry-pick discipline is retired — `dev` is now the source of truth and release branches fast-forward off it. As a side effect this v0.5.4 release formally publishes the dev-only work that had accumulated, including:

- **Lazy on-demand tokenisation.** Switching languages no longer re-tokenises eagerly; the tokens cache is repaired on first use of the new language and persists. Cross-machine workspaces with a stale cache get a repair banner + a re-tokenise affordance.
- **Grey is no longer rolled by the random colour picker.** Slate-grey is reserved as the "no colour assigned" indicator across the UI, so the auto-assignment palette skips it. The colour picker still offers grey as a manual choice.
- **Mojibake repair at the loader.** Common encoding-corruption patterns get fixed up at file ingestion instead of leaking into downstream analyses.
- **Cache-dir alignment + dotted-column accessors** for the tokenise + table paths.

See the [wordflow CHANGELOG](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/blob/v0.5.4/CHANGELOG.md) for the full v0.5.4 entry.

## Release History

| Published (AEST) | Version | ARDC BinderHub | Tauri Windows | Tauri macOS | Local command |
| --- | --- | --- | --- | --- | --- |
| 2026-09-03 | `0.7.7` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/7364496?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.7/ldaca-wordflow_0.7.7_windows-x86_64.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.7/ldaca-wordflow_0.7.7_darwin-aarch64.dmg) | `uvx --refresh ldaca-wordflow@0.7.7` |
| 2026-08-28 | `0.7.6` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/20fff5f?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.6/ldaca-wordflow_0.7.6_windows-x86_64.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.6/ldaca-wordflow_0.7.6_darwin-aarch64.dmg) | `uvx --refresh ldaca-wordflow@0.7.6` |
| 2026-08-28 | `0.7.5` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/f3a7edd?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.5/ldaca-wordflow_0.7.5_windows-x86_64.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.5/ldaca-wordflow_0.7.5_darwin-aarch64.dmg) | `uvx --refresh ldaca-wordflow@0.7.5` |
| 2026-08-19 | `0.7.2` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/019a84a?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.2/ldaca-wordflow_0.7.2_windows-x86_64.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.2/ldaca-wordflow_0.7.2_darwin-aarch64.dmg) | `uvx --refresh ldaca-wordflow@0.7.2` |
| 2026-07-29 | `0.7.1` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/cb44413?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.1/ldaca-wordflow_0.7.1_windows-x86_64.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.1/ldaca-wordflow_0.7.1_darwin-aarch64.dmg) | `uvx --refresh ldaca-wordflow@0.7.1` |
| 2026-07-27 | `0.7.0` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/d603d55?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.0/ldaca-wordflow_0.7.0_windows-x86_64.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.0/ldaca-wordflow_0.7.0_darwin-aarch64.dmg) | `uvx --refresh ldaca-wordflow@0.7.0` |
| 2026-06-01 | `0.5.6` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/1efb6c2?labpath=index.ipynb) | [Full](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.6/ldaca-wordflow-bundle-x64-0.5.6.msi) / [Lite](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.6/ldaca-wordflow-slim-x64-0.5.6.msi) | [Full](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.6/ldaca-wordflow-bundle-apple-silicon-0.5.6.dmg) / [Lite](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.6/ldaca-wordflow-slim-apple-silicon-0.5.6.dmg) | `uvx --refresh ldaca-wordflow@0.5.6` |
| 2026-05-27 | `0.5.5` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/c2cb50e?labpath=index.ipynb) | [Full](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.5/ldaca-wordflow-bundle-x64-0.5.5.msi) / [Lite](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.5/ldaca-wordflow-slim-x64-0.5.5.msi) | [Full](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.5/ldaca-wordflow-bundle-apple-silicon-0.5.5.dmg) / [Lite](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.5/ldaca-wordflow-slim-apple-silicon-0.5.5.dmg) | `uvx --refresh ldaca-wordflow@0.5.5` |
| 2026-05-25 | `0.5.4` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/af696f9?labpath=index.ipynb) | [Full](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.4/ldaca-wordflow-bundle-x64-0.5.4.msi) / [Lite](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.4/ldaca-wordflow-slim-x64-0.5.4.msi) | [Full](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.4/ldaca-wordflow-bundle-apple-silicon-0.5.4.dmg) / [Lite](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.4/ldaca-wordflow-slim-apple-silicon-0.5.4.dmg) | `uvx --refresh ldaca-wordflow@0.5.4` |
| 2026-05-25 | `0.5.3` ‡ | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/ad73a87?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.3/LDaCA.Wordflow_0.5.3_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.3/ldaca-desktop-apple-silicon-0.5.3.dmg) | `uvx --refresh ldaca-wordflow@0.5.3` |
| 2026-05-21 | `0.5.1` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/98c8082?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.1/LDaCA.Wordflow_0.5.1_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.1/ldaca-desktop-apple-silicon-0.5.1.dmg) | `uvx --refresh ldaca-wordflow@0.5.1` |
| 2026-05-17 | `0.5.0` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/0fa075e?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.0/LDaCA.Wordflow_0.5.0_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.0/ldaca-desktop-apple-silicon-0.5.0.dmg) | `uvx --refresh ldaca-wordflow@0.5.0` |
| 2026-05-15 | `0.4.4` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/b8d0cdc?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.4/LDaCA.Wordflow_0.4.4_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.4/ldaca-desktop-apple-silicon-0.4.4.dmg) | `uvx --refresh ldaca-wordflow@0.4.4` |
| 2026-05-15 | `0.4.3` † | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/5b2f422?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.3/LDaCA.Wordflow_0.4.2_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.3/ldaca-desktop-apple-silicon-0.4.2.dmg) | `uvx --refresh ldaca-wordflow@0.4.3` |
| 2026-05-15 | `0.4.2` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/107cce6?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.2/LDaCA.Wordflow_0.4.2_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.2/ldaca-desktop-apple-silicon-0.4.2.dmg) | `uvx --refresh ldaca-wordflow@0.4.2` |
| 2026-05-15 | `0.4.1` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/b463efa?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.1/LDaCA.Text.Analytics_0.4.1_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.1/ldaca-desktop-apple-silicon-0.4.1.dmg) | `uvx --refresh ldaca-web-app@0.4.1` |
| 2026-05-12 | `0.3.2` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/54b6daf0141f077c0de94c0213acae33cf3d397a?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.3.2/LDaCA.Text.Analytics_0.3.2_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.3.2/ldaca-desktop-apple-silicon-0.3.2.dmg) | `uvx --refresh ldaca-web-app@0.3.2` |
| 2026-05-06 | `0.2.9` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/6c68cb11622ee245a2c2063947baa73939bae2c7?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.2.9/LDaCA.Text.Analytics_0.2.9_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.2.9/ldaca-desktop-apple-silicon-0.2.9.dmg) | `uvx --refresh ldaca-web-app@0.2.9` |
| 2026-05-03 | `0.2.2` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/8427a10ec8607cf3087d341b871cb64d4ab64dd2?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.2.2/LDaCA.Text.Analytics_0.2.2_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.2.2/ldaca-desktop-apple-silicon.dmg) | `uvx --refresh ldaca-web-app@0.2.2` |

Historical release rows above `v0.4.2` keep the `ldaca-web-app` install command since those versions only exist under the old PyPI name. GitHub release-asset links auto-redirect from the old `ldaca_web_app` repo slug to `ldaca-wordflow`.

† `v0.4.3` ships byte-identical code to `v0.4.4` on the `pip install` path, but a missed version source meant its desktop assets were stamped `0.4.2` (the filename — and the "About" / "Installed apps" entry on the installed binary — both read `0.4.2`). `v0.4.4` re-cuts the same code with the version string corrected across all five build inputs. Pip users of `0.4.3` see a cosmetic version mismatch only; desktop users should re-download `v0.4.4`.

‡ `v0.5.3` re-stamps `v0.5.2`. The `v0.5.2` PyPI wheel was cut from a release-branch cherry-pick that silently dropped three commits from `dev` — the workspace-rename fix and the two file-tree feature additions — so the published wheel was a near-no-op. `v0.5.2` has been yanked on PyPI and never had desktop builds released (the root tag was retracted before the desktop workflow ran). Use `v0.5.3`.

## Citation

If you use LDaCA Wordflow in your research, please cite it:

> Guo, S., Sun, C., Bednarek, M., Haan, S., Lynch, M. & Rehman, A. (2026), _LDaCA Wordflow_ [Computer software]. https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/. DOI: [10.5281/zenodo.20408328](https://doi.org/10.5281/zenodo.20408328)

The DOI above is the **concept DOI** — it always resolves to the latest version on Zenodo. Each release also has its own version-specific DOI on its Zenodo record.

## Local development

```bash
uvx --refresh ldaca-wordflow@latest
```

For source development with hot reload, run the backend and Vite separately.
The backend task uses the exact development allowlist below so either loopback
frontend hostname works without enabling wildcard CORS:

```bash
cd ldaca_wordflow/backend
CORS_ALLOWED_ORIGINS='["http://localhost:3000","http://127.0.0.1:3000"]' \
  .venv/bin/python -m uvicorn ldaca_wordflow.main:app --reload --port 8001
```

Run the repository's `Start Frontend` task separately for Vite on port `3000`.
The backend-only process does not start or supervise Vite.
