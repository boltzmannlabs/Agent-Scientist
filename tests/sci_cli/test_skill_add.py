"""Guided skills use explicit consent and the real profile-scoped install path."""

import copy
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from cli import SciCLI
from sci_cli import skill_add as wizard
from sci_cli.skill_add_sources import Source, bundle_from_files, load_source
from sci_cli.skill_add_draft import DraftRoute


SKILL = "---\nname: lab-summary\ndescription: Summarize research inputs.\n---\n# Summary\nReview inputs and report limitations.\n"


class ScriptUI:
    def __init__(self, answers):
        self.answers = iter(answers)
        self.output = []
        self.questions = []

    def show(self, text):
        self.output.append(str(text))

    def ask(self, question, choices=()):
        self.questions.append(question)
        answer = next(self.answers)
        if answer is None:
            raise wizard.Cancelled()
        return answer

    def choose(self, question, choices):
        answer = self.ask(question)
        assert answer in choices, (answer, choices)
        if answer == "Cancel":
            raise wizard.Cancelled()
        return answer


def cli_fixture():
    return SimpleNamespace(_agent_running=False, provider="fixture", model="fixture-model",
                           api_key=None, base_url=None, history=[{"role": "user", "content": "hello"}],
                           agent=SimpleNamespace(system_prompt="cached scientific prompt", tools=["read_file"]))


def source_folder(tmp_path):
    folder = tmp_path / "source with spaces"
    folder.mkdir()
    (folder / "SKILL.md").write_text(SKILL)
    (folder / "references").mkdir()
    (folder / "references" / "guide.md").write_text("Check missing values.\n")
    return folder


@pytest.fixture
def multiplex_scope():
    from agent.secret_scope import set_multiplex_context, reset_multiplex_context
    token = set_multiplex_context(True)
    try:
        yield
    finally:
        reset_multiplex_context(token)


def test_command_resolves_dispatches_and_completes(monkeypatch):
    from sci_cli.commands import resolve_command, COMMANDS
    from sci_cli.commands_completion import SlashCommandCompleter
    from prompt_toolkit.document import Document
    from prompt_toolkit.completion import CompleteEvent

    invoked = Mock()
    monkeypatch.setattr(wizard, "run_add_skill", invoked)
    cli = SciCLI.__new__(SciCLI)
    for spelling in ("/Add_skill", "/add_skill", "/ADD_SKILL"):
        definition = resolve_command(spelling)
        handler, takes_arg = cli._slash_handler(definition.name)
        assert takes_arg
        getattr(cli, handler)(spelling)
        invoked.assert_called_with(cli, spelling)
    assert "/Add_skill" in COMMANDS
    completions = list(SlashCommandCompleter().get_completions(
        Document("/Add_"), CompleteEvent(completion_requested=True)))
    # The completer replaces the word after '/', leaving the slash in place.
    assert any("/Add_"[:len("/Add_") + c.start_position] + c.text == "/Add_skill"
               for c in completions)


def test_existing_modal_adapter_and_literal_safe_preview(monkeypatch):
    import cli as cli_module
    output = Mock()
    monkeypatch.setattr(cli_module, "_cprint", output)
    callback = Mock(return_value={"outcome": "submitted", "answers": {"skill_add": "Save"}})
    ui = wizard.WizardUI(SimpleNamespace(_app=SimpleNamespace(is_running=True), _clarify_callback=callback))
    ui.show("[Guide](references/guide.md)\x1b[2J")
    output.assert_called_once_with("[Guide](references/guide.md)[2J")
    assert ui.choose("Review", ("Save", "Cancel")) == "Save"
    assert callback.call_args.args[0][0]["choices"] == ["Save", "Cancel"]
    callback.return_value = {"outcome": "cancelled", "answers": {}}
    with pytest.raises(wizard.Cancelled):
        ui.ask("Question")


