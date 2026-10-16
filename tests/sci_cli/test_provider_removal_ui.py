"""The visible removal row and /model remove share one profile-bound backend."""

import threading
from types import SimpleNamespace
import pytest

from cli import SciCLI
from sci_cli import provider_removal as removal
from sci_cli.native_profile_creation import profile_scope
from sci_constants import get_sci_home


def test_picker_action_and_quoted_command_use_same_scoped_worker(tmp_path, monkeypatch):
    main = tmp_path / "main"
    active = main / "profiles" / "a"
    active.mkdir(parents=True)
    monkeypatch.setenv("SCI_HOME", str(main))
    calls, done = [], threading.Event()

    def run(cli, requested="", rows=()):
        calls.append((get_sci_home(), requested, rows, threading.current_thread()))
        done.set()

    monkeypatch.setattr(removal, "run", run)
    rows = [{"slug": "fixture", "name": "Fixture", "models": ["one"], "is_current": False}]
    cli = SimpleNamespace(_app=object(), _model_picker_state={"stage": "provider", "providers": rows, "selected": 0})
    cli._close_model_picker = lambda: setattr(cli, "_model_picker_state", None)
    rendered = []
    cli._render_scroll_list_panel = lambda state, title, hint, choices, **kw: rendered.extend(choices)
    SciCLI._get_model_picker_display_fragments(cli)
    assert "Remove provider…" in rendered
    event = SimpleNamespace(app=SimpleNamespace(invalidate=lambda: None))
    with profile_scope(active):
        SciCLI._tui_model_picker_down(cli, event)
        assert rendered[cli._model_picker_state["selected"]] == "Remove provider…"
        SciCLI._handle_model_picker_selection(cli)
        assert done.wait(5)
        assert calls[-1][:3] == (active, "", rows)
        assert calls[-1][3] is not threading.current_thread()
        done.clear()
        SciCLI._handle_model_switch(cli, '/model remove "My Lab"')
        assert done.wait(5)
        assert calls[-1][:2] == (active, "My Lab")
    # The last row remains Cancel, never a destructive action.
    cli._model_picker_state = {"stage": "provider", "providers": rows, "selected": len(rows)}
    SciCLI._tui_model_picker_down(cli, event)
    assert rendered[cli._model_picker_state["selected"]] == "Cancel"
    count = len(calls)
    SciCLI._handle_model_picker_selection(cli)
    assert cli._model_picker_state is None and len(calls) == count


def test_closed_modal_and_invalid_commands_cannot_write_or_probe(tmp_path, monkeypatch):
    from sci_cli.config import atomic_config_replace
    import cli as cli_module

    home = tmp_path / "sci"
    home.mkdir()
    monkeypatch.setenv("SCI_HOME", str(home))
    path = home / "config.yaml"
    atomic_config_replace(path, {"model": {"provider": "openrouter", "default": "fixture"}})
    before = path.read_bytes()
    messages = []
    monkeypatch.setattr(cli_module, "_cprint", messages.append)
    cli = SimpleNamespace(_app=SimpleNamespace(is_running=True), provider="openrouter", base_url="",
                          _clarify_callback=lambda questions: {"outcome": "cancelled", "answers": {}})
    with profile_scope(home):
        removal.run(cli, "anthropic")
        assert "cancelled" in messages[-1]
        assert removal.dispatch(cli, 'remove "unfinished')
        assert removal.dispatch(cli, 'remove one two')
        assert not removal.dispatch(cli, "some-model")
    assert path.read_bytes() == before
    assert not (home / "auth.json").exists() and not (home / "backups").exists()
    # Controlled terminal walkthrough through the actual clarify adapter, not
    # the fake UI: removing a built-in disables selection without uninstalling code.
    answers = iter(["Delete provider definitions in main and all profiles", "Confirm removal"])
    cli._clarify_callback = lambda questions: {"outcome": "submitted", "answers": {"skill_add": next(answers)}}
    with profile_scope(home):
        removal.run(cli, "anthropic")
        from sci_cli.runtime_provider import resolve_runtime_provider
        assert any("Provider removed:" in message for message in messages), messages
        with pytest.raises(ValueError, match="disabled"):
            resolve_runtime_provider(requested="anthropic")
    assert any("Provider removed: Anthropic" in message for message in messages)
    assert not (home / "auth.json").exists()
