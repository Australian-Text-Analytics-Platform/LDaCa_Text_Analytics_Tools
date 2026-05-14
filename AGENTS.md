# AGENTS.md — LDaCA Text Analytics Tools (master repo)

Start here before exploring. This is the **master repo** for the LDaCA Text Analytics Tools suite. It is a thin orchestration layer that pins working versions of multiple sibling tool repos (currently the web app, the docs site, and the sample data catalogue) so they can be composed into a Binder launch and into a unified landing page.

> Renamed convention: prefer "master repo" or "tools repo" when speaking to humans; the GitHub slug is `ldaca_text_analytics_tools`.

## Repo map

```
LDaCA-Text-Analytics-Tools/             ← THIS REPO (master)
├── AGENTS.md                           ← you are here
├── CLAUDE.md                           ← imports AGENTS.md for Claude Code
├── HANDOVER.md                         ← what changed since 2026-04-25 (read once)
├── MIGRATION_PLAN.md                   ← active migration tasks (transient)
├── README.md                           ← landing page + release history table
├── pyproject.toml                      ← uv project "ldaca-web-app-binder" (Binder shim)
├── binder/                             ← Nectar BinderHub config (environment.yml, postBuild)
├── index.ipynb                         ← Jupyter notebook that launches the web app on Binder
├── ai_annotator/                       ← legacy standalone tool (kept for archive; not active)
├── tests/                              ← master-level smoke tests
├── ldaca_web_app/                      ← submodule → ATAP/ldaca_web_app
├── ldaca-analytics-docs/               ← submodule → ATAP/ldaca-analytics-docs
└── ldaca-analytics-sample-data/        ← submodule → ATAP/ldaca-analytics-sample-data
```

### Submodule pointers + branch policy

| Submodule | Tracks branch | Production tag | Why this branch |
|---|---|---|---|
| `ldaca_web_app` | `v0.4` | `v0.4.1` | The multilingual line is the active release line; `main` is stuck at v0.3.5 for back-compat consumers |
| `ldaca-analytics-docs` | `v0.4` | (continuously deployed via gh-pages) | Each minor version of the web app has a matching docs branch (`v0.3`, `v0.4`); the web app's `VITE_DOCS_BASE_URL` resolves to that branch's published path |
| `ldaca-analytics-sample-data` | `main` | n/a | Single dataset catalogue, no versioning needed yet |

The web app itself has nested submodules (`backend`, `docworkspace`, `polars-text`, `ldaca-tabulator`). When working from this master repo, `git submodule update --init --recursive` walks the tree.

## Working pattern for agents

You will almost always be making changes inside ONE submodule. The master repo's job is to record which SHA of that submodule the production Binder + landing page should use. Workflow:

1. **`cd <submodule>` to make code changes.** Use the submodule's own branch (`v0.4` on the web app for now), commit, and push to that submodule's `origin`. The submodule has its own CI, tests, and release workflow — they all keep working unchanged.
2. **Return to the master root** and `git add <submodule>` to capture the new pointer. Commit with a short message like `Bump ldaca_web_app submodule for <reason>`. Push.
3. **If a change spans submodules** (the genuine win of having a master) — e.g. renaming a feature in `ldaca_web_app/frontend/src/...` *and* updating its tutorial in `ldaca-analytics-docs/...` — make the two submodule commits, then capture both pointer bumps in a single master commit. The master commit is the atomic unit.

### gh CLI conventions

Because each submodule has its own GitHub repo, every `gh` invocation must specify `--repo`:

| Operation | Command |
|---|---|
| Web app workflow runs | `gh run list --repo Australian-Text-Analytics-Platform/ldaca_web_app` |
| Backend (submodule of web app) workflow runs | `gh run list --repo Australian-Text-Analytics-Platform/ldaca_web_app_backend` |
| Docs workflow runs | `gh run list --repo Australian-Text-Analytics-Platform/ldaca-analytics-docs` |
| Sample data | `gh run list --repo Australian-Text-Analytics-Platform/ldaca-analytics-sample-data` |
| Master (this repo) | `gh run list --repo Australian-Text-Analytics-Platform/ldaca_text_analytics_tools` |

