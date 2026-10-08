"""Environment preparation is guided, consented, and never invents scientific installs."""

import threading
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sci_cli import science_profiles_environment as env
from sci_cli.config_defaults import DEFAULT_SANDBOX_IMAGE
from sci_cli.skill_add import Cancelled

IMAGE = "sha256:" + "b" * 64


def scripted_ui(answers):
    pending = iter(answers)
    def choose(question, choices):
        answer = next(pending)
        assert answer in choices, (answer, question, choices)
        if answer == "Cancel":
            raise Cancelled()
        return answer
    return SimpleNamespace(choose=choose, show=Mock(), ask=Mock(side_effect=AssertionError("No image name should be requested")))


def test_standard_workspace_needs_no_image_name_and_actions_follow_separate_consent(tmp_path, monkeypatch):
    actions = []
    ui = scripted_ui([env.STANDARD, "Check available environments", "Approve download", "Approve check", "Use this workspace"])
    real_choose = ui.choose
    def choose(question, options):
        result = real_choose(question, options)
        actions.append(result)
        return result
    ui.choose = choose
    def inspect():
        assert actions[-1] == "Check available environments"
        return {}
    def download(args, *a, **kw):
        assert actions[-1] == "Approve download"
        assert args == ["pull", DEFAULT_SANDBOX_IMAGE]
    def check(image, commands, *a):
        assert actions[-1] == "Approve check"
        assert image == IMAGE and {"bash", "python3"} <= set(commands)
        return []
    monkeypatch.setattr(env, "installed_images", inspect)
    monkeypatch.setattr(env, "run_preparation", download)
    monkeypatch.setattr(env, "resolve_image", lambda image: IMAGE)
    monkeypatch.setattr(env, "check_commands", check)
    assert env.choose_environment(tmp_path, [], {}, ui, threading.Event()) == IMAGE
    ui.ask.assert_not_called()


def test_installed_standard_never_downloads_and_cancel_never_executes(tmp_path, monkeypatch):
    monkeypatch.setattr(env, "installed_images", lambda: {IMAGE: [DEFAULT_SANDBOX_IMAGE]})
    monkeypatch.setattr(env, "resolve_image", lambda _: IMAGE)
    download, check = Mock(side_effect=AssertionError("must not download")), Mock(return_value=[])
    monkeypatch.setattr(env, "run_preparation", download)
    monkeypatch.setattr(env, "check_commands", check)
    for answers in ([env.STANDARD, "Cancel"], [env.STANDARD, "Check available environments", "Cancel"]):
        with pytest.raises(Cancelled):
            env.choose_environment(tmp_path, [], {}, scripted_ui(answers), threading.Event())
    check.assert_not_called()
    ui = scripted_ui([env.STANDARD, "Check available environments", "Approve check", "Use this workspace"])
    assert env.choose_environment(tmp_path, [], {}, ui, threading.Event()) == IMAGE
    download.assert_not_called()
    check.assert_called_once()


def test_declared_missing_requirements_block_acceptance_without_running_skill_text(tmp_path, monkeypatch):
    skill = tmp_path / "skills" / "antibody"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text('---\nname: antibody\nrequired_commands: [anarci, "touch /host/file"]\ndeps: [science-package]\n---\nRun custom scientific protocol.\n')
    commands, notes = env.requirements(tmp_path, ["antibody"])
    assert commands == ["anarci", "bash"]
    assert notes[0]["dependencies"] == ["science-package"]
    monkeypatch.setattr(env, "installed_images", lambda: {IMAGE: [DEFAULT_SANDBOX_IMAGE]})
    monkeypatch.setattr(env, "resolve_image", lambda _: IMAGE)
    monkeypatch.setattr(env, "check_commands", lambda *a: ["anarci"])
    ui = scripted_ui([env.STANDARD, "Check available environments", "Approve check", "Cancel"])
    with pytest.raises(Cancelled):
        env.choose_environment(tmp_path, ["antibody"], {}, ui, threading.Event())
    assert any("Missing commands: anarci" in c.args[0] for c in ui.show.call_args_list)


def test_advanced_picker_uses_installed_ids_and_probe_has_no_mounts_network_or_pull(tmp_path, monkeypatch):
    monkeypatch.setattr(env, "installed_images", lambda: {IMAGE: ["science:installed"]})
    resolve = Mock(return_value=IMAGE)
    monkeypatch.setattr(env, "resolve_image", resolve)
    run = Mock(return_value="")
    monkeypatch.setattr(env, "run_preparation", run)
    monkeypatch.setattr(env, "docker_command", lambda *a: "")
    ui = scripted_ui([env.ADVANCED, "Check available environments", f"science:installed ({IMAGE[7:19]})", "Approve check", "Use this workspace"])
    assert env.choose_environment(tmp_path, [], {}, ui, threading.Event()) == IMAGE
    args = run.call_args.args[0]
    assert "--pull=never" in args and "--network=none" in args and "--read-only" in args
    assert not any(a in {"-v", "--volume", "--mount", "--env", "--env-file"} for a in args)
    assert args[-1] == "bash"
    resolve.assert_called_once_with(IMAGE)


def test_preparation_cancellation_stops_owned_process_and_reports_progress(monkeypatch):
    cancel = threading.Event()
    proc = Mock()
    proc.poll.return_value = None
    def wait(timeout):
        cancel.set()
    proc.wait.side_effect = wait
    monkeypatch.setattr("tools.environments.docker.find_docker", lambda: "/fixture/docker")
    monkeypatch.setattr(env.subprocess, "Popen", lambda *a, **kw: proc)
    ui = SimpleNamespace(show=Mock())
    with pytest.raises(Cancelled):
        env.run_preparation(["pull", DEFAULT_SANDBOX_IMAGE], ui, cancel, stage="Download", timeout=900)
    proc.terminate.assert_called_once()
    assert "elapsed" in ui.show.call_args.args[0]
