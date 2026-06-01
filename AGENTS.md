# AGENTS.md — LDaCA Text Analytics Tools (master repo)

Start here before exploring. This is the **master repo** for the LDaCA Text Analytics Tools suite. It is a thin orchestration layer that pins working versions of multiple sibling tool repos (currently Wordflow, the Wordflow docs site, and the sample data catalogue) so they can be composed into a Binder launch and into a unified landing page.

> Renamed convention: prefer "master repo" or "tools repo" when speaking to humans; the GitHub slug is `ldaca_text_analytics_tools`. The biggest tool inside the suite is **LDaCA Wordflow** — the React/FastAPI web app (formerly `ldaca-web-app`); renamed across PyPI / GitHub / Python module at v0.4.2 on 2026-05-15.

## Repo map

```
LDaCA-Text-Analytics-Tools/             ← THIS REPO (master)
├── AGENTS.md                           ← you are here
├── CLAUDE.md                           ← imports AGENTS.md for Claude Code
├── HANDOVER.md                         ← what changed since 2026-04-25 (read once)
├── README.md                           ← landing page + release history table
├── pyproject.toml                      ← uv project "ldaca-wordflow-binder" (Binder shim)
├── binder/                             ← Nectar BinderHub config (environment.yml, postBuild)
├── index.ipynb                         ← Jupyter notebook that launches Wordflow on Binder
├── ai_annotator/                       ← legacy standalone tool (kept for archive; not active)
├── tests/                              ← master-level smoke tests
├── _pypi_placeholders/                 ← gitignored; local-only build dirs for PyPI placeholder/shim packages
├── ldaca_wordflow/                     ← submodule → ATAP/ldaca-wordflow (web app)
├── ldaca_wordflow_docs/                ← submodule → ATAP/ldaca-wordflow-docs
└── ldaca-analytics-sample-data/        ← submodule → ATAP/ldaca-analytics-sample-data
```

### Submodule pointers + branch policy

| Submodule | Tracks branch | Production tag | Why this branch |
|---|---|---|---|
| `ldaca_wordflow` | `v0.5` | `v0.5.6` | The active Wordflow release line; `main`, `dev`, and `v0.5` all track it (fast-forwarded each release — `dev` is the source of truth). `v0.4`/`v0.3` remain only for back-port hot-fixes / legacy consumers |
| `ldaca_wordflow_docs` | `v0.4` | (continuously deployed via gh-pages) | Each minor version of Wordflow has a matching docs branch (`v0.3`, `v0.4`); Wordflow's `VITE_DOCS_BASE_URL` resolves to that branch's published path |
| `ldaca-analytics-sample-data` | `main` | n/a | Single dataset catalogue, no versioning needed yet |

Wordflow itself has nested submodules (`backend`, `docworkspace`, `polars-text`, `ldaca-tabulator`). The backend lives at `Australian-Text-Analytics-Platform/ldaca-wordflow-backend` (renamed from `ldaca_web_app_backend` at v0.4.2); the others kept their existing repo names. When working from this master repo, `git submodule update --init --recursive` walks the tree.

## Working pattern for agents

You will almost always be making changes inside ONE submodule. The master repo's job is to record which SHA of that submodule the production Binder + landing page should use. Workflow:

1. **`cd <submodule>` to make code changes.** Use the submodule's own branch (`v0.4` on Wordflow for now), commit, and push to that submodule's `origin`. The submodule has its own CI, tests, and release workflow — they all keep working unchanged.
2. **Return to the master root** and `git add <submodule>` to capture the new pointer. Commit with a short message like `Bump ldaca_wordflow submodule for <reason>`. Push.
3. **If a change spans submodules** (the genuine win of having a master) — e.g. renaming a feature in `ldaca_wordflow/frontend/src/...` *and* updating its tutorial in `ldaca_wordflow_docs/...` — make the two submodule commits, then capture both pointer bumps in a single master commit. The master commit is the atomic unit.

### gh CLI conventions

Because each submodule has its own GitHub repo, every `gh` invocation must specify `--repo`. GitHub redirects from the OLD slugs (`ldaca_web_app`, `ldaca-analytics-docs`, `ldaca_web_app_backend`) still work, but record the new ones in scripts:

| Operation | Command |
|---|---|
| Wordflow workflow runs | `gh run list --repo Australian-Text-Analytics-Platform/ldaca-wordflow` |
| Backend (submodule of Wordflow) workflow runs | `gh run list --repo Australian-Text-Analytics-Platform/ldaca-wordflow-backend` |
| Docs workflow runs | `gh run list --repo Australian-Text-Analytics-Platform/ldaca-wordflow-docs` |
| Sample data | `gh run list --repo Australian-Text-Analytics-Platform/ldaca-analytics-sample-data` |
| Master (this repo) | `gh run list --repo Australian-Text-Analytics-Platform/ldaca_text_analytics_tools` |

### Validated commands from master root

```bash
# Sync the master and walk all submodules to their recorded SHAs
git submodule sync --recursive
git submodule update --init --recursive --checkout --force

# Trigger the standard release pipeline (Wordflow v0.4.x — runs inside the submodule)
git -C ldaca_wordflow checkout v0.4
# … make changes, commit, tag, push from inside the submodule
# … then come back here and bump the pointer

# Build the Binder image locally (works on macOS via Docker Desktop)
uv sync                                 # resolves the ldaca-wordflow-binder wrapper
# index.ipynb defines the launch flow; binder/environment.yml is the conda base

# Run the master's smoke tests
uv run pytest -q tests/
```

