"""Validated secret capture must preserve credentials and conversation state."""

from pathlib import Path
from types import SimpleNamespace

from sci_cli.callbacks import prompt_for_secret
from sci_cli.config import load_env, save_env_value
from sci_cli.plugins import PluginContext, PluginManager
from sci_cli.plugins_manifest import PluginManifest


def test_validated_capture_preserves_keys_on_failure_and_cancel(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(tmp_path / "profile"))
    save_env_value("TEST_ONBOARDING_API_KEY", "previous")
    cli = SimpleNamespace()
    for value in ("invalid", "", "accepted"):
        monkeypatch.setattr("sci_cli.callbacks.masked_secret_prompt", lambda _: value)
        result = prompt_for_secret(cli, "TEST_ONBOARDING_API_KEY", "API key",
                                   validator=lambda value: value == "accepted")
        expected = "accepted" if value == "accepted" else "previous"
        assert load_env()["TEST_ONBOARDING_API_KEY"] == expected
        assert result["validated"] == (value == "accepted")
        assert value == "" or value not in str(result)
    assert (tmp_path / "profile" / ".env").stat().st_mode & 0o077 == 0
    captured = capsys.readouterr()
    assert "accepted" not in captured.out + captured.err


def test_onboarding_context_defers_refresh_and_refuses_remote_secret_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(tmp_path / "profile"))
    manager = PluginManager()
    ctx = PluginContext(PluginManifest(name="example", key="example", source="user"), manager)
    assert not ctx.prompt_secret("EXAMPLE_API_KEY", "Key")["success"]
    assert not ctx.refresh_tools(now=True)
    agent = SimpleNamespace(tools=[{"cached": "prefix"}], system_prompt="unchanged")
    manager._cli_ref = SimpleNamespace(agent=agent, conversation_history=[{"role": "user", "content": "hello"}])
    assert not ctx.refresh_tools()
    assert agent.tools == [{"cached": "prefix"}]
    assert agent.system_prompt == "unchanged"
    monkeypatch.setenv("SCI_HOME", str(tmp_path / "other"))
    import pytest
    with pytest.raises(RuntimeError, match="owning profile"):
        ctx.prompt_secret("EXAMPLE_API_KEY", "Key")
