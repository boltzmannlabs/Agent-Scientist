"""The user wrapper quotes its checkout, propagates failures, and skips login unattended."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.platforms("posix")
@pytest.mark.parametrize("failure", [0, 23])
def test_user_installer_order_and_failure(tmp_path, failure):
    source = tmp_path / "checkout with spaces"
    (source / "pm").mkdir(parents=True)
    shutil.copy2(ROOT / "install-sci.sh", source / "install-sci.sh")
    for name in ("pyproject.toml", "uv.lock", "pm/lock.json"):
        (source / name).touch()
    log = tmp_path / "calls"
    (source / "setup-sci.sh").write_text(
        '#!/bin/bash\nset -e\nprintf "setup:%s\\n" "$*" >> "$CALL_LOG"\n'
        'if [ "$SETUP_FAILURE" != 0 ]; then exit "$SETUP_FAILURE"; fi\n'
        'mkdir -p "$(dirname "$0")/.sci/bin"\n'
        'cp "$FIXTURE_CLI" "$(dirname "$0")/.sci/bin/sci"\n'
        'chmod +x "$(dirname "$0")/.sci/bin/sci"\n')
    cli = tmp_path / "fixture-cli"
    cli.write_text('#!/bin/bash\nprintf "cli:%s\\n" "$*" >> "$CALL_LOG"\n')
    env = {**os.environ, "CALL_LOG": str(log), "FIXTURE_CLI": str(cli),
           "SETUP_FAILURE": str(failure), "HOME": str(tmp_path)}
    result = subprocess.run(["bash", str(source / "install-sci.sh"), "--non-interactive"],
                            env=env, text=True, capture_output=True, timeout=20)
    assert result.returncode == failure
    calls = log.read_text().splitlines()
    assert calls[0] == "setup:--user-install"
    if failure:
        assert calls == ["setup:--user-install"]
        assert "stopped during installing runtime and dependencies" in result.stderr
        assert "is installed" not in result.stdout
    else:
        assert calls == ["setup:--user-install", "cli:--help"]
        assert "Agent Scientist is installed" in result.stdout
        assert "sci setup" in result.stdout


@pytest.mark.platforms("posix")
def test_unknown_option_stops_before_setup():
    result = subprocess.run(["bash", str(ROOT / "install-sci.sh"), "--invalid"],
                            text=True, capture_output=True, timeout=10)
    assert result.returncode == 2 and "Unknown option" in result.stderr
