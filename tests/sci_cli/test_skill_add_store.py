"""Installation conflicts use fresh disk state, not the offer-time skill index."""

import copy

import pytest

from sci_cli.skill_add_sources import bundle_from_files
from sci_cli.skill_add_store import existing_skill, save_reviewed, scanned_bundle


SKILL = "---\nname: research-check\ndescription: Review scientific inputs.\n---\n# Check\nDisclose limitations.\n"


def test_native_skill_conflicts_are_profile_scoped_even_when_not_offered(tmp_path, monkeypatch):
    from pathlib import Path
    from agent.prompt_builder import _SKILLS_PROMPT_CACHE, build_skills_system_prompt
    from agent.secret_scope import set_secret_scope, reset_secret_scope, set_multiplex_context, reset_multiplex_context
    from sci_constants import set_sci_home_override, reset_sci_home_override
    from tools.skill_manager_tool import _create_skill
    from tools.skills_tool import _find_all_skills

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    home_a, home_b = tmp_path / "home-a", tmp_path / "home-b"
    for home in (home_a, home_b):
        (home / "skills").mkdir(parents=True)
        (home / "config.yaml").write_text("model:\n  default: unchanged\nskills:\n  disabled: [unrelated]\n")
    monkeypatch.setenv("SCI_HOME", str(home_a))
    bundle = bundle_from_files({"SKILL.md": SKILL}, "fixture")
    multiplex = set_multiplex_context(True)
    try:
        for home in (home_a, home_b, home_a):
            scope = set_sci_home_override(home)
            secrets = set_secret_scope({}, profile_home=str(home))
            try:
                if home == home_a:
                    native = home / "skills" / "research" / bundle.name / "SKILL.md"
                    if not native.exists():
                        hidden = SKILL.replace("description:", "requires_apps: [missing-demo-app]\ndescription:")
                        assert _create_skill(bundle.name, hidden, category="research")["success"]
                    before = native.read_bytes()
                    assert not any(s["name"] == bundle.name for s in _find_all_skills(skip_disabled=True))
                    assert not _create_skill(bundle.name, SKILL)["success"]
                    build_skills_system_prompt()
                    cached = copy.deepcopy(_SKILLS_PROMPT_CACHE)
                    config = (home / "config.yaml").read_bytes()
                    assert existing_skill(bundle.name)
                    with scanned_bundle(bundle) as (staged, scan):
                        with pytest.raises(FileExistsError, match="already exists"):
                            save_reviewed(bundle, staged, scan)
                    assert native.read_bytes() == before
                    assert not (home / "skills" / bundle.name).exists()
                    assert (home / "config.yaml").read_bytes() == config
                    assert _SKILLS_PROMPT_CACHE == cached
                else:
                    assert not existing_skill(bundle.name)
                    with scanned_bundle(bundle) as (staged, scan):
                        destination, status = save_reviewed(bundle, staged, scan)
                    assert destination == home / "skills" / bundle.name
                    assert (destination / "SKILL.md").read_text() == SKILL
                    assert status.startswith("Enabled.")
            finally:
                reset_secret_scope(secrets)
                reset_sci_home_override(scope)
    finally:
        reset_multiplex_context(multiplex)
