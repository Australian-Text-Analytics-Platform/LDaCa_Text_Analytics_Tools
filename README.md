# LDaCA Binder

This repository is the Binder wrapper for the LDaCA web application. It opens the `ldaca_web_app` repository directly in Binder without building a Docker image.

## Repository layout

- `binder/` contains the repo2docker environment and post-build setup.
- `ldaca_web_app/` is the application submodule (used only for local development; Binder installs from PyPI).
- `ldaca_web_app_launch.ipynb` is the Binder notebook entry point.
- `utils.py` provides Binder-specific helpers (JupyterHub proxy URL detection).

## Binder launch

[![Binder](https://mybinder.org/badge_logo.svg)](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/ldaca_web_app_binder/main?labpath=ldaca_web_app_launch.ipynb)

## Local development

```bash
uv sync
```
