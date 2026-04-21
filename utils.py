"""Binder-specific helpers for the LDaCA web app notebook launcher."""

from __future__ import annotations

import os


def display_app_link(port: int = 8001) -> None:
    """Show a clickable link to open the web app, adapting to Binder/JupyterHub or local."""
    base = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "")
    if base:
        if not base.endswith("/"):
            base += "/"
        url = f"{base}proxy/{port}/"
    else:
        url = f"http://localhost:{port}/"

    try:
        from IPython.display import Javascript, Markdown, display

        display(Javascript(f"window.open('{url}', '_blank');"))
        display(
            Markdown(
                f"Click the following link to open the web app:\n# [Open web app]({url})"
            )
        )
    except ImportError:
        print(f"Open web app: {url}")
