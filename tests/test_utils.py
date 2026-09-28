"""Origin selection for the Binder notebook."""

import asyncio

import pytest

import utils


def test_nectar_origin_does_not_wait_for_jupyterlab_javascript(monkeypatch):
    monkeypatch.delenv("WORDFLOW_PUBLIC_ORIGIN", raising=False)
    monkeypatch.setenv("BINDER_LAUNCH_HOST", "https://binderhub.rc.nectar.org.au/")

    async def unexpected_probe(_timeout):
        raise AssertionError("Nectar must not wait for Javascript output")

    monkeypatch.setattr(utils, "_sniff_forwarded_host", unexpected_probe)
    assert asyncio.run(utils.discover_public_origin()) == "https://binder.rc.nectar.org.au"


def test_explicit_origin_overrides_host(monkeypatch):
    monkeypatch.setenv("BINDER_LAUNCH_HOST", "https://binderhub.rc.nectar.org.au/")
    monkeypatch.setenv("WORDFLOW_PUBLIC_ORIGIN", "https://example.org:8443/")
    assert asyncio.run(utils.discover_public_origin()) == "https://example.org:8443"


@pytest.mark.parametrize("origin", ["https://example.org/path", "https://user@example.org", "file:///tmp/app"])
def test_explicit_origin_rejects_non_origins(monkeypatch, origin):
    monkeypatch.setenv("WORDFLOW_PUBLIC_ORIGIN", origin)
    with pytest.raises(ValueError, match="must be an HTTP\\(S\\) origin"):
        asyncio.run(utils.discover_public_origin())
