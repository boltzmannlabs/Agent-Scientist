"""Bundled connector authorization must precede discovery and every operation."""

import json
import sys
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

import pytest

from agent.secret_scope import set_multiplex_context, reset_multiplex_context
from gateway.run import _profile_runtime_scope
from sci_cli.callbacks import prompt_for_secret
from sci_cli.config import load_config, load_env, save_config, save_env_value
from sci_cli.plugins import PluginManager


@pytest.fixture
def auth_server():
    state = {"revoked": False, "calls": []}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            state["calls"].append(self.path)
            if self.path == "/artifact.csv":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"id,value\nfixture-1,1\nfixture-2,2\n")
                return
            ok = self.headers.get("Authorization") == "Bearer fixture-valid" and not state["revoked"]
            self.send_response(200 if ok else 401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            payload = {"status": "success" if ok else "error"}
            if ok and self.path == "/result":
                payload["OutputData"] = {"fixture": {"download_link":
                    f"http://127.0.0.1:{self.server.server_port}/artifact.csv"}}
            self.wfile.write(json.dumps(payload).encode())

        def do_POST(self):
            state["calls"].append(self.path)
            assert self.path == "/submit"
            assert self.headers.get("Authorization") == "Bearer fixture-valid"
            state["submission"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"success": true, "docId": "fixture-job"}')

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield state, f"http://127.0.0.1:{server.server_port}/api/get-projects"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(5)


@contextmanager
def profile(home):
    home.mkdir(exist_ok=True)
    multiplex_token = set_multiplex_context(True)
    try:
        with _profile_runtime_scope(home, hydrate_secrets=False):
            yield
    finally:
        reset_multiplex_context(multiplex_token)


def discover(monkeypatch, endpoint):
    manager = PluginManager()
    manager.discover_and_load()
    loaded = manager._plugins["boltzmann"]
    assert not loaded.error, loaded.error
    module = loaded.module
    helpers = sys.modules[module.__name__ + ".nodeapi_helpers"]
    monkeypatch.setattr(helpers, "_AUTH_CHECK_URL", endpoint)
    return manager, module


def capture(manager, monkeypatch, value):
    cli = SimpleNamespace(agent=SimpleNamespace(system_prompt="cached-prefix", tools=[{"old": "tools"}]),
                          conversation_history=[{"role": "user", "content": "unchanged"}])
    cli._secret_capture_callback = lambda key, prompt, **kw: prompt_for_secret(cli, key, prompt, **kw)
    manager._cli_ref = cli
    monkeypatch.setattr("sci_cli.callbacks.masked_secret_prompt", lambda _: value)
    return manager._plugin_commands["add_boltz"]["handler"](""), cli


def test_command_is_required_and_activation_is_deferred_and_profile_local(tmp_path, monkeypatch, auth_server, capsys):
    state, endpoint = auth_server
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(tmp_path / "a"))
    monkeypatch.delenv("SCI_BUNDLED_PLUGINS", raising=False)
    monkeypatch.chdir(tmp_path)
    a, b = tmp_path / "a", tmp_path / "b"
    with profile(a):
        save_config({"model": {"default": "keep-model"}, "display": {"skin": "mono"},
                     "platform_toolsets": {"cli": ["terminal", "no_mcp"]},
                     "agent": {"disabled_toolsets": ["boltzmann", "browser"]}})
        save_env_value("BOLTZMANN_API_KEY", "fixture-valid")
        manager, module = discover(monkeypatch, endpoint)
        try:
            from sci_cli.commands import is_gateway_known_command
            from sci_cli.commands_platforms import telegram_bot_commands
            assert not is_gateway_known_command("add_boltz")
            assert "add_boltz" not in dict(telegram_bot_commands())
            assert "add_boltz" in manager._plugin_commands
            assert not module.available()  # a preexisting key is not command approval
            assert not state["calls"]  # discovery never contacts the service
            assert not manager._plugin_skills
            from tools.registry import registry
            names = {schema["name"] for schema in module.SCHEMAS}
            assert not registry.get_definitions(names, quiet=True)
            for name in names:
                assert json.loads(getattr(module.tools, "handle_" + name)())["authorization_required"]
            assert not state["calls"]
            for value, outcome in (("", "CANCELLED"), ("invalid", "FAILED"), ("fixture-valid", "SAVED")):
                message, cli = capture(manager, monkeypatch, value)
                assert outcome in message
                assert load_env()["BOLTZMANN_API_KEY"] == "fixture-valid"
                assert cli.agent.system_prompt.encode() == b"cached-prefix"
                assert cli.agent.tools == [{"old": "tools"}]
                assert cli.conversation_history == [{"role": "user", "content": "unchanged"}]
                assert not manager._plugin_skills  # default never live-registers skills
                assert module.available() == (outcome == "SAVED")
            assert "next session" in message
            assert load_config()["model"]["default"] == "keep-model"
            assert load_config()["display"]["skin"] == "mono"
            assert load_config()["platform_toolsets"]["cli"] == ["terminal", "no_mcp", "boltzmann"]
            assert load_config()["agent"]["disabled_toolsets"] == ["browser"]
            with profile(b):
                save_env_value("BOLTZMANN_API_KEY", "fixture-valid")
                assert not module.available()  # same key, different home, no receipt
            assert module.available()  # A → B → A
        finally:
            manager.unload()
        fresh, fresh_module = discover(monkeypatch, endpoint)
        try:
            assert fresh_module.available()
            assert "boltzmann:tools" in fresh._plugin_skills
            assert fresh._plugins["boltzmann"].tools_registered
            skill = fresh._plugin_skills["boltzmann:tools"]["path"]
            assert skill.is_relative_to(Path(__file__).resolve().parents[2] / "plugins" / "boltzmann")
            catalog = json.loads((skill.parent / "references/module-registry.v1.json").read_text())
            for entry in catalog["modules"]:
                assert (skill.parent / "references" / entry["path"]).is_file()
            assert {d["function"]["name"] for d in registry.get_definitions(names, quiet=True)} == names
        finally:
            fresh.unload()
    output = capsys.readouterr()
    assert "fixture-valid" not in output.out + output.err
    assert set(state["calls"]) == {"/api/get-projects"}


