"""Release sampling follows tag chronology across CalVer and SemVer."""
import os
import json
from pathlib import Path
import subprocess

import pytest

from scripts.releases.pick_tags import pick_tags


def test_sampling_includes_newest_stable_and_excludes_candidate(tmp_path):
    def git(*args, env=None):
        return subprocess.run(["git", *args], cwd=tmp_path, env=env, check=True, capture_output=True, text=True)

    git("init", "-b", "main")
    git("config", "user.name", "fixture")
    git("config", "user.email", "fixture@example.invalid")
    for index, tag in enumerate(["v2026.7.20", "v0.27.0", "v0.28.0"]):
        env = {**os.environ, "GIT_AUTHOR_DATE": f"2026-08-{index + 1:02d}T00:00:00Z", "GIT_COMMITTER_DATE": f"2026-08-{index + 1:02d}T00:00:00Z"}
        git("commit", "--allow-empty", "-m", tag, env=env)
        git("tag", tag)
    assert pick_tags(tmp_path, 1, "v0.28.0") == ["v0.27.0"]
    assert pick_tags(tmp_path, 3, "v0.28.0") == ["v2026.7.20", "v0.27.0"]


@pytest.mark.platforms("linux")
def test_scheduled_install_sampler_accepts_product_versions_in_numeric_order(tmp_path):
    def git(*args):
        return subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True, text=True)

    git("init", "-b", "main")
    git("-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "--allow-empty", "-m", "fixture")
    releases = ["v1.0.0.0", "v1.0.0.2", "v1.0.0.10"]
    for tag in [*releases, "v1.0.0.11-canary", "backup/release"]:
        git("tag", tag)
    script = Path(__file__).resolve().parents[2] / "scripts/sandbox/pick-release-tags.sh"
    for count, expected in [(1, releases[-1:]), (2, [releases[0], releases[-1]]), (5, releases)]:
        result = subprocess.run(["bash", str(script), "--repo", str(tmp_path), "--count", str(count)],
                                capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == expected
