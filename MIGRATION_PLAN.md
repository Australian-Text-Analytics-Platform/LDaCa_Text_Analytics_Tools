# Migration plan — move agent work to the master repo

This is a transient checklist. Delete this file once every box is ticked and the working pattern from [AGENTS.md](AGENTS.md) has been validated end-to-end at least once. Each step is a discrete, reviewable commit on the master repo.

## Why we're doing this

Three independent reasons:

1. **Atomic doc+code commits.** Multilingual features have tutorials lagging behind the code because the two repos move separately. A master commit can record both submodule pointer bumps in one reviewable unit.
2. **The Binder launcher is growing.** `binder/` and `index.ipynb` already live at the master; future notebooks (AI annotator, etc.) belong here too.
3. **Landing page consolidation.** `README.md` is the public entry point listing every LDaCA text-analytics tool. The web app is one of several.

See [HANDOVER.md](HANDOVER.md) for the substantive change history this migration locks in.

## Current state (as of 2026-05-15)

- Master repo: `ldaca_text_analytics_tools` on branch `main` at commit `0e00ff1 Add ldaca-analytics-docs as submodule`.
- Recorded submodule pointers:
  - `ldaca_web_app` → `8fc7d04` (= v0.4.1, on the `v0.4` branch)
  - `ldaca-analytics-docs` → `9f64e23` (on `heads/v0.3`)
- Working-tree drift (NOT yet committed):
  - `ldaca_web_app` has unrecorded new commits — pointer needs a bump.
  - `ldaca-analytics-docs` has unrecorded new commits — pointer needs a bump or branch swap.
  - `ldaca-analytics-sample-data/` is an untracked directory containing a clone of the GitHub repo; not registered as a submodule.
- README still lists `v0.3.2` as "Latest". Out of date by three releases.
- `.gitmodules` declares `ldaca_web_app` with `branch = main` — but `main` is the legacy v0.3.5 line; production now lives on the `v0.4` branch.

## Migration steps

### 1. Register `ldaca-analytics-sample-data` as a submodule

```bash
cd /path/to/LDaCA-Text-Analytics-Tools

# The working tree already has the sample-data directory cloned. Move it
# aside so `git submodule add` can create the submodule without colliding,
# then drop the temp copy.
mv ldaca-analytics-sample-data ldaca-analytics-sample-data.tmp
git submodule add https://github.com/Australian-Text-Analytics-Platform/ldaca-analytics-sample-data.git ldaca-analytics-sample-data
rm -rf ldaca-analytics-sample-data.tmp
```

Verify:

```bash
cat .gitmodules                          # should list all three submodules
git submodule status                     # should show 3 entries with SHAs
git status -s                            # expect: new file .gitmodules, new file ldaca-analytics-sample-data
```

Commit:

```bash
git commit -m "Register ldaca-analytics-sample-data as submodule"
```

### 2. Switch `ldaca_web_app` branch tracking from `main` to `v0.4`

In `.gitmodules`:

```ini
[submodule "ldaca_web_app"]
    path = ldaca_web_app
    url = https://github.com/Australian-Text-Analytics-Platform/ldaca_web_app.git
    branch = v0.4    # was: main
```

Then sync + advance the pointer to the v0.4 tip:

```bash
git submodule set-branch --branch v0.4 ldaca_web_app
git submodule update --remote --merge ldaca_web_app
git -C ldaca_web_app status              # confirm we're on v0.4, clean
git add .gitmodules ldaca_web_app
git commit -m "Track ldaca_web_app on v0.4 branch (multilingual release line)"
```

### 3. Pin `ldaca-analytics-docs` to the `v0.4` branch

The docs site has parallel branches matching web-app minor versions. Since we're tracking the web app on `v0.4`, the docs submodule should also live on `v0.4`.

```bash
# Decide whether to add `branch = v0.4` declaration in .gitmodules.
# The submodule is currently bare (no branch line), which means `git submodule
# update --remote` won't move it. Adding `branch = v0.4` makes future
# `--remote` syncs follow the right line.

