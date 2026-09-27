"""Keep the Binder launch cells executable by the shipped Python kernel."""

import ast
import json
from pathlib import Path


def test_notebook_code_cells_compile_with_top_level_await():
    notebook = json.loads((Path(__file__).resolve().parents[1] / "index.ipynb").read_text())
    assert notebook["metadata"]["kernelspec"]["name"] == "python3"
    code = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert code
    for cell in code:
        compile("".join(cell["source"]), cell["id"], "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
        assert cell["execution_count"] is None
        assert not cell["outputs"]


def test_launch_cell_passes_binder_proxy_and_storage(monkeypatch, tmp_path):
    import asyncio
    import sys
    from types import ModuleType, SimpleNamespace

    notebook = json.loads((Path(__file__).resolve().parents[1] / "index.ipynb").read_text())
    source = "".join(next(cell["source"] for cell in notebook["cells"] if cell["cell_type"] == "code"))
    calls = []

    async def launch(previous, **settings):
        calls.append((previous, settings))
        return SimpleNamespace(version="v8.0.0", data_dir=settings["data_dir"])

    async def origin():
        return "https://binder.example"

    launcher = ModuleType("launcher")
    launcher.launch = launch
    utils = ModuleType("utils")
    utils.discover_public_origin = origin
    display_module = ModuleType("IPython.display")
    display_module.Markdown = lambda text: text
    display_module.display = lambda text: None
    monkeypatch.setitem(sys.modules, "launcher", launcher)
    monkeypatch.setitem(sys.modules, "utils", utils)
    monkeypatch.setitem(sys.modules, "IPython.display", display_module)
    monkeypatch.setenv("JUPYTERHUB_SERVICE_PREFIX", "/user/test/")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    namespace = {}
    executable = compile(source, "index.ipynb", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    asyncio.run(eval(executable, namespace))
    first_server = namespace["wordflow_server"]
    asyncio.run(eval(executable, namespace))
    assert calls[0] == (None, {
        "port": 8002,
        "data_dir": tmp_path,
        "public_prefix": "/user/test/proxy/8002/",
        "origin": "https://binder.example",
    })
    assert calls[1][0] is first_server
