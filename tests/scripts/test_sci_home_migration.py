"""A home migration retains tenant boundaries, secrets, history and prior grants."""
import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

from scripts.sci_home_migration import migrate


def test_real_homes_keep_secrets_and_history_and_rebase_reviewed_settings(tmp_path, monkeypatch):
    from sci_cli.config import read_user_config_raw, atomic_config_replace
    from sci_cli.science_profiles import config_digest
    from sci_constants import set_sci_home_override, reset_sci_home_override, get_sci_home
    from agent.secret_scope import load_env_file

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    old, new = tmp_path / ".hermes", tmp_path / ".sci"
    monkeypatch.setenv("SCI_HOME", str(new))
    for name in ("A", "B"):
        home = old / "profiles" / name
        home.mkdir(parents=True)
        config = {"model": {"provider": "codex"}, "terminal": {"cwd": str(home / "workspace")},
                  "skills": {"disabled": ["autonomous-ai-agents/hermes-agent", "unrelated"]},
                  "unrelated": {"api_key": "hermes-secret-KEEP", "threshold": 17}}
        atomic_config_replace(home / "config.yaml", config)
        (home / ".env").write_text(f'HERMES_PRIVATE_TOKEN="hermes-secret-{name}"\n')
        (home / "auth.json").write_text('{"access_token":"hermes-auth-KEEP"}')
        (home / "science-profile.json").write_text(json.dumps({"config_digest": config_digest(config) if name == "A" else "unreviewed"}))
        with sqlite3.connect(home / "state.db") as db:
            db.execute("create table history(message text)")
            db.execute("insert into history values(?)", (f"hermes research history {name}",))
        (home / "skills").mkdir()
        (home / "skills" / "hermes-note.md").write_text("Read ~/.hermes/skills\n")
        (home / "workspace-link").symlink_to(home / "workspace")
        (home / "workspace").mkdir()
    before = {p: p.read_bytes() for p in old.rglob('*') if p.is_file()}
    report = migrate(old, new)
    assert report["existing_profiles_requiring_review"] == ["B"]
    for name in ("A", "B", "A"):
        home = new / "profiles" / name
        token = set_sci_home_override(home)
        try:
            assert get_sci_home() == home
            assert load_env_file(home / ".env")["SCI_PRIVATE_TOKEN"] == f"hermes-secret-{name}"
            config = read_user_config_raw(home / "config.yaml")
            assert config["terminal"]["cwd"] == str(home / "workspace")
            assert config["unrelated"] == {"api_key": "hermes-secret-KEEP", "threshold": 17}
            assert config["skills"]["disabled"] == ["autonomous-ai-agents/sci-agent", "unrelated"]
            expected_digest = config_digest(config) if name == "A" else "unreviewed"
            assert json.loads((home / "science-profile.json").read_text())["config_digest"] == expected_digest
            assert (home / "workspace-link").resolve() == home / "workspace"
            assert (home / "workspace").is_dir()
            with sqlite3.connect(home / "state.db") as db:
                assert db.execute("select message from history").fetchone()[0] == f"hermes research history {name}"
            assert (home / "auth.json").read_bytes() == (old / "profiles" / name / "auth.json").read_bytes()
        finally:
            reset_sci_home_override(token)
    assert all(p.read_bytes() == data for p, data in before.items())
    with pytest.raises(ValueError, match="new directory"):
        migrate(old, new)


@pytest.mark.parametrize("authorized", [False, True])
def test_relocating_boltzmann_receipt_never_grants_new_permission(tmp_path, authorized):
    from sci_cli.plugins_manifest import _portable_skill_namespace
    old, new = tmp_path / ".hermes", tmp_path / ".sci"
    old.mkdir()
    key = "fixture-only"
    (old / ".env").write_text(f"BOLTZMANN_API_KEY={key}\n")
    receipt = Path("plugin-data") / _portable_skill_namespace("boltzmann") / "state.json"
    (old / receipt).parent.mkdir(parents=True)
    digest = lambda home: hashlib.sha256(f"{home}\0{key}".encode()).hexdigest()
    original = digest(old) if authorized else "unapproved"
    (old / receipt).write_text(json.dumps({"authorization": original, "unrelated": "keep"}))
    migrate(old, new)
    state = json.loads((new / receipt).read_text())
    assert state["authorization"] == (digest(new) if authorized else original)
    assert state["unrelated"] == "keep"
