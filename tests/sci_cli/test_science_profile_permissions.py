"""Project policy is applied at execution, not just by hiding tool schemas."""

import json
from types import SimpleNamespace
from unittest.mock import Mock


def test_external_gate_survives_registry_changes_and_fails_closed(monkeypatch):
    from sci_cli.science_profile_permissions import install_gate
    from sci_cli.middleware import run_tool_execution_middleware
    agent = SimpleNamespace(tools=[{"function": {"name": name}} for name in
                                   ("terminal", "skill_view", "mcp_fixture_read", "delegate_task")])
    ask, execute = Mock(return_value=False), Mock(return_value="done")
    lease = install_gate(agent, ask)
    try:
        assert "delegate_task" not in agent.valid_tool_names
        denied = run_tool_execution_middleware("mcp_fixture_read", {"query": "private"}, execute)
        assert "not approved" in denied
        execute.assert_not_called()
        ask.return_value = True
        assert run_tool_execution_middleware("mcp_fixture_read", {}, execute) == "done"
        ask.side_effect = EOFError("controller lost")
        execute.reset_mock()
        assert "blocked" in run_tool_execution_middleware("mcp_fixture_read", {}, execute)
        assert "permissions" in run_tool_execution_middleware("mcp_future_tool", {}, execute)
        assert "background" in run_tool_execution_middleware("terminal", {"background": True}, execute)
        execute.assert_not_called()
    finally:
        lease.dispose()


def test_isolated_skill_view_does_not_install_or_expand_shell(tmp_path, monkeypatch):
    from sci_constants import get_sci_home
    from tools import skills_tool
    from sci_cli.science_profile_permissions import install_gate
    from sci_cli.middleware import run_tool_execution_middleware
    root = get_sci_home() / "skills" / "fixture"
    root.mkdir(parents=True)
    (root / "SKILL.md").write_text("---\nname: fixture\ndescription: Research fixture\ndeps: [uninstalled]\nrequired_environment_variables: [SECRET]\n---\n!`touch /host-side-effect`\n")
    setup = Mock(side_effect=AssertionError("must not set up on host"))
    monkeypatch.setattr(skills_tool, "_skill_readiness", setup)
    monkeypatch.setattr(skills_tool, "_preprocess_skill", setup)
    import pm
    monkeypatch.setattr(pm, "ensure", setup)
    agent = SimpleNamespace(tools=[{"function": {"name": "skill_view"}}])
    lease = install_gate(agent, Mock())
    try:
        result = json.loads(run_tool_execution_middleware("skill_view", {"name": "fixture"}, setup))
        assert result["success"], result
        assert "!`touch /host-side-effect`" in result["content"]
        setup.assert_not_called()
    finally:
        lease.dispose()
