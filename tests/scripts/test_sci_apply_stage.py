"""Rehearsed source cutover preserves user files and stops on concurrent edits."""
from pathlib import Path
import subprocess

import pytest

from scripts.sci_apply_stage import apply_stage
from scripts.sci_namespace_migration import prepare


@pytest.mark.parametrize("changed_after_review", [False, True])
def test_cutover_preserves_dirty_source_in_backup(tmp_path, changed_after_review):
    root, stage, backup = (tmp_path / p for p in ("original", "stage", "backup"))
    root.mkdir()
    backup.mkdir()
    (backup / "source-before.tar").touch()
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    (root / "hermes_constants.py").write_text('VALUE="hermes"\n')
    (root / "hermes").write_text('from hermes_constants import VALUE\n')
    (root / "pyproject.toml").write_text('[project.scripts]\nhermes="hermes_cli.main:main"\n')
    (root / "artifacts").mkdir()
    (root / "artifacts" / "research.txt").write_text("private research stays exactly here")
    prepare(root, stage)
    if changed_after_review:
        (root / "hermes_constants.py").write_text("new user edit")
        with pytest.raises(ValueError, match="changed after rehearsal"):
            apply_stage(root, stage, backup)
        assert (root / "hermes_constants.py").read_text() == "new user edit"
        assert not (root / "sci_constants.py").exists()
    else:
        result = apply_stage(root, stage, backup)
        assert result["leftovers_requiring_review"] == []
        assert (root / "sci_constants.py").read_text() == 'VALUE="sci"\n'
        assert not (root / "hermes_constants.py").exists()
        assert (backup / "moved-files/hermes_constants.py").read_text() == 'VALUE="hermes"\n'
    assert (root / "artifacts/research.txt").read_text() == "private research stays exactly here"
