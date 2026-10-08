"""Real fresh-profile workers against a loopback-only, controlled model provider."""

import json
import os
from pathlib import Path
import subprocess
import sys

from tests.fakes.fake_llm_provider import FakeLLMServer, Text, write_sci_home


def test_fresh_profile_worker_turns_restart_and_a_b_a_isolation(tmp_path, monkeypatch):
    from sci_cli.science_profiles import ProfileSpec, create
    from sci_cli.science_profile_commands import activate
    from types import SimpleNamespace
    from unittest.mock import Mock

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    home = tmp_path / ".sci"
    monkeypatch.setenv("SCI_HOME", str(home))
    monkeypatch.setattr("sci_cli.profiles._notify_multiplexer", lambda *a: None)
    monkeypatch.setattr("sci_cli.profiles._maybe_register_gateway_service", lambda *a: None)
    with FakeLLMServer(default_text="SCI fixture response", aux=lambda _: Text("SCI fixture response")) as server:
        write_sci_home(home, server.base_url)
        skill = home / "skills/science/fixture"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: fixture\ndescription: Review scientific evidence\n---\nSeparate evidence from hypotheses.\n")
        profiles = [create(ProfileSpec(name, purpose, "Cite evidence", "", setup_pending=True,
                                       skills=["science/fixture"]), home)
                    for name, purpose in (("antibody", "ANTIBODY_ONLY"), ("molecule", "MOLECULE_ONLY"))]
        parent = SimpleNamespace(agent=SimpleNamespace(system_prompt="cached", tools=["unchanged"]),
                                 conversation_history=[{"role": "user", "content": "main only"}])
        before = (home / "config.yaml").read_bytes()
        for target in (profiles[0], profiles[1], profiles[0]):
            activate(parent, f'/activate "{target.name}" profile', SimpleNamespace(show=Mock()))
            start = len(server.requests)
            # Use the prepared test interpreter; no package installs or live credentials.
            env = {k: v for k, v in os.environ.items()
                   if k in {"PATH", "LANG", "TZ", "TMPDIR", "SYSTEMROOT"}}
            env.update(HOME=str(tmp_path), SCI_HOME=str(target), SCI_DISABLE_LAZY_INSTALLS="1",
                       SCI_TEST_ISOLATION=str(home), OPENAI_API_KEY="sk-fake-e2e", NO_PROXY="127.0.0.1,localhost")
            script = """
import ipaddress, runpy, socket
connect = socket.socket.connect
def loopback_only(sock, address):
    if isinstance(address, tuple) and not ipaddress.ip_address(address[0]).is_loopback:
        raise OSError('Fixture refuses non-loopback network access')
    return connect(sock, address)
socket.socket.connect = loopback_only
runpy.run_module('sci_cli.science_profile_worker', run_name='__main__')
"""
            result = subprocess.run([sys.executable, "-c", script], cwd=Path(__file__).resolve().parents[2],
                                    env=env, input='{"kind":"turn","text":"hello"}\n'
                                    '{"kind":"turn","text":"what skills are available?"}\n{"kind":"close"}\n',
                                    text=True, capture_output=True, timeout=90)
            events = [json.loads(line) for line in result.stdout.splitlines()]
            assert result.returncode == 0, result.stderr[-3000:]
            assert [e["kind"] for e in events] == ["ready", "result", "result"], (events, result.stderr[-3000:])
            assert all(not e["failed"] and e["text"] == "SCI fixture response" for e in events[1:])
            requests = [r["body"] for r in server.requests[start:] if r["kind"] == "main"]
            assert len(requests) == 2
            systems = [[m for m in r["messages"] if m["role"] == "system"] for r in requests]
            assert systems[0] == systems[1]
            text = json.dumps(systems[0])
            assert "built by Boltzmann Labs" in text
            assert "hermes-agent.nousresearch.com" not in text
            assert "Do not load skills, browse, or run commands solely to introduce yourself" in text
            assert ("ANTIBODY_ONLY" in text) == (target.name == "antibody")
            assert ("MOLECULE_ONLY" in text) == (target.name == "molecule")
            assert "fixture" in text
            assert requests[0]["tools"] == requests[1]["tools"]
            names = {t["function"]["name"] for t in requests[0]["tools"]}
            assert "skill_view" in names and "terminal" not in names
        assert (home / "config.yaml").read_bytes() == before
        assert parent.agent.system_prompt == "cached" and parent.agent.tools == ["unchanged"]
        assert parent.conversation_history == [{"role": "user", "content": "main only"}]
