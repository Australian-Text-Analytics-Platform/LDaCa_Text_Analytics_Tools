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

- Published (AEST): 2026-05-25
- Package: `ldaca-wordflow@0.5.3` (re-stamps yanked v0.5.2; workspace-rename fix + file-tree productivity + Apache-2.0 relicense; see the [wordflow CHANGELOG](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/blob/v0.5.3/CHANGELOG.md) for the full list)
- Nectar BinderHub: [![Binder](https://mybinder.org/badge_logo.svg)](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/ad73a87?labpath=index.ipynb)
- Tauri desktop: [Windows MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.3/LDaCA.Wordflow_0.5.3_x64_en-US.msi) | [macOS DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.3/ldaca-desktop-apple-silicon-0.5.3.dmg)
- Run locally: `uvx --refresh ldaca-wordflow@0.5.3`

## What's new in v0.5.3 — Workspace Rename Fix + File-tree Productivity + Apache-2.0

**Workspace rename keeps data blocks loadable.** In v0.5.1 and earlier, renaming a workspace silently invalidated all of its data blocks — the scan paths inside the saved plan still pointed at the old workspace directory, so reopening the renamed workspace either produced empty blocks or failed on materialisation. v0.5.3 rebases those scan paths transactionally as part of the rename, so blocks stay valid across renames. This was the headline fix that v0.5.2 was meant to ship; v0.5.2 has been yanked from PyPI after the release-branch cherry-pick dropped this commit (and two file-tree feature commits) on its way to the published wheel.

**File-tree productivity.** Three small additions add up to a much faster data-loader pass:

- **Folder operations:** delete a folder (with explicit confirmation), drag a file or folder onto another folder to move it, and folder expand/collapse state is remembered for the session so navigating a deep dataset keeps your context between dialogs.
- **Name your data block when adding a file** — the Add-file flow now offers an editable name field so the resulting workspace node carries the label you intend, not the auto-derived filename stem.
- **Find your newly uploaded workspace** — uploading a workspace ZIP now scrolls the matching row into view in the workspace list and highlights it with the existing hint system, so you can tell at a glance which workspace just landed and load it from there.

**Apache-2.0 relicense.** Source files now carry Apache-2.0 headers and `NOTICE` lists the LDaCA + SIH joint copyright for 2025-2026. No behavioural changes for end users. Previous releases remain available under their original MIT license.

**AI Annotator hidden from the sidebar.** The early-prototype AI Annotator tool is removed from the sidebar nav and from the "Edit visible views" toggle. The feature code and routing are intact; it remains accessible via direct URL while the tool matures. See the [wordflow CHANGELOG](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/blob/v0.5.3/CHANGELOG.md) for the full v0.5.3 entry.

## Release History

| Published (AEST) | Version | Nectar BinderHub | Tauri Windows | Tauri macOS | Local command |
| --- | --- | --- | --- | --- | --- |
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

## Local development

```bash
uvx --refresh ldaca-wordflow@latest
```
