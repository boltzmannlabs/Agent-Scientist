"""Fresh-install fixtures explicitly choose SCI and redirect Git to a local origin."""

import subprocess

import pytest


@pytest.mark.platforms("posix")
def test_installer_source_is_explicit_and_clone_stays_local(tmp_path):
    from tests.e2e.core.upgrade import _install_helpers as install

    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", "-q", str(origin)], check=True)
    sandbox = install.new_sandbox(tmp_path / "sandbox", origin)
    source = sandbox.env["SCI_REPO_URL"]
    assert source == install.OFFICIAL_HTTPS
    result = sandbox.run(["git", "clone", "-q", source, str(sandbox.checkout)], timeout=15)
    assert result.returncode == 0, result.stderr
    assert sandbox.checkout.is_dir()
    origin_config = (sandbox.checkout / ".git/config").read_text(encoding="utf-8-sig")
    assert f"url = {source}" in origin_config
