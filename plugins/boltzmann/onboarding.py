"""Secure CLI-only authorization; default activation leaves the live agent untouched."""

from pathlib import Path

from sci_cli.config import is_managed, load_config
from .auth import KEY_NAME, authorize_saved_key
from .nodeapi_helpers import validate_api_key


def register_skills(ctx):
    ctx.register_skill("tools", Path(__file__).parent / "skills" / "boltzmann-tools" / "SKILL.md",
                       description="List Boltzmann scientific tools by module and run authenticated workflows.")


def enable_toolset(*, expected_config=None, after_save=None):
    from agent.skill_utils import parse_config_string_list
    from sci_cli.config import _CONFIG_LOCK, get_config_path, read_user_config_raw, atomic_config_write
    from sci_cli.plugins_state import _locked_plugin_state
    from sci_cli.tools_config import _get_platform_tools
    # Plugin discovery can use worker threads which read configuration. Never
    # wait for it while holding the config writer's lock.
    defaults = sorted(_get_platform_tools(load_config(), "cli"))
    with _locked_plugin_state(get_config_path()), _CONFIG_LOCK:
        raw = read_user_config_raw()
        if expected_config is not None and raw != expected_config:
            raise ValueError("Profile configuration changed during authorization; retry.")
        configured = raw.get("platform_toolsets", {}).get("cli")
        selected = (parse_config_string_list(configured) if configured is not None
                    else defaults)
        patch = {"platform_toolsets": {"cli": list(dict.fromkeys([*selected, "boltzmann"]))}}
        plugins = raw.get("plugins", {})
        enabled = parse_config_string_list(plugins.get("enabled"))
        patch["plugins"] = {"enabled": list(dict.fromkeys([*enabled, "boltzmann"]))}
        plugin_disabled = parse_config_string_list(plugins.get("disabled"))
        if "boltzmann" in plugin_disabled:
            patch["plugins"]["disabled"] = [name for name in plugin_disabled if name != "boltzmann"]
        disabled = parse_config_string_list(raw.get("agent", {}).get("disabled_toolsets"))
        if "boltzmann" in disabled:
            patch["agent"] = {"disabled_toolsets": [name for name in disabled if name != "boltzmann"]}
        # Only these settings change. The general setup saver also migrates
        # unrelated backend values, which would invalidate a reviewed sandbox.
        for section, values in patch.items():
            raw.setdefault(section, {}).update(values)
        atomic_config_write(get_config_path(), raw)
        if after_save is not None:
            after_save(read_user_config_raw())


def add_boltz(ctx, raw_args, *, complete_setup=None):
    words = raw_args.strip().split()
    if any(word not in {"--now", "--replace"} for word in words):
        return "Usage: /Add_boltz [--now] [--replace]. Never paste a key in the command; use the masked prompt."
    if is_managed():
        return "Boltzmann setup is unavailable in a managed installation. Contact your administrator."
    print("[Add_boltz] Enter a key securely. Validation sends it only to "
          "https://nodeapis.boltzmann.co/api/get-projects (read-only, 15s timeout). "
          "No scientific job will run. Empty Enter cancels.")
    try:
        result = ctx.prompt_secret(KEY_NAME, "Enter your Boltzmann API key",
                                   validator=validate_api_key)
        if result.get("skipped"):
            return "[Add_boltz] CANCELLED. Existing authorization is unchanged. " + result["message"]
        if not result.get("success") or not result.get("validated"):
            return "[Add_boltz] FAILED. No new authorization granted. " + result.get("message", "Key not validated.")
    except Exception:
        return "[Add_boltz] FAILED during credential capture/storage. No new authorization granted. Check credential storage permissions."
    try:
        if complete_setup is None:
            enable_toolset()
        else:
            complete_setup()
        authorize_saved_key()
    except Exception:
        return ("[Add_boltz] FAILED while enabling. The validated key was saved; settings may be partially updated. "
                "Activation was not confirmed. Check profile write permissions and run /Add_boltz again.")
    if "--now" in words:
        from sci_cli.plugins import discover_plugins
        discover_plugins(force=True)
        register_skills(ctx)
        if ctx.refresh_tools(now=True):
            return "[Add_boltz] SAVED. Boltzmann enabled now by explicit request; the prompt cache may be rebuilt."
    return ("[Add_boltz] SAVED. All five Boltzmann operations authorized for this profile. "
            "Enabled. Available automatically in your next session. Restart agent-sci to load them. "
            "The current conversation is unchanged.")
