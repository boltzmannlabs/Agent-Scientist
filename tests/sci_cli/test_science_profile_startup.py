"""Worker startup must bind managed dependencies before reading profile YAML."""

import builtins
import io
import json
from pathlib import Path
import queue
import threading
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


def test_worker_bootstraps_before_real_profile_preflight_and_keeps_wire_clean(tmp_path, monkeypatch, capsys):
    from sci_cli.science_profiles import ProfileSpec, create
    from sci_cli.science_profiles_sandbox import validate_runtime
    from sci_cli.science_profile_worker import main

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    source = tmp_path / ".sci"
    source.mkdir()
    monkeypatch.setenv("SCI_HOME", str(source))
    monkeypatch.setattr("sci_cli.profiles._notify_multiplexer", lambda *a: None)
    monkeypatch.setattr("sci_cli.profiles._maybe_register_gateway_service", lambda *a: None)
    home = create(ProfileSpec("omics", "science", "scientist", "", setup_pending=True), source)
    monkeypatch.setenv("SCI_HOME", str(home))
    before = (home / "config.yaml").read_bytes()
    imported = builtins.__import__
    booted = []

    def import_with_bootstrap(name, *args, **kwargs):
        if name == "sci_bootstrap":
            booted.append(True)
            print("fixture bootstrap diagnostics")
            return SimpleNamespace()
        return imported(name, *args, **kwargs)

    def preflight(path):
        if not booted:
            raise ModuleNotFoundError("No module named 'ruamel'")
        assert validate_runtime(path).name == "omics"
        raise RuntimeError("preflight completed; fixture stops before model initialization")

    monkeypatch.setattr(builtins, "__import__", import_with_bootstrap)
    monkeypatch.setattr("sci_cli.science_profiles_sandbox.validate_runtime", preflight)
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    capsys.readouterr()
    main()
    captured = capsys.readouterr()
    event = json.loads(captured.out)
    assert event["kind"] == "error" and "preflight completed" in event["message"]
    assert "fixture bootstrap diagnostics" in captured.err
    assert (home / "config.yaml").read_bytes() == before


def test_startup_progress_does_not_claim_ready_when_worker_fails():
    from sci_cli.science_profile_runtime import Worker

    worker = Worker.__new__(Worker)
    worker.spec = SimpleNamespace(name="omics")
    worker.cancel = threading.Event()
    worker.ui = SimpleNamespace(show=Mock())
    worker.events = queue.Queue()
    worker.events.put({"kind": "error", "message": "fixture startup failed"})
    with pytest.raises(RuntimeError, match="fixture startup failed"):
        worker.receive("ready", 60)
    messages = "\n".join(call.args[0] for call in worker.ui.show.call_args_list)
    assert "Starting profile" in messages
    assert "ready" not in messages.lower()
