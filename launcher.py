"""Launch a verified native Wordflow release. Python only orchestrates the process."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import socket
import subprocess
import tarfile
import tempfile
import time
from urllib.request import Request, urlopen
import zipfile

REPOSITORY = "Australian-Text-Analytics-Platform/ldaca-wordflow"
RELEASE_URL = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"


def target() -> str:
    values = {("Linux", "x86_64"): "x86_64-unknown-linux-gnu", ("Darwin", "arm64"): "aarch64-apple-darwin", ("Windows", "AMD64"): "x86_64-pc-windows-msvc"}
    try:
        return values[platform.system(), platform.machine()]
    except KeyError as error:
        raise RuntimeError("No native Wordflow server archive is published for this platform") from error


def read_url(url: str) -> bytes:
    with urlopen(Request(url, headers={"User-Agent": "Wordflow-Binder-launcher"}), timeout=60) as response:
        return response.read()


def release_assets(release: dict, triple: str) -> tuple[str, str, str]:
    tag = release["tag_name"]
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag) or release.get("prerelease") or release.get("draft"):
        raise RuntimeError("Latest release is not a stable Wordflow release")
    extension = "zip" if triple.endswith("windows-msvc") else "tar.gz"
    name = f"wordflow-server-{triple}.{extension}"
    assets = {item["name"]: item["browser_download_url"] for item in release["assets"]}
    if name not in assets or "server-SHA256SUMS" not in assets:
        raise RuntimeError(f"Latest release {tag} lacks {name} or server-SHA256SUMS. No older or unverified release was selected.")
    return name, assets[name], assets["server-SHA256SUMS"]


def verify_file(path: Path, expected: str) -> None:
    with path.open("rb") as handle:
        actual = hashlib.file_digest(handle, "sha256").hexdigest()
    if actual != expected:
        raise RuntimeError(f"Checksum mismatch for {path.name}")


def extract_archive(archive: Path, destination: Path, root_name: str) -> None:
    def safe(name: str) -> None:
        parts = name.replace("\\", "/").split("/")
        if not parts or parts[0] != root_name or any(p in {"..", "."} or ":" in p for p in parts):
            raise RuntimeError(f"Unsafe archive entry: {name}")
    if archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as source:
            for entry in source.infolist():
                safe(entry.filename)
                if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                    raise RuntimeError("Archive symlinks are not permitted")
            source.extractall(destination)
    else:
        with tarfile.open(archive) as source:
            for entry in source.getmembers():
                safe(entry.name)
                if not (entry.isfile() or entry.isdir()):
                    raise RuntimeError("Archive links and special files are not permitted")
            source.extractall(destination, filter="data")


def resolve_package(cache: Path) -> tuple[str, Path]:
    # One latest lookup per fresh launch; asset URLs come from that exact release.
    release = json.loads(read_url(RELEASE_URL))
    triple = target()
    name, archive_url, checksum_url = release_assets(release, triple)
    sums = read_url(checksum_url).decode("ascii").splitlines()
    entries = [line.split() for line in sums]
    matches = [parts[0] for parts in entries if len(parts) == 2 and parts[1] == name]
    if len(matches) != 1 or not re.fullmatch(r"[a-fA-F0-9]{64}", matches[0]):
        raise RuntimeError(f"No unique valid checksum for {name}")
    root_name = name.removesuffix(".tar.gz").removesuffix(".zip")
    cache = cache / release["tag_name"]
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / name
    if not archive.exists():
        with tempfile.NamedTemporaryFile(dir=cache, delete=False) as temporary:
            staging = Path(temporary.name)
            try:
                with urlopen(Request(archive_url, headers={"User-Agent": "Wordflow-Binder-launcher"}), timeout=60) as response:
                    shutil.copyfileobj(response, temporary)
                temporary.flush()
                verify_file(staging, matches[0])
                staging.replace(archive)
            finally:
                staging.unlink(missing_ok=True)
    verify_file(archive, matches[0])
    installed = cache / root_name
    # Re-extract verified bytes to avoid trusting a stale/modified executable in cache.
    with tempfile.TemporaryDirectory(dir=cache) as temporary:
        stage = Path(temporary)
        extract_archive(archive, stage, root_name)
        if installed.exists():
            shutil.rmtree(installed)
        (stage / root_name).replace(installed)
    exe = installed / ("wordflow-server.exe" if triple.endswith("windows-msvc") else "wordflow-server")
    if not exe.is_file():
        raise RuntimeError("Verified archive does not contain the server executable")
    return release["tag_name"], exe


@dataclass
class Server:
    process: subprocess.Popen
    version: str
    data_dir: Path
    port: int
    prefix: str
    log: Path

    def healthy(self) -> bool:
        if self.process.poll() is not None:
            return False
        try:
            status = json.loads(read_url(f"http://127.0.0.1:{self.port}/api/server"))
            return status.get("public_base_path") == self.prefix
        except (OSError, ValueError):
            return False

    async def close(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            await asyncio.to_thread(self.process.wait)


async def launch(previous: Server | None = None, *, port: int = 8002, data_dir: Path | None = None, public_prefix: str = "/", origin: str | None = None, cache: Path | None = None) -> Server:
    if previous and await asyncio.to_thread(previous.healthy):
        print(f"Reusing Wordflow {previous.version} at {previous.prefix}")
        return previous
    if previous and previous.process.poll() is None:
        raise RuntimeError("The owned Wordflow process is not ready. Stop it explicitly before launching again.")
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError as error:
            raise RuntimeError(f"Port {port} is occupied; no unrelated process was terminated") from error
    version, executable = await asyncio.to_thread(resolve_package, cache or Path.home() / ".cache/wordflow/releases")
    directory = (data_dir or Path.home() / "wordflow").expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    prefix = public_prefix.rstrip("/") + "/"
    arguments = [str(executable), "--bind", f"127.0.0.1:{port}", "--public-base-path", prefix]
    if origin:
        arguments += ["--allowed-origin", origin]
    log = directory / "server.log"
    with log.open("ab") as output:
        process = subprocess.Popen(arguments, env={**os.environ, "DATA_DIR": str(directory)}, stdin=subprocess.DEVNULL, stdout=output, stderr=output)
    server = Server(process, version, directory, port, prefix, log)
    try:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Wordflow exited with {process.returncode}; see {log}")
            if await asyncio.to_thread(server.healthy):
                print(f"Wordflow {version}\nStorage: {directory}\nApplication: {prefix}")
                return server
            await asyncio.sleep(0.2)
        raise RuntimeError(f"Wordflow did not become ready; see {log}")
    except BaseException:
        await server.close()
        raise
