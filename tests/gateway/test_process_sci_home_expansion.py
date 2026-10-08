"""Gateway identity-file readers expand a literal ``~`` in SCI_HOME.

``python -m gateway.run`` never passes through the CLI's ``normalize_sci_home_env()``, so the
process-level home readers (PID/lock/status, lifecycle ledger, heartbeat) must expand on their own
or a fish-style ``SCI_HOME='~/.sci'`` lands the identity files under ``<cwd>/~/.sci``.
"""

from pathlib import Path

import pytest

from gateway import lifecycle_ledger, shutdown_watchdog, status


@pytest.mark.parametrize(
    "reader",
    [status._get_process_sci_home, lifecycle_ledger._process_sci_home,
     shutdown_watchdog._process_sci_home],
    ids=["status", "lifecycle_ledger", "shutdown_watchdog"],
)
def test_process_home_readers_expand_literal_tilde(reader, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("SCI_HOME", "~/.x")
    assert reader() == tmp_path / ".x"
    assert reader().is_absolute()
    monkeypatch.setenv("SCI_HOME", str(tmp_path / ".abs"))
    assert reader() == Path(tmp_path / ".abs")
