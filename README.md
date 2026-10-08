# LDaCA Text Analytics Tools

## Current release: Wordflow 0.7.11 (stable)

Released 8 October 2026. Wordflow 0.7.11 is the stable version for workshops and everyday use; Wordflow 0.8 is in beta.

- Try it in your browser: [Launch Wordflow 0.7.11 on ARDC BinderHub](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/6d244bb?labpath=index.ipynb)
- Desktop app, with everything included: [Windows](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.11/ldaca-wordflow_0.7.11_windows-x86_64.msi) · [macOS (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.11/ldaca-wordflow_0.7.11_darwin-aarch64.dmg)
- Run locally with Python: `uvx --refresh ldaca-wordflow@0.7.11`
- What's new: [release notes](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/tag/v0.7.11)

The Binder launch above runs from the `binder-v0.7` branch, which installs `ldaca-wordflow[deploy]==0.7.11` from PyPI. The launcher described below, on `main`, is for the Wordflow 0.8 native server; use the links above until 0.8 is released as stable.


This repository launches [LDaCA Wordflow](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow) on Binder. The notebook downloads a checksum-verified native server from the latest stable Wordflow release, runs it on loopback, and opens its React interface through Jupyter Server Proxy. Wordflow's source, frontend build tools, Python package and model assets are not installed in the Binder image.

[Open the notebook on Nectar BinderHub](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/main?labpath=index.ipynb) · [Open on mybinder.org](https://mybinder.org/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/main?labpath=index.ipynb) · [Desktop and server releases](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/latest)

## Launch and storage

Open `index.ipynb` and run **Launch Wordflow**. The launcher resolves one release, downloads its platform archive and `server-SHA256SUMS` from that release, verifies the archive, and caches it by release tag. Re-running the cell reuses the healthy server. The **Stop Wordflow** cell requests a graceful shutdown.

Set `DATA_DIR` before launching to choose storage; the default is `~/wordflow`. The server keeps uploaded files in `data/` and saved `.wfpj` projects in `projects/`. Use Wordflow's **Data files** and **Project** controls to upload, import, save and download. Binder storage normally disappears when the session ends. Download projects you need to keep.

The notebook needs a Python kernel to orchestrate the native process and Jupyter Server Proxy to expose it. The app itself runs as a Rust executable with its production frontend embedded. ICU and optional model files are downloaded when first used.

On Nectar, the launcher uses the public notebook origin `https://binder.rc.nectar.org.au`. On another Binder host, it tries to discover the origin through the browser. If that host blocks notebook JavaScript, set `WORDFLOW_PUBLIC_ORIGIN` to the exact origin shown in your browser URL (scheme, hostname and optional port, without a path) before running the launch cell.

## Release and tests

Release archives use stable platform names, such as [`wordflow-server-x86_64-unknown-linux-gnu.tar.gz`](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/latest/download/wordflow-server-x86_64-unknown-linux-gnu.tar.gz). The launcher selects the archive and checksum from the same release and refuses an incomplete or unverified release.

Launcher tests: `python -m pytest -q tests/` (install `pytest` in a development environment). These tests check archive validation and lifecycle; the notebook and web interface must also be exercised on an actual Binder deployment after a native release is published.
