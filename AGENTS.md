# Binder launcher repository

This repository owns the Binder notebook and launcher for LDaCA Wordflow. The Wordflow application, native server and release workflow live in [the Wordflow repository](https://github.com/Australian-Text-Analytics-Platform/ldaca-wordflow); do not vendor or build them here.

- `index.ipynb`: user-facing launch and stop cells.
- `launcher.py`: checksum-verified release selection, extraction, process lifecycle and local cache.
- `utils.py`: discover the exact browser origin used by Jupyter Server Proxy.
- `binder/environment.yml`: minimal notebook kernel and proxy dependencies.
- `tests/`: launcher and notebook checks.
- `docs/`: public landing page.

The notebook may use Python's standard library and IPython because Jupyter executes it. Do not add a Wordflow Python package, uv, PyTorch or frontend build to the Binder image. Keep the server on loopback and pass its observed public origin and proxy prefix explicitly. Use one resolved release for each archive and checksum pair, and keep cached releases separate. Preserve files in `DATA_DIR` across server restarts within a Binder session.

Run `python -m pytest -q tests/` before committing. Browser and proxy acceptance requires an actual Binder launch; local tests do not establish that deployment works. Keep historical release notes in Git history rather than active launcher instructions.