## Active release lines

- **Wordflow** (formerly `ldaca-web-app`):
  - `v0.5` = `v0.5.6` (active release line — what users should install). `v0.4` (`v0.4.2`) and `v0.3` remain only for back-port hot-fixes / legacy consumers.
  - `main`, `dev`, and `v0.5` all track the active release line — `dev` is the source of truth and the release branches fast-forward off it. The earlier practice of parking `main` (web app **and** backend) at the legacy `v0.3.5` line is **retired** as of v0.5.6; `main` now follows the current release. PyPI back-compat for the old name is handled by the `ldaca-web-app` shim package, not by `main`.
  - `v0.5` is the deploy target for the Nectar VM and PyPI's `latest`.
  - PyPI primary name: `ldaca-wordflow` from 0.4.2 onward. The one-shot legacy shim `ldaca-web-app==0.4.2` depends on `ldaca-wordflow==0.4.2` so `pip install ldaca-web-app` keeps resolving; 0.5+ ships only to `ldaca-wordflow`. Defensive PyPI names `wordflows` and `ldaca-wordflow==0.3.5` are placeholder-only and not actively maintained.
- **Docs**: branches mirror Wordflow's minor lines. `v0.3` is the matching docs for the legacy line; `v0.4` is current. Each branch is published to `gh-pages` under `/v0.3/` and `/v0.4/` paths so Wordflow's runtime docs registry can fetch the right version.
- **Sample data**: a single rolling catalogue at `main`. No version branches yet.

## What lives where (so you don't grep blindly)

| Need to change | Repo |
|---|---|
| A UI button, table column, analysis tab | `ldaca_wordflow/frontend/src/...` |
| An API endpoint, polars op, embedder routing | `ldaca_wordflow/backend/src/...` |
| A tutorial, reference page, FAQ | `ldaca_wordflow_docs/` (on the `v0.4` branch for the active line) |
| A sample dataset, catalogue entry, README for a corpus | `ldaca-analytics-sample-data/` |
| The Binder launch notebook, the README landing-page table, the desktop-build link history | THIS REPO (master) |
| The release history table on the landing page | `README.md` at master root |

## Critical gotchas (see HANDOVER.md for full context)

- **Submodule path-source overrides mask drift in published wheels.** Wordflow's `backend/pyproject.toml` *used to* carry `[tool.uv.sources] docworkspace = { path = "../docworkspace", editable = true }`. Local validation passed because uv resolved docworkspace from the sibling. The published wheel only declared `docworkspace>=0.2.7` and PyPI's 0.2.7 wheel lacked features the override was masking. Fixed in v0.4.1 by publishing `docworkspace==0.2.8` and removing the override. **If you ever re-add a path source, treat it as a deferred bug, not a permanent solution.**
- **Polars-text feature gates.** Every new polars op may require a `polars-plan` Cargo feature in `polars-text`. Missing one breaks workspace save/load with `unknown variant 'XXX'`. Check `polars-text/Cargo.toml` if you add an unfamiliar polars expression.
- **docworkspace, polars-text, ldaca-tabulator** are nested submodules of Wordflow. From the master, they're at `ldaca_wordflow/{name}/`. Be careful when running `git submodule status` — `+` markers can indicate either an unpushed submodule commit (action needed) or a parallel-line drift you should NOT auto-commit.
- **PyPI Trusted Publishing is per-(project, repo)**. When Wordflow-backend's GitHub repo was renamed at v0.4.2, the OIDC publish step on PyPI failed with `invalid-publisher` until a new trusted-publisher entry was added on the `ldaca-wordflow` PyPI project pointing at `Australian-Text-Analytics-Platform/ldaca-wordflow-backend` + `release.yml`. If you ever rename a release-emitting repo again, expect to add a fresh PyPI trusted-publisher record before the first tag push.
- **Wordflow is singular, not plural.** It is one tool (the largest) within the LDaCA Text Analytics Tools suite — never write "Wordflow tools". The features inside Wordflow are its analyses, modules, or features.

## Naming conventions

- **Internal UI / in-app prose**: "Wordflow" (the LDaCA logo above the sidebar provides the brand context).
- **Citations / login / formal contexts**: "LDaCA Wordflow" (full name).
- **Suite umbrella**: "LDaCA Text Analytics Tools" — refers to this master repo's overall content, NOT to Wordflow specifically.

## Do not

- Do **not** commit to the master from inside a submodule. `cd ..` first.
- Do **not** modify `ldaca_wordflow/backend/pyproject.toml` from the master to change dep pins; Wordflow owns its dependency declarations and the master only records which SHA to ship.
- Do **not** rebuild the frontend bundle from the master. That's a Wordflow-internal step (`npm run build -w frontend` from inside `ldaca_wordflow/`, then `node scripts/deploy-frontend-to-backend.mjs`). The master records the resulting submodule pointer.
- Do **not** treat the `binder/Dockerfile` (if regenerated) as source — it's a published-image pointer managed by the workflow.

## When in doubt

The submodule's own `AGENTS.md` (e.g., `ldaca_wordflow/AGENTS.md`) is the authoritative source for that submodule's conventions. Read it before making non-trivial changes there.