def test_real_import_enablement_and_profile_isolation(tmp_path, monkeypatch, multiplex_scope):
    from sci_constants import set_sci_home_override, reset_sci_home_override
    from sci_cli.config import read_user_config_raw
    from tools.skills_hub import HubLockFile
    from tools.skills_tool import _find_all_skills
    from agent.secret_scope import set_secret_scope, reset_secret_scope
    from agent.prompt_builder import build_skills_system_prompt, _SKILLS_PROMPT_CACHE
    from tools.environments.local import served_profile_child_env
    folder = source_folder(tmp_path)
    homes = [tmp_path / "home-a", tmp_path / "home-b"]
    for home in homes:
        home.mkdir()
        (home / "config.yaml").write_text(
            "# preserve me\nmodel:\n  default: unchanged\nskills:\n"
            "  disabled: [lab-summary, other-skill]\n"
            "  platform_disabled:\n    cli: [lab-summary, cli-only]\n    telegram: [lab-summary]\n")
    cli = cli_fixture()
    cli.agent._cached_system_prompt = "Byte-stable prompt\n  exact spacing\n"
    before = copy.deepcopy(vars(cli))
    for home in homes:
        token = set_sci_home_override(home)
        secret_token = set_secret_scope({}, profile_home=str(home))
        try:
            # Seed a real cached skill index; installing must not rebuild it.
            (home / "skills").mkdir(exist_ok=True)
            build_skills_system_prompt()
            cached = dict(_SKILLS_PROMPT_CACHE)
            ui = ScriptUI(["Save", "Save and enable for the next session"])
            source = load_source(str(folder))
            wizard.review(cli, ui, source.bundle, source, "")
            installed = home / "skills" / "lab-summary"
            assert (installed / "SKILL.md").read_bytes() == (folder / "SKILL.md").read_bytes(), ui.output
            assert (installed / "references/guide.md").read_text() == "Check missing values.\n"
            assert HubLockFile().get_installed("lab-summary")
            cfg = read_user_config_raw()
            assert cfg["skills"]["disabled"] == ["other-skill"]
            assert cfg["skills"]["platform_disabled"] == {"cli": ["cli-only"], "telegram": ["lab-summary"]}
            assert cfg["model"]["default"] == "unchanged"
            assert "# preserve me" in (home / "config.yaml").read_text()
            assert any(s["name"] == "lab-summary" for s in _find_all_skills())
            assert any("Enabled. Available automatically in your next session." in line for line in ui.output)
            # Wizard status is CLI-local; live agent/history/config are untouched.
            assert {k: v for k, v in vars(cli).items() if k != "_skill_add_statuses"} == before
            assert dict(_SKILLS_PROMPT_CACHE) == cached
            fresh = subprocess.run([sys.executable, "-c",
                "from agent.prompt_builder import build_skills_system_prompt; print(build_skills_system_prompt())"],
                env=served_profile_child_env(target_home=home), capture_output=True, text=True, timeout=30)
            assert fresh.returncode == 0, fresh.stderr
            assert "lab-summary" in fresh.stdout
        finally:
            reset_secret_scope(secret_token)
            reset_sci_home_override(token)
    token = set_sci_home_override(homes[0])
    secret_token = set_secret_scope({}, profile_home=str(homes[0]))
    try:
        assert HubLockFile().get_installed("lab-summary")
        ui = ScriptUI(["Save", "Cancel"])
        source = load_source(str(folder))
        with pytest.raises(wizard.Cancelled):
            wizard.review(cli, ui, source.bundle, source, "")
        assert any("already exists" in line for line in ui.output)
        assert (homes[0] / "skills/lab-summary/SKILL.md").read_text() == SKILL
    finally:
        reset_secret_scope(secret_token)
        reset_sci_home_override(token)


@pytest.mark.parametrize("answers", [["Cancel"], ["Save", "Cancel"]])
def test_cancel_never_installs(tmp_path, answers):
    from sci_constants import get_skills_dir
    folder = source_folder(tmp_path)
    ui = ScriptUI(answers)
    source = load_source(str(folder))
    with pytest.raises(wizard.Cancelled):
        wizard.review(cli_fixture(), ui, source.bundle, source, "")
    assert not (get_skills_dir() / "lab-summary").exists()


