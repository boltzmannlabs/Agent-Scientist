"""/Add_tool and /Add_mcp are ordinary user-turn shortcuts, not installers."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock
import threading

import pytest
from prompt_toolkit.buffer import Buffer

from cli import SciCLI


def make_cli():
    instance = SciCLI.__new__(SciCLI)
    instance._pending_agent_seed = None
    instance._pending_resume_sessions = None
    instance._agent_running = False
    instance._voice_lock = threading.Lock()
    instance._voice_mode = instance._voice_continuous = False
    instance._app = SimpleNamespace(current_buffer=Buffer(), invalidate=Mock(), is_running=True)
    instance.agent = SimpleNamespace(system_prompt="byte-stable", tools=["terminal", "read_file"])
    instance.conversation_history = [{"role": "user", "content": "previous"}, {"role": "assistant", "content": "response"}]
    instance._turn_summary_begin = Mock()
    instance._tui_after_turn = Mock()
    instance._print_user_message_preview = Mock()
    instance.chat = Mock()
    instance._clarify_callback = Mock(side_effect=AssertionError("No wizard"))
    return instance


@pytest.mark.parametrize("command,kind", [("Add_tool", "tool"), ("Add_mcp", "MCP server")])
@pytest.mark.parametrize("case", ["original", "lower", "upper"])
@pytest.mark.parametrize("tool_request,expected", [
    ("add this tool:https://github.com/bio-tools/biotoolsLLMAnnotate", "add this tool:https://github.com/bio-tools/biotoolsLLMAnnotate"),
    ("https://github.com/Author/Project", "add this tool: https://github.com/Author/Project"),
    ('Install this tool from "/tmp/Project Folder"\nInspect its README first.', 'Install this tool from "/tmp/Project Folder"\nInspect its README first.'),
    ("/tmp/Project", "/tmp/Project"),
    ("!echo this is text", "!echo this is text"),
])
def test_request_reaches_normal_chat_once_without_altering_prompt_or_tools(command, kind, case, tool_request, expected):
    from sci_cli.commands import COMMANDS, resolve_command
    spelling = "/" + (command if case == "original" else getattr(command, case)())
    if tool_request.startswith("https://"):
        expected = f"add this {kind}: " + tool_request
    instance = make_cli()
    before = deepcopy((vars(instance.agent), instance.conversation_history))
    assert "/" + command in COMMANDS
    assert resolve_command(spelling).subcommands == ()
    # Drive the real input loop, command dispatcher and one-shot seed consumer.
    # Only chat itself is controlled: the test must never download/install code.
    instance._tui_process_one_input(spelling + " " + tool_request)
    instance.chat.assert_called_once_with(expected, images=None, voice_input=False)
    instance._print_user_message_preview.assert_called_once_with(expected)
    instance._clarify_callback.assert_not_called()
    assert instance._pending_agent_seed is None
    assert (vars(instance.agent), instance.conversation_history) == before


@pytest.mark.parametrize("command,kind", [("Add_tool", "tool"), ("Add_mcp", "MCP server")])
@pytest.mark.parametrize("draft", ["", "my unfinished request"])
def test_bare_command_prefills_only_empty_composer_and_waits_for_normal_submission(command, kind, draft, capsys):
    instance = make_cli()
    instance._app.current_buffer.text = draft
    instance._tui_process_one_input("/" + command)
    assert instance._app.current_buffer.text == (draft or f"add this {kind}: ")
    instance.chat.assert_not_called()
    instance._clarify_callback.assert_not_called()
    assert instance._pending_agent_seed is None
    assert f"Type your {kind} request and link" in capsys.readouterr().out
    # No armed wizard state: the next normal message is just a normal chat turn.
    message = f"add this {kind}:https://github.com/author/project"
    instance._tui_process_one_input(message)
    instance.chat.assert_called_once_with(message, images=None, voice_input=False)


@pytest.mark.parametrize("entry,source_kind", [
    ("inline", "url"), ("inline", "file"), ("inline", "folder"),
    ("inline", "request"), ("inline", "windows"),
    ("link", "url"), ("file", "file"), ("file", "folder"),
    ("file", "zip"), ("other", "url"), ("other", "identifier"),
    ("cancel", "url"), ("handoff_cancel", "url"),
])
@pytest.mark.parametrize("spelling", ["/Add_skill", "/add_skill", "/ADD_SKILL"])
def test_skill_sources_reach_normal_chat_without_reading_or_drafting(tmp_path, monkeypatch, entry, source_kind, spelling):
    from sci_cli import skill_add, skill_add_sources

    folder = tmp_path / "Research Skill Collection"
    folder.mkdir()
    source = folder / "notes.md"
    source.write_text("Scientific source material.\n" * 6000)
    values = {
        "url": "https://github.com/BioTender-max/awesome-bio-agent-skills",
        "file": f'"{source}"', "folder": f'"{folder}"', "zip": f'"{folder / "skill.zip"}"',
        "identifier": "owner/repository/path/to/skill",
        "request": "Install this skill from https://example.org/SKILL.md; don't replace existing skills.",
        "windows": r'"C:\Research Folder\sample skill"',
    }
    value = values[source_kind]
    instance = make_cli()
    before = deepcopy((vars(instance.agent), instance.conversation_history))
    draft = Mock(side_effect=AssertionError("Only Describe a workflow may draft"))
    download = Mock(side_effect=AssertionError("Slash dispatch must not fetch source material"))
    monkeypatch.setattr(skill_add, "prepare_route", draft)
    monkeypatch.setattr(skill_add_sources, "remote_source", download)
    choices = {"link": "Paste a link", "file": "Provide a file/folder", "other": value, "cancel": "Cancel"}
    answers = [choices[entry], value] if entry in {"link", "file"} else [choices.get(entry, value)]
    if entry != "inline":
        instance._clarify_callback = Mock(side_effect=[
            {"outcome": "submitted", "answers": {"skill_add": answer}} for answer in answers])
    if entry == "handoff_cancel":
        import cli as cli_module
        render = cli_module._cprint

        def cancel_handoff(text):
            if "HANDED TO AGENT" in text:
                raise KeyboardInterrupt()
            render(text)

        monkeypatch.setattr(cli_module, "_cprint", cancel_handoff)
    instance._tui_process_one_input(spelling + (" " + value if entry == "inline" else ""))
    if entry in {"cancel", "handoff_cancel"}:
        instance.chat.assert_not_called()
        assert instance._pending_agent_seed is None
        assert (vars(instance.agent), instance.conversation_history) == before
        draft.assert_not_called()
        download.assert_not_called()
        return
    instance.chat.assert_called_once()
    request = instance.chat.call_args.args[0]
    assert request.startswith("add this skill:") and value in request
    assert "already exists" in request and "do not overwrite" in request.lower()
    assert "next session" in request and "collection" in request.lower()
    assert instance._pending_agent_seed is None
    assert (vars(instance.agent), instance.conversation_history) == before
    draft.assert_not_called()
    download.assert_not_called()
    if entry == "inline":
        instance._clarify_callback.assert_not_called()
    else:
        assert instance._clarify_callback.call_count == (2 if entry in {"link", "file"} else 1)
    assert not list(folder.glob("**/SKILL.md"))
