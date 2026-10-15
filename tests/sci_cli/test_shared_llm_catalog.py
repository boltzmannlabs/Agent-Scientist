"""Shared inference providers must resolve without sharing project state or secrets."""

from pathlib import Path

import pytest


@pytest.fixture
def homes(tmp_path, monkeypatch):
    from sci_cli.config import atomic_config_replace
    from agent.secret_scope import set_multiplex_active

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    main = tmp_path / "science-root"
    a, b = main / "profiles" / "a", main / "profiles" / "b"
    for home in (main, a, b):
        home.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("SCI_HOME", str(main))
    atomic_config_replace(main / "config.yaml", {
        "model": {"provider": "custom:lab", "default": "lab-model"},
        "providers": {"pooled": {"base_url": "http://127.0.0.1:54321/v1", "models": ["pool-model"]}},
        "custom_providers": [{"name": "lab", "base_url": "http://127.0.0.1:54322/v1",
                              "api_key": "${LAB_KEY}", "models": ["lab-model"]}],
        "mcp_servers": {"private-research": {"url": "https://research.invalid"}},
        "terminal": {"cwd": "/main-only"},
        "model_catalog": {"excluded_providers": ["copilot-acp"]},
    })
    (main / ".env").write_text(
        "LAB_KEY=main-lab-fixture\nOPENROUTER_API_KEY=sk-or-v1-main-fixture\nBOLTZMANN_API_KEY=private-main\n")
    for home in (a, b):
        atomic_config_replace(home / "config.yaml", {
            "model": {"provider": "openai-codex", "default": "profile-model"},
            "terminal": {"cwd": str(home / "workspace")},
            "mcp_servers": {},
        })
    (b / ".env").write_text("OPENROUTER_API_KEY=sk-or-v1-profile-b-fixture\nBOLTZMANN_API_KEY=private-b\n")
    set_multiplex_active(True)
    try:
        yield main, a, b
    finally:
        set_multiplex_active(False)


def test_shared_catalog_and_runtime_a_b_a_without_copying_secrets(homes, monkeypatch):
    from sci_cli.native_profile_creation import profile_scope
    from sci_cli.inventory import load_picker_context, build_models_payload
    from sci_cli.auth import write_credential_pool
    from agent.credential_pool import PooledCredential
    from sci_cli.runtime_provider import resolve_runtime_provider
    from sci_cli import model_switch_providers as picker
    from sci_cli.shared_llm import provider_config
    from sci_cli.config import load_config
    from agent.secret_scope import get_secret_str

    main, a, b = homes
    before = {p: p.read_bytes() for home in homes for p in (home / "config.yaml", home / ".env") if p.exists()}
    with profile_scope(main):
        row = PooledCredential(provider="pooled", id="pool-fixture", label="fixture", auth_type="api_key",
                               priority=0, source="manual", access_token="main-pool-fixture",
                               base_url="http://127.0.0.1:54321/v1")
        write_credential_pool("pooled", [row.to_dict()])

    # Only catalog/network discovery is controlled. Config, secret scopes, provider
    # matching and credential-pool resolution exercise their real implementations.
    monkeypatch.setattr("agent.models_dev.fetch_models_dev", lambda **kw: {
        "openrouter": {"name": "OpenRouter", "env": ["OPENROUTER_API_KEY"], "models": {}}})
    monkeypatch.setattr(picker, "_build_curated_lists", lambda *a, **kw: {"openrouter": ["or-model"]})
    monkeypatch.setattr(picker, "_live_or_curated_ids", lambda slug, *a, **kw: ["or-model"])
    monkeypatch.setattr(picker, "_collect_authed_provider_slugs", lambda *a, **kw: [])
    monkeypatch.setattr(picker, "_lap_overlay_rows", lambda *a: None)
    monkeypatch.setattr(picker, "_lap_canonical_rows", lambda *a: None)
    monkeypatch.setattr(picker, "_discover_endpoint_models", lambda *a, **kw: (None, False))
    for home in (main, a, b, a):
        with profile_scope(home):
            ctx = load_picker_context()
            payload = build_models_payload(ctx, probe_custom_providers=False)
            names = {p["name"] for p in payload["providers"]}
            assert {"pooled", "lab"} <= names
            assert "openrouter" in {p["slug"] for p in payload["providers"]}
            assert ctx.current_model == ("lab-model" if home == main else "profile-model")
            assert resolve_runtime_provider(requested="custom:lab")["api_key"] == "main-lab-fixture"
            assert resolve_runtime_provider(requested="pooled")["api_key"] == "main-pool-fixture"
            runtime = resolve_runtime_provider(requested="openrouter")
            assert runtime["api_key"] == ("sk-or-v1-profile-b-fixture" if home == b else "sk-or-v1-main-fixture"), home.name
            pool = runtime.get("credential_pool")
            if pool is not None:
                assert pool.select().access_token == runtime["api_key"]
            view = provider_config(load_config())
            if home != main:
                assert view["mcp_servers"] == {}
                assert view["terminal"]["cwd"] == str(home / "workspace")
                assert get_secret_str("LAB_KEY", "") == ""
                assert get_secret_str("BOLTZMANN_API_KEY", "") == ("private-b" if home == b else "")
    assert all(p.read_bytes() == contents for p, contents in before.items())
    for home in (a, b):
        text = (home / "auth.json").read_text() if (home / "auth.json").exists() else ""
        assert all(secret not in text for secret in ("main-pool-fixture", "sk-or-v1-main-fixture", "main-lab-fixture"))


def test_local_provider_overrides_and_exclusions_remain_authoritative(homes):
    from sci_cli.config import atomic_config_replace, read_user_config_raw
    from sci_cli.native_profile_creation import profile_scope
    from sci_cli.inventory import load_picker_context
    from sci_cli.runtime_provider import resolve_runtime_provider
    from sci_cli.auth import write_credential_pool
    from agent.credential_pool import PooledCredential

    main, a, b = homes
    config = read_user_config_raw(b / "config.yaml")
    config["custom_providers"] = [{"name": "lab", "base_url": "http://127.0.0.1:54323/v1",
                                    "api_key": "profile-b-lab", "models": ["b-model"]}]
    config["providers"] = {"pooled": {"enabled": False}}
    config["model_catalog"] = {"excluded_providers": ["anthropic"]}
    atomic_config_replace(b / "config.yaml", config)
    with profile_scope(main):
        row = PooledCredential(provider="custom:lab", id="fixture", label="fixture", auth_type="api_key",
                               priority=0, source="manual", access_token="main-lab-fixture",
                               base_url="http://127.0.0.1:54322/v1")
        write_credential_pool("custom:lab", [row.to_dict()])
    for home, key in [(a, "main-lab-fixture"), (b, "profile-b-lab"), (a, "main-lab-fixture")]:
        with profile_scope(home):
            assert resolve_runtime_provider(requested="custom:lab")["api_key"] == key
            if home == b:
                assert set(load_picker_context().excluded_providers) == {"copilot-acp", "anthropic"}
                with pytest.raises(ValueError, match="disabled"):
                    resolve_runtime_provider(requested="pooled")
