"""Distribute complete skill bundles without shipping a user's runtime state."""

import ast
import shutil
import subprocess
from pathlib import Path

import sci_yaml as yaml

REPO = Path(__file__).resolve().parents[2]


def test_template_policy_and_portable_skill_resources():
    from sci_cli.config_skill_defaults import INITIAL_DISABLED_SKILLS
    from tools.skills_sync import _discover_bundled_skills

    template = yaml.safe_load((REPO / "cli-config.yaml.example").read_text())
    assert template["skills"]["disabled"] == list(INITIAL_DISABLED_SKILLS)
    bundles = _discover_bundled_skills(REPO / "skills")
    names = {name for name, _ in bundles}
    assert set(INITIAL_DISABLED_SKILLS) <= names
    for _, folder in bundles:
        for source in folder.rglob("*"):
            if not source.is_file() or "__pycache__" in source.parts:
                continue
            assert not source.is_symlink()
            if source.suffix == ".py":
                ast.parse(source.read_text(), filename=str(source))
            if source.name == "provenance.json":
                import json
                provenance = json.loads(source.read_text())
                assert "python" not in provenance  # no personal interpreter path
                assert (folder / "LICENSE.upstream.md").is_file()


def test_packaged_snapshot_sync_preserves_complete_bundles(tmp_path, monkeypatch):
    from scripts.bundles.payload import INERT_SNAPSHOT_DIRS, snapshot
    from sci_cli.config import seed_config_file
    from tools.skills_sync import _discover_bundled_skills, sync_skills
    from tools.skills_tool import _find_all_skills

    checkout = tmp_path / "release-fixture"
    checkout.mkdir()
    shutil.copytree(REPO / "skills", checkout / "skills", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy2(REPO / "cli-config.yaml.example", checkout)
    shutil.copy2(REPO / ".gitignore", checkout)
    # A disposable Git fixture tests the real archive path without staging this checkout.
    for args in (["init", "-q"], ["add", "skills", "cli-config.yaml.example"],
                 ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                  "-c", "commit.gpgsign=false", "commit", "-qm", "fixture"]):
        subprocess.run(["git", *args], cwd=checkout, check=True, capture_output=True)
    packaged = tmp_path / "packaged"
    snapshot(checkout, "HEAD", packaged, exclude=INERT_SNAPSHOT_DIRS)
    for _, folder in _discover_bundled_skills(checkout / "skills"):
        for source in folder.rglob("*"):
            if source.is_file():
                assert (packaged / source.relative_to(checkout)).read_bytes() == source.read_bytes()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    home = tmp_path / "fresh-home"
    monkeypatch.setenv("SCI_HOME", str(home))
    monkeypatch.setenv("SCI_BUNDLED_SKILLS", str(packaged / "skills"))
    monkeypatch.chdir(tmp_path)
    seed_config_file(home / "config.yaml", template=packaged / "cli-config.yaml.example")
    sync_skills(quiet=True)
    for _, folder in _discover_bundled_skills(packaged / "skills"):
        for source in folder.rglob("*"):
            if source.is_file():
                installed = home / "skills" / source.relative_to(packaged / "skills")
                assert installed.read_bytes() == source.read_bytes()
    active = {s["name"] for s in _find_all_skills()}
    assert "paired-antibody-generation" in active
    assert "api-integration-review" not in active
    assert not (home / ".env").exists()
    assert not (home / "skills" / ".usage.json").exists()
