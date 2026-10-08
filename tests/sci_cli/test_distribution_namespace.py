"""Distribution boundaries: exact launcher and no upstream namespace rollback."""

import pytest


def test_unpublished_distribution_refuses_resolution_before_network(tmp_path, monkeypatch):
    from sci_cli import source_releases
    from sci_cli.update_contract import evaluate_update_admission

    (tmp_path / "sci-unpublished-distribution").touch()
    def unexpected(*args, **kwargs):
        pytest.fail("Unpublished SCI build must not contact upstream release services")
    monkeypatch.setattr(source_releases, "_resolve_channel", unexpected)
    monkeypatch.setattr(source_releases, "source_repository", unexpected)
    refusal = evaluate_update_admission(tmp_path)
    assert refusal is not None and "not published" in refusal.message
    with pytest.raises(ValueError, match="not published"):
        source_releases.resolve_source_target("main", cwd=tmp_path)


def test_public_launcher_uses_the_same_entry_as_internal_command():
    from sci_cli._launchers import ENTRY_POINTS, WINDOWS_BIN_LAUNCHERS, _launcher_script
    from pathlib import Path

    assert ENTRY_POINTS["agent-sci"] == ENTRY_POINTS["sci"]
    assert "agent-sci" in WINDOWS_BIN_LAUNCHERS
    assert _launcher_script("agent-sci", Path.cwd(), None) == _launcher_script("sci", Path.cwd(), None)
