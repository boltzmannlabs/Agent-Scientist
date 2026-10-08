"""Routing consumes explicit grants, isolates histories, and stops on cancellation."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sci_cli.science_profiles import ProfileSpec, Source
from sci_cli.science_profile_router import run_pipeline, transfer_requires_confirmation
from sci_cli.skill_add import Cancelled

IMAGE = "sha256:" + "a" * 64


def test_pipeline_grants_private_transfers_and_worker_lifecycle(monkeypatch, tmp_path):
    profiles = {n: ProfileSpec(n, n, "scientist", IMAGE, routing_terms=[n])
                for n in ("antibody", "molecule")}
    profiles["antibody"].collaborators = ["molecule"]
    plan = [{"profile": "antibody", "prompt": "review antibodies", "needs": []},
            {"profile": "molecule", "prompt": "compare molecules", "needs": [0]}]
    monkeypatch.setattr("sci_cli.science_profile_router.completion", lambda *a: json.dumps(plan))
    monkeypatch.setattr("sci_cli.profiles.get_profile_dir", lambda n: tmp_path / n)
    workers = []
    class FixtureWorker:
        def __init__(self, home, cli, ui):
            self.name, self.closed, self.prompts = home.name, False, []
            workers.append(self)
        def turn(self, text):
            self.prompts.append(text)
            return {"text": f"public evidence from {self.name}", "failed": False}
        def close(self):
            self.closed = True
    monkeypatch.setattr("sci_cli.science_profile_runtime.Worker", FixtureWorker)
    cli = SimpleNamespace(provider="fixture", model="fixture", conversation_history=[{"content": "main private history"}])
    ui = SimpleNamespace(show=Mock(), choose=Mock(return_value="Keep separate results"))
    assert run_pipeline(cli, "compare antibodies and small molecules", profiles, ui)
    assert all(w.closed for w in workers)
    assert "public evidence from antibody" in workers[1].prompts[0]
    assert "main private history" not in str([w.prompts for w in workers])
    assert ui.choose.call_count == 1  # optional synthesis only; collaboration already approved
    profiles["antibody"].sources = [Source("/private/research")]
    assert transfer_requires_confirmation(profiles["antibody"], "molecule", "ordinary output")
    profiles["antibody"].public_sources = True
    assert not transfer_requires_confirmation(profiles["antibody"], "molecule", "public evidence")
    assert transfer_requires_confirmation(profiles["antibody"], "molecule", "patient record")
    profiles["antibody"].collaborators = []
    ui.choose.side_effect = Cancelled()
    workers.clear()
    with pytest.raises(Cancelled):
        run_pipeline(cli, "compare", profiles, ui)
    assert len(workers) == 1 and workers[0].closed
    assert cli.conversation_history == [{"content": "main private history"}]


def test_routing_ambiguity_and_model_change_do_not_execute_workers(monkeypatch):
    from sci_cli.science_profile_router import route_input
    from sci_constants import sci_home_key
    worker = Mock(side_effect=AssertionError("must not start a worker"))
    monkeypatch.setattr("sci_cli.science_profile_runtime.Worker", worker)
    monkeypatch.setattr("sci_cli.science_profile_router.completion", lambda *a: '{"clarify":"Which target?"}')
    ui = SimpleNamespace(show=Mock())
    cli = SimpleNamespace(provider="fixture", model="new-model", base_url=None,
                          _science_routing=(sci_home_key(), "fixture", "old-model", None))
    monkeypatch.setattr("sci_cli.science_profile_router.WizardUI", lambda _: ui)
    assert route_input(cli, "ambiguous request")
    assert "changed" in ui.show.call_args.args[0]
    assert run_pipeline(cli, "ambiguous", {}, ui)
    assert "Which target?" in ui.show.call_args.args[0]
    worker.assert_not_called()
