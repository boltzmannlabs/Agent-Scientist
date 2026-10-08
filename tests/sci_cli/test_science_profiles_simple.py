"""Scientist-facing creation saves selections, not a promise that software is ready."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sci_cli.science_profiles import read_spec
from sci_cli.science_profiles_ui import create_wizard


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    root = tmp_path / ".sci"
    root.mkdir()
    monkeypatch.setenv("SCI_HOME", str(root))
    monkeypatch.setattr("sci_cli.profiles._notify_multiplexer", lambda *a: None)
    monkeypatch.setattr("sci_cli.profiles._maybe_register_gateway_service", lambda *a: None)
    for forbidden in ("sci_cli.science_profiles_environment.choose_environment",
                      "sci_cli.science_profiles_sandbox.resolve_image",
                      "sci_cli.mcp_config._probe_single_server"):
        monkeypatch.setattr(forbidden, Mock(side_effect=AssertionError("No preparation during creation")))
    return root


def add_skill(home, name, description):
    path = home / "skills" / name
    path.mkdir(parents=True)
    (path / "SKILL.md").write_text(f"---\nname: {path.name}\ndescription: {description}\n---\nResearch instructions.\n")
    return path


def test_science_filter_and_done_first_searchable_pages(home):
    from sci_cli.science_profiles_catalog import science_skills, select_science_items
    add_skill(home, "creative/poster", "Scientific poster design")
    add_skill(home, "autonomous-ai-agents/codex", "Coding agent")
    for index in range(9):
        add_skill(home, f"science/biology/antibody-{index}", "Analyze antibody sequences")
    found = science_skills(home)
    assert len(found) == 9 and all(k.startswith("science/") for k in found)
    step = iter(["Search", "select", "Done"])
    def choose(question, options):
        assert options[0] == "Done"
        assert len(options) <= 10
        item = next(step)
        return next(o for o in options if "antibody-8 —" in o) if item == "select" else item
    ui = SimpleNamespace(choose=choose, ask=lambda _: "antibody-8", show=Mock())
    assert select_science_items(ui, "Science skills", found) == ["science/biology/antibody-8"]


def test_simple_creation_saves_tools_and_sources_without_preparation_and_activates(home, tmp_path, monkeypatch):
    from sci_cli.config import atomic_config_write, read_user_config_raw
    from tools.mcp_schema_cache import write_cache_entry, config_fingerprint
    from sci_cli.profiles import get_profile_dir
    from sci_cli.science_profile_commands import activate
    from sci_cli.science_profiles_sandbox import validate_runtime
    skill = add_skill(home, "science/antibody", "Review antibody sequences")
    (skill / "references").mkdir()
    (skill / "references" / "guide.md").write_text("Supporting reference")
    cfg = {"command": "never-launched", "args": [], "env": {"SECRET": "do-not-copy"}}
    atomic_config_write(home / "config.yaml", {"mcp_servers": {"tooluniverse": cfg, "boltzmann": cfg}, "unrelated": "unchanged"})
    write_cache_entry("tooluniverse", config_fingerprint(cfg), tools=[{"name": "antibody_search", "description": "Search antibody evidence"}])
    before = (home / "config.yaml").read_bytes()
    paper = tmp_path / "downloaded paper.txt"
    paper.write_text("Private research")
    choices = iter(["science/antibody", "Done", "tooluniverse", "boltzmann", "Done", "antibody_search", "Done",
                    "Add file or folder", "Add reference URL", "Done", "Create profile"])
    answers = iter([f'"{paper}"', "https://example.invalid/paper"])
    def choose(question, options):
        item = next(choices)
        return next(o for o in options if o == item or o.startswith(item + " —"))
    ui = SimpleNamespace(choose=choose, ask=lambda _: next(answers), show=Mock())
    parent_agent = object()
    cli = SimpleNamespace(agent=parent_agent, conversation_history=[{"role": "user", "content": "main history"}])
    create_wizard(cli, '/Create_profile "antibody-study"', ui)
    target = get_profile_dir("antibody-study")
    spec = read_spec(target)
    from sci_cli.science_profiles_catalog import BOLTZMANN_WORKFLOW_TOOLS
    assert spec.pending_tools == {"tooluniverse": ["antibody_search"], "boltzmann": list(BOLTZMANN_WORKFLOW_TOOLS)}
    assert spec.setup_pending and spec.image == "" and not spec.mcp_tools
    assert spec.sources[0].location == str(paper) and not spec.allow_llm_sources
    assert (target / "skills/science/antibody/references/guide.md").read_text() == "Supporting reference"
    saved = read_user_config_raw(target / "config.yaml")
    assert saved["platform_toolsets"]["cli"] == ["skills"] and saved["mcp_servers"] == {}
    assert "do-not-copy" not in (target / "config.yaml").read_text()
    assert (home / "config.yaml").read_bytes() == before
    validate_runtime(target)  # No Docker check, even when all runtime services are absent.
    activate(cli, '/activate "antibody-study" profile', ui)
    assert cli._science_active[1] == "antibody-study" and cli.agent is parent_agent
    assert cli.conversation_history == [{"role": "user", "content": "main history"}]


def test_pending_profiles_stay_scoped_a_b_a_and_runtime_gate_excludes_host_tools(home, monkeypatch):
    from sci_cli.science_profiles import ProfileSpec, create
    from sci_cli.science_profiles_sandbox import validate_runtime
    from sci_cli.science_profile_permissions import install_gate
    from sci_cli.middleware import run_tool_execution_middleware
    a = create(ProfileSpec("antibody", "antibody", "science", "", setup_pending=True), home)
    b = create(ProfileSpec("molecule", "molecule", "science", "", setup_pending=True), home)
    for target in (a, b, a):
        monkeypatch.setenv("SCI_HOME", str(target))
        assert validate_runtime(target).name == target.name
    agent = SimpleNamespace(tools=[{"function": {"name": name}} for name in ("terminal", "read_file", "skill_view")])
    lease = install_gate(agent, Mock(), allow_local=False)
    execute = Mock()
    try:
        assert agent.valid_tool_names == {"skill_view"}
        assert "permissions" in run_tool_execution_middleware("terminal", {"command": "touch /host"}, execute)
        execute.assert_not_called()
    finally:
        lease.dispose()


def test_optional_setup_cancel_preserves_project_and_service_setup_grants_only_selected(home, monkeypatch):
    from sci_cli.config import atomic_config_write, read_user_config_raw
    from sci_cli.science_profiles import ProfileSpec, create, MANIFEST
    from sci_cli.science_profiles_setup import prepare_profile
    from sci_cli.science_profiles_sandbox import validate_runtime
    from sci_cli.skill_add import Cancelled
    atomic_config_write(home / "config.yaml", {"mcp_servers": {"tooluniverse": {"url": "https://example.invalid/mcp"}}})
    target = create(ProfileSpec("saved-project", "science", "scientist", "", setup_pending=True,
                               pending_tools={"tooluniverse": ["review_antibody"]}, capability_source_home=str(home)), home)
    original = {p: (target / p).read_bytes() for p in ("config.yaml", MANIFEST)}
    cli = SimpleNamespace()
    cancelled = SimpleNamespace(choose=Mock(side_effect=Cancelled()), show=Mock())
    with pytest.raises(Cancelled):
        prepare_profile(cli, target, cancelled)
    assert all((target / p).read_bytes() == data for p, data in original.items())
    assert cli._science_cancel is None
    probe = Mock(return_value=[("review_antibody", "Evidence review"), ("unselected_tool", "Never granted")])
    monkeypatch.setattr("sci_cli.mcp_config._probe_single_server", probe)
    answers = iter(["Connect tooluniverse", "Check connection", "Save setup"])
    def choose(question, options):
        answer = next(answers)
        if answer == "Check connection":
            probe.assert_not_called()
        assert answer in options
        return answer
    prepare_profile(cli, target, SimpleNamespace(choose=choose, show=Mock()))
    spec = validate_runtime(target)
    assert spec.setup_pending and not spec.pending_tools
    assert spec.mcp_tools == {"tooluniverse": ["review_antibody"]}
    assert read_user_config_raw(target / "config.yaml")["mcp_servers"]["tooluniverse"]["tools"]["include"] == ["review_antibody"]


def test_routing_is_explicit_session_selection_and_does_not_include_later_profiles(home, monkeypatch):
    from sci_cli.science_profiles import ProfileSpec, create, read_spec
    from sci_cli.science_profile_commands import routing
    from sci_cli.science_profile_router import route_input
    a = create(ProfileSpec("antibody", "antibody research", "science", "", setup_pending=True), home)
    create(ProfileSpec("molecule", "molecule research", "science", "", setup_pending=True), home)
    choices = iter(["antibody", "Done", "Enable routing"])
    def choose(question, options):
        item = next(choices)
        return next(o for o in options if o == item or o.startswith(item + " —"))
    ui = SimpleNamespace(choose=choose, show=Mock())
    model_route = SimpleNamespace(provider="fixture", model="fixture", endpoint="local", close=Mock())
    monkeypatch.setattr("sci_cli.skill_add_draft.prepare_route", lambda _: model_route)
    cli = SimpleNamespace(provider="fixture", model="fixture")
    routing(cli, "/profile_routing on", ui)
    create(ProfileSpec("later-project", "antibody research", "science", "", setup_pending=True), home)
    pipeline = Mock(return_value=True)
    monkeypatch.setattr("sci_cli.science_profile_router.run_pipeline", pipeline)
    monkeypatch.setattr("sci_cli.science_profile_router.WizardUI", lambda _: ui)
    assert route_input(cli, "Review antibodies")
    selected = pipeline.call_args.args[2]
    assert set(selected) == {"antibody"} and selected["antibody"].routing_terms
    assert not read_spec(a).routing_terms  # Session consent never changes the saved profile.
