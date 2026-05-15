"""Binder-specific helpers for the LDaCA Wordflow notebook launcher."""

from __future__ import annotations

import os
import time

# Silence huggingface_hub's tqdm progress bars before the backend's
# model_prefetch fires. In Jupyter, hf_hub auto-selects tqdm.notebook
# whose __del__ path crashes when bars are built off the main thread —
# the downloads succeed, but the tracebacks land in the cell output.
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")


def display_app_link(port: int = 8001, startup_delay: float = 3.0) -> None:
    """Show a clickable link to open Wordflow, adapting to Binder/JupyterHub or local.

    Waits ``startup_delay`` seconds before auto-opening the new tab so the
    backend has time to bind its port — otherwise the first request races
    the FastAPI startup and the user gets a 500.
    """
    base = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "")
    if base:
        if not base.endswith("/"):
            base += "/"
        url = f"{base}proxy/{port}/"
    else:
        url = f"http://localhost:{port}/"

    if startup_delay > 0:
        time.sleep(startup_delay)

    try:
        from IPython.display import Javascript, Markdown, display

        display(Javascript(f"window.open('{url}', '_blank');"))
        display(
            Markdown(
                f"Click the following link to open LDaCA Wordflow:\n# [Open LDaCA Wordflow]({url})"
            )
        )
    except ImportError:
        print(f"Open LDaCA Wordflow: {url}")