def test_draft_consent_revision_and_tool_free_provider_call(tmp_path, monkeypatch):
    from sci_constants import get_skills_dir
    response = SimpleNamespace(choices=[SimpleNamespace(finish_reason="stop",
        message=SimpleNamespace(content=json.dumps({"SKILL.md": SKILL}), tool_calls=None))])
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=Mock(return_value=response))))
    routes = []
    def prepare(cli):
        routes.append("prepared")
        return DraftRoute(client, "fixture", "fixture-model", "local fixture", 131072)
    monkeypatch.setattr(wizard, "prepare_route", prepare)
    cancelled = ScriptUI(["Describe a workflow", "Summarize", "CSV", "Report", "Research only", "Cancel"])
    wizard.run_add_skill(cli_fixture(), '/Add_skill', ui=cancelled)
    client.chat.completions.create.assert_not_called()
    ui = ScriptUI(["Describe a workflow", "Summarize", "CSV", "Report", "Research only", "Approve this draft",
                   "Revise with model", "Mention missing data", "Approve this draft",
                   "Edit", "SKILL.md", "Replace text", "Review inputs", "Review input completeness",
                   "Save", "Save and enable for the next session"])
    wizard.run_add_skill(cli_fixture(), '/Add_skill', ui=ui)
    calls = client.chat.completions.create.call_args_list
    assert len(calls) == 2, ui.output
    assert sum("Send this material" in q for q in ui.questions) == 2
    assert all(c.kwargs["tools"] == [] and c.kwargs["model"] == "fixture-model" for c in calls)
    assert all([m["role"] for m in c.kwargs["messages"]] == ["system", "user"] for c in calls)
    assert "Mention missing data" in calls[1].kwargs["messages"][-1]["content"]
    assert "Review input completeness" in (get_skills_dir() / "lab-summary/SKILL.md").read_text()


def test_unsafe_scan_and_enablement_failure_reported(tmp_path, monkeypatch):
    from sci_constants import get_skills_dir
    from sci_cli import skill_add_store
    folder = source_folder(tmp_path)
    import tools.skills_guard as guard
    real_scan = guard.scan_skill
    def dangerous(*args, **kwargs):
        result = real_scan(*args, **kwargs)
        result.verdict = "dangerous"
        return result
    monkeypatch.setattr(guard, "scan_skill", dangerous)
    ui = ScriptUI(["Save", "Cancel"])
    source = load_source(str(folder))
    with pytest.raises(wizard.Cancelled):
        wizard.review(cli_fixture(), ui, source.bundle, source, "")
    assert not (get_skills_dir() / "lab-summary").exists()
    monkeypatch.setattr(guard, "scan_skill", real_scan)
    monkeypatch.setattr(skill_add_store, "enable_next_session", Mock(side_effect=OSError("fixture")))
    ui = ScriptUI(["Save", "Save and enable for the next session"])
    wizard.review(cli_fixture(), ui, source.bundle, source, "")
    assert (get_skills_dir() / "lab-summary").exists()
    assert any("enablement failed" in s for s in ui.output)
    assert not any("Enabled. Available" in s for s in ui.output)


def test_duplicate_rename_and_failed_install_rollback(tmp_path, monkeypatch):
    from tools.skills_hub import HubLockFile
    from sci_constants import get_skills_dir
    folder = source_folder(tmp_path)
    first = ScriptUI(["Save", "Save and enable for the next session"])
    source = load_source(str(folder))
    wizard.review(cli_fixture(), first, source.bundle, source, "")
    renamed = ScriptUI(["Save", "Rename", "lab-summary-new", "Save", "Save and enable for the next session"])
    wizard.review(cli_fixture(), renamed, source.bundle, source, "")
    assert (get_skills_dir() / "lab-summary/SKILL.md").read_text() == SKILL
    assert "name: lab-summary-new" in (get_skills_dir() / "lab-summary-new/SKILL.md").read_text()
    monkeypatch.setattr(HubLockFile, "record_install", Mock(side_effect=OSError("fixture disk failure")))
    failed = ScriptUI(["Rename", "lab-summary-failed", "Save", "Save and enable for the next session"])
    with pytest.raises(OSError, match="fixture disk failure"):
        wizard.review(cli_fixture(), failed, source.bundle, source, "")
    assert not (get_skills_dir() / "lab-summary-failed").exists()
    assert not HubLockFile().get_installed("lab-summary-failed")
    assert not any("Enabled. Available" in s for s in failed.output)


