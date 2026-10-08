"""The namespace rehearsal must be executable and leave the original untouched."""

from pathlib import Path
import subprocess
import sys

import pytest

from scripts.sci_namespace_migration import prepare, rewrite


def test_staged_imports_and_launcher_work_without_changing_source(tmp_path):
    root = tmp_path / "original"
    root.mkdir()
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    (root / "hermes_constants.py").write_text('def get_hermes_home(): return ".hermes"\n')
    (root / "hermes").write_text('from hermes_constants import get_hermes_home\nprint(get_hermes_home())\n')
    (root / "pyproject.toml").write_text('[project.scripts]\nhermes = "hermes_cli.main:main"\n')
    (root / "LICENSE").write_text("Copyright Hermes contributors\n")
    snapshots = {path.name: path.read_bytes() for path in root.iterdir() if path.is_file()}
    destination = tmp_path / "renamed"
    report = prepare(root, destination)
    result = subprocess.run([sys.executable, str(destination / "agent-sci")],
                            cwd=destination, capture_output=True, text=True, check=True)
    assert result.stdout.strip() == ".sci"
    assert report["live_home_modified"] is False
    assert {name: (root / name).read_bytes() for name in snapshots} == snapshots
    assert (destination / "LICENSE").read_bytes() == snapshots["LICENSE"]
    with pytest.raises(ValueError, match="must not exist"):
        prepare(root, destination)


def test_external_service_identities_survive_internal_rename(monkeypatch):
    monkeypatch.delenv("HERMES_HOME", raising=False)
    monkeypatch.delenv("SCI_HOME", raising=False)
    material = (
        'from hermes_cli.config import load_config\n'
        'DEFAULT_NOUS_CLIENT_ID = "hermes-cli"\n'
        'model = "NousResearch/Hermes-3-Llama-3.1-8B"\n'
        'url = "https://github.com/NousResearch/hermes-agent"\n'
        'home = os.environ.get("HERMES_HOME", "~/.hermes")\n'
        'dependencies = {"hermes-parser": "^0.25.1", "hermes-estree": "0.25.1"}\n'
    )
    result = rewrite(material, "example.py")
    original, renamed = {}, {}
    # Execute assignments only: this tests the values the runtime will consume.
    import os
    exec(material.split("\n", 1)[1], {"os": os}, original)
    exec(result.split("\n", 1)[1], {"os": os}, renamed)
    for key in ("DEFAULT_NOUS_CLIENT_ID", "model", "url", "dependencies"):
        assert renamed[key] == original[key]
    assert renamed["home"].endswith(".sci")
