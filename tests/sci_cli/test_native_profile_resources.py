"""Real profile/plugin discovery and fail-closed backend preparation contracts."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


def test_reviewed_plugin_reuses_code_but_grants_only_selected_profiles(tmp_path, monkeypatch):
    from sci_cli.config import atomic_config_replace, read_user_config_raw
    from sci_cli.native_profile_creation import create_native, profile_scope
    from sci_cli.native_profile_services import catalog, setup_plugin
    from sci_cli.plugins import get_plugin_manager
    from sci_cli.profiles import get_profile_dir
    from tools.registry import registry

    main = tmp_path / ".sci"
    plugin = main / "plugins" / "fixture-capability"
    plugin.mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(main))
    monkeypatch.setattr("sci_cli.profiles._notify_multiplexer", lambda *_: None)
    monkeypatch.setattr("sci_cli.profiles._maybe_register_gateway_service", lambda *_: None)
    empty = tmp_path / "empty-bundled"
    empty.mkdir()
    monkeypatch.setattr("sci_cli.plugins.get_bundled_plugins_dir", lambda: empty)
    (plugin / "plugin.yaml").write_text("name: fixture-capability\nversion: '1.0'\nprovides_tools: [fixture_info]\n")
    (plugin / "__init__.py").write_text(
        "def register(ctx):\n"
        "    ctx.register_tool(name='fixture_info', toolset='fixture_science',\n"
        "        schema={'name':'fixture_info','description':'Fixture metadata',"
        "'parameters':{'type':'object','properties':{}}}, handler=lambda args: {'fixture': True})\n")
    config = {"plugins": {"enabled": ["fixture-capability"]}, "terminal": {"backend": "local"}}
    atomic_config_replace(main / "config.yaml", config)
    ui = SimpleNamespace(show=Mock(), choose=Mock(return_value="Approve plugin"))
    managers = []
    try:
        with profile_scope(main):
            manager = get_plugin_manager()
            managers.append(manager)
            manager.discover_and_load()
            manifest = catalog(main, config)["plugin:fixture-capability"][2]
            service = setup_plugin(SimpleNamespace(), ui, main, "fixture-capability", manifest, config)
            assert service.toolsets == ["fixture_science"]
        for name, services in (("selected", [service]), ("unselected", [])):
            home = get_profile_dir(name)
            create_native(name, main, [], services, [], {"backend": "local", "cwd": str(home / "workspace")}, "Scientist")
        assert (get_profile_dir("selected") / "plugins/fixture-capability").resolve() == plugin.resolve()
        for name in ("selected", "unselected", "selected"):
            with profile_scope(get_profile_dir(name)):
                manager = get_plugin_manager()
                if manager not in managers:
                    managers.append(manager)
                manager.discover_and_load()
                assert (registry.get_entry("fixture_info") is not None) == (name == "selected")
                cfg = read_user_config_raw(get_profile_dir(name) / "config.yaml")
                assert ("fixture_science" in cfg["platform_toolsets"]["cli"]) == (name == "selected")
    finally:
        for manager in managers:
            manager.unload()


def test_environment_never_inherits_main_mounts_or_falls_back_without_consent(tmp_path, monkeypatch):
    from sci_cli.native_profile_environment import prepare_environment
    from sci_cli.skill_add import Cancelled
    import threading
    config = {"terminal": {"backend": "docker", "docker_image": "approved-image",
              "docker_volumes": ["/private:/private"], "env_passthrough": ["PRIVATE_KEY"],
              "docker_extra_args": ["--privileged"], "docker_shared_container_key": "main"}}
    ui = SimpleNamespace(show=Mock(), choose=Mock(side_effect=Cancelled()))
    monkeypatch.setattr("sci_cli.science_profiles_sandbox.docker_command", Mock(return_value="fixture"))
    resolve = Mock(side_effect=ValueError("missing image"))
    monkeypatch.setattr("sci_cli.science_profiles_sandbox.resolve_image", resolve)
    download = Mock()
    monkeypatch.setattr("sci_cli.science_profiles_environment.run_preparation", download)
    with pytest.raises(Cancelled):
        prepare_environment(config, tmp_path / "new", ui, threading.Event())
    download.assert_not_called()
    resolve.side_effect = None
    resolve.return_value = "sha256:fixture"
    terminal = prepare_environment(config, tmp_path / "new", ui, threading.Event())
    assert terminal["docker_volumes"] == [f"{tmp_path / 'new/workspace'}:/workspace:rw"]
    assert not terminal["env_passthrough"] and not terminal["docker_extra_args"]
    assert not terminal["docker_shared_container_key"]
    assert config["terminal"]["docker_volumes"] == ["/private:/private"]
    with pytest.raises(ValueError, match="no host fallback"):
        prepare_environment({"terminal": {"backend": "ssh"}}, tmp_path / "new", ui, threading.Event())