### Validated commands from master root

```bash
# Sync the master and walk all submodules to their recorded SHAs
git submodule sync --recursive
git submodule update --init --recursive --checkout --force

# Trigger the standard release pipeline (web app v0.4.x — runs inside the submodule)
git -C ldaca_web_app checkout v0.4
# … make changes, commit, tag, push from inside the submodule
# … then come back here and bump the pointer

# Build the Binder image locally (works on macOS via Docker Desktop)
uv sync                                 # resolves the ldaca-web-app-binder wrapper
# index.ipynb defines the launch flow; binder/environment.yml is the conda base

# Run the master's smoke tests
uv run pytest -q tests/
```

## Active release lines

- **Web app**:
  - `main` = `v0.3.5` (legacy, no multilingual)
  - `v0.4` = `v0.4.1` (active, multilingual stack — what users should install)
  - Both lines coexist; `main` is parked, `v0.4` is the deploy target for Nectar VM and PyPI's `latest`.
- **Docs**: branches mirror the web app's minor lines. `v0.3` is the matching docs for the legacy line; `v0.4` is current. Each branch is published to `gh-pages` under `/v0.3/` and `/v0.4/` paths so the web app's runtime docs registry can fetch the right version.
- **Sample data**: a single rolling catalogue at `main`. No version branches yet.

## What lives where (so you don't grep blindly)

| Need to change | Repo |
|---|---|
| A UI button, table column, analysis tab | `ldaca_web_app/frontend/src/...` |
| An API endpoint, polars op, embedder routing | `ldaca_web_app/backend/src/...` |
| A tutorial, reference page, FAQ | `ldaca-analytics-docs/` (on the `v0.4` branch for the active line) |
| A sample dataset, catalogue entry, README for a corpus | `ldaca-analytics-sample-data/` |
| The Binder launch notebook, the README landing-page table, the desktop-build link history | THIS REPO (master) |
| The release history table on the landing page | `README.md` at master root |

## Critical gotchas (see HANDOVER.md for full context)

- **Submodule path-source overrides mask drift in published wheels.** The web app's `backend/pyproject.toml` *used to* carry `[tool.uv.sources] docworkspace = { path = "../docworkspace", editable = true }`. Local validation passed because uv resolved docworkspace from the sibling. The published wheel only declared `docworkspace>=0.2.7` and PyPI's 0.2.7 wheel lacked features the override was masking. Fixed in v0.4.1 by publishing `docworkspace==0.2.8` and removing the override. **If you ever re-add a path source, treat it as a deferred bug, not a permanent solution.**
- **Polars-text feature gates.** Every new polars op may require a `polars-plan` Cargo feature in `polars-text`. Missing one breaks workspace save/load with `unknown variant 'XXX'`. Check `polars-text/Cargo.toml` if you add an unfamiliar polars expression.
- **docworkspace, polars-text, ldaca-tabulator** are nested submodules of the web app. From the master, they're at `ldaca_web_app/{name}/`. Be careful when running `git submodule status` — `+` markers can indicate either an unpushed submodule commit (action needed) or a parallel-line drift you should NOT auto-commit.

## Do not

- Do **not** commit to the master from inside a submodule. `cd ..` first.
- Do **not** modify `ldaca_web_app/backend/pyproject.toml` from the master to change dep pins; the web app owns its dependency declarations and the master only records which SHA to ship.
- Do **not** rebuild the frontend bundle from the master. That's a web-app-internal step (`npm run build -w frontend` from inside `ldaca_web_app/`, then `node scripts/deploy-frontend-to-backend.mjs`). The master records the resulting submodule pointer.
- Do **not** treat the `binder/Dockerfile` (if regenerated) as source — it's a published-image pointer managed by the workflow.

## When in doubt

The submodule's own `AGENTS.md` (e.g., `ldaca_web_app/AGENTS.md`) is the authoritative source for that submodule's conventions. Read it before making non-trivial changes there.
