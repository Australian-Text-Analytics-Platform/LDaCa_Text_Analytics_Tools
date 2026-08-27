# AGENTS.md — LDaCA Text Analytics Tools (master repo)

Start here before exploring. This is the **master repo** for the LDaCA Text Analytics Tools suite. It is a thin orchestration layer for the Binder launch and landing page. It pins Wordflow only; Wordflow owns its documentation and sample-data submodules.

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
└── ldaca_wordflow/                     ← submodule → ATAP/ldaca-wordflow (web app, docs, sample data)
```

### Submodule pointers + branch policy

| Submodule | Tracks branch | Production tag | Why this branch |
|---|---|---|---|
| `ldaca_wordflow` | `main` | `v0.7.6` | `main` (renamed from `dev` on 2026-08-25; the old `main` was deleted) is the integration source of truth; Binder installs an exact published release from `binder/environment.yml` |

Wordflow contains the `ldaca-wordflow-docs`, `ldaca-analytics-sample-data`, `polars-text`, and `polars-source-utils` submodules. When working from this master repo, `git submodule update --init --recursive` walks that tree.

## Working pattern for agents

You will almost always be making changes inside ONE submodule. The master repo's job is to record which SHA of that submodule the production Binder + landing page should use. Workflow:

1. **`cd ldaca_wordflow` to make Wordflow changes.** Use its `main` branch (the former `dev`, renamed 2026-08-25), commit, and push to its `origin`. The submodule has its own CI, tests, and release workflow.
2. **Return to the master root** and `git add <submodule>` to capture the new pointer. Commit with a short message like `Bump ldaca_wordflow submodule for <reason>`. Push.

### gh CLI conventions

Because each submodule has its own GitHub repo, every `gh` invocation must specify `--repo`. GitHub redirects from the OLD slugs (`ldaca_web_app`, `ldaca-analytics-docs`, `ldaca_web_app_backend`) still work, but record the new ones in scripts:

| Operation | Command |
|---|---|
| Wordflow workflow runs | `gh run list --repo Australian-Text-Analytics-Platform/ldaca-wordflow` |
| Master (this repo) | `gh run list --repo Australian-Text-Analytics-Platform/ldaca_text_analytics_tools` |

### Validated commands from master root

```bash
# Sync the master and walk all submodules to their recorded SHAs
git submodule sync --recursive
git submodule update --init --recursive --checkout --force

# Work on the Wordflow integration branch inside the submodule
git -C ldaca_wordflow checkout main
# … make changes, commit, tag, push from inside the submodule
# … then come back here and bump the pointer

# Build the Binder image locally (works on macOS via Docker Desktop)
uv sync                                 # resolves the ldaca-wordflow-binder wrapper
# index.ipynb defines the launch flow; binder/environment.yml is the conda base

# Run the master's smoke tests
uv run pytest -q tests/
```

## Active release lines

- **Wordflow** (formerly `ldaca-web-app`): `main` (the former `dev`, renamed 2026-08-25) is the integration source of truth and `v0.7.6` is the current published release pinned by this Binder repository.
- **Docs and sample data**: owned and pinned by Wordflow. Do not add duplicate top-level submodules here.

## What lives where (so you don't grep blindly)

| Need to change | Repo |
|---|---|
| A UI button, table column, analysis tab | `ldaca_wordflow/frontend/src/...` |
| An API endpoint, polars op, embedder routing | `ldaca_wordflow/backend/src/...` |
| A tutorial, reference page, FAQ | `ldaca_wordflow/ldaca-wordflow-docs/` |
| A sample dataset, catalogue entry, README for a corpus | `ldaca_wordflow/ldaca-analytics-sample-data/` |
| The Binder launch notebook, the README landing-page table, the desktop-build link history | THIS REPO (master) |
| The release history table on the landing page | `README.md` at master root |

## Critical gotchas (see HANDOVER.md for full context)

- **Submodule path-source overrides mask drift in published wheels.** Wordflow's `backend/pyproject.toml` *used to* carry `[tool.uv.sources] docworkspace = { path = "../docworkspace", editable = true }`. Local validation passed because uv resolved docworkspace from the sibling. The published wheel only declared `docworkspace>=0.2.7` and PyPI's 0.2.7 wheel lacked features the override was masking. Fixed in v0.4.1 by publishing `docworkspace==0.2.8` and removing the override. **If you ever re-add a path source, treat it as a deferred bug, not a permanent solution.**
- **Polars-text feature gates.** Every new polars op may require a `polars-plan` Cargo feature in `polars-text`. Missing one breaks workspace save/load with `unknown variant 'XXX'`. Check `polars-text/Cargo.toml` if you add an unfamiliar polars expression.
- **Wordflow owns its nested submodules.** From the master, they live below `ldaca_wordflow/`. Be careful when running `git submodule status` — `+` markers can indicate either an unpushed submodule commit or intentional branch drift; inspect before changing pointers.
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
