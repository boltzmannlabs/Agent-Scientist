"""SCI's default discovery must work without contacting an upstream documentation host."""

import json
from pathlib import Path


def test_default_catalogs_are_offline_and_preserve_removals_across_profiles(tmp_path, monkeypatch):
    import httpx
    import urllib.request
    from sci_cli import model_catalog, plugin_catalog
    from tools import skills_hub_search
    from tools.skills_hub_official import OptionalSkillSource

    def forbidden(*args, **kwargs):
        raise AssertionError("Default catalogs must not make a network request")

    monkeypatch.setattr(httpx, "get", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    monkeypatch.setattr("tools.skills_hub._skills_hub_http_get", forbidden)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    homes = [tmp_path / "A", tmp_path / "B"]
    for home in homes:
        (home / "cache").mkdir(parents=True)
        (home / "cache/plugin-catalog.json").write_text(json.dumps({
            "entries": [], "removed": [{"name": home.name, "reason": "fixture security removal"}]}))
    for home in (homes[0], homes[1], homes[0]):
        monkeypatch.setenv("SCI_HOME", str(home))
        assert model_catalog.get_catalog(force_refresh=True) == {}
        assert skills_hub_search._load_sci_index() is None
        assert plugin_catalog.load_catalog_live() == plugin_catalog.load_catalog()
        assert [e.name for e in plugin_catalog.live_removed_list()] == [home.name]
        assert OptionalSkillSource()._list_remote_skill_dirs() == {}
    # Old URLs persisted by a prior version cannot restore the inherited dependency.
    assert model_catalog._fetch_manifest(
        "https://hermes-agent.nousresearch.com/docs/api/model-catalog.json", 1) is None


def test_new_home_identity_and_seeded_manual_are_local(tmp_path, monkeypatch):
    from sci_cli.config import _ensure_default_soul_md
    from agent.prompt_builder import DEFAULT_AGENT_IDENTITY, load_soul_md
    from tools import skills_sync, skills_tool

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    home = tmp_path / ".sci"
    home.mkdir()
    monkeypatch.setenv("SCI_HOME", str(home))
    (home / skills_sync.NO_BUNDLED_SKILLS_MARKER).touch()
    _ensure_default_soul_md(home)
    skills_sync.sync_skills(quiet=True)
    assert load_soul_md(home_override=home) == DEFAULT_AGENT_IDENTITY
    result = skills_tool.skill_view("sci-agent")
    assert "Boltzmann Labs" in result and "Scientific execution policy" in result
    assert "hermes-agent.nousresearch.com" not in result
    assert "built by Nous" not in result
