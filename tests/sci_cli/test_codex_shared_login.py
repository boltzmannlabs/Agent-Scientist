"""Codex reuse validates the actual source and follows rotation without copying grants."""

import base64
import json
from pathlib import Path
import time
from types import SimpleNamespace

import pytest

from sci_cli.native_profile_creation import profile_scope
from sci_cli.config import atomic_config_replace


def token(label, *, account="fixture-account", expiry=None):
    claims = {"sub": "fixture-user", "https://api.openai.com/auth": {"chatgpt_account_id": account},
              "exp": expiry if expiry is not None else time.time() + 3600, "generation": label}
    encoded = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return "fixture." + encoded + ".signature"


@pytest.fixture
def env(tmp_path, monkeypatch):
    from agent.secret_scope import set_multiplex_active
    main = tmp_path / "science-root"
    homes = main, main / "profiles" / "a", main / "profiles" / "b"
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(main))
    external = tmp_path / "current-codex"
    external.mkdir()
    monkeypatch.setenv("CODEX_HOME", str(external))
    for h in homes:
        h.mkdir(parents=True)
        atomic_config_replace(h / "config.yaml", {
            "model": {"provider": "lmstudio", "default": "profile-model-" + h.name},
            "providers": {"openai-codex": {"enabled": False}},
            "model_catalog": {"excluded_providers": ["openai-codex", "codex", "anthropic"]},
        })
        (h / ".env").write_text("BOLTZMANN_API_KEY=private-fixture\n")
    set_multiplex_active(True)
    try:
        yield homes, external
    finally:
        set_multiplex_active(False)


class HTTP:
    def __init__(self, calls, status=200):
        self.calls, self.status = calls, status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, url, *, headers):
        self.calls.append((url, headers["Authorization"]))
        return SimpleNamespace(status_code=self.status)

    def post(self, *args, **kwargs):
        pytest.fail("Reusing Codex must not spend its refresh token")


def test_current_codex_login_wins_over_stale_sci_and_chat_titles_follow_rotation(env, monkeypatch):
    from sci_cli import auth, auth_codex
    from sci_cli.auth_commands import auth_add_command
    from sci_cli.runtime_provider import resolve_runtime_provider
    from agent import auxiliary_client as aux
    from sci_cli.config import read_user_config_raw

    homes, external = env
    main, a, b = homes
    old, current, rotated = token("stale-sci"), token("current-codex"), token("rotated-codex")
    (external / "config.toml").write_text('cli_auth_credentials_store = "file"\n', encoding="utf-8-sig")
    (main / "auth.json").write_text(json.dumps({"providers": {"openai-codex": {
        "tokens": {"access_token": old, "refresh_token": "stale-copy"}}}}))
    independent = token("independent", account="other-account")
    (b / "auth.json").write_text(json.dumps({"providers": {"openai-codex": {
        "tokens": {"access_token": independent, "refresh_token": "independent-grant"}}},
        "providers-other": {"lab": {"access_token": "private-fixture"}}}))
    auth_path = external / "auth.json"
    auth_path.write_text(json.dumps({"tokens": {"access_token": current, "refresh_token": "owned-by-codex"}}))
    calls = []
    monkeypatch.setattr(auth_codex, "_codex_http_client", lambda **kw: HTTP(calls))
    monkeypatch.setattr(auth, "_prompt_yes_no", lambda *args, **kwargs: True)
    config_before = {h: read_user_config_raw(h / "config.yaml")["model"] for h in homes}
    with profile_scope(a):
        auth_add_command(SimpleNamespace(provider="openai-codex", auth_type="oauth", browser=False))
    assert calls == [("https://chatgpt.com/backend-api/wham/usage", "Bearer " + current)]
    assert "owned-by-codex" not in (main / "auth.json").read_text()
    assert current not in (main / "auth.json").read_text()
    assert auth._load_auth_store(main / "auth.json")["providers"]["openai-codex"]["external_codex_home"] == str(external)
    pool_rows = auth._load_auth_store(main / "auth.json")["credential_pool"]["openai-codex"]
    assert any(row.get("access_token") == independent for row in pool_rows)
    assert auth._load_auth_store(b / "auth.json")["providers-other"]["lab"]["access_token"] == "private-fixture"
    monkeypatch.setattr(aux, "_client_cache", {})
    monkeypatch.setattr(aux, "_pool_cache_hint", lambda *args, **kwargs: "")
    monkeypatch.setattr(aux, "_aux_probe_active", lambda: False)
    builds = []

    def build(provider, model, async_mode, **kwargs):
        builds.append(kwargs)
        return SimpleNamespace(api_key=kwargs["explicit_api_key"], base_url=kwargs["explicit_base_url"]), model

    monkeypatch.setattr(aux, "resolve_provider_client", build)
    for expected in (current, rotated):
        if expected == rotated:
            auth_path.write_text(json.dumps({"tokens": {"access_token": rotated, "refresh_token": "rotated-only-in-codex"}}))
        for h in (main, a, b, a):
            with profile_scope(h):
                assert resolve_runtime_provider(requested="openai-codex")["api_key"] == expected
                assert aux._resolve_codex_credential_and_base()[0] == expected
                for provider in ("openai-codex", "auto"):
                    client, _ = aux._get_cached_client(provider, model="fixture", task="title_generation",
                                                      main_runtime={"provider": "openai-codex", "api_key": old})
                    assert client.api_key == expected
                assert read_user_config_raw(h / "config.yaml")["model"] == config_before[h]
                assert "anthropic" in read_user_config_raw(h / "config.yaml")["model_catalog"]["excluded_providers"]
    assert len(calls) == 1  # discovery/status/runtime never perform hidden validation probes
    for h in (a, b):
        assert not auth._load_auth_store(h / "auth.json").get("providers", {}).get("openai-codex")
    auth_path.write_text(json.dumps({"tokens": {"access_token": token("other", account="different-workspace")}}))
    with profile_scope(a), pytest.raises(auth.AuthError, match="another account/workspace"):
        resolve_runtime_provider(requested="openai-codex")


