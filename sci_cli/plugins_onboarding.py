"""Host-owned interactive onboarding surfaces for external plugins."""

import sys
from types import SimpleNamespace

from sci_constants import sci_home_key


class PluginOnboardingContextMixin:
    def prompt_secret(self, name, prompt, *, validator=None, standalone=False):
        """Capture and validate before saving; never return the secret to the caller.

        ``standalone`` is for an interactive setup hook, not a remote slash command.
        Messaging surfaces without a local CLI fail closed instead of reading server stdin.
        """
        if self._manager.scope_key != sci_home_key():
            raise RuntimeError("Plugin onboarding must run in its owning profile")
        cli = self._manager._cli_ref
        if cli is not None:
            return cli._secret_capture_callback(name, prompt, validator=validator)
        if standalone and sys.stdin.isatty() and sys.stdout.isatty():
            from sci_cli.callbacks import prompt_for_secret
            return prompt_for_secret(SimpleNamespace(), name, prompt, validator=validator)
        return {"success": False, "skipped": True, "validated": False,
                "message": "Open Sci in a local interactive terminal to enter this credential securely."}

    def refresh_tools(self, *, now=False):
        """Opt-in CLI tool refresh, without resetting history or injecting a user turn.

        The default never changes a live prompt/tool snapshot. Call only after an
        explicit user request such as a slash command's ``--now`` flag.
        """
        if not now:
            return False
        if self._manager.scope_key != sci_home_key():
            raise RuntimeError("Plugin refresh must run in its owning profile")
        cli = self._manager._cli_ref
        if cli is None or getattr(cli, "_agent_running", False):
            return False
        from sci_cli.config import load_config
        from sci_cli.tools_config import _get_platform_tools
        from tools.mcp_tool_agent import refresh_agent_mcp_tools, reprobe_tool_availability
        config = load_config()
        enabled = sorted(_get_platform_tools(config, "cli"))
        reprobe_tool_availability()
        if cli.agent is not None:
            refresh_agent_mcp_tools(cli.agent, enabled_override=enabled,
                                    disabled_override=config.get("agent", {}).get("disabled_toolsets", []))
        cli.enabled_toolsets = enabled
        return True
