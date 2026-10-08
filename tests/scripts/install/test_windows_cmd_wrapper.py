"""The Windows CMD entry point uses the checked-out SCI setup, not a remote script."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.platforms("windows")
@pytest.mark.parametrize("exit_code", [0, 23])
def test_local_setup_path_arguments_and_exit_code(tmp_path, exit_code):
    checkout = tmp_path / "checkout with spaces"
    scripts = checkout / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts/install.cmd", scripts)
    log = tmp_path / "called.txt"
    (checkout / "setup-sci.ps1").write_text(
        'param([string]$Marker)\n'
        'Set-Content -LiteralPath $env:SETUP_CALL_LOG -Value $Marker\n'
        f'exit {exit_code}\n')
    result = subprocess.run(
        ["cmd.exe", "/d", "/c", f'""{scripts / "install.cmd"}" -Marker "fixture value""'],
        env={**os.environ, "SETUP_CALL_LOG": str(log)},
        capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == exit_code
    assert log.read_text().strip() == "fixture value"


@pytest.mark.platforms("windows")
def test_incomplete_checkout_stops_without_launching_setup(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy2(ROOT / "scripts/install.cmd", scripts)
    result = subprocess.run(
        ["cmd.exe", "/d", "/c", str(scripts / "install.cmd")],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 2
    assert "Incomplete SCI checkout" in result.stdout
