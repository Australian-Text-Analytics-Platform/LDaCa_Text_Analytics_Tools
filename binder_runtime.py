"""Thin Binder-facing launcher surface for the installed web app package."""

from __future__ import annotations

import asyncio
import argparse
import logging
import os
import sys
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Sequence

from binder_utils import display_app_link

DIRECT_APP_PATH = "ldaca-app"
DIRECT_APP_TITLE = "LDaCA Web App"


def _is_plan_introspection_error(exc: Exception) -> bool:
    """Return whether ``exc`` came from unsupported plan deserialization."""
    message = str(exc)
    return "failed to deserialize plan" in message or "unknown variant" in message


def _install_docworkspace_gc_guard() -> None:
    """Keep workspace saves working when plan-path introspection cannot parse a plan.

    Binder currently runs published wheels, so an unsupported Polars plan variant
    inside ``polars_text.list_source_paths`` would otherwise bubble out of
    ``docworkspace`` garbage collection and turn a normal workspace mutation into
    a 500 response. The safe fallback is to skip garbage collection for that save
    attempt and leave existing data files untouched.
    """
    try:
        workspace_io = import_module("docworkspace.workspace.io")
    except ImportError:
        return

    if getattr(workspace_io, "_binder_gc_guard_installed", False):
        return

    original_gc = getattr(workspace_io, "_garbage_collect_workspace_data", None)
    if original_gc is None:
        return

    def guarded_gc(*args: Any, **kwargs: Any) -> None:
        try:
            original_gc(*args, **kwargs)
        except ValueError as exc:
            if not _is_plan_introspection_error(exc):
                raise

    workspace_io._garbage_collect_workspace_data = guarded_gc
    workspace_io._binder_gc_guard_installed = True


def _load_web_app() -> Any:
    """Import the installed web app package with a clear Binder error."""
    try:
        return import_module("ldaca_web_app")
    except ImportError as exc:
        raise RuntimeError(
            "ldaca-web-app is not installed in this Binder environment. "
            "Rebuild the image or check binder/postBuild."
        ) from exc


def get_web_app_version() -> str:
    """Return the installed ldaca-web-app distribution version."""
    try:
        return version("ldaca-web-app")
    except PackageNotFoundError:
        return "not installed"


def configure_notebook_logging(level: str = "ERROR") -> str:
    """Raise notebook-visible backend loggers to the requested minimum level."""
    normalized = level.strip().upper()
    if normalized not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}:
        raise ValueError(
            "level must be one of CRITICAL, ERROR, WARNING, INFO, DEBUG"
        )

    numeric_level = getattr(logging, normalized)
    logger_names = (
        "",
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "httpx",
        "httpcore",
        "ldaca_web_app",
        "py.warnings",
    )
    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)
        for handler in logger.handlers:
            handler.setLevel(numeric_level)

    logging.captureWarnings(True)
    os.environ["LDACA_NOTEBOOK_LOG_LEVEL"] = normalized
    return normalized


def _reapply_notebook_logging_from_env() -> str | None:
    """Reapply the requested notebook log level after server startup resets it."""
    configured_level = os.environ.get("LDACA_NOTEBOOK_LOG_LEVEL")
    if not configured_level:
        return None

    return configure_notebook_logging(configured_level)


def start_server(
    *,
    backend: bool = True,
    frontend: bool = True,
    port: int | None = None,
    host: str | None = None,
    background: bool = False,
    root_path: str | None = None,
) -> asyncio.Task[None] | None:
    """Delegate notebook server startup to the installed web app package."""
    _install_docworkspace_gc_guard()

    if background:
        # Hugging Face downloads can try to render notebook widgets from a
        # background startup thread, which breaks under Binder/ipykernel.
        os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

    web_app = _load_web_app()
    task = web_app.start_server(
        backend=backend,
        frontend=frontend,
        port=port,
        host=host,
        background=background,
        root_path=root_path,
    )
    _reapply_notebook_logging_from_env()
    return task


def start_direct_app_server(*, port: int, host: str = "127.0.0.1") -> None:
    """Run the web app in the foreground for jupyter-server-proxy."""
    _install_docworkspace_gc_guard()
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

    web_app = _load_web_app()
    _reapply_notebook_logging_from_env()
    web_app.start_server(
        backend=True,
        frontend=True,
        port=port,
        host=host,
        background=False,
        root_path="",
    )


def _server_proxy_command(port: int) -> list[str]:
    """Build the command used by jupyter-server-proxy to launch the app."""
    return [
        sys.executable,
        "-m",
        "binder_runtime",
        "--port",
        str(port),
        "--host",
        "127.0.0.1",
    ]


def setup_jupyter_server_proxy() -> dict[str, Any]:
    """Register the direct Binder app route with jupyter-server-proxy."""
    return {
        "command": _server_proxy_command,
        "timeout": 60,
        "absolute_url": False,
        "launcher_entry": {
            "title": DIRECT_APP_TITLE,
            "path_info": f"{DIRECT_APP_PATH}/",
        },
        "new_browser_tab": True,
    }


def _build_argument_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for the direct app server entry point."""
    parser = argparse.ArgumentParser(
        description="Start the LDaCA Binder web app for jupyter-server-proxy."
    )
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Launch the direct Binder app server from the command line."""
    args = _build_argument_parser().parse_args(argv)
    start_direct_app_server(port=args.port, host=args.host)


class _WorkspaceManagerProxy:
    """Defer workspace manager access until the installed package is ready."""

    def __getattr__(self, name: str) -> Any:
        return getattr(_load_web_app().workspace_manager, name)


workspace_manager = _WorkspaceManagerProxy()

__all__ = [
    "configure_notebook_logging",
    "display_app_link",
    "get_web_app_version",
    "setup_jupyter_server_proxy",
    "start_server",
    "workspace_manager",
]


if __name__ == "__main__":
    main()