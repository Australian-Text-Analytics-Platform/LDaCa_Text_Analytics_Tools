# Rename plan — `ldaca-web-app` → `ldaca-wordflow`

Transient checklist. Execute after [MIGRATION_PLAN.md](MIGRATION_PLAN.md) and [PLACEHOLDER_PYPI_PLAN.md](PLACEHOLDER_PYPI_PLAN.md) are both done. This is the biggest change in the sequence — read it end-to-end before starting, and **don't combine phases**.

## Why we're doing this

"Wordflow" is the preferred product name. The current `ldaca-web-app` / `ldaca-analytics-docs` names predate the product naming and treat the tool as generic; everything will be consistent with the product brand after this rename.

## What gets renamed (decision table)

Following the existing pattern (`ldaca_web_app` directory + `ldaca-web-app` PyPI name): underscores for directory + Python module, hyphens for GitHub + PyPI.

| Surface | Before | After |
|---|---|---|
| GitHub repo (web app) | `ldaca_web_app` | `ldaca-wordflow` |
| GitHub repo (docs) | `ldaca-analytics-docs` | `ldaca-wordflow-docs` |
| Master `.gitmodules` path (web app) | `ldaca_web_app` | `ldaca_wordflow` |
| Master `.gitmodules` path (docs) | `ldaca-analytics-docs` | `ldaca_wordflow_docs` |
| PyPI primary package | `ldaca-web-app` | `ldaca-wordflow` (becomes primary at v0.4.2) |
| PyPI legacy shim | n/a | `ldaca-web-app==0.4.2` (depends on `ldaca-wordflow==0.4.2`) |
| Python module (backend) | `ldaca_web_app` | `ldaca_wordflow` |
| Console script (CLI command) | `ldaca-web-app` | `ldaca-wordflow` (+ `ldaca-web-app` alias for back-compat) |
| Frontend product label | "LDaCA Web App" | "LDaCA Wordflow" |
| Tauri bundle product name | "LDaCA Text Analytics" | "LDaCA Wordflow" (optional cosmetic — decide separately) |
| Docs URL base | `.../ldaca-analytics-docs/v0.X` | `.../ldaca-wordflow-docs/v0.X` |

The PyPI release that lands the rename is **v0.4.2** on both names (new primary + legacy shim).

## Prerequisites

- [ ] [MIGRATION_PLAN.md](MIGRATION_PLAN.md) executed: master repo is the working root, all three submodules registered correctly, `v0.4` is the active branch on web-app + docs.
- [ ] [PLACEHOLDER_PYPI_PLAN.md](PLACEHOLDER_PYPI_PLAN.md) executed: `ldaca-wordflow==0.3.5` and `wordflows==0.3.5` are claimed on PyPI.
- [ ] No in-flight release. Confirm: backend's `Package And Release` workflow is idle on `v0.4`; parent's `Desktop Release` is idle.
- [ ] Working tree clean across master + all submodules. `git submodule foreach git status` shows clean everywhere.
- [ ] You have PyPI publish rights on BOTH names (use the project-scoped API tokens you created during the placeholder publish).

## Phases

Each phase is one or more reviewable commits. Don't merge phases together — if something breaks, you want to revert one phase at a time.

---

### Phase 1 — Rename GitHub repos (low risk, GitHub auto-redirects)

```bash
gh repo rename ldaca-wordflow \
    --repo Australian-Text-Analytics-Platform/ldaca_web_app
gh repo rename ldaca-wordflow-docs \
    --repo Australian-Text-Analytics-Platform/ldaca-analytics-docs
```

GitHub:

- Auto-creates redirects from old URLs to new ones (HTTP 301 on web; transparent on git operations).
- Preserves all tags, branches, releases, issues, PRs, stars.
- Updates `${{ github.repository }}` in all workflows automatically.

Verify by visiting the old URLs in a browser and confirming the redirect lands on the new repo.

