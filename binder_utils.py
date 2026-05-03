"""Binder-specific helpers for the LDaCA web app notebook launcher."""

from __future__ import annotations

from html import escape
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def _wait_for_local_server(port: int, timeout_seconds: float = 15.0) -> None:
    """Wait briefly until the local server starts accepting HTTP requests."""
    deadline = time.monotonic() + timeout_seconds
    probe_urls = (
        f"http://127.0.0.1:{port}/health",
        f"http://127.0.0.1:{port}/",
    )

    while time.monotonic() < deadline:
        for probe_url in probe_urls:
            try:
                with urlopen(probe_url, timeout=1.0) as response:
                    if response.status < 500:
                        return
            except HTTPError as exc:
                if exc.code < 500:
                    return
            except URLError:
                pass
        time.sleep(0.25)


def _build_app_url(port: int) -> str:
    """Return the Binder/JupyterHub-aware URL for the proxied web app."""
    base = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "")
    if base:
        if not base.endswith("/"):
            base += "/"
        return f"{base}proxy/{port}/"
    return f"http://localhost:{port}/"


def display_app_link(
    port: int = 8001,
    *,
    app_version: str | None = None,
    auto_open: bool = True,
) -> str:
    """Show a prominent launch button for the web app and return its URL."""
    _wait_for_local_server(port)

    url = _build_app_url(port)
    version_markup = ""
    if app_version:
        version_markup = (
            "<div style=\"margin:0 0 0.5rem 0;font-size:0.95rem;"
            "color:#355070;font-weight:600;\">"
            f"ldaca-web-app version: {escape(app_version)}"
            "</div>"
        )

    try:
        from IPython.display import HTML, Javascript, display

        if auto_open:
            display(Javascript(f"window.open('{url}', '_blank');"))

        display(
            HTML(
                """
                <div style="
                    margin: 1rem 0;
                    padding: 1.25rem 1.4rem;
                    border-radius: 18px;
                    background: linear-gradient(135deg, #f7f7f2 0%, #e9f5db 100%);
                    border: 1px solid #cfe1b9;
                    box-shadow: 0 10px 30px rgba(64, 81, 59, 0.08);
                    font-family: Georgia, 'Iowan Old Style', serif;
                ">
                    <div style="font-size: 1.35rem; font-weight: 700; color: #1f3b2d; margin-bottom: 0.35rem;">
                        Launch the LDaCA Text Analytics Web App
                    </div>
                """
                + version_markup
                + f"""
                    <div style="font-size: 0.98rem; color: #4f5d4d; margin-bottom: 1rem;">
                        The web interface opens in a new browser tab. If your browser blocks the automatic tab,
                        use the button below.
                    </div>
                    <a href="{escape(url)}" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">
                        <span style="
                            display:inline-block;
                            background:#264653;
                            color:#ffffff;
                            font-size:1rem;
                            font-weight:700;
                            padding:0.8rem 1.25rem;
                            border-radius:999px;
                            letter-spacing:0.01em;
                        ">
                            Open Web App
                        </span>
                    </a>
                </div>
                """
            )
        )
    except ImportError:
        print(f"Open web app: {url}")

    return url