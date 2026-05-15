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

- Published (AEST): 2026-05-15
- Package: `ldaca-wordflow@0.4.3` (CJK perf + multilingual UX polish; see the [wordflow CHANGELOG](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/blob/v0.4.3/CHANGELOG.md) for the full list)
- Nectar BinderHub: [![Binder](https://mybinder.org/badge_logo.svg)](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/5b2f422?labpath=index.ipynb)
- Tauri desktop: [Windows MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.3/LDaCA.Wordflow_0.4.3_x64_en-US.msi) | [macOS DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.3/ldaca-desktop-apple-silicon-0.4.3.dmg)
- Run locally: `uvx --refresh ldaca-wordflow@0.4.3`

## Release History

| Published (AEST) | Version | Nectar BinderHub | Tauri Windows | Tauri macOS | Local command |
| --- | --- | --- | --- | --- | --- |
| 2026-05-15 | `0.4.3` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/5b2f422?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.3/LDaCA.Wordflow_0.4.3_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.3/ldaca-desktop-apple-silicon-0.4.3.dmg) | `uvx --refresh ldaca-wordflow@0.4.3` |
| 2026-05-15 | `0.4.2` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/107cce6?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.2/LDaCA.Wordflow_0.4.2_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.2/ldaca-desktop-apple-silicon-0.4.2.dmg) | `uvx --refresh ldaca-wordflow@0.4.2` |
| 2026-05-15 | `0.4.1` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/b463efa?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.1/LDaCA.Text.Analytics_0.4.1_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.4.1/ldaca-desktop-apple-silicon-0.4.1.dmg) | `uvx --refresh ldaca-web-app@0.4.1` |
| 2026-05-12 | `0.3.2` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/54b6daf0141f077c0de94c0213acae33cf3d397a?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.3.2/LDaCA.Text.Analytics_0.3.2_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.3.2/ldaca-desktop-apple-silicon-0.3.2.dmg) | `uvx --refresh ldaca-web-app@0.3.2` |
| 2026-05-06 | `0.2.9` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/6c68cb11622ee245a2c2063947baa73939bae2c7?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.2.9/LDaCA.Text.Analytics_0.2.9_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.2.9/ldaca-desktop-apple-silicon-0.2.9.dmg) | `uvx --refresh ldaca-web-app@0.2.9` |
| 2026-05-03 | `0.2.2` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/8427a10ec8607cf3087d341b871cb64d4ab64dd2?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.2.2/LDaCA.Text.Analytics_0.2.2_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.2.2/ldaca-desktop-apple-silicon.dmg) | `uvx --refresh ldaca-web-app@0.2.2` |

Historical release rows above `v0.4.2` keep the `ldaca-web-app` install command since those versions only exist under the old PyPI name. GitHub release-asset links auto-redirect from the old `ldaca_web_app` repo slug to `ldaca-wordflow`.

## Local development

```bash
uvx --refresh ldaca-wordflow@latest
```
