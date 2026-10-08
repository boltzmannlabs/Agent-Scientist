"""Publication must fail before writes while the distribution is unconfigured."""

import sys

import pytest

from scripts import release


@pytest.mark.parametrize("arguments", [
    ["--canary", "--publish"],
    ["--prune-canaries", "--publish"],
    ["release", "--commit", "a" * 40],
    ["publish", "--version", "1.0.0"],
    ["abandon", "--version", "1.0.0"],
])
def test_unpublished_release_refuses_before_remote_actions(tmp_path, monkeypatch, capsys, arguments):
    (tmp_path / "sci-unpublished-distribution").touch()
    monkeypatch.setattr(release, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["release.py", *arguments])

    def unexpected(*args, **kwargs):
        pytest.fail("Publication refusal must precede git or external processes")

    monkeypatch.setattr(release.subprocess, "run", unexpected)
    with pytest.raises(SystemExit) as refused:
        release.main()
    assert refused.value.code == 2
    assert "SCI publication is disabled" in capsys.readouterr().err
