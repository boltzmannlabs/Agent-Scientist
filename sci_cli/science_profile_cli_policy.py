"""Preserve saved legacy execution rules when opening an ordinary native CLI."""

import json


def prepare(cli):
    from sci_constants import get_sci_home
    from sci_cli.science_profiles import MANIFEST
    from sci_cli.science_profiles_sandbox import validate_runtime

    home = get_sci_home()
    if not (home / MANIFEST).is_file():
        if getattr(cli, "_legacy_science_policy_home", None):
            raise ValueError("The saved profile execution policy was removed. Execution is blocked; no host fallback.")
        return None
    # Recheck before every turn, including one reusing a cached agent. Checking
    # does not rewrite the saved profile or its conversation's cached prefix.
    spec = validate_runtime(home)
    cli._legacy_science_policy_home = str(home)
    if cli.agent is None:
        cli.enabled_toolsets = (["skills"] if spec.setup_pending else ["terminal", "file", "skills"]) + list(spec.mcp_tools)
        if spec.boltzmann_enabled:
            cli.enabled_toolsets.append("boltzmann")
        cli.ignore_rules = True
        cli.max_turns = min(cli.max_turns, 30)
        budget = getattr(cli, "run_budget_seconds", None)
        cli.run_budget_seconds = min(budget, spec.max_seconds) if budget is not None else spec.max_seconds
        if not getattr(cli, "_legacy_science_prompt_loaded", False):
            prompt = (home / "SOUL.md").read_text()
            if spec.setup_pending:
                prompt += ("\nLocal execution is NOT ready. Do not claim to run programs or read project files. "
                           "The saved isolated environment still needs setup; never fall back to host execution. "
                           "Skill instructions are available without running their scripts.\n")
            prompt += "\nServices still requiring setup (NOT callable): " + json.dumps(spec.pending_tools)
            if spec.allow_llm_sources:
                prompt += "\nApproved references: " + json.dumps([
                    source.location if source.location.startswith("https://") else f"/sources/{i}"
                    for i, source in enumerate(spec.sources)])
            cli.system_prompt = prompt + ("\n" + cli.system_prompt if cli.system_prompt else "")
            cli._legacy_science_prompt_loaded = True
    return spec


def install(cli, spec):
    if spec is None:
        return
    from sci_cli.science_profile_permissions import install_gate
    from agent.redact import redact_sensitive_text

    def ask(kind, **values):
        # Legacy workers already have a permission transport. Interactive CLI
        # turns use a fresh, explicit approval for each external transfer.
        callback = getattr(cli, "_science_permission_ask", None)
        if callback is not None:
            return callback(kind, **values)
        return cli._approval_callback(
            redact_sensitive_text(json.dumps(values, ensure_ascii=False)),
            "Approve this external profile tool call/data transfer?",
            allow_permanent=False, allow_session=False) == "once"

    previous = getattr(cli, "_legacy_science_gate", None)
    if previous is not None:
        previous.dispose()
    from sci_cli.science_profiles_catalog import BOLTZMANN_WORKFLOW_TOOLS
    cli._legacy_science_gate = install_gate(cli.agent, ask, allow_local=not spec.setup_pending,
        external_tools=BOLTZMANN_WORKFLOW_TOOLS if spec.boltzmann_enabled else ())
