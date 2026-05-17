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

- Published (AEST): 2026-05-17
- Package: `ldaca-wordflow@0.5.0` (demo snapshots across all 5 analysis tools + Trends client-side re-aggregation + dtype normalisation on load; see the [wordflow CHANGELOG](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/blob/v0.5.0/CHANGELOG.md) for the full list)
- Nectar BinderHub: [![Binder](https://mybinder.org/badge_logo.svg)](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/0fa075e?labpath=index.ipynb)
- Tauri desktop: [Windows MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.0/LDaCA.Wordflow_0.5.0_x64_en-US.msi) | [macOS DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.5.0/ldaca-desktop-apple-silicon-0.5.0.dmg)
- Run locally: `uvx --refresh ldaca-wordflow@0.5.0`

## What's new in v0.5.0 — Demo Snapshots

**Save an analysis exactly the way it appears on screen, then re-open it later or share with a collaborator — no re-run required.**

Every one of the five analysis tools — Concordance, Quotation, Trends, Token Frequency, Topic Modelling — now has Save / Open snapshot buttons in its header. Saved bundles are small `.ldaca-snapshot` zips that travel through email, Slack, or the new Sample Data dialog's "Demo snapshots" import tab. Loaded snapshots render in a read-only viewer with a banner showing where they came from.

The headline feature is **Trends client-side re-aggregation**. Trends snapshots are captured as **data-rich payloads**: pick the finest time bin (down to seconds) and up to 3 group-by columns at save time, and the viewer can locally coarsen frequency (daily → weekly → monthly → …), drop group dimensions, and case-fold the legend — all without a backend round-trip. A 200 000-row hard cap protects bundle size, with a live cardinality-aware estimator and an opt-in backend dry-run for verification near the cap.

Two infrastructure improvements ship alongside:

- **Dtype normalisation on load** — mixed-precision columns (`Int8` / `Float32` / naïve datetimes) are now coerced to a canonical profile (Int64 / Float64 / Datetime[μs, UTC] / Utf8) with one consolidated warning per file. Workspace save / reopen no longer fails on integer-width mismatches from some sample-data feeds.
- **Centralized "Disabled in snapshot view" tooltip** — every read-only control across all five tools now surfaces the same hover hint, with no native-`title=` 1–2 s delay.

Token-frequency and Topic-modelling snapshots also keep their post-fit controls live (stopwords filter, words-per-topic slider, display caps, sort), so the viewer is interactive enough to support real exploration of a saved analysis. See the [wordflow CHANGELOG](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/blob/v0.5.0/CHANGELOG.md) for the full v0.5.0 entry.

## Release History

| Published (AEST) | Version | Nectar BinderHub | Tauri Windows | Tauri macOS | Local command |
| --- | --- | --- | --- | --- | --- |
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
