"""Research profiles publish atomically and never inherit unrelated project access."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sci_cli.science_profiles import ProfileSpec, Source, create, read_spec

IMAGE = "sha256:" + "a" * 64


@pytest.fixture
def homes(tmp_path, monkeypatch):
    from sci_cli import profiles
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    home = tmp_path / ".sci"
    home.mkdir()
    monkeypatch.setenv("SCI_HOME", str(home))
    monkeypatch.setattr(profiles, "_notify_multiplexer", lambda *_: None)
    monkeypatch.setattr(profiles, "_maybe_register_gateway_service", lambda *_: None)
    from sci_cli.config import atomic_config_write
    atomic_config_write(home / "config.yaml", {"model": {"provider": "openai-codex", "default": "fixture"},
                                               "unrelated": {"keep": True}})
    (home / ".env").write_text("PRIVATE_SERVICE_TOKEN=do-not-copy\n")
    return home


def test_creation_is_atomic_scoped_and_only_mounts_consented_sources(homes, tmp_path, monkeypatch):
    from sci_cli.config import read_user_config_raw
    from sci_cli.science_profiles_sandbox import validate_runtime
    monkeypatch.setattr("sci_cli.science_profiles_sandbox.resolve_image", lambda _: IMAGE)
    source = tmp_path / "research"
    source.mkdir()
    (source / "data.txt").write_text("project material")
    before = (homes / "config.yaml").read_bytes()
    a = create(ProfileSpec("antibody", "Antibody research", "Do not invent evidence", IMAGE,
                           sources=[Source(str(source))], allow_llm_sources=True), homes)
    b = create(ProfileSpec("molecule", "Small molecule research", "Cite evidence", IMAGE,
                           sources=[Source(str(source))]), homes)
    for target in (a, b, a):
        monkeypatch.setenv("SCI_HOME", str(target))
        spec = validate_runtime(target)
        assert spec.name == target.name
        cfg = read_user_config_raw(target / "config.yaml")
        assert cfg["terminal"]["docker_network"] is False
        assert cfg["terminal"]["docker_mount_cwd_to_workspace"] is False
        assert any(":/sources/" in v for v in cfg["terminal"]["docker_volumes"]) == spec.allow_llm_sources
        assert "PRIVATE_SERVICE_TOKEN" not in (target / ".env").read_text()
    assert (homes / "config.yaml").read_bytes() == before
    with pytest.raises(FileExistsError):
        create(ProfileSpec("antibody", "x", "x", IMAGE), homes)
    assert read_spec(a).purpose == "Antibody research"


def test_unsafe_material_and_staging_failure_never_publish_profile(homes, tmp_path, monkeypatch):
    source = tmp_path / "unsafe"
    source.mkdir()
    (source / "linked").symlink_to(homes / ".env")
    with pytest.raises(ValueError, match="Symlink"):
        create(ProfileSpec("unsafe", "x", "x", IMAGE, sources=[Source(str(source), "copy")]), homes)
    assert not (homes / "profiles" / "unsafe").exists()
    from sci_cli import profiles
    def fail(staged):
        (staged / "partial.txt").write_text("unpublished")
        raise RuntimeError("deliberate fixture failure")
    with pytest.raises(RuntimeError):
        profiles.create_profile("incomplete", no_skills=True, no_alias=True, prepare_staging=fail)
    assert not (homes / "profiles" / "incomplete").exists()
    from sci_cli.science_profiles_sandbox import validate_runtime
    a = create(ProfileSpec("edited", "x", "x", IMAGE), homes)
    from sci_cli.config import atomic_config_write, read_user_config_raw
    cfg = read_user_config_raw(a / "config.yaml")
    cfg["terminal"]["backend"] = "local"
    atomic_config_write(a / "config.yaml", cfg)
    with pytest.raises(ValueError, match="sandbox settings"):
        validate_runtime(a)


def test_activation_preserves_parent_and_routing_plan_enforces_grants(homes, monkeypatch):
    from sci_cli.science_profile_commands import activate
    from sci_cli.science_profile_router import validate_plan, route_input
    from sci_cli.commands import resolve_command, COMMANDS
    spec = ProfileSpec("antibody", "antibody", "scientist", IMAGE, routing_terms=["antibody"])
    create(spec, homes)
    monkeypatch.setattr("sci_cli.science_profiles_sandbox.resolve_image", lambda _: IMAGE)
    ui = SimpleNamespace(show=Mock())
    agent = object()
    cli = SimpleNamespace(agent=agent, conversation_history=[{"role": "user", "content": "main"}])
    for spelling in ("/Create_profile", "/CREATE_PROFILE", "/create_profile"):
        assert resolve_command(spelling).name == "create_profile"
    assert "/Create_profile" in COMMANDS
    activate(cli, '/activate "antibody" profile', ui)
    assert cli._science_active[1] == "antibody"
    activate(cli, "/activate main", ui)
    assert cli.agent is agent
    assert cli.conversation_history == [{"role": "user", "content": "main"}]
    assert route_input(cli, "ordinary main request") is False
    valid = [{"profile": "antibody", "prompt": "review", "needs": []}]
    assert validate_plan(valid, {"antibody": spec}) == valid
    with pytest.raises(ValueError, match="Dependencies"):
        validate_plan([{**valid[0], "needs": [0]}], {"antibody": spec})
    with pytest.raises(ValueError, match="consent"):
        validate_plan([{**valid[0], "profile": "unapproved"}], {"antibody": spec})


def test_terminal_wizard_creates_reviewed_profile_and_cancel_never_publishes(homes, monkeypatch):
    from sci_cli.science_profiles_ui import create_wizard
    from sci_cli.skill_add import Cancelled
    from sci_cli.profiles import get_profile_dir
    prepare = Mock(return_value=IMAGE)
    monkeypatch.setattr("sci_cli.science_profiles_environment.choose_environment", prepare)
    answers = iter([])
    choices = iter(["Done", "Create profile"])
    ui = SimpleNamespace(ask=lambda _: next(answers), choose=lambda *a: next(choices), show=Mock())
    create_wizard(SimpleNamespace(), '/Create_profile "antibody-study"', ui)
    home = get_profile_dir("antibody-study")
    assert read_spec(home).setup_pending
    assert "Ready:" in ui.show.call_args.args[0]
    prepare.assert_not_called()
    ui.choose = Mock(side_effect=Cancelled())
    create_wizard(SimpleNamespace(), '/Create_profile "cancelled-study"', ui)
    assert not get_profile_dir("cancelled-study").exists()
    assert "cancelled" in ui.show.call_args.args[0]


def test_remote_permissions_are_explicit_and_configuration_changes_fail_closed(homes, monkeypatch):
    from sci_cli.config import atomic_config_write, read_user_config_raw
    from sci_cli.science_profiles import reviewed_remote_config
    from sci_cli.science_profiles_sandbox import validate_runtime
    config = read_user_config_raw(homes / "config.yaml")
    remote = {"url": "https://mcp.example.invalid/mcp", "auth": "none"}
    for unsafe in ({**remote, "headers": {"Authorization": "private"}},
                   {**remote, "command": "unapproved"}, {**remote, "key_cmd": "unapproved"}):
        with pytest.raises(ValueError):
            reviewed_remote_config("literature", unsafe)
    config["mcp_servers"] = {"literature": remote}
    atomic_config_write(homes / "config.yaml", config)
    target = create(ProfileSpec("literature-study", "review papers", "cite sources", IMAGE,
                                mcp_tools={"literature": ["search_papers"]}), homes)
    saved = read_user_config_raw(target / "config.yaml")
    server = saved["mcp_servers"]["literature"]
    assert server["tools"]["include"] == ["search_papers"]
    assert not server["sampling"]["enabled"]
    monkeypatch.setattr("sci_cli.science_profiles_sandbox.resolve_image", lambda _: IMAGE)
    validate_runtime(target)
    server["url"] = "https://unapproved.example.invalid/mcp"
    atomic_config_write(target / "config.yaml", saved)
    with pytest.raises(ValueError, match="changed"):
        validate_runtime(target)
