"""SCI release identities survive source installs and ordered native packaging."""

import json
import subprocess

import pytest


@pytest.mark.parametrize("version", ["1.0.0.0", "1.2.1.3", "1.9.999.99"])
def test_release_identity_roundtrip_and_ordered_bumps(tmp_path, version):
    from sci_cli.update_channel import STABLE_TAG_RE, canary_tag_for_date, is_canary_tag
    from sci_cli.version_info import _git_version_info
    from scripts.releases.versioning import derive_next_version, parse_attempt_ref, version_from_tag
    from scripts.releases.sequencer import plan
    from scripts.termux.deb_version import channel_for_tag, deb_version_for_tag

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=tmp_path, text=True).strip()

    git("init", "-q", "-b", "main")
    git("config", "user.name", "Fixture")
    git("config", "user.email", "fixture@example.invalid")
    git("-c", "commit.gpgSign=false", "commit", "-qm", "fixture", "--allow-empty")
    tag = "v" + version
    git("-c", "tag.gpgSign=false", "tag", "-a", tag, "-m", "fixture release")
    info = _git_version_info(tmp_path)
    assert info.base_version == info.display_version == version
    assert info.distance == 0
    assert STABLE_TAG_RE.fullmatch(tag) and version_from_tag(tag) == version
    assert parse_attempt_ref("rc.1-" + tag) == (version, 1)
    assert deb_version_for_tag(tag) == version + "-1"
    canary = canary_tag_for_date(version, "20261016T120000Z")
    assert is_canary_tag(canary) and channel_for_tag(canary) == "canary"
    assert deb_version_for_tag(canary).startswith(version + "~canary.")
    before = list(map(int, version.split(".")))
    for index, bump in enumerate(("major", "milestone", "minor", "patch")):
        after = list(map(int, derive_next_version(published=version, bump=bump).split(".")))
        assert after[:index] == before[:index]
        assert after[index] == before[index] + 1
        assert all(value == 0 for value in after[index + 1:])
    patch = derive_next_version(published=version, bump="patch")
    assert plan([{"version": patch, "state": "green", "autopublish": True}], head=version) == [
        {"flip": patch}, {"advance": patch}]
    # Exercise the actual claim writer against a LOCAL remote, not production.
    origin = tmp_path.parent / (tmp_path.name + "-origin.git")
    subprocess.run(["git", "init", "--bare", "-q", str(origin)], check=True)
    git("remote", "add", "origin", str(origin))
    git("push", "-q", "origin", "main", "refs/tags/" + tag)
    from scripts.releases.entrypoint import release
    result = release(git("rev-parse", "HEAD"), bump="patch", repo=tmp_path, remote="origin",
                     repository="example/sci-agent", published=(version, git("rev-parse", "HEAD")),
                     execute=lambda command: "[]" if command[:3] == ["gh", "run", "list"] else "")
    assert result["version"] == patch and result["tag"] == "rc.1-v" + patch
    assert git("rev-parse", result["tag"] + "^{commit}") == git("rev-parse", "HEAD")


def test_native_mapping_preserves_order_provenance_and_feed_identity(tmp_path):
    from scripts.releases.semver import package_version, compare
    from scripts.releases.stamping import stamp, validate_bootstrap_version
    from scripts.releases.darwin import merge_mac_feeds, parse_mac_feed
    from scripts.releases.commit_build import version_at

    versions = ["1.0.0.0", "1.0.0.1", "1.0.1.0", "1.0.999.999", "1.1.0.0", "1.2.1.3"]
    native = [package_version(value) for value in versions]
    for left, right in zip(native, native[1:]):
        assert compare(left, right) < 0
    assert len(set(native)) == len(versions)
    assert package_version("1.2.1.3") == "1.2001.3"
    assert package_version("1.2.1.3+canary.20261016T120000Z").startswith("1.2001.3+")
    with pytest.raises(ValueError, match="minor < 1000"):
        package_version("1.0.1000.0")
    installer = tmp_path / "apps/bootstrap-installer/src-tauri"
    installer.mkdir(parents=True)
    (installer / "tauri.conf.json").write_text('{"version":"0.0.0"}')
    (installer / "Cargo.toml").write_text('[package]\nversion="0.0.0"\n')
    stamp(tmp_path, versions[-1])
    validate_bootstrap_version(tmp_path, versions[-1])
    assert json.loads((installer / "tauri.conf.json").read_text())["version"] == native[-1]
    assert version_at(None, "a" * 40, run=lambda *args: '[project]\nversion="1.2.1.3"') == versions[-1]
    legs = {}
    for arch in ("arm64", "x64"):
        legs[arch + "-stable-mac.yml"] = json.dumps({"version": native[-1], "files": [{
            "url": f"SciBundled-{versions[-1]}-mac-{arch}.zip", "sha512": "a" * 86 + "==", "size": 100}]})
    merged = merge_mac_feeds(legs, "v" + versions[-1])
    assert merged["tag"] == "v" + versions[-1]
    assert merged["version"] == native[-1]
    assert parse_mac_feed(merged["text"])["version"] == native[-1]
    assert all("v" + versions[-1] in row["url"] for row in merged["files"])
