"""Upgrade lanes run their prepared controller, not an implicit second PM install."""

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

import pytest
from ruamel.yaml import YAML


@pytest.mark.platforms("linux")
@pytest.mark.parametrize("shard", ["core", "handoff"])
def test_upgrade_step_selects_its_prepared_interpreter_and_keeps_test_arguments(tmp_path, shard):
    root = Path(__file__).resolve().parents[2]
    workflow = YAML(typ="safe").load((root / ".github/workflows/tests.yml").read_text(encoding="utf-8"))
    step = next(step for step in workflow["jobs"]["e2e-upgrade"]["steps"]
                if "scripts/run_tests.sh --include-integration" in step.get("run", ""))
    activate = tmp_path / ".venv/bin/activate"
    activate.parent.mkdir(parents=True)
    activate.write_text(f"export VIRTUAL_ENV={shlex.quote(sys.prefix)}\n", encoding="utf-8")
    suite = tmp_path / "tests/e2e/core/upgrade"
    if shard != "core":
        suite /= shard
    suite.mkdir(parents=True)
    fixture = suite / "test_fixture.py"
    fixture.touch()
    runner = tmp_path / "scripts/run_tests.sh"
    runner.parent.mkdir()
    runner.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n"
        "\"$SCI_PYTHON\" -c 'import json, sys, pytest; "
        "print(\"RUNNER:\" + json.dumps({\"prefix\": sys.prefix, \"args\": sys.argv[1:]}))' \"$@\"\n",
        encoding="utf-8",
    )
    runner.chmod(0o755)
    env = {key: value for key, value in os.environ.items() if key != "SCI_PYTHON"}
    result = subprocess.run(["bash", "-e", "-c", step["run"]], cwd=tmp_path,
                            env={**env, "SHARD": shard}, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    record = json.loads(next(line.removeprefix("RUNNER:") for line in result.stdout.splitlines()
                             if line.startswith("RUNNER:")))
    assert record["prefix"] == sys.prefix
    assert record["args"] == ["--include-integration", str(fixture.relative_to(tmp_path))]
