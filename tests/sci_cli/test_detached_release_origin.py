"""A checkout without a publisher must never borrow upstream release infrastructure."""

import subprocess

import pytest


@pytest.mark.real_release_channels
def test_missing_origin_refuses_release_network_and_remote_creation(tmp_path, monkeypatch):
    from sci_cli import banner, source_check, source_releases, update_cmd_git

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)

    def unexpected(*args, **kwargs):
        pytest.fail("Unconfigured release lookup must not perform network I/O")

    monkeypatch.setattr(source_releases.urllib.request, "urlopen", unexpected)
    monkeypatch.setattr(source_check, "_request", unexpected)
    monkeypatch.setattr(banner, "_latest_release_cache", None)
    with pytest.raises(ValueError, match="No SCI release repository"):
        source_releases.source_repository(["git"], tmp_path)
    with pytest.raises(ValueError, match="endpoint is not configured"):
        source_releases._resolve_channel("main", "example/sci")
    assert source_check._github_compare("a" * 40, "b" * 40) is None
    assert not update_cmd_git._add_upstream_remote(["git"], tmp_path)
    assert not update_cmd_git._offer_upstream_remote(["git"], tmp_path, assume_yes=True, input_fn=unexpected)
    assert banner.get_latest_release_tag(tmp_path) is None
    assert subprocess.check_output(["git", "remote"], cwd=tmp_path) == b""


def test_explicit_origin_resolves_without_network(tmp_path, monkeypatch):
    from sci_cli import source_releases

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/example/scientist.git"],
                   cwd=tmp_path, check=True)
    def unexpected(*args, **kwargs):
        pytest.fail("Reading a Git origin must not contact a publisher")
    monkeypatch.setattr(source_releases.urllib.request, "urlopen", unexpected)
    assert source_releases.source_repository(["git"], tmp_path) == "example/scientist"
