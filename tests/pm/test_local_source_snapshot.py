"""Local optional dependencies survive PM's writable workspace staging."""

import pytest

from pm.package import InstallError
from pm.workspace import _copy_core_inputs


@pytest.mark.parametrize("as_archive", [False, True])
def test_local_dependency_staged_without_mutating_source(tmp_path, as_archive):
    source = tmp_path / "source"
    source.mkdir()
    vendor = source / "third_party" / "speech"
    vendor.mkdir(parents=True)
    (vendor / "pyproject.toml").write_text('[project]\nname="speech"\nversion="1"\n')
    original = "def speak(): return 'fixture'\n"
    (vendor / "speech.py").write_text(original)
    relative = "third_party/speech"
    if as_archive:
        relative = "third_party/speech.whl"
        (source / relative).write_text(original)
    (source / "pyproject.toml").write_text(
        '[project]\nname="fixture"\nversion="1"\n'
        '[tool.setuptools.packages.find]\ninclude=["agent*"]\n'
        f'[tool.uv.sources]\nspeech={{path="{relative}"}}\n')
    snapshot = tmp_path / "generation"
    snapshot.mkdir()
    _copy_core_inputs(source, snapshot)
    relative_file = relative if as_archive else f"{relative}/speech.py"
    copied = snapshot / relative_file
    assert copied.read_text() == original
    copied.write_text("modified snapshot")
    assert (source / relative_file).read_text() == original


def test_local_dependency_cannot_escape_source_checkout(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "pyproject.toml").write_text(
        '[project]\nname="fixture"\nversion="1"\n'
        '[tool.uv.sources]\nspeech={path="../private"}\n')
    target = tmp_path / "generation"
    target.mkdir()
    with pytest.raises(InstallError, match="escapes the core project"):
        _copy_core_inputs(source, target)