> The `gh-pages` site for docs follows the rename automatically:
> `australian-text-analytics-platform.github.io/ldaca-analytics-docs/...` →
> `australian-text-analytics-platform.github.io/ldaca-wordflow-docs/...`
> Old URLs return 404 (GitHub Pages does NOT auto-redirect; the web app's `VITE_DOCS_BASE_URL` MUST be updated in Phase 4 before any deploy lands).

---

### Phase 2 — Rename local directories + update master `.gitmodules`

From the master repo:

```bash
git mv ldaca_web_app ldaca_wordflow
git mv ldaca-analytics-docs ldaca_wordflow_docs
```

`git mv` on a submodule directory moves the worktree and `.git` metadata pointer in lockstep. Verify:

```bash
git status                       # should show renames + .gitmodules edit needed
cat .gitmodules                  # both old paths still there — fix in next step
```

Edit `.gitmodules`:

```ini
[submodule "ldaca_wordflow"]
    path = ldaca_wordflow
    url = https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow.git
    branch = v0.4

[submodule "ldaca_wordflow_docs"]
    path = ldaca_wordflow_docs
    url = https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow-docs.git
    branch = v0.4

[submodule "ldaca-analytics-sample-data"]
    path = ldaca-analytics-sample-data
    url = https://github.com/Australian-Text-Analytics-Platform/ldaca-analytics-sample-data.git
    branch = main
```

(Sample-data is unchanged in this rename.)

Sync the submodule metadata in `.git/config` and the submodules' own `.git/config` files:

```bash
git submodule sync --recursive
```

Commit on master:

```bash
git add .gitmodules ldaca_wordflow ldaca_wordflow_docs
git commit -m "Rename submodules: ldaca_web_app → ldaca_wordflow; ldaca-analytics-docs → ldaca_wordflow_docs"
```

> Note: the GitHub auto-redirect would make the OLD submodule URLs in `.gitmodules` continue to work indefinitely, but recording the new URL is cleaner and avoids future archaeology.

---

### Phase 3 — Rename the Python module inside the web app (HIGHEST RISK)

This is the biggest sweep in the rename. Do it in its own commit. **Run the test suite before pushing.**

```bash
cd ldaca_wordflow/backend
git mv src/ldaca_web_app src/ldaca_wordflow
```

Update `pyproject.toml`:

```toml
[project]
name = "ldaca-wordflow"          # was: ldaca-web-app
version = "0.4.2"
# … other fields unchanged

[project.scripts]
ldaca-wordflow = "ldaca_wordflow.cli:main"
ldaca-web-app = "ldaca_wordflow.cli:main"    # back-compat alias
```

Sweep import statements across the codebase:

```bash
# From backend/
grep -rlE "ldaca_web_app|ldaca-web-app" src/ tests/ scripts/ | \
    xargs sed -i '' -E 's/ldaca_web_app/ldaca_wordflow/g; s/ldaca-web-app/ldaca-wordflow/g'
```

> Use `sed -i ''` on macOS (BSD sed); `sed -i` on Linux. Test the regex on one file first.

**Verify before committing:**

```bash
# 1. No leftover references in code
grep -rE "ldaca_web_app|ldaca-web-app" src/ tests/ scripts/ | grep -v "back-compat\|deprecated\|legacy"

# 2. Refresh lockfile
env -u CONDA_PREFIX uv lock

# 3. Tests pass
env -u CONDA_PREFIX uv run pytest -q

# 4. The new CLI works
env -u CONDA_PREFIX uv run ldaca-wordflow --help
env -u CONDA_PREFIX uv run ldaca-web-app --help    # back-compat alias

# 5. Build the wheel and smoke-test from it
env -u CONDA_PREFIX uv build
env -u CONDA_PREFIX uvx --from dist/ldaca_wordflow-0.4.2-py3-none-any.whl ldaca-wordflow --help
```

Commit on the `v0.4` branch of the web app submodule:

```bash
git add -A
git commit -m "Rename Python module ldaca_web_app → ldaca_wordflow; bump to 0.4.2"
```

Don't push yet — wait until Phase 4 + 5 land so the release commit is coherent.

---

### Phase 4 — Sweep cross-repo links (frontend env, README, workflows)

Within the web app submodule:

- `frontend/.env`: `VITE_DOCS_BASE_URL=https://australian-text-analytics-platform.github.io/ldaca-wordflow-docs/v0.4`
- `frontend/package.json`: bump version to `0.4.2`
- `frontend/src-tauri/tauri.conf.json`: bump version to `0.4.2`; optionally change `productName` to "LDaCA Wordflow" (cosmetic — decide separately)
- `frontend/src-tauri/Cargo.toml`: bump version to `0.4.2`
- Sweep frontend source for any user-visible "LDaCA Web App" strings → "LDaCA Wordflow" (search `frontend/src/**` for `Web App` literal). The product chip in the header is the most visible one.
- `pyproject.toml` (root of web-app submodule, the workspace shim): bump to `0.4.2`
- `CHANGELOG.md`: add `## [0.4.2] — YYYY-MM-DD` entry titled "Rename to ldaca-wordflow"; describe what changed and that the old name still works as a shim.
- `DEPLOY.md`: search for any literal references to `ldaca_web_app` repo URL or `ldaca-web-app` package name; update.

Within the docs submodule (now at `ldaca_wordflow_docs/`):

- The published docs URL pattern changes from `.../ldaca-analytics-docs/v0.4/` to `.../ldaca-wordflow-docs/v0.4/`. This is mechanical (GitHub Pages follows the repo name), but any cross-link inside markdown that uses absolute URLs needs updating. Find/replace:

```bash
cd ldaca_wordflow_docs
grep -rlE "ldaca-analytics-docs|ldaca_web_app" | \
    xargs sed -i '' -E 's|ldaca-analytics-docs|ldaca-wordflow-docs|g; s/ldaca_web_app/ldaca_wordflow/g'
```

- Any "LDaCA Web App" prose in tutorials → "LDaCA Wordflow".
- Commit on the docs submodule's `v0.4` branch.

Rebuild the frontend bundle so the version literal and the new docs URL are baked into the released artifact:

```bash
# From the web app submodule root
npm run build -w frontend
node scripts/deploy-frontend-to-backend.mjs
```

Verify the version + new strings are in the bundle (mirroring DEPLOY.md step 3 + 7).

Commit on the web app submodule's `v0.4` branch:

```bash
git add -A
git commit -m "Sweep cross-repo links + rebuild bundle for 0.4.2 rename"
```

---

### Phase 5 — Tag + publish `ldaca-wordflow==0.4.2`

This is the first **real** primary release on the new name (the placeholder `0.3.5` from PLACEHOLDER_PYPI_PLAN was metadata-only).

Within the web app submodule:

```bash
git push origin v0.4
git tag v0.4.2
git push origin v0.4.2     # triggers Package And Release workflow → PyPI
```

The `Package And Release` workflow inherits `${{ github.repository }}` (which is now `Australian-Text-Analytics-Platform/ldaca-wordflow` post-rename) and the wheel's PyPI metadata is read from the updated `pyproject.toml`. **Both the GitHub release URL and the PyPI package name are now `ldaca-wordflow`** for v0.4.2 — different namespace from earlier `ldaca-web-app==0.4.1`.

Verify on PyPI:

```bash
curl -s https://pypi.org/pypi/ldaca-wordflow/0.4.2/json | python3 -c \
    "import sys, json; d=json.load(sys.stdin); print(d['info']['version']); print([u['filename'] for u in d['urls']])"

uvx --refresh --from ldaca-wordflow==0.4.2 python -c \
    "from importlib.metadata import version; print('ldaca-wordflow', version('ldaca-wordflow'))"
```

Capture the new `ldaca-wordflow==0.4.2` wheel's SHA / size for the release notes.

---

### Phase 6 — Publish the `ldaca-web-app==0.4.2` legacy shim

This is what `ldaca-web-app` becomes from this release onward: a meta-package that pulls in the renamed primary. Users who `pip install ldaca-web-app` keep getting the real app, just transparently via the new package name.

There are two possible shim policies:

| Policy | Behaviour | Cost |
|---|---|---|
| **One-shot deprecation** | Publish `ldaca-web-app==0.4.2` once. Future releases (`0.5.0`, …) go ONLY to `ldaca-wordflow`. Old name pins at 0.4.2 forever. | Zero ongoing cost. Users on `pip install ldaca-web-app@latest` are stuck at 0.4.2. |
| **Rolling shim** | At every future `ldaca-wordflow==X.Y.Z` release, also publish `ldaca-web-app==X.Y.Z` shim. | Constant publish overhead, but `pip install ldaca-web-app@latest` keeps working forever. |

**Recommendation: one-shot deprecation.** Communicate the rename in the README + release notes; let the old name be a soft sunset rather than a perpetual mirror. Six months out, yank old `ldaca-web-app` versions if migration coverage looks good.

To publish the shim, create `LDaCA-Text-Analytics-Tools/_pypi_placeholders/ldaca-web-app-shim/` (gitignored, like the placeholder dirs):

```toml
[project]
name = "ldaca-web-app"
version = "0.4.2"
description = "Renamed to ldaca-wordflow. This shim installs the new package; please migrate your dependencies to ldaca-wordflow."
readme = "README.md"
requires-python = ">=3.14"
license = { text = "MIT" }
authors = [{ name = "Australian Text Analytics Platform" }]
dependencies = ["ldaca-wordflow==0.4.2"]
classifiers = ["Development Status :: 7 - Inactive"]

[project.urls]
Homepage = "https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
bypass-selection = true
```

`README.md`:

```markdown
# ldaca-web-app (renamed)

This package was renamed to [`ldaca-wordflow`](https://pypi.org/project/ldaca-wordflow/).

`ldaca-web-app==0.4.2` is a shim that installs the new package. Future
releases ship only to `ldaca-wordflow`. Please update your dependencies:

    pip install ldaca-wordflow

Source: https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow
```

Publish:

```bash
cd _pypi_placeholders/ldaca-web-app-shim
env -u CONDA_PREFIX uv build
env -u CONDA_PREFIX uv run twine upload --repository testpypi dist/*   # always test first
env -u CONDA_PREFIX uv run twine upload dist/*
```

Verify both the shim and the underlying primary resolve cleanly:

```bash
uvx --refresh --from ldaca-web-app==0.4.2 python -c \
    "from importlib.metadata import version; print('ldaca-web-app', version('ldaca-web-app')); print('ldaca-wordflow', version('ldaca-wordflow'))"
# Expected: ldaca-web-app 0.4.2 / ldaca-wordflow 0.4.2
```

---

### Phase 7 — Update the master repo to reflect everything

From the master repo, bump submodule pointers + refresh public-facing copy:

```bash
git -C ldaca_wordflow checkout v0.4
git -C ldaca_wordflow pull origin v0.4
git -C ldaca_wordflow_docs checkout v0.4
git -C ldaca_wordflow_docs pull origin v0.4

# Update README's Latest section and history table to v0.4.2 + new name
# (replace "ldaca-web-app" mentions in the table with "ldaca-wordflow")
# Update binder/environment.yml: ldaca-web-app==X.X.X → ldaca-wordflow==0.4.2
# Update master pyproject.toml dependency from ldaca-web-app[deploy] to ldaca-wordflow[deploy]
env -u CONDA_PREFIX uv lock

git add .
git commit -m "Rename complete: bump submodules to v0.4.2 (ldaca-wordflow); refresh README + Binder pin"
git push origin main
git tag binder-2026-MM-DD
git push origin binder-2026-MM-DD
```

Validate the Binder launch end-to-end from the new master commit, same as MIGRATION_PLAN.md step 6.

---

### Phase 8 — Update [AGENTS.md](AGENTS.md) and other agent context

The repo map in AGENTS.md still references the OLD directory names. After Phase 2, those names are stale. Update:

- Submodule paths: `ldaca_web_app/` → `ldaca_wordflow/`, `ldaca-analytics-docs/` → `ldaca_wordflow_docs/`
- gh CLI repo args: `ldaca_web_app` → `ldaca-wordflow`, `ldaca-analytics-docs` → `ldaca-wordflow-docs`
- "Web app" prose → "Wordflow"
- HANDOVER.md: add a note at the top noting the rename happened on YYYY-MM-DD and the names changed

Update the saved memory `~/.claude/projects/...` project key — the working directory string changes if anything refers to the old name.

Commit on master.

---

## Done criteria

- [ ] `gh repo view Australian-Text-Analytics-Platform/ldaca-wordflow` succeeds
- [ ] `gh repo view Australian-Text-Analytics-Platform/ldaca-wordflow-docs` succeeds
- [ ] Master's `.gitmodules` references the new GitHub URLs and the new local paths
- [ ] `git -C ldaca_wordflow log -1` shows the rename commits + the v0.4.2 release commit
- [ ] `pip install ldaca-wordflow==0.4.2` works and runs the CLI as `ldaca-wordflow --help`
- [ ] `pip install ldaca-web-app==0.4.2` works (via shim) and the CLI still works as `ldaca-web-app --help`
- [ ] `uvx ldaca-wordflow@latest --help` resolves to 0.4.2
- [ ] The web app's Binder launcher (notebook) installs and starts cleanly from the master at the post-rename commit
- [ ] The docs at `australian-text-analytics-platform.github.io/ldaca-wordflow-docs/v0.4/` load
- [ ] The frontend's docs panel fetches successfully (verify a tutorial loads in the app)
- [ ] Tauri builds for v0.4.2 attach to the `Australian-Text-Analytics-Platform/ldaca-wordflow` releases page with the new name in the artifact filenames (or kept old artifact filenames if you opt out of the cosmetic Tauri rename)
- [ ] [AGENTS.md](AGENTS.md) and [HANDOVER.md](HANDOVER.md) reflect the new names
- [ ] This file (`RENAME_PLAN.md`) deleted

## What this rename does NOT do

- **Doesn't touch nested submodules** (`backend`'s `docworkspace`, `polars-text`, `ldaca-tabulator`). Those keep their existing repo names. Rename them later if the team wants.
- **Doesn't migrate users automatically.** The shim covers `pip install ldaca-web-app` but downstream consumers' `pyproject.toml` files still reference `ldaca-web-app`. The migration is opt-in; you can email users / drop a release-note callout.
- **Doesn't rename historic GitHub release artifact filenames.** Old `LDaCA.Text.Analytics_0.3.X_x64_en-US.msi` downloads on v0.3.5 stay where they are. Only v0.4.2+ gets renamed artifact filenames if you opt into the Tauri cosmetic rename.
- **Doesn't move PyPI version history.** `ldaca-web-app==0.3.5` stays on PyPI under the old name forever. `ldaca-wordflow` starts at 0.3.5 (placeholder) and 0.4.2 (real); 0.4.0 / 0.4.1 only ever existed on `ldaca-web-app`.

## Rollback path

If Phase 5 (PyPI publish) succeeds but Phase 7 reveals a critical bug, the fix is forward-only — publish `ldaca-wordflow==0.4.3` with the fix; do NOT try to unpublish 0.4.2 (PyPI prevents republish anyway). If Phases 1–4 reveal a problem before any PyPI release, revert the commits on `v0.4` and reset the GitHub repo names back via `gh repo rename` (GitHub allows un-renaming back as long as the redirect target is still you).
