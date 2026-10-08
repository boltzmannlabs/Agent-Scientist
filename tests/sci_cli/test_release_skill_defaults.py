"""First-install choices must not become live runtime defaults for existing users."""

from pathlib import Path

import pytest
import sci_yaml as yaml


@pytest.mark.parametrize("method", ["template", "fallback", "save"])
def test_first_creation_and_real_discovery_are_profile_local(tmp_path, monkeypatch, method):
    from agent import secret_scope
    from agent.skill_utils import get_disabled_skill_names
    from gateway.run import _profile_runtime_scope
    from sci_cli import config
    from sci_cli.config_skill_defaults import INITIAL_DISABLED_SKILLS
    from tools.skills_sync import sync_skills
    from tools.skills_tool import _find_all_skills

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.chdir(tmp_path)
    home_a, home_b = tmp_path / ".sci", tmp_path / ".sci" / "profiles" / "b"
    monkeypatch.setenv("SCI_HOME", str(home_a))
    home_b.mkdir(parents=True)
    path_b = home_b / "config.yaml"
    path_b.write_text("skills:\n  disabled: []\ncustom_project_setting: keep\n")
    bytes_b = path_b.read_bytes()
    secret_scope.set_multiplex_active(True)
    try:
        with _profile_runtime_scope(home_a, prepared_secret_scope={}):
            target = home_a / "config.yaml"
            if method == "save":
                config.save_config(config.load_config())
            else:
                template = None if method == "template" else tmp_path / "absent-template"
                config.seed_config_file(target, template=template)
            assert set(yaml.safe_load(target.read_text())["skills"]["disabled"]) == set(INITIAL_DISABLED_SKILLS)
            bytes_a = target.read_bytes()
            sync_skills(quiet=True)
            all_a = {s["name"] for s in _find_all_skills(skip_disabled=True)}
            active_a = {s["name"] for s in _find_all_skills()}
            assert active_a == all_a - set(INITIAL_DISABLED_SKILLS)
            assert "sci-agent" in active_a
            assert "paired-antibody-generation" in active_a
        with _profile_runtime_scope(home_b, prepared_secret_scope={}):
            sync_skills(quiet=True)
            assert not get_disabled_skill_names()
            active_b = {s["name"] for s in _find_all_skills()}
            assert active_b == all_a
            assert path_b.read_bytes() == bytes_b
        with _profile_runtime_scope(home_a, prepared_secret_scope={}):
            assert get_disabled_skill_names() == set(INITIAL_DISABLED_SKILLS)
            assert {s["name"] for s in _find_all_skills()} == active_a
            assert target.read_bytes() == bytes_a
    finally:
        secret_scope.set_multiplex_active(False)


@pytest.mark.parametrize("selection", [{}, {"skills": None}, {"skills": {"disabled": []}},
    {"skills": {"disabled": None}},
    {"skills": {"disabled": ["paired-antibody-generation"], "platform_disabled": {"telegram": ["arxiv"]}}}])
def test_existing_settings_and_explicit_first_choices_survive(tmp_path, monkeypatch, selection):
    from copy import deepcopy

    from sci_cli import config
    from sci_cli.config_skill_defaults import with_initial_skill_defaults

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    home = tmp_path / ".sci"
    home.mkdir()
    monkeypatch.setenv("SCI_HOME", str(home))
    target = home / "config.yaml"
    original = {**selection, "custom_project_setting": {"label": "preserved"}}
    target.write_text(yaml.safe_dump(original))
    before = target.read_bytes()
    assert config.seed_config_file(target) is False
    assert target.read_bytes() == before
    loaded = config.load_config()
    assert target.read_bytes() == before
    loaded["custom_project_setting"]["new_note"] = "requested"
    config.save_config(loaded)
    saved = yaml.safe_load(target.read_text())
    # The existing loader normalizes a null section to schema defaults. Assert
    # the selection contract, not the spelling of that equivalent empty state.
    assert (saved.get("skills") or {}).get("disabled") == (selection.get("skills") or {}).get("disabled")
    assert (saved.get("skills") or {}).get("platform_disabled") == (selection.get("skills") or {}).get("platform_disabled")
    assert saved["custom_project_setting"] == {"label": "preserved", "new_note": "requested"}
    initial = deepcopy(selection)
    seeded = with_initial_skill_defaults(initial)
    assert initial == selection
    if "skills" in selection:
        assert seeded["skills"] == selection["skills"]
