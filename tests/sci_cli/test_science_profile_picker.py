"""Description clipping must never make a picker item unselectable."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest


def test_trimmed_modal_answers_select_and_toggle_science_items():
    from sci_cli.skill_add import WizardUI
    from sci_cli.science_profiles_catalog import select_science_items
    options = {"bio-agent-skills-hub": "Discover and invoke 1,676 deduplicated biomedical AI agent skills from the Awesome Bio Agent Skills Hub",
               "plugin:prankweb": "Plugin-wide access: Local protein ligand-binding-site predictions using the standalone P2Rank 2.5.1 software"}
    steps = iter(["bio-agent-skills-hub", "plugin:prankweb", "bio-agent-skills-hub", "bio-agent-skills-hub", "Done"])
    def callback(questions):
        wanted = next(steps)
        label = next(c for c in questions[0]["choices"] if wanted in c)
        return {"outcome": "submitted", "answers": {"skill_add": label.strip()}}
    ui = WizardUI(SimpleNamespace(_app=SimpleNamespace(is_running=True), _clarify_callback=callback))
    ui.show = Mock()
    assert set(select_science_items(ui, "Scientific capabilities", options)) == set(options)
    # Other wizard menus may supply whitespace too; map to the original identity.
    ui.cli._clarify_callback = lambda _: {"outcome": "submitted", "answers": {"skill_add": "choice"}}
    assert ui.choose("Select", ["choice ", "Cancel"]) == "choice "
    with pytest.raises(ValueError, match="distinct"):
        ui.choose("Ambiguous", ["choice", "choice "])


def test_tool_catalog_prioritizes_tooluniverse_and_boltzmann_without_loading_code(tmp_path, monkeypatch):
    from sci_cli.native_profile_services import catalog
    from sci_cli.plugins_manifest import PluginManifest
    manifests = {name: PluginManifest(name=name, provides_tools=[f"{name}_info"], description=name)
                 for name in ("prankweb", "boltzmann", "aaa")}
    monkeypatch.setattr("sci_cli.plugins_discovery.collect_directory_manifests", lambda: [])
    monkeypatch.setattr("sci_cli.plugins_discovery.resolve_manifest_winners", lambda _: manifests)
    cfg = {"mcp_servers": {"pubmed": {}, "tooluniverse": {}, "another": {}}}
    keys = list(catalog(tmp_path, cfg))
    assert keys[:2] == ["mcp:tooluniverse", "plugin:boltzmann"]
    assert "plugin:prankweb" in keys and "mcp:pubmed" in keys