@pytest.mark.parametrize("approve_retry", [False, True])
def test_timeout_receipt_preserves_inputs_requires_fresh_consent_and_isolates_profiles(tmp_path, monkeypatch, approve_retry):
    from sci_cli.skill_add_status import status_for
    from sci_constants import get_skills_dir, set_sci_home_override, reset_sci_home_override

    cli = cli_fixture()
    before = copy.deepcopy(vars(cli))
    bundle = bundle_from_files({"SKILL.md": SKILL}, "fixture")
    model_calls = Mock(side_effect=[TimeoutError("credential-must-not-appear"), bundle])
    monkeypatch.setattr(wizard, "generate", model_calls)
    clients = []

    def prepare(shell):
        client = Mock()
        clients.append(client)
        return DraftRoute(client, shell.provider, shell.model, "fixture endpoint", 131072)

    monkeypatch.setattr(wizard, "prepare_route", prepare)
    failed = ScriptUI(["Describe a workflow", "Summarize", "CSV", "Report", "Research only", "Approve this draft", "Return to prompt"])
    wizard.run_add_skill(cli, '/Add_skill', ui=failed)
    assert status_for(cli).phase == "FAILED"
    assert "credential-must-not-appear" not in "\n".join(failed.output)
    assert any("attempt has stopped" in line for line in failed.output)
    assert any("Nothing was saved or enabled" in line for line in failed.output)
    assert clients[0].close.call_count == 1
    assert not (get_skills_dir() / bundle.name).exists()
    query = ScriptUI([])
    wizard.run_add_skill(cli, "/Add_skill status", ui=query)
    assert "FAILED" in query.output[-1] and "retry" in query.output[-1]
    assert model_calls.call_count == 1  # Status never dispatches another model request.

    token = set_sci_home_override(tmp_path / "other-profile")
    try:
        assert status_for(cli).phase == "NOT STARTED" and status_for(cli).pending is None
    finally:
        reset_sci_home_override(token)
    assert status_for(cli).phase == "FAILED"

    cli.provider, cli.model = "new-provider", "new-model"
    answers = (["Approve this draft", "Save", "Save and enable for the next session"]
               if approve_retry else ["Cancel"])
    retry = ScriptUI(answers)
    wizard.run_add_skill(cli, "/Add_skill retry", ui=retry)
    assert any("new-provider / new-model" in line for line in retry.output)
    assert "What inputs" not in "\n".join(retry.questions)
    assert cli.history == before["history"] and vars(cli.agent) == vars(before["agent"])
    if approve_retry:
        assert model_calls.call_count == 2
        assert model_calls.call_args_list[0].args[1] == model_calls.call_args_list[1].args[1]
        assert status_for(cli).phase == "SAVED"
        assert (get_skills_dir() / bundle.name).exists()
    else:
        assert model_calls.call_count == 1
        assert status_for(cli).phase == "CANCELLED"
        assert not (get_skills_dir() / bundle.name).exists()


def test_progress_stops_before_failure_and_retry_has_no_overlapping_call(tmp_path, monkeypatch):
    import threading
    from sci_cli import skill_add_status as status_module
    from agent.auxiliary_client import _notify_aux_progress

    monkeypatch.setattr(status_module, "HEARTBEAT_SECONDS", 0.01)
    heartbeat_seen = threading.Event()

    class ProgressUI(ScriptUI):
        def show(self, text):
            super().show(text)
            if "elapsed. Provider output received" in text:
                heartbeat_seen.set()

    cli = cli_fixture()
    client = Mock()
    monkeypatch.setattr(wizard, "prepare_route", lambda shell: DraftRoute(client, "fixture", "model", "fixture", 131072))
    call_count = 0

    def provider(route, messages, source):
        nonlocal call_count
        call_count += 1
        assert len([t for t in threading.enumerate() if t.name == "skill-add-progress"]) == 1
        if call_count == 1:
            _notify_aux_progress()
            assert heartbeat_seen.wait(5), "Progress reporter never showed actual provider activity"
            raise TimeoutError("fixture")
        return bundle_from_files({"SKILL.md": SKILL}, "fixture")

    monkeypatch.setattr(wizard, "generate", provider)
    ui = ProgressUI(["Describe a workflow", "Summarize", "CSV", "Report", "Research only", "Approve this draft",
                     "Retry draft", "Approve this draft", "Cancel"])
    wizard.run_add_skill(cli, '/Add_skill', ui=ui)
    assert call_count == 2 and client.close.call_count == 2
    assert not any(t.name == "skill-add-progress" for t in threading.enumerate())
    failure = next(i for i, line in enumerate(ui.output) if "[Add_skill] FAILED" in line)
    retry = next(i for i, line in enumerate(ui.output[failure + 1:], failure + 1) if "PREPARING MODEL" in line)
    assert not any("DRAFTING —" in line for line in ui.output[failure:retry])
    assert "CANCELLED" in ui.output[-1]
