"""SCI Git updates work before native publication, without borrowing another feed."""

import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from sci_cli import source_releases


pytestmark = pytest.mark.real_release_channels


def git(root, *args):
    return subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
         "-c", "commit.gpgsign=false", *args],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout.strip()


@pytest.mark.parametrize("origin,allowed", [
    ("https://github.com/{repository}.git", True),
    ("git@github.com:{repository}.git", True),
    ("ssh://git@github.com/{repository}.git", True),
    ("https://github.com/unrelated/project.git", False),
    ("https://github.com/{repository}-other.git", False),
    ("https://github.com.example.invalid/{repository}.git", False),
])
def test_source_admission_is_origin_bound_and_does_not_unlock_native_feeds(
        tmp_path, monkeypatch, origin, allowed):
    from sci_cli.update_contract import evaluate_update_admission

    monkeypatch.setattr(source_releases, "_PUBLIC_BASE", "")
    root = tmp_path / "checkout"
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "remote", "add", "origin", origin.format(repository=source_releases.OFFICIAL_REPOSITORY))
    (root / "sci-unpublished-distribution").touch()

    def unexpected_network(*args, **kwargs):
        pytest.fail("Origin admission/main selection needs no release server")

    monkeypatch.setattr(source_releases.urllib.request, "urlopen", unexpected_network)
    assert source_releases.is_official_source_checkout(root) is allowed
    refusal = evaluate_update_admission(root)
    if allowed:
        assert refusal is None
        target = source_releases.resolve_source_target("main", ["git"], root)
        assert target.repository == source_releases.source_repository(["git"], root)
        assert target.branch == "main" and target.commit is None
        with pytest.raises(ValueError, match="not published"):
            source_releases.resolve_source_target("stable", ["git"], root)
        (root / "install-stamp.json").write_text(json.dumps({"source": "commit-build"}))
        assert evaluate_update_admission(root).code == "commit-build"
    else:
        assert refusal.code == "unpublished-distribution"
        with pytest.raises(ValueError, match="not published"):
            source_releases.resolve_source_target("main", ["git"], root)


def test_notification_check_and_apply_follow_sci_origin_and_preserve_profile_state(
        tmp_path, monkeypatch, capsys):
    from sci_cli import main, update_cmd
    from sci_cli.banner import _format_update_notice
    from sci_cli.source_check import check_for_updates

    monkeypatch.setattr(source_releases, "_PUBLIC_BASE", "")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file")
    remote = tmp_path / "origin.git"
    seed = tmp_path / "seed"
    root = tmp_path / "checkout"
    git(tmp_path, "init", "--bare", "-b", "main", str(remote))
    git(tmp_path, "clone", str(remote), str(seed))
    (seed / "sci-unpublished-distribution").touch()
    (seed / "science.txt").write_text("old source\n")
    git(seed, "add", ".")
    git(seed, "commit", "-m", "initial")
    git(seed, "push", "origin", "main")
    git(tmp_path, "clone", str(remote), str(root))
    old = git(root, "rev-parse", "HEAD")
    approved_url = f"https://github.com/{source_releases.OFFICIAL_REPOSITORY}.git"
    git(root, "config", "remote.origin.url", approved_url)
    git(root, "config", f"url.{remote.as_uri()}.insteadOf", approved_url)
    # A stale inherited upstream must not be preferred over SCI's origin.
    git(root, "remote", "add", "upstream", str(tmp_path / "missing-upstream.git"))
    (seed / "science.txt").write_text("updated source\n")
    git(seed, "commit", "-am", "advance source")
    git(seed, "push", "origin", "main")
    expected = git(seed, "rev-parse", "HEAD")

    homes = [tmp_path / "profile-a", tmp_path / "profile-b"]
    preserved = {}
    for index, home in enumerate(homes):
        home.mkdir()
        for relative, content in {
            "config.yaml": f"model: {{default: fixture-{index}}}\nupdates: {{check: true}}\n",
            "auth.json": '{"fixture": true}\n',
            "sessions/example.json": '[{"role": "user", "content": "fixture"}]\n',
            "skills/local/SKILL.md": "---\nname: local\ndescription: Fixture\n---\nPrivate instructions\n",
        }.items():
            path = home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            preserved[path] = path.read_bytes()
    before_git = {p: p.read_bytes() for p in (root / ".git").rglob("*") if p.is_file()}
    for home in [homes[0], homes[1], homes[0]]:
        monkeypatch.setenv("SCI_HOME", str(home))
        status = check_for_updates(install_root=root, home=home, passive=True)
        assert status["updateAvailable"] is True, status
        assert status["targetSha"] == expected
        assert (home / "source-checks").is_dir()
        assert "sci update" in _format_update_notice(status["behind"])
    assert {p: p.read_bytes() for p in before_git} == before_git
    assert git(root, "rev-parse", "HEAD") == old

    monkeypatch.setattr(main, "PROJECT_ROOT", root)
    monkeypatch.setenv("SCI_INSTALL_ROOT", str(root))
    update_cmd._cmd_update_check()
    assert "Update available" in capsys.readouterr().out
    assert git(root, "rev-parse", "HEAD") == old
    opts = update_cmd._UpdateOptions(
        pre_update_version=None, gw_input_fn=None, assume_yes=True,
        keep_stash=False, switch_branch=False, discard_local_changes=False,
    )
    monkeypatch.setattr(update_cmd, "_resolve_update_options", lambda *_: opts)
    monkeypatch.setattr(update_cmd, "_begin_update_receipt_and_plan", lambda *_: None)
    monkeypatch.setattr(main, "_run_pre_update_backup", lambda *_: None)
    monkeypatch.setattr(main, "_pause_windows_gateways_for_update", lambda: None)
    monkeypatch.setattr(update_cmd, "_prepare_git_command", lambda: (False, ["git"], False))
    completed = []
    # No dependency installation, native build or host-service restart in this
    # source-selection/pull fixture; the existing completion tests own that tail.
    monkeypatch.setattr(update_cmd, "_complete_source_update", completed.append)
    update_cmd._cmd_update_impl(SimpleNamespace(branch=None, channel=None), False)
    assert git(root, "rev-parse", "HEAD") == expected
    assert (root / "science.txt").read_text() == "updated source\n"
    assert len(completed) == 1 and completed[0]["expected_sha"] == expected
    assert completed[0]["home"] == str(homes[0])
    assert {p: p.read_bytes() for p in preserved} == preserved
    assert git(root, "config", "--get", "remote.origin.url") == approved_url
    assert git(root, "remote", "get-url", "upstream").endswith("missing-upstream.git")
