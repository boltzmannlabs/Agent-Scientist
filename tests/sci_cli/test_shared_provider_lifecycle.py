"""Shared additions and remove/re-add must preserve each profile's research state."""

from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from sci_cli.config import atomic_config_replace, read_user_config_raw
from sci_cli.native_profile_creation import profile_scope


@pytest.fixture
def homes(tmp_path, monkeypatch):
    from agent.secret_scope import set_multiplex_active
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    main = tmp_path / "science-root"
    monkeypatch.setenv("SCI_HOME", str(main))
    owners = main, main / "profiles" / "a", main / "profiles" / "b"
    for home in owners:
        home.mkdir(parents=True)
        atomic_config_replace(home / "config.yaml", {
            "model": {"provider": "openrouter", "default": "old-model"},
            "auxiliary": {"title_generation": {"provider": "openrouter", "model": "old-title", "timeout": 19}},
            "terminal": {"cwd": str(home / "workspace")}, "skills": {"disabled": ["private"]},
            "mcp_servers": {"lab": {"url": "https://research.invalid"}},
        })
        (home / ".env").write_text("BOLTZMANN_API_KEY=private-science-key\n")
        (home / "SOUL.md").write_text("Profile persona: " + home.name)
        (home / "sessions").mkdir()
        (home / "sessions" / "chat.json").write_text('{"messages": [{"role": "user", "content": "private chat"}]}')
    set_multiplex_active(True)
    try:
        yield owners
    finally:
        set_multiplex_active(False)


class UI:
    def __init__(self):
        self.messages = []

    def choose(self, question, choices):
        if question == "Choose removal scope:":
            return "Delete provider definitions in main and all profiles"
        if "After removal:" in question:
            return "Leave unconfigured" if "title_generation" in question else "Choose a replacement provider/model"
        return "Confirm removal"

    def ask(self, question):
        return "lmstudio" if "provider ID" in question else "fixture-local-model"

    def show(self, text):
        self.messages.append(text)


def test_remove_readd_from_profile_restores_shared_inventory_and_keeps_selections(homes, monkeypatch):
    from sci_cli.provider_removal import run
    from sci_cli.auth_commands import auth_add_command
    from sci_cli.runtime_provider import resolve_runtime_provider
    from sci_cli.shared_llm import provider_config
    from sci_cli.config import load_config
    from sci_cli import auth

    main, a, b = homes
    private = {path: path.read_bytes() for h in homes for path in
               (h / ".env", h / "SOUL.md", h / "sessions" / "chat.json")}
    live = SimpleNamespace(provider="lmstudio", model="fixture-local-model", base_url="",
                           agent=SimpleNamespace(provider="openrouter", system_prompt="cached-prefix", tools=["unchanged"]),
                           conversation_history=[{"role": "user", "content": "kept"}])
    baseline = deepcopy(vars(live))
    ui = UI()
    with profile_scope(a):
        run(live, "openrouter", ui=ui)
    assert any("Provider removed:" in msg for msg in ui.messages), ui.messages
    selections = {}
    for home in (main, a, b, a):
        with profile_scope(home):
            raw = read_user_config_raw(home / "config.yaml")
            assert raw["model"] == {"provider": "lmstudio", "default": "fixture-local-model"}
            assert raw["auxiliary"]["title_generation"] == {"provider": "unconfigured", "timeout": 19}
            with pytest.raises(ValueError, match="disabled"):
                resolve_runtime_provider(requested="openrouter")
            from sci_cli.shared_provider_lifecycle import enforce_runtime_access, ProviderRemovedError
            from agent.error_classifier import classify_api_error
            with pytest.raises(ProviderRemovedError) as stopped:
                enforce_runtime_access("openrouter")
            verdict = classify_api_error(stopped.value, provider="openrouter")
            assert not verdict.retryable and not verdict.should_fallback and not verdict.should_rotate_credential
            from agent.turn_api_call import perform_api_call
            with pytest.raises(ProviderRemovedError):
                perform_api_call(live.agent, api_kwargs={}, _original_api_kwargs={}, _llm_middleware_trace=None,
                                 _moa_prepared_request=None, _retry=None, thinking_spinner=None, retry_count=0,
                                 api_call_count=0, api_request_id="fixture", effective_task_id="fixture",
                                 turn_id="fixture", interrupted=False)
            selections[home] = raw["model"]
    monkeypatch.setattr("sci_cli.auth_commands.sys.stdin.isatty", lambda: False)
    with profile_scope(b):
        auth_add_command(SimpleNamespace(provider="openrouter", api_key="sk-or-v1-shared-fixture", auth_type="api_key", label="fixture"))
    for home in (main, a, b, a):
        with profile_scope(home):
            view = provider_config(load_config())
            assert "openrouter" not in view["model_catalog"]["excluded_providers"]
            assert read_user_config_raw(home / "config.yaml")["model"] == selections[home]
            assert resolve_runtime_provider(requested="openrouter")["api_key"] == "sk-or-v1-shared-fixture"
            if home != main:
                store = auth._load_auth_store()
                assert not store.get("credential_pool", {}).get("openrouter")
    assert all(path.read_bytes() == data for path, data in private.items())
    assert vars(live) == baseline


@pytest.mark.parametrize("schema", ["providers", "custom_providers"])
def test_profile_endpoint_addition_publishes_only_llm_definition_and_preserves_other_settings(homes, schema):
    from sci_cli.shared_provider_lifecycle import publish
    from sci_cli.runtime_provider import resolve_runtime_provider
    from sci_cli.config import save_env_value
    from agent.secret_scope import get_secret_str

    main, a, b = homes
    original = {h: read_user_config_raw(h / "config.yaml") for h in homes}
    entry = {"name": "lab-models", "base_url": "http://127.0.0.1:54321/v1", "key_env": "SCI_LAB_LLM_API_KEY", "models": ["lab-fixture"]}
    config = deepcopy(original[a])
    config[schema] = {"lab-models": entry} if schema == "providers" else [entry]
    atomic_config_replace(a / "config.yaml", config)
    provider = "lab-models" if schema == "providers" else "custom:lab-models"
    with profile_scope(a):
        save_env_value("SCI_LAB_LLM_API_KEY", "shared-endpoint-fixture")
        publish(provider)
    for h in (main, a, b, a):
        with profile_scope(h):
            assert resolve_runtime_provider(requested=provider)["api_key"] == "shared-endpoint-fixture"
            from sci_cli.main_provider_setup import _named_custom_provider_map
            from sci_cli.config import load_config
            info = _named_custom_provider_map(load_config())["custom:lab-models"]
            assert info["key_env"] == "SCI_LAB_LLM_API_KEY"
            assert info["api_key"] == "shared-endpoint-fixture" if h != main else not info["api_key"]
            raw = read_user_config_raw(h / "config.yaml")
            for key in ("model", "terminal", "auxiliary", "skills", "mcp_servers"):
                assert raw[key] == original[h][key]
            assert get_secret_str("BOLTZMANN_API_KEY") == "private-science-key"
            if h != main:
                assert not raw.get(schema)
