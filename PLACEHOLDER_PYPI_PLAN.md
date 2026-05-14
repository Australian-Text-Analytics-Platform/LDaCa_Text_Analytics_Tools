# Placeholder PyPI plan — claim `ldaca-wordflow` and `wordflows`

Transient checklist. Execute after [MIGRATION_PLAN.md](MIGRATION_PLAN.md) is done. Delete this file once both names are claimed on PyPI and the done-criteria boxes are ticked.

## Purpose

Reserve two PyPI names before the upcoming rename:

- **`ldaca-wordflow`** — the future canonical name (replaces `ldaca-web-app`). Today we publish a placeholder that depends on `ldaca-web-app==0.3.5`, so `pip install ldaca-wordflow==0.3.5` works and installs the existing stable code. After [RENAME_PLAN.md](RENAME_PLAN.md) executes, this name becomes the PRIMARY package and `ldaca-web-app` becomes the shim pointing here.
- **`wordflows`** — a defensive name-grab. Publish-and-forget: one placeholder release that depends on `ldaca-web-app==0.3.5`, then leave it dormant. Intended to prevent confusable typosquats; not actively maintained beyond the initial release.

Both names are confirmed available on PyPI as of 2026-05-15.

## Sequencing rationale

We pin to `ldaca-web-app==0.3.5` (not `0.4.1`) because:

- 0.3.5 is the existing stable line on `main` and what `uvx --refresh ldaca-web-app@latest` resolved to for most of the placeholders' intended users.
- 0.4.x is fresh (yanked + hot-fixed within hours), so anchoring a placeholder to it is more change-surface than benefit.
- The rename plan will publish `ldaca-wordflow==0.4.2` as the first real primary release, so leaving `0.3.5` and `0.4.0..0.4.1` unclaimed on `ldaca-wordflow` is intentional — only the placeholder release ever uses `0.3.5` on the new name.

## Steps

### 1. Build the `ldaca-wordflow` placeholder

Create a fresh, minimal repo (or local directory; it's so small that a one-off uv project on disk is fine). Suggested local path: `LDaCA-Text-Analytics-Tools/_pypi_placeholders/ldaca-wordflow/` (gitignore it; don't commit to the master).

`pyproject.toml`:

```toml
[project]
name = "ldaca-wordflow"
version = "0.3.5"
description = "Placeholder. Reserves the ldaca-wordflow name on PyPI ahead of the ldaca-web-app → ldaca-wordflow rename. Installs ldaca-web-app==0.3.5."
readme = "README.md"
requires-python = ">=3.14"
license = { text = "MIT" }
authors = [{ name = "Australian Text Analytics Platform" }]
dependencies = ["ldaca-web-app==0.3.5"]
classifiers = ["Development Status :: 7 - Inactive"]

[project.urls]
Homepage = "https://github.com/Australian-Text-Analytics-Platform/ldaca_text_analytics_tools"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
bypass-selection = true                # no Python module to package — just metadata
```

> Hatch needs `bypass-selection = true` (or an equivalent empty-package shim) so it doesn't fail with "no packages found". If hatch refuses regardless, fall back to `setuptools` with an empty `packages = []` declaration.

`README.md`:

```markdown
# ldaca-wordflow (placeholder)

This is a placeholder release reserving the `ldaca-wordflow` name on PyPI
ahead of the upcoming rename from `ldaca-web-app`.

For the actual application, install `ldaca-web-app==0.3.5` directly, or
wait for `ldaca-wordflow==0.4.2+` which will be the first real release on
this name.

Source: https://github.com/Australian-Text-Analytics-Platform/ldaca_text_analytics_tools
```

### 2. Build the `wordflows` placeholder

Same shape, different name. Suggested path: `LDaCA-Text-Analytics-Tools/_pypi_placeholders/wordflows/`.

`pyproject.toml`:

