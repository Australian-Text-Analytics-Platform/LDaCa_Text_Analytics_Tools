"""Binder-specific helpers for the LDaCA Wordflow notebook launcher."""

from __future__ import annotations

import logging
import os
import time
import urllib.error
import urllib.request

# Silence huggingface_hub's tqdm progress bars before the backend's
# model_prefetch fires. In Jupyter, hf_hub auto-selects tqdm.notebook
# whose __del__ path crashes when bars are built off the main thread —
# the downloads succeed, but the tracebacks land in the cell output.
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")


def _quiet_logging() -> None:
    """Suppress backend + uvicorn INFO output so the launcher cell stays clean.

    Uvicorn rebuilds its logging config on start_server() with log_level="info",
    which would otherwise overwrite any pre-set level on the uvicorn loggers,
    so we call this once after start_server has had a chance to initialize.
    """
    logging.disable(logging.INFO)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error", "ldaca_wordflow"):
        logging.getLogger(name).setLevel(logging.WARNING)


def _wait_until_ready(probe_url: str, timeout: float, interval: float = 0.25) -> bool:
    """Poll ``probe_url`` until the backend serves a non-5xx response.

    The backend binds its port a beat before its startup events finish
    wiring the route table / static mounts (and, on a cold Binder, before
    model prefetch settles). During that window the root request returns a
    5xx — which is exactly the "500 : Internal Server Error" the auto-opened
    tab lands on. A fixed sleep can't cover a variable cold start, so we wait
    for an actual clean response instead.

    Returns ``True`` once ready, ``False`` if ``timeout`` elapses first (in
    which case the caller opens the tab anyway rather than hang forever).
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(probe_url, timeout=2) as resp:
                if resp.status < 500:
                    return True
        except urllib.error.HTTPError as exc:
            # A 4xx still means the app is up and routing; only 5xx means
            # "startup not finished — keep waiting".
            if exc.code < 500:
                return True
        except (urllib.error.URLError, ConnectionError, OSError):
            pass  # not listening yet
        time.sleep(interval)
    return False


def display_app_link(
    port: int = 8001, startup_delay: float = 3.0, ready_timeout: float = 60.0
) -> None:
    """Show a clickable link to open Wordflow, adapting to Binder/JupyterHub or local.

    Waits at least ``startup_delay`` seconds and then until the backend
    actually serves a clean response (up to ``ready_timeout``) before
    auto-opening the new tab. Opening the moment the port binds races the
    FastAPI startup and the first request lands on a 500 — so we probe the
    in-container ``localhost`` root until it's genuinely ready.
    """
    _quiet_logging()

    base = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "")
    if base:
        if not base.endswith("/"):
            base += "/"
        url = f"{base}proxy/{port}/"
    else:
        url = f"http://localhost:{port}/"

    # Minimum grace, then wait for real readiness. The user-facing URL may be
    # a JupyterHub proxy path (relative + cookie-authed), so probe the backend
    # directly on localhost — once that serves cleanly, the proxied tab will too.
    if startup_delay > 0:
        time.sleep(startup_delay)
    _wait_until_ready(f"http://localhost:{port}/", timeout=ready_timeout)

    # Uvicorn finishes setup_logging during its first request; re-apply so any
    # later access-log records still respect WARNING.
    _quiet_logging()

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
