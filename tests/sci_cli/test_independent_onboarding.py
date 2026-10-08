"""Agent Scientist setup and scientific connections do not require a Nous identity."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import threading
from unittest.mock import Mock


def test_quick_setup_uses_provider_choice_and_preserves_saved_capabilities(tmp_path, monkeypatch):
    from sci_cli import setup, setup_quick
    from sci_cli.config import atomic_config_write, load_config, read_user_config_raw

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(tmp_path / ".sci"))
    home = tmp_path / ".sci"
    initial = {"mcp_servers": {"science": {"url": "https://example.invalid/mcp"}},
               "web": {"backend": "searxng"}, "display": {"skin": "fixture"}}
    atomic_config_write(home / "config.yaml", initial)
    selected = []

    def select_model():
        selected.append(True)
        cfg = read_user_config_raw(home / "config.yaml")
        cfg["model"] = {"provider": "custom", "default": "fixture-model",
                        "base_url": "http://127.0.0.1:12345/v1"}
        atomic_config_write(home / "config.yaml", cfg)

    monkeypatch.setattr("sci_cli.main.select_provider_and_model", select_model)
    monkeypatch.setattr(setup_quick, "_run_nous_flow", Mock(side_effect=AssertionError("unexpected Nous login")))
    monkeypatch.setattr(setup, "setup_terminal_backend", lambda cfg: None)
    monkeypatch.setattr(setup, "prompt_choice", lambda *a, **k: 1)
    monkeypatch.setattr("sci_cli.gateway.ensure_gateway_service", lambda **k: None)
    monkeypatch.setattr(setup, "_print_setup_summary", lambda *a: None)
    setup_quick._run_first_time_quick_setup(load_config(), home, False)
    saved = read_user_config_raw(home / "config.yaml")
    assert selected == [True]
    assert saved["model"]["default"] == "fixture-model"
    assert all(saved[key] == value for key, value in initial.items())
    assert not (home / "auth.json").exists()
    from sci_cli.main_provider_setup import _build_provider_picker_rows
    rows, default = _build_provider_picker_rows(saved, None, {}, {})
    assert rows[default][0] != "nous"
    rows, default = _build_provider_picker_rows(saved, "openai-codex", {}, {})
    assert rows[default][0] == "openai-codex" or "openai-codex" in rows[default][2]


def test_no_guest_signup_and_real_search_and_mcp_work_across_profiles(tmp_path, monkeypatch):
    from agent.secret_scope import set_multiplex_context, reset_multiplex_context
    from gateway.run import _profile_runtime_scope
    from sci_cli import anon_auth, free_tier_bootstrap
    from sci_cli.config import atomic_config_write, load_config
    from sci_cli.mcp_config import _probe_single_server
    from plugins.web import keyless_mcp
    from tools.mcp_tool_config import _load_mcp_config
    from tools.web_tools import web_search_tool

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(tmp_path / "a"))
    monkeypatch.setenv("SCI_SHARED_AUTH_DIR", str(tmp_path / "shared-auth"))
    # A launch environment must not silently opt a fresh profile into a Nous account.
    monkeypatch.setenv("SCI_GUEST_ONBOARDING", "1")
    calls = []

    class SearchFixture(BaseHTTPRequestHandler):
        def do_POST(self):
            request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert not self.headers.get("Authorization")
            query = request["params"]["arguments"]["query"]
            calls.append(query)
            payload = {"jsonrpc": "2.0", "id": request["id"], "result": {"content": [
                {"type": "text", "text": f"Title: {query}\nURL: https://example.org/{query}\nHighlights:\nFixture evidence"}
            ]}}
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), SearchFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr(keyless_mcp, "EXA_MCP_URL", f"http://127.0.0.1:{server.server_port}/mcp")
    homes = [tmp_path / "a", tmp_path / "b"]
    for home in homes:
        # No executable test is called: discovery only, and a real subprocess/stdio handshake.
        code = '''import json, sys
for line in sys.stdin:
    request = json.loads(line)
    if "id" not in request:
        continue
    if request["method"] == "initialize":
        result = {"protocolVersion": request["params"]["protocolVersion"],
                  "capabilities": {"tools": {}},
                  "serverInfo": {"name": "fixture", "version": "1"}}
    elif request["method"] == "tools/list":
        result = {"tools": [{"name": "reference_PROFILE", "description": "Fixture",
                             "inputSchema": {"type": "object"}}]}
    else:
        raise RuntimeError("Unexpected tool execution")
    print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}), flush=True)'''.replace("PROFILE", home.name)
        atomic_config_write(home / "config.yaml", {
            "model": {"provider": "custom", "default": "fixture", "base_url": "http://127.0.0.1:12345/v1"},
            "web": {"backend": "exa", "provider_tier": {"exa": "free"}, "cache_enabled": False,
                    "keyless_rescue": False},
            "mcp_servers": {"fixture": {"command": sys.executable, "args": ["-c", code]}},
        })
    originals = {home: (home / "config.yaml").read_bytes() for home in homes}
    multiplex = set_multiplex_context(True)
    try:
        for home in (homes[0], homes[1], homes[0]):
            with _profile_runtime_scope(home, prepared_secret_scope={}):
                assert load_config()["nous"]["guest"] is False
                assert not anon_auth.guest_enabled()
                free_tier_bootstrap.reset_for_tests()
                record = free_tier_bootstrap.run_bootstrap(announce=False)
                assert not record.has_identity and record.provider_configured
                result = json.loads(web_search_tool(home.name, 1))
                assert result["success"] and result["data"]["web"][0]["title"] == home.name
                tools = _probe_single_server("fixture", _load_mcp_config()["fixture"], connect_timeout=20)
                assert [name for name, _ in tools] == [f"reference_{home.name}"]
                assert not (home / "auth.json").exists()
                assert (home / "config.yaml").read_bytes() == originals[home]
        assert calls == ["a", "b", "a"]
    finally:
        reset_multiplex_context(multiplex)
        free_tier_bootstrap.reset_for_tests()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
