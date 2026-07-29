"""Binder-specific helpers for the LDaCA Wordflow notebook launcher."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

# Silence huggingface_hub's tqdm progress bars before the backend's
# model_prefetch fires. In Jupyter, hf_hub auto-selects tqdm.notebook
# whose __del__ path crashes when bars are built off the main thread —
# the downloads succeed, but the tracebacks land in the cell output.
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")


def _public_hub_hosts() -> set[str]:
    """Collect the hub's public hostname(s) from Binder/JupyterHub env vars."""

    hosts: set[str] = set()
    for var in (
        "BINDER_LAUNCH_HOST",
        "JUPYTERHUB_PUBLIC_URL",
        "JUPYTERHUB_PUBLIC_HUB_URL",
        "JUPYTERHUB_HOST",
    ):
        raw = os.environ.get(var, "").strip()
        if not raw:
            continue
        host = urlsplit(raw).hostname if "://" in raw else raw.split(":")[0]
        if host:
            hosts.add(host.casefold().rstrip("."))
    return hosts


def _patch_baked_api_base() -> None:
    """Blank the localhost API base baked into the 0.7.0 frontend bundle.

    The published wheel's SPA was built with
    ``VITE_BACKEND_API_BASE=http://localhost:8001/api`` left over from a dev
    environment. In the frontend's URL resolution that build-time override
    outranks the runtime ``basePath`` injection that handles reverse-proxy
    serving, so behind a hub proxy the app polls the *viewer's* machine
    (net::ERR_CONNECTION_REFUSED on /health). Blanking the constant lets the
    bundle fall through to the runtime-config base path. Idempotent, and a
    no-op once a fixed wheel ships or when Wordflow is not installed.
    """

    try:
        import ldaca_wordflow
    except ImportError:
        return
    assets = (
        Path(ldaca_wordflow.__file__).parent / "resources" / "frontend" / "build" / "assets"
    )
    if not assets.is_dir():
        return
    # The constant lands in a different chunk per release (env-*.js in 0.7.0,
    # compiler-runtime-*.js in 0.7.1), so sweep every chunk.
    baked = "http://localhost:8001/api"
    for bundle in assets.glob("*.js"):
        try:
            text = bundle.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # the wheel ships macOS "._*" AppleDouble files
        patched = text
        for quote in ("`", "'", '"'):
            patched = patched.replace(f"{quote}{baked}{quote}", quote * 2)
        if patched != text:
            bundle.write_text(patched, encoding="utf-8")
            print(f"Patched baked dev API base out of {bundle.name}.")


_patch_baked_api_base()


# Exposed for tests: the ephemeral sniffer port while a sniff is in flight.
_sniff_port: int | None = None


async def _sniff_forwarded_host(timeout: float) -> tuple[str, str] | None:
    """Learn the exact (host, scheme) jupyter-server-proxy forwards to apps.

    Serves one ephemeral localhost endpoint and asks the notebook's own
    browser to fetch it through the hub proxy. The Host header of that request
    is precisely what Wordflow's ExactHostMiddleware will later see — no
    guessing from env vars, which name the *launch* host (BINDER_LAUNCH_HOST)
    rather than the JupyterHub domain the session actually runs on (on Nectar
    the two differ, and JUPYTERHUB_PUBLIC_URL is left empty). Returns None if
    no browser answers within ``timeout`` (e.g. headless execution).
    """

    global _sniff_port
    loop = asyncio.get_running_loop()
    result: asyncio.Future[tuple[str, str]] = loop.create_future()

    async def handle(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            raw = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=5)
        except (asyncio.IncompleteReadError, asyncio.LimitOverrunError, TimeoutError):
            raw = b""
        headers: dict[str, str] = {}
        for line in raw.split(b"\r\n")[1:]:
            if b":" in line:
                key, value = line.split(b":", 1)
                headers[key.strip().lower().decode("latin-1")] = value.strip().decode(
                    "latin-1"
                )
        writer.write(
            b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
            b"Content-Length: 2\r\nConnection: close\r\n\r\nok"
        )
        try:
            await writer.drain()
        finally:
            writer.close()
        host = urlsplit(f"//{headers.get('host', '')}").hostname
        # X-Forwarded-Proto may list one entry per proxy hop
        # ("https,http" on Nectar); the first is the browser-facing scheme.
        scheme = headers.get("x-forwarded-proto", "").split(",")[0].strip().casefold()
        if host and not result.done():
            result.set_result(
                (
                    host.casefold().rstrip("."),
                    scheme if scheme in {"http", "https"} else "https",
                )
            )

    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    _sniff_port = port = server.sockets[0].getsockname()[1]
    prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
    probe_url = f"{prefix if prefix.endswith('/') else prefix + '/'}proxy/{port}/"
    try:
        try:
            from IPython.display import Javascript, display

            display(Javascript(f"void fetch('{probe_url}', {{cache: 'no-store'}});"))
        except ImportError:
            print(f"Fetch {probe_url} from your browser to identify the hub host.")
        return await asyncio.wait_for(result, timeout)
    except TimeoutError:
        return None
    finally:
        _sniff_port = None
        server.close()
        await server.wait_closed()


def _merge_env_list(name: str, additions: set[str]) -> None:
    """Union ``additions`` into the JSON-list env var ``name``."""

    try:
        existing = set(json.loads(os.environ.get(name, "[]")))
    except (json.JSONDecodeError, TypeError):
        existing = set()
    os.environ[name] = json.dumps(sorted(existing | additions))


async def configure_hub_networking(sniff_timeout: float = 15.0) -> None:
    """Allowlist the hub's public host before the Wordflow backend launches.

    Wordflow v0.7 rejects requests whose Host header is not allowlisted
    (``ExactHostMiddleware``, default: localhost only) and unsafe requests
    whose Origin does not match the request origin (``CsrfOriginMiddleware``).
    jupyter-server-proxy forwards the browser's original Host and Origin, so
    without this the proxied app answers every request with
    ``host_not_allowed``. The allowlists come from the TRUSTED_HOSTS and
    CORS_ALLOWED_ORIGINS settings env vars, which must be in place before
    ``start_async_server()`` loads settings — call this first, from the same
    cell. Outside a hub (no JUPYTERHUB_SERVICE_PREFIX) this is a no-op.
    """

    if not os.environ.get("JUPYTERHUB_SERVICE_PREFIX"):
        return

    hosts = _public_hub_hosts()
    schemes = {"https"}
    sniffed = await _sniff_forwarded_host(sniff_timeout)
    if sniffed is not None:
        host, scheme = sniffed
        hosts.add(host)
        schemes.add(scheme)
    else:
        print(
            "Warning: could not detect the hub host via the browser; "
            f"falling back to env-derived hosts {sorted(hosts) or '(none)'}."
        )

    if not hosts:
        return
    _merge_env_list("TRUSTED_HOSTS", {"localhost", "127.0.0.1", "::1"} | hosts)
    # The hub terminates TLS; the backend may see the proxied request as plain
    # http, so the browser's https Origin must be allowlisted explicitly
    # rather than relying on the same-origin comparison.
    _merge_env_list(
        "CORS_ALLOWED_ORIGINS",
        {f"{scheme}://{host}" for host in hosts for scheme in schemes},
    )


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
