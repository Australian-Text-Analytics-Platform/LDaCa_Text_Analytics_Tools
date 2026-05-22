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

- Published (AEST): 2026-05-21
- Package: `ldaca-wordflow@0.5.1` (multi-user tokens-cache safety + lazy on-demand tokenisation + concordance L1/R1 polish + mojibake repair on load; see the [wordflow CHANGELOG](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/blob/v0.5.1/CHANGELOG.md) for the full list)
- Nectar BinderHub: [![Binder](https://mybinder.org/badge_logo.svg)](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/98c8082?labpath=index.ipynb)
- Tauri desktop: [Windows MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.1/LDaCA.Wordflow_0.5.1_x64_en-US.msi) | [macOS DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.1/ldaca-desktop-apple-silicon-0.5.1.dmg)
- Run locally: `uvx --refresh ldaca-wordflow@0.5.1`

## What's new in v0.5.1 — Multi-user Cache Safety + Lazy Tokenisation

**Multi-user tokens-cache safety.** A workspace tokenised by one user and shared with another no longer writes cache parquets into the original author's folder — each user's cache stays in their own tree. The previous shared `.cache/` directory was readable by every authenticated user via the data-loader, effectively exposing tokenised content across accounts; v0.5.1 moves the cache inside each user's own folder and rewrites a shared workspace's lazy tokens expression on load to stamp it under the current user's identity. Matters for the Nectar multi-user deployment and for any future filesystem where ACLs aren't relied on for separation.

**Lazy on-demand tokenisation by default.** The tokens cache is now a side effect of analysis (filled lazily on the first collect), not something the user manages explicitly. The Tokenise dialog completes instantly; per-row tokens fill in on demand under an advisory lock. The Phase 2.5 "repair banner" + cross-machine workspace repair flow is replaced by an automatic plan-time alignment hook that handles cross-user, cross-machine, and cross-OS path differences uniformly. v0.5.0 and earlier workspaces are auto-migrated to the lazy form on first open.

Polish across the analyses ships alongside:

- **Concordance:** L1/R1 columns now sit adjacent to the match, with duplicates dimmed in-place and a per-column text-colour picker; a "Hide L1/R1" toggle keeps the tighter layout available when those columns aren't useful.
- **Token-frequency:** last-used language + model persist to preferences; %DIFF / LogRatio formulas aligned with the Lancaster wizard so cross-tool keyness comparisons agree to the published reference.
- **Mojibake repair at the data-loader boundary** — classic `Ã©` / `â€™` garbage from UTF-8 re-encoded through CP-1252 is detected and repaired on load via `ftfy`, gated to the encoding fixers only so CJK / Arabic / Cyrillic corpora stay untouched.

One graph-rendering safety fix that previously only existed in source-checkout users now reaches PyPI users via `docworkspace>=0.2.9`: a failing `Node.info()` (e.g. source parquet moved or deleted) returns a per-node error envelope rather than 500'ing the whole graph endpoint. See the [wordflow CHANGELOG](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/blob/v0.5.1/CHANGELOG.md) for the full v0.5.1 entry.

## Release History

| Published (AEST) | Version | Nectar BinderHub | Tauri Windows | Tauri macOS | Local command |
| --- | --- | --- | --- | --- | --- |
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

## Local development

```bash
uvx --refresh ldaca-wordflow@latest
```
