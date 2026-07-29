"""Binder-specific helpers for the LDaCA Wordflow notebook launcher."""

from __future__ import annotations

import asyncio
import logging
import os
import urllib.error
import urllib.request

# Silence huggingface_hub's tqdm progress bars before the backend's
# model_prefetch fires. In Jupyter, hf_hub auto-selects tqdm.notebook
# whose __del__ path crashes when bars are built off the main thread —
# the downloads succeed, but the tracebacks land in the cell output.
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")


def _quiet_logging() -> None:
    """Suppress backend + uvicorn INFO output so the launcher cell stays clean.

    Uvicorn rebuilds its logging config with log_level="info" when the server
    starts, which would otherwise overwrite any pre-set level on the uvicorn
    loggers, so we call this once after start_async_server has returned.
    """
    logging.disable(logging.INFO)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error", "ldaca_wordflow"):
        logging.getLogger(name).setLevel(logging.WARNING)


def _probe_once(probe_url: str) -> bool:
    """One blocking readiness probe. ``True`` if the backend serves a non-5xx.

    A 4xx still means the app is up and routing; only a 5xx (or no connection
    yet) means "startup not finished — keep waiting". Runs off the event loop
    via ``asyncio.to_thread`` so the short blocking ``urlopen`` never stalls the
    loop the server task lives on.
    """
    try:
        with urllib.request.urlopen(probe_url, timeout=2) as resp:
            return resp.status < 500
    except urllib.error.HTTPError as exc:
        return exc.code < 500
    except (urllib.error.URLError, ConnectionError, OSError):
        return False


async def _await_until_ready(
    probe_url: str, timeout: float, interval: float = 0.25
) -> bool:
    """Cooperatively poll ``probe_url`` until the backend serves a clean response.

    CRUCIAL: ``start_async_server()`` runs the server as an ``asyncio.Task``
    on the *same* event loop that runs this notebook cell. A blocking poll
    (``time.sleep`` + sync ``urlopen``) would starve that loop, so the server
    task could never answer — the poll would then spin until it timed out.
    Here every wait yields control back to the loop (``await asyncio.sleep`` /
    ``asyncio.to_thread``), letting the server task respond. Since v0.7 the
    launcher only returns after startup completes, so the first probe normally
    succeeds immediately; this remains as a belt-and-braces check.

    Returns ``True`` once ready, ``False`` if ``timeout`` elapses first (in
    which case the caller opens the tab anyway rather than hang forever).
    """
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if await asyncio.to_thread(_probe_once, probe_url):
            return True
        await asyncio.sleep(interval)
    return False


async def display_app_link(
    port: int = 8001, startup_delay: float = 0.0, ready_timeout: float = 30.0
) -> None:
    """Show a clickable link to open Wordflow, adapting to Binder/JupyterHub or local.

    Awaitable — call it as ``await display_app_link(port=PORT)`` from the
    notebook cell. It waits until the backend actually serves a clean response
    (up to ``ready_timeout``) before auto-opening the new tab, so the tab never
    lands on the startup-race "500 : Internal Server Error". Because the wait is
    cooperative (see ``_await_until_ready``), the background server task is free
    to run while we wait, so readiness is reached almost immediately rather than
    being blocked behind the poll.
    """
    _quiet_logging()

    base = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "")
    if base:
        if not base.endswith("/"):
            base += "/"
        url = f"{base}proxy/{port}/"
    else:
        url = f"http://localhost:{port}/"

    # Optional minimum grace, then wait for real readiness. The user-facing URL
    # may be a JupyterHub proxy path (relative + cookie-authed), so probe the
    # backend directly on localhost — once that serves cleanly, the proxied tab
    # will too.
    if startup_delay > 0:
        await asyncio.sleep(startup_delay)
    await _await_until_ready(f"http://localhost:{port}/", timeout=ready_timeout)

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
