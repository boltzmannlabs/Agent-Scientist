"""Boltzmann workflow dependencies are one selection, not independent toggles."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sci_cli.science_profiles_catalog import BOLTZMANN_WORKFLOW_TOOLS


def test_picker_includes_workflow_without_individual_questions_and_keeps_scope(tmp_path, monkeypatch):
    from sci_cli.config import atomic_config_write
    from sci_cli.science_profiles_ui import choose_tools
    from tools.mcp_schema_cache import config_fingerprint, write_cache_entry

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    homes = [tmp_path / "a", tmp_path / "b"]
    cfg = {"url": "https://example.invalid/mcp"}
    for home in homes:
        monkeypatch.setenv("SCI_HOME", str(home))
        atomic_config_write(home / "config.yaml", {"mcp_servers": {"boltzmann": cfg}})
        rows = [{"name": name, "description": name} for name in (*BOLTZMANN_WORKFLOW_TOOLS, f"extra_{home.name}")]
        write_cache_entry("boltzmann", config_fingerprint(cfg), tools=rows)

    for home in (homes[0], homes[1], homes[0]):
        monkeypatch.setenv("SCI_HOME", str(home))
        before = (home / "config.yaml").read_bytes()
        answers = iter(["boltzmann", "Done", "Done"])

        def choose(question, options):
            assert not any(any(option.startswith(name + " —") for name in BOLTZMANN_WORKFLOW_TOOLS)
                           for option in options)
            if "additional tools" in question:
                assert any(f"extra_{home.name} —" in option for option in options)
                assert not any(f"extra_{'b' if home.name == 'a' else 'a'} —" in option for option in options)
            answer = next(answers)
            return next(option for option in options if option == answer or option.startswith(answer + " —"))

        ui = SimpleNamespace(choose=choose, show=Mock())
        assert choose_tools(home, ui) == {"boltzmann": list(BOLTZMANN_WORKFLOW_TOOLS)}
        assert (home / "config.yaml").read_bytes() == before  # Selection grants nothing live.


def test_setup_requires_complete_bundle_then_saves_explicit_allowlist_without_extra_prompts(tmp_path, monkeypatch):
    from sci_cli.config import atomic_config_write, read_user_config_raw
    from sci_cli.science_profiles import ProfileSpec, create, MANIFEST
    from sci_cli.science_profiles_setup import prepare_profile
    from sci_cli.science_profiles_sandbox import validate_runtime

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    root = tmp_path / ".sci"
    monkeypatch.setenv("SCI_HOME", str(root))
    monkeypatch.setattr("sci_cli.profiles._notify_multiplexer", lambda *a: None)
    monkeypatch.setattr("sci_cli.profiles._maybe_register_gateway_service", lambda *a: None)
    atomic_config_write(root / "config.yaml", {"mcp_servers": {"boltzmann": {"url": "https://example.invalid/mcp"}}})
    # Includes a legacy partial selection: setup completes its required dependencies too.
    home = create(ProfileSpec("antibodies", "science", "scientist", "", setup_pending=True,
                              pending_tools={"boltzmann": ["boltzmann_submit"]},
                              capability_source_home=str(root)), root)
    originals = {name: (home / name).read_bytes() for name in ("config.yaml", MANIFEST)}
    cli = SimpleNamespace(agent=object(), conversation_history=[{"role": "user", "content": "unchanged"}])
    parent_agent = cli.agent
    probe = Mock(return_value=[("boltzmann_submit", "Submit")])
    monkeypatch.setattr("sci_cli.mcp_config._probe_single_server", probe)
    ui = SimpleNamespace(show=Mock(), choose=Mock(side_effect=["Connect boltzmann", "Check connection"]))
    with pytest.raises(ValueError, match="required Boltzmann workflow operations are missing"):
        prepare_profile(cli, home, ui)
    assert all((home / name).read_bytes() == data for name, data in originals.items())
    probe.reset_mock()
    probe.return_value = [(name, name) for name in (*BOLTZMANN_WORKFLOW_TOOLS, "future_admin_tool")]
    responses = iter(["Connect boltzmann", "Check connection", "Save setup"])

    def choose(question, options):
        answer = next(responses)
        if answer == "Check connection":
            probe.assert_not_called()
        assert all((home / name).read_bytes() == data for name, data in originals.items())
        assert answer in options
        return answer

    ui.choose = choose
    assert prepare_profile(cli, home, ui)
    spec = validate_runtime(home)
    assert spec.mcp_tools == {"boltzmann": list(BOLTZMANN_WORKFLOW_TOOLS)}
    assert not spec.pending_tools and spec.setup_pending  # No local-execution grant.
    saved = read_user_config_raw(home / "config.yaml")
    assert saved["mcp_servers"]["boltzmann"]["tools"]["include"] == list(BOLTZMANN_WORKFLOW_TOOLS)
    assert cli.agent is parent_agent and cli.conversation_history == [{"role": "user", "content": "unchanged"}]
