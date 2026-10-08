# Binder launcher repository

This repository owns the Binder notebook and the LDaCA Text Analytics Tools landing page. The Wordflow application, its releases and its documentation live in [the Wordflow repository](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow); do not vendor or build them here.

`main` runs the current stable release, Wordflow 0.7.11, installed from PyPI:

- `index.ipynb`: launch, inspect and stop cells. The launch cell sets `LOG_LEVEL=WARNING` and calls `ldaca_wordflow.start_async_server` with the Jupyter proxy `root_path`.
- `utils.py`: `configure_hub_networking()` finds the public hub host and adds it to Wordflow's allowed hosts and origins before it starts.
- `binder/environment.yml`: Python 3.14.5 and the exact `ldaca-wordflow[deploy]==X.Y.Z` pin. Keep the exact `python=X.Y.Z` form; repo2docker ignores ranges.
- `docs/`: public landing page (GitHub Pages from `main:/docs`).

Branches:

- `binder-v0.8`: the Wordflow 0.8 native-server launcher (checksum-verified release download, no Python package). Bring it back to `main` when 0.8 is the stable release.
- `binder-v0.7`: the earlier pinned v0.7 launcher with the legacy `ldaca_wordflow` submodule; kept for old links only.

For a new 0.7.x release, change the pin, the version and installer links in `README.md` and `docs/index.html`, and launch the Binder link once so the image is built. Browser and proxy behaviour can only be checked on a real Binder launch.
