"""An unpublished SCI bootstrap cannot silently fetch the upstream product."""

import json
import os
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.platforms("posix")
@pytest.mark.parametrize("args", [[], ["--stage", "repository", "--json"]])
def test_missing_source_stops_before_external_actions(tmp_path, args):
    sentinels = tmp_path / "bin"
    sentinels.mkdir()
    marker = tmp_path / "unexpected-external-action"
    for command in ("git", "curl", "uv"):
        stub = sentinels / command
        stub.write_text('#!/bin/sh\ntouch "$PROBE_MARKER"\nexit 99\n')
        stub.chmod(0o755)
    home = tmp_path / "sci-home"
    env = {**os.environ, "SCI_REPO_URL": "", "SCI_HOME": str(home),
           "SCI_INSTALL_DIR": str(tmp_path / "installation"),
           "HOME": str(tmp_path), "PROBE_MARKER": str(marker),
           "PATH": f"{sentinels}:{os.environ['PATH']}"}
    env.pop("TERMUX_VERSION", None)
    env.pop("PREFIX", None)
    result = subprocess.run(["bash", str(ROOT / "scripts/install.sh"), *args],
                            env=env, capture_output=True, text=True, timeout=10)
    assert result.returncode != 0
    assert "SCI_REPO_URL" in result.stderr and "Nothing was downloaded" in result.stderr
    assert not marker.exists()
    assert not (tmp_path / "installation").exists()
    if args:
        frames = [json.loads(line) for line in result.stdout.splitlines() if line.startswith("{")]
        assert frames and frames[-1]["ok"] is False


@pytest.mark.platforms("windows")
def test_windows_missing_source_stops_before_repository_creation(tmp_path):
    env = {**os.environ, "SCI_REPO_URL": "", "SCI_HOME": str(tmp_path / "home")}
    destination = tmp_path / "installation"
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(ROOT / "scripts/install.ps1"), "-Stage", "repository", "-Json",
         "-InstallDir", str(destination)],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode != 0
    assert "SCI_REPO_URL" in result.stdout + result.stderr
    assert not destination.exists()
