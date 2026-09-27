"""Binder-specific helpers for the LDaCA Wordflow notebook launcher."""

from __future__ import annotations

import asyncio
import os
from urllib.parse import urlsplit

_sniff_port: int | None = None


async def _sniff_forwarded_host(timeout: float) -> tuple[str, str] | None:
    """Learn the exact (host, scheme) jupyter-server-proxy forwards to apps.

    Serves one ephemeral localhost endpoint and asks the notebook's own
    browser to fetch it through the hub proxy. The Host header of that request
    supplies the public origin passed explicitly to the native server — no
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


async def discover_public_origin(sniff_timeout: float = 15.0) -> str:
    """Discover the notebook's browser origin and pass it explicitly to the native host."""
    sniffed = await _sniff_forwarded_host(sniff_timeout)
    if sniffed is None:
        raise RuntimeError("Could not discover this notebook's public origin. Run the cell in your browser, or supply its exact origin explicitly.")
    host, scheme = sniffed
    return f"{scheme}://{host}"
