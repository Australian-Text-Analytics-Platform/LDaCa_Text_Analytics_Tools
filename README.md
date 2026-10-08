# LDaCA Text Analytics Tools

## Current release: Wordflow 0.7.11 (stable)

Released 8 October 2026. Wordflow 0.7.11 is the stable version for workshops and everyday use; Wordflow 0.8 is in beta.

- Try it in your browser: [Launch Wordflow 0.7.11 on ARDC BinderHub](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/main?labpath=index.ipynb)
- Desktop app, with everything included: [Windows](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.11/ldaca-wordflow_0.7.11_windows-x86_64.msi) · [macOS (Apple Silicon)](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/download/v0.7.11/ldaca-wordflow_0.7.11_darwin-aarch64.dmg)
- Run locally with Python: `uvx --refresh ldaca-wordflow@0.7.11`
- What's new: [release notes](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/tag/v0.7.11)

The Binder launch above runs from `main`, which installs `ldaca-wordflow[deploy]==0.7.11` from PyPI. The Wordflow 0.8 native-server launcher is on the [`binder-v0.8`](https://github.com/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/tree/binder-v0.8) branch until 0.8 is released as stable.


This repository launches [LDaCA Wordflow](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow) on Binder and hosts the LDaCA Text Analytics Tools landing page. Wordflow itself is developed in its own repository.

[Open the notebook on Nectar BinderHub](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/main?labpath=index.ipynb) · [Open on mybinder.org](https://mybinder.org/v2/gh/Australian-Text-Analytics-Platform/LDaCa_Text_Analytics_Tools/main?labpath=index.ipynb) · [Releases](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow/releases/latest)

## Launch and storage

The Binder image installs the Wordflow release pinned in `binder/environment.yml` from PyPI. Open `index.ipynb` and run the launch cell: it starts Wordflow inside the notebook kernel on `127.0.0.1:8001` and shows a link that opens it through Jupyter Server Proxy. The **Stop Wordflow** cell stops it.

The launch cell shows only Wordflow's warnings and errors. Set `LOG_LEVEL` to `"INFO"` in that cell to see a line for every request.

Wordflow keeps its data under `DATA_ROOT` (default `~/Documents/ldaca`). Binder storage normally disappears when the session ends, so download any Project you want to keep.

## Files

- `index.ipynb`: launch, inspect and stop cells.
- `utils.py`: works out the public host that Jupyter Server Proxy forwards, so Wordflow accepts its requests.
- `binder/environment.yml`: Python and the pinned `ldaca-wordflow[deploy]` release.
- `docs/`: the landing page, published with GitHub Pages.

## Releasing a new Wordflow 0.7.x

Change the pin in `binder/environment.yml`, update the version, installer links and release date here and in `docs/index.html`, then launch the Binder link once so BinderHub builds the new image.