@pytest.mark.parametrize("case", ["rejected-current", "rejected-saved", "rejected-fresh", "keyring", "expired", "cancel"])
def test_failed_login_never_reports_success_or_reenables_profiles(env, monkeypatch, capsys, case):
    from sci_cli import auth, auth_codex
    from sci_cli.auth_commands import auth_add_command

    homes, external = env
    main, a, b = homes
    access = token(case, expiry=1 if case == "expired" else None)
    if case in {"rejected-current", "expired", "keyring", "cancel"}:
        (external / "auth.json").write_text(json.dumps({"tokens": {"access_token": access, "refresh_token": "external-fixture"}}))
    if case == "keyring":
        (external / "config.toml").write_text('cli_auth_credentials_store = "keyring"\n')
    if case == "rejected-saved":
        (a / "auth.json").write_text(json.dumps({"providers": {"openai-codex": {"tokens": {
            "access_token": access, "refresh_token": "sci-fixture"}}}}))
    monkeypatch.setattr(auth, "_prompt_yes_no", lambda *args, **kw: True)
    if case == "cancel":
        def cancel(*args, **kwargs):
            raise KeyboardInterrupt()
        monkeypatch.setattr(auth, "_prompt_yes_no", cancel)
    calls = []
    monkeypatch.setattr(auth_codex, "_codex_http_client", lambda **kw: HTTP(calls, 401))
    monkeypatch.setattr("sci_cli.auth_codex_browser.codex_oauth_login", lambda args: {
        "tokens": {"access_token": access, "refresh_token": "fresh-fixture"}})
    before = {h / "config.yaml": (h / "config.yaml").read_bytes() for h in homes}
    with profile_scope(a):
        args = SimpleNamespace(provider="openai-codex", auth_type="oauth", browser=False)
        if case == "cancel":
            auth_add_command(args)
        else:
            with pytest.raises(SystemExit, match="Login failed"):
                auth_add_command(args)
    assert all(p.read_bytes() == value for p, value in before.items())
    assert "authentication verified" not in capsys.readouterr().out
    assert not auth._load_auth_store(main / "auth.json").get("providers", {}).get("openai-codex")
