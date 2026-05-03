# LDaCa Text Analytics Tools

This repository publishes notebook-first Binder launches for pinned
`ldaca-web-app` releases, alongside versioned Tauri desktop downloads for the
same published versions. Use the latest section for the newest published
environment, or pick a specific historical version when you need a stable,
versioned setup.

## Latest

- Published (AEST): 2026-05-03
- Package: `ldaca-web-app@0.2.3`
- Nectar BinderHub: [![Binder](https://mybinder.org/badge_logo.svg)](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/54b34a3a654acc94f303522aa29a5e93f929a1af?labpath=index.ipynb)
- Tauri desktop: [Windows MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca_web_app/releases/download/v0.2.3/LDaCA.Text.Analytics_0.2.2_x64_en-US.msi) | [macOS DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca_web_app/releases/download/v0.2.3/ldaca-desktop-apple-silicon.dmg)
- Run locally: `uvx --refresh ldaca-web-app@0.2.3`

## Release History

| Published (AEST) | Version | Nectar BinderHub | Tauri Windows | Tauri macOS | Local command |
| --- | --- | --- | --- | --- | --- |
| 2026-05-03 | `0.2.3` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/54b34a3a654acc94f303522aa29a5e93f929a1af?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca_web_app/releases/download/v0.2.3/LDaCA.Text.Analytics_0.2.2_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca_web_app/releases/download/v0.2.3/ldaca-desktop-apple-silicon.dmg) | `uvx --refresh ldaca-web-app@0.2.3` |
| 2026-05-03 | `0.2.2` | [Open notebook](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/8427a10ec8607cf3087d341b871cb64d4ab64dd2?labpath=index.ipynb) | [MSI](https://github.com/Australian-Text-Analytics-Platform/ldaca_web_app/releases/download/v0.2.2/LDaCA.Text.Analytics_0.2.2_x64_en-US.msi) | [DMG (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca_web_app/releases/download/v0.2.2/ldaca-desktop-apple-silicon.dmg) | `uvx --refresh ldaca-web-app@0.2.2` |

## Local development

```bash
uvx --refresh ldaca-web-app@latest
```
