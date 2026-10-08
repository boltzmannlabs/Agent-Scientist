from sci_cli.main_provider_setup import _prompt_reasoning_effort_selection
from sci_cli.setup import _current_reasoning_effort


def test_reasoning_menu_orders_minimal_before_low(monkeypatch):
    captured = {}

    def _fake_radiolist(title, items, *, selected=0, cancel_returns=None, description=None):
        captured["items"] = items
        captured["selected"] = selected
        return selected  # pick the pre-selected (current) entry

    monkeypatch.setattr("sci_cli.curses_ui.curses_radiolist", _fake_radiolist)

    selected = _prompt_reasoning_effort_selection(
        ["low", "minimal", "medium", "high"],
        current_effort="medium",
    )

    assert selected == "medium"
    assert [item.split()[0] for item in captured["items"][:4]] == [
        "minimal",
        "low",
        "medium",
        "high",
    ]


def test_current_reasoning_effort_reads_dict_form():
    """The setup wizard's "currently in use" lookup must see the dict form's tier (or `none`
    when it disables thinking), never `str(dict)`."""
    assert _current_reasoning_effort({"agent": {"reasoning_effort": {"enabled": True, "effort": "Thinking"}}}) == "thinking"
    assert _current_reasoning_effort({"agent": {"reasoning_effort": {"enabled": False}}}) == "none"
    assert _current_reasoning_effort({"agent": {"reasoning_effort": "high"}}) == "high"


def test_custom_model_menu_uses_declared_template_levels(monkeypatch):
    from types import SimpleNamespace
    from sci_cli.cli_model_switch_mixin import CLIModelSwitchMixin, _picker_reasoning_rows
    from sci_cli.main_provider_setup import _main_model_reasoning_efforts
    from sci_cli.model_switch import ModelSwitchResult
    from providers import get_provider_profile

    captured = []

    def choose(title, items, *, selected=0, cancel_returns=None, description=None):
        captured[:] = items
        return selected

    monkeypatch.setattr("sci_cli.curses_ui.curses_radiolist", choose)
    model, provider = "qwen3.8-27b", "custom:qwen_custom"
    efforts = _main_model_reasoning_efforts(model, provider)
    assert set(efforts) == {"low", "medium", "xhigh"}
    assert set(efforts) < set(get_provider_profile(provider).supported_reasoning_efforts(model))
    assert _prompt_reasoning_effort_selection(efforts, current_effort="xhigh") == "xhigh"
    assert [row.split()[0] for row in captured[:-2]] == efforts
    assert captured[-2] == "Disable reasoning"
    result = ModelSwitchResult(success=True, new_model=model, target_provider=provider)
    rows = _picker_reasoning_rows(result)
    assert [value for value, label in rows[:-2]] == efforts
    committed = []
    picker = SimpleNamespace(
        _model_picker_state={"stage": "reasoning", "selected": 2, "switch_result": result},
        _commit_picker_result=lambda result, persist, reasoning_effort: committed.append(reasoning_effort),
    )
    CLIModelSwitchMixin._handle_model_picker_selection(picker)
    assert committed == [efforts[2]]
