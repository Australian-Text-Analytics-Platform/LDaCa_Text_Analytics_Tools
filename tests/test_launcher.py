import asyncio
import hashlib
import io
import json
from pathlib import Path
import socket
import tarfile

import pytest
import launcher


def release(name):
    return {"tag_name": "v0.8.0", "assets": [{"name": name, "browser_download_url": "https://example/archive"}, {"name": "server-SHA256SUMS", "browser_download_url": "https://example/checksums"}]}


def test_missing_latest_asset_never_selects_an_older_release():
    with pytest.raises(RuntimeError, match="No older or unverified"):
        launcher.release_assets(release("wrong.tar.gz"), "x86_64-unknown-linux-gnu")
    with pytest.raises(RuntimeError, match="not a stable"):
        launcher.release_assets({**release("x"), "prerelease": True}, "x86_64-unknown-linux-gnu")


def test_checksum_failure(tmp_path):
    file = tmp_path / "archive"
    file.write_bytes(b"untrusted")
    with pytest.raises(RuntimeError, match="Checksum mismatch"):
        launcher.verify_file(file, "0" * 64)
    launcher.verify_file(file, hashlib.sha256(b"untrusted").hexdigest())


@pytest.mark.parametrize("entry_name,kind", [("../escape", tarfile.REGTYPE), ("pkg/symlink", tarfile.SYMTYPE), ("pkg/hardlink", tarfile.LNKTYPE), ("pkg/../../escape", tarfile.REGTYPE)])
def test_unsafe_archives(tmp_path, entry_name, kind):
    archive = tmp_path / "test.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        entry = tarfile.TarInfo(entry_name)
        entry.type = kind
        entry.linkname = "/tmp/escape"
        output.addfile(entry)
    with pytest.raises(RuntimeError):
        launcher.extract_archive(archive, tmp_path / "out", "pkg")


def test_port_conflict_does_not_download_or_terminate(monkeypatch):
    monkeypatch.setattr(launcher, "resolve_package", lambda _: pytest.fail("must check port before fetching release"))
    with socket.socket() as occupied:
        occupied.bind(("127.0.0.1", 0))
        with pytest.raises(RuntimeError, match="no unrelated process"):
            asyncio.run(launcher.launch(port=occupied.getsockname()[1]))


def test_cache_rechecks_archive_without_redownloading(tmp_path, monkeypatch):
    triple = "x86_64-unknown-linux-gnu"
    name = f"wordflow-server-{triple}.tar.gz"
    version_cache = tmp_path / "v0.8.0"
    version_cache.mkdir()
    archive = version_cache / name
    root = name.removesuffix(".tar.gz")
    with tarfile.open(archive, "w:gz") as output:
        entry = tarfile.TarInfo(f"{root}/wordflow-server")
        data = b"fixture executable"
        entry.size = len(data)
        output.addfile(entry, io.BytesIO(data))
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    requests = []
    def read(url):
        requests.append(url)
        if url == launcher.RELEASE_URL:
            return json.dumps(release(name)).encode()
        assert url.endswith("checksums")
        return f"{checksum}  {name}\n".encode()
    monkeypatch.setattr(launcher, "target", lambda: triple)
    monkeypatch.setattr(launcher, "read_url", read)
    for _ in range(2):
        version, executable = launcher.resolve_package(tmp_path)
        assert version == "v0.8.0"
        assert executable.read_bytes() == b"fixture executable"
    assert requests.count(launcher.RELEASE_URL) == 2


def test_owned_healthy_process_is_reused(monkeypatch):
    class Previous:
        version = "v0.8.0"
        prefix = "/user/test/proxy/8002/"
        def healthy(self):
            return True
    previous = Previous()
    monkeypatch.setattr(launcher, "resolve_package", lambda _: pytest.fail("healthy rerun must not resolve latest"))
    assert asyncio.run(launcher.launch(previous)) is previous


@pytest.mark.parametrize("triple,extension", [
    ("x86_64-unknown-linux-gnu", "tar.gz"),
    ("aarch64-apple-darwin", "tar.gz"),
    ("x86_64-pc-windows-msvc", "zip"),
])
def test_asset_names_are_stable_across_versions(triple, extension):
    name = f"wordflow-server-{triple}.{extension}"
    for tag in ["v0.8.0", "v0.9.0"]:
        assert launcher.release_assets({**release(name), "tag_name": tag}, triple)[0] == name


def test_successive_releases_have_independent_caches(tmp_path, monkeypatch):
    triple = "x86_64-unknown-linux-gnu"
    name = f"wordflow-server-{triple}.tar.gz"
    root = name.removesuffix(".tar.gz")
    monkeypatch.setattr(launcher, "target", lambda: triple)
    paths = []
    for tag in ["v0.8.0", "v0.9.0"]:
        directory = tmp_path / tag
        directory.mkdir()
        archive = directory / name
        data = tag.encode()
        with tarfile.open(archive, "w:gz") as output:
            entry = tarfile.TarInfo(f"{root}/wordflow-server")
            entry.size = len(data)
            output.addfile(entry, io.BytesIO(data))
        checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
        monkeypatch.setattr(launcher, "read_url", lambda url: (
            json.dumps({**release(name), "tag_name": tag}).encode()
            if url == launcher.RELEASE_URL else f"{checksum}  {name}\n".encode()
        ))
        version, executable = launcher.resolve_package(tmp_path)
        assert version == tag
        assert executable.read_bytes() == data
        paths.append(executable)
    assert paths[0] != paths[1]
    assert paths[0].read_bytes() == b"v0.8.0"
