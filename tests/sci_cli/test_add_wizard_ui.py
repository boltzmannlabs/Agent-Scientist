"""Exercise the real wizard adapter instead of bypassing its choice validation."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sci_cli.skill_add import WizardUI


def test_other_source_reaches_review_without_implicit_approval(tmp_path):
    from sci_cli import skill_add
    from sci_cli.skill_add_status import status_for
    from tests.sci_cli.test_skill_add import SKILL

    source = tmp_path / "source with spaces"
    source.mkdir()
    (source / "SKILL.md").write_text(SKILL)
    answers = iter([f'"{source}"', "Cancel"])
    questions, output = [], []

    def clarify(batch):
        questions.append(batch[0])
        return {"outcome": "submitted", "answers": {"skill_add": next(answers)}}

    cli = SimpleNamespace(_app=SimpleNamespace(is_running=True), _agent_running=False,
                          _clarify_callback=clarify)
    ui = WizardUI(cli)
    ui.show = output.append
    skill_add.run_add_skill(cli, "/Add_skill", ui=ui)
    assert status_for(cli).phase == "CANCELLED", output
    assert questions[0]["allow_other"] is True
    assert len({q["question"] for q in questions}) == len(questions), questions
    assert all(q["allow_other"] is False for q in questions[1:] if q["choices"])
    assert status_for(cli).pending is None


def test_closed_choice_rejects_free_text_and_timeout_is_not_user_cancellation():
    from sci_cli.skill_add import Cancelled
    answers = iter(["yes please", "Approve download"])
    questions = []

    def clarify(batch):
        questions.append(batch[0])
        return {"outcome": "submitted", "answers": {"skill_add": next(answers)}}

    cli = SimpleNamespace(_app=SimpleNamespace(is_running=True), _clarify_callback=clarify)
    ui = WizardUI(cli)
    ui.show = Mock()
    assert ui.choose("Download?", ("Cancel", "Approve download")) == "Approve download"
    assert len(questions) == 2
    assert all(q["allow_other"] is False for q in questions)
    cli._clarify_callback = lambda batch: {"outcome": "timed_out", "answers": {}}
    with pytest.raises(TimeoutError, match="input"):
        ui.ask("Waiting")
    cli._clarify_callback = lambda batch: {"outcome": "cancelled", "answers": {}}
    with pytest.raises(Cancelled):
        ui.ask("Cancelled")