```toml
[project]
name = "wordflows"
version = "0.3.5"
description = "Defensive placeholder. Reserves the wordflows name on PyPI; installs ldaca-web-app==0.3.5. Not actively maintained — see ldaca-wordflow for releases."
readme = "README.md"
requires-python = ">=3.14"
license = { text = "MIT" }
authors = [{ name = "Australian Text Analytics Platform" }]
dependencies = ["ldaca-web-app==0.3.5"]
classifiers = ["Development Status :: 7 - Inactive"]

[project.urls]
Homepage = "https://github.com/Australian-Text-Analytics-Platform/ldaca_text_analytics_tools"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
bypass-selection = true
```

README mirrors the `ldaca-wordflow` placeholder but states "this is a defensive name-grab; install ldaca-wordflow instead".

### 3. Validate locally

For each placeholder dir:

```bash
cd _pypi_placeholders/ldaca-wordflow
env -u CONDA_PREFIX uv build
twine check --strict dist/*

# Smoke-test the resolution chain — install into a tmp venv and confirm
# that ldaca-web-app==0.3.5 is pulled in.
env -u CONDA_PREFIX uv run --isolated --with dist/ldaca_wordflow-0.3.5-py3-none-any.whl \
    python -c "from importlib.metadata import version; print('ldaca-wordflow', version('ldaca-wordflow')); print('ldaca-web-app', version('ldaca-web-app'))"
# Expected: ldaca-wordflow 0.3.5 / ldaca-web-app 0.3.5
```

Repeat for `wordflows`.

### 4. Publish to TestPyPI first

```bash
env -u CONDA_PREFIX uv run twine upload --repository testpypi dist/*

# Verify
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    ldaca-wordflow==0.3.5
python -c "from importlib.metadata import version; print(version('ldaca-web-app'))"
```

If both placeholders install + resolve cleanly on TestPyPI, proceed.

### 5. Publish to real PyPI

Two separate uploads:

```bash
cd _pypi_placeholders/ldaca-wordflow
env -u CONDA_PREFIX uv run twine upload dist/*

cd ../wordflows
env -u CONDA_PREFIX uv run twine upload dist/*
```

> PyPI publish for placeholders is a manual local `twine upload` — these are throwaway one-off releases that don't warrant a permanent GitHub Actions workflow. Use a project-scoped PyPI API token rather than account-wide.

### 6. Verify on PyPI

```bash
curl -s https://pypi.org/pypi/ldaca-wordflow/json | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['info']['version'], '|', d['info']['summary'])"
curl -s https://pypi.org/pypi/wordflows/json | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['info']['version'], '|', d['info']['summary'])"

# End-to-end resolve test
uvx --refresh --from ldaca-wordflow==0.3.5 python -c \
  "from importlib.metadata import version; print('ldaca-web-app', version('ldaca-web-app'))"
```

## Done criteria

- [ ] `pip install ldaca-wordflow==0.3.5` resolves and pulls `ldaca-web-app==0.3.5`
- [ ] `pip install wordflows==0.3.5` resolves and pulls `ldaca-web-app==0.3.5`
- [ ] Both PyPI project pages exist with clear placeholder descriptions linking back to the master repo
- [ ] The `_pypi_placeholders/` directory is in the master's `.gitignore` (and stays out of git history)
- [ ] This file (`PLACEHOLDER_PYPI_PLAN.md`) deleted
- [ ] [RENAME_PLAN.md](RENAME_PLAN.md) is the next plan to execute

## Notes for the future-rename author

- The placeholder pyproject `description` and README are temporary copy. After the rename, the `ldaca-wordflow` project page becomes the canonical product page — see [RENAME_PLAN.md](RENAME_PLAN.md) for the metadata update that lands with v0.4.2.
- `wordflows` stays a placeholder permanently. Do NOT publish further versions; let it remain at `0.3.5` forever. Its purpose is just to prevent the name from being grabbed.
- If a community user actually starts using `pip install wordflows`, redirect them to `ldaca-wordflow` in the README; don't try to keep `wordflows` in sync.