def test_revocation_blocks_all_operations_including_cached_results_and_downloads(tmp_path, monkeypatch, auth_server):
    state, endpoint = auth_server
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(tmp_path / "a"))
    monkeypatch.delenv("SCI_BUNDLED_PLUGINS", raising=False)
    monkeypatch.chdir(tmp_path)
    with profile(tmp_path / "a"):
        manager, module = discover(monkeypatch, endpoint)
        try:
            message, _ = capture(manager, monkeypatch, "fixture-valid")
            assert "SAVED" in message
            tools = module.tools
            tools._store_cache("job", "doc", {"status": "completed", "private": "result"})
            assert tools._check_cache("job", "doc")["private"] == "result"
            with profile(tmp_path / "b"):
                save_env_value("BOLTZMANN_API_KEY", "fixture-valid")
                assert tools._check_cache("job", "doc") is None
            assert tools._check_cache("job", "doc") is not None
            assert json.loads(tools.handle_boltzmann_status(job_name="job", doc_id="doc"))["private"] == "result"
            state["revoked"] = True
            for schema in module.SCHEMAS:
                handler = getattr(tools, "handle_" + schema["name"])
                result = json.loads(handler(job_name="job", doc_id="doc", download_url="https://unused.invalid/file",
                                            output_folder=str(tmp_path / "must-not-exist")))
                assert result["authorization_required"] is True
                assert "private" not in result
            assert not (tmp_path / "must-not-exist").exists()
            save_env_value("BOLTZMANN_API_KEY", "")
            assert not module.available()
            assert json.loads(tools.handle_boltzmann_submit())["authorization_required"]
            assert set(state["calls"]) == {"/api/get-projects"}
        finally:
            manager.unload()


def test_fresh_authorized_connector_executes_fixture_job_without_local_plugin(tmp_path, monkeypatch, auth_server):
    state, endpoint = auth_server
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(tmp_path / "fresh"))
    monkeypatch.delenv("SCI_BUNDLED_PLUGINS", raising=False)
    monkeypatch.delenv("conv_id", raising=False)
    monkeypatch.chdir(tmp_path)
    with profile(tmp_path / "fresh"):
        manager, module = discover(monkeypatch, endpoint)
        try:
            assert not module.available()
            message, _ = capture(manager, monkeypatch, "fixture-valid")
            assert "SAVED" in message
        finally:
            manager.unload()
        manager, module = discover(monkeypatch, endpoint)
        try:
            helpers = sys.modules[module.__name__ + ".nodeapi_helpers"]
            base = endpoint.removesuffix("/api/get-projects")
            monkeypatch.setattr(helpers, "_SUBMIT_URL", base + "/submit")
            monkeypatch.setattr(helpers, "_FETCH_URL", base + "/result")
            inputs = {"n_samples": 20, "file_format": "csv"}
            submitted = json.loads(module.tools.handle_boltzmann_submit(
                job_name="Random_Antibody_Generation", experiment_data=inputs,
                experiment_name="approved-fixture"))
            assert submitted["doc_id"] == "fixture-job"
            assert state["submission"] == {"job_name": submitted["job_name"],
                "experimentData": inputs, "experimentName": "approved-fixture"}
            status = json.loads(module.tools.handle_boltzmann_status(
                job_name=submitted["job_name"], doc_id=submitted["doc_id"]))
            result = json.loads(module.tools.handle_boltzmann_download(
                download_url=status["OutputData"]["fixture"]["download_link"],
                output_folder=str(tmp_path / "outputs")))
            assert Path(result["output_paths"][0]).read_text().splitlines() == [
                "id,value", "fixture-1,1", "fixture-2,2"]
            assert state["calls"].count("/submit") == 1
            assert set(state["calls"]) <= {"/api/get-projects", "/submit", "/result", "/artifact.csv"}
        finally:
            manager.unload()
