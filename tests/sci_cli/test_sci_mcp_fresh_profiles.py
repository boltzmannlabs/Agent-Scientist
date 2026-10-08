"""Real MCP handshake/discovery in new SCI homes, with no business-tool calls."""
import json
from pathlib import Path
import sys

from gateway.run import _profile_runtime_scope
from sci_cli.config import atomic_config_write, read_user_config_raw
from sci_cli.mcp_config import _probe_single_server, _save_mcp_server


def test_saved_mcp_connections_probe_in_a_b_a_without_live_registration(tmp_path, monkeypatch):
    from tools import mcp_tool
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    fixture = Path(__file__).resolve().parents[1] / "e2e/core/mcp_plugins/mcp_fixture_server.py"
    a, b = tmp_path / "a", tmp_path / "b"
    before = dict(mcp_tool._servers)
    for home in (a, b):
        home.mkdir()
        atomic_config_write(home / "config.yaml", {"display": {"skin": "mono"}})
        with _profile_runtime_scope(home, hydrate_secrets=False):
            cfg = {"command": sys.executable, "args": [str(fixture)],
                   "env": {"MCPE2E_LOG": str(home / "wire.jsonl"), "MCPE2E_NAME": home.name},
                   "connect_timeout": 15, "sampling": {"enabled": False},
                   "tools": {"include": ["noargs_probe"], "resources": False, "prompts": False}}
            assert _save_mcp_server("fixture", cfg)
    for home in (a, b, a):
        with _profile_runtime_scope(home, hydrate_secrets=False):
            config = read_user_config_raw(home / "config.yaml")
            assert config["display"]["skin"] == "mono"
            assert config["mcp_servers"]["fixture"]["tools"]["include"] == ["noargs_probe"]
            info = {}
            found = _probe_single_server("fixture", config["mcp_servers"]["fixture"], details=info)
            assert info["initialized"] and "noargs_probe" in dict(found)
            assert dict(mcp_tool._servers) == before
    for home, count in ((a, 2), (b, 1)):
        messages = [json.loads(line)["msg"] for line in (home / "wire.jsonl").read_text().splitlines()]
        methods = [m.get("method") for m in messages]
        assert methods.count("initialize") == count
        assert methods.count("tools/list") == count
        assert "tools/call" not in methods