git submodule set-branch --branch v0.4 ldaca-analytics-docs
git -C ldaca-analytics-docs checkout v0.4
git -C ldaca-analytics-docs pull --ff-only origin v0.4
git add .gitmodules ldaca-analytics-docs
git commit -m "Track ldaca-analytics-docs on v0.4 branch"
```

### 4. Refresh `README.md` to point at v0.4.1

The current README's "Latest" section says `v0.3.2`. Replace with v0.4.1, prepend a new release-history row, and update the BinderHub launch hash to the current master `HEAD` once steps 1–3 are committed. Pattern (one row):

```markdown
| 2026-05-15 | `0.4.1` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/<COMMIT-SHA>?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca_web_app/releases/download/v0.4.1/LDaCA.Text.Analytics_0.4.1_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca_web_app/releases/download/v0.4.1/ldaca-desktop-apple-silicon-0.4.1.dmg) | `uvx --refresh ldaca-web-app@0.4.1` |
```

Note: insert a row for v0.4.0 only if you want users to see it; given it's yanked on PyPI and superseded, omitting it is reasonable. If you keep it, add an "(superseded — use 0.4.1)" tag to the row.

Also: bump the `Latest` block at the top of `README.md` to show v0.4.1.

Commit:

```bash
git commit -m "README: promote v0.4.1 to Latest; refresh BinderHub launch hash"
```

### 5. Update the Binder shim to pin the v0.4.1 web app

`binder/environment.yml` currently pins `ldaca-web-app==0.1.20`. That's ancient. Update to `0.4.1`:

```yaml
dependencies:
  - python=3.14
  - pip
  - pip:
      - uv
      - jupyter_server_proxy
      - ldaca-web-app==0.4.1
      - --extra-index-url https://download.pytorch.org/whl/cpu
      - torch
```

Also update the master's root `pyproject.toml` if the version pin appears there too. The `ldaca-web-app-binder` project depends on `ldaca-web-app[deploy]`; if you want a strict lower bound, set `ldaca-web-app[deploy]>=0.4.1`.

Commit:

```bash
uv lock                                  # refresh master uv.lock
git commit -am "Bump Binder pin to ldaca-web-app==0.4.1"
```

### 6. Validate the launch path end-to-end

This is the bit the Binder users care about. Run locally before pushing the master:

```bash
# 1. Master uv project resolves cleanly
uv sync

# 2. The index.ipynb launcher imports without errors
uv run jupyter nbconvert --to notebook --execute --output /tmp/test.ipynb index.ipynb

# 3. Optional: build the repo2docker image (if Docker is available)
# repo2docker --no-build .
```

If you have access to push to a test branch on the master repo, push it and trigger a BinderHub launch against that commit:

```
https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/<TEST-BRANCH>?labpath=index.ipynb
```

Confirm the web app responds inside the BinderHub session before merging into `main`.

### 7. Push the master, tag the release

```bash
git push origin main
git tag binder-2026-05-15
git push origin binder-2026-05-15
```

(The master uses date-stamped tags for Binder-launch snapshots, not semver — see prior tag history.)

### 8. Update saved memory + close out

After this migration, the agent should treat `/Users/mily/Workspace/ATAP/LDaCA-Text-Analytics-Tools/` as the working root, not `/Users/mily/Workspace/ATAP/LDaCA-Text-Analytics-Tools/ldaca_web_app/`. Update the relevant `MEMORY.md` line in `~/.claude/projects/...`:

- Old project path key referenced `ldaca-web-app` directly.
- New: `ldaca-text-analytics-tools` (this folder name with case-insensitive slugging).

The simplest move: open Claude Code in the master folder once and let it auto-create the memory directory. Carry forward the high-value feedback / project memory files manually.

### 9. Cleanup (low-priority)

- `ai_annotator/` looks empty — confirm and remove if so.
- `build/` and `__pycache__/` at master root are uv/Python build artefacts and should be gitignored if they aren't already.
- `backup/` — check what's in it and either commit-with-purpose or remove.

## What this migration does NOT change

- The web app's release process (still `cd ldaca_web_app && ...` per its own `DEPLOY.md`).
- The PyPI publish pipeline (still triggered by `v*` tags on the web app's `v0.4` branch, NOT by master tags).
- The Nectar VM deploy target — that consumes the web-app repo directly, not the master.
- Submodule remotes — no repo renames in this migration. (If you later rename `ldaca_web_app` to `ldaca-web-app`, that's a separate migration; GitHub auto-redirects make it low-risk but the `.gitmodules` URL should be updated as a cleanup commit.)

## Done criteria

- [ ] `git submodule status` from master root lists three submodules, all clean, all at branch tips
- [ ] `cat .gitmodules` shows correct `branch = ...` for each
- [ ] `README.md` "Latest" section reads v0.4.1
- [ ] `binder/environment.yml` pins `ldaca-web-app==0.4.1`
- [ ] BinderHub launch from a test commit reaches the web app UI
- [ ] [AGENTS.md](AGENTS.md) validated by doing one round-trip change (edit something trivial in the web app, commit there, bump submodule pointer from master, push)
- [ ] This file (`MIGRATION_PLAN.md`) deleted
