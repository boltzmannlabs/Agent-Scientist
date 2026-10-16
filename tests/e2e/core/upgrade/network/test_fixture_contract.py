"""The transport fixture enables channels only in its private source origin."""

import json

from sci_cli import source_releases
from sci_cli.release_channels import validate_manifest, validate_record
from tests.e2e.core.upgrade import _install_helpers as I
from tests.e2e.core.upgrade.network import _seed as S


def test_fixture_publisher_is_confined_to_its_disposable_origin(tmp_path):
    original = I.git("show", "HEAD:sci_cli/source_releases.py", cwd=I.H.WORKTREE)
    origin = I.make_origin(tmp_path, I.head_sha())
    commit = S.channel_fixture_origin(origin, tmp_path)
    configured = I.git("show", f"{commit}:sci_cli/source_releases.py", cwd=origin)
    assert configured.replace(f'_PUBLIC_BASE = "https://{S.ASSETS}"', '_PUBLIC_BASE = ""') == original
    assert source_releases._PUBLIC_BASE == ""


def test_fixture_release_validates_against_the_real_protocol():
    objects = S.stable_objects("a" * 40)
    record = validate_record(json.loads(objects["/releases/channels/stable.json"]),
                             name="stable", repository=S.REPOSITORY)
    manifest = json.loads(objects["/" + record["head"]["manifestKey"]])
    checked = validate_manifest(manifest, record, f"https://{S.ASSETS}")
    assert checked["request"]["repository"] == source_releases.OFFICIAL_REPOSITORY
