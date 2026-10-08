"""Binder-specific helpers for the LDaCA Wordflow notebook launcher."""

from __future__ import annotations

import asyncio
import json
import os
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
