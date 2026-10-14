"""Portable, opt-in science defaults. Inspection never installs or connects."""

from copy import deepcopy

DEFAULTS = {
    "tooluniverse": {
        "command": "tooluniverse", "args": [], "enabled": False,
        "tools": {"include": ["list_tools", "grep_tools", "get_tool_info", "find_tools", "execute_tool"],
                  "resources": False, "prompts": False},
        "sampling": {"enabled": False}, "elicitation": {"enabled": False},
    },
    "pubmed": {
        "url": "https://pubmed.caseyjhand.com/mcp", "transport": "http", "enabled": False,
        "tools": {"include": ["pubmed_search_articles", "pubmed_fetch_articles",
                              "pubmed_fetch_fulltext", "pubmed_format_citations"],
                  "resources": False, "prompts": False},
        "sampling": {"enabled": False}, "elicitation": {"enabled": False},
    },
}


def missing_defaults(config):
    """Explicitly disabled/custom entries are still present: never replace them."""
    return {name: deepcopy(value) for name, value in DEFAULTS.items()
            if name not in config.get("mcp_servers", {})}


def prepare_default(name, ui):
    config = deepcopy(DEFAULTS[name])
    if name == "tooluniverse":
        from pm import ensure_python_tool
        from sci_cli.native_profile_services import progress
        ui.show("ToolUniverse: install pinned tooluniverse==1.5.7 into a managed, isolated environment. "
                "This downloads executable third-party code from the configured package index. "
                "Installation does not approve running it. Approved downloads remain after cancellation.")
        ui.show("ToolUniverse's execute_tool is a dispatcher into its internal catalog, not per-scientific-tool isolation. "
                "That internal catalog may change. Select only discovery operations if you do not want to grant dispatcher access.")
        ui.choose("Approve managed ToolUniverse installation?", ["Install dependencies", "Cancel"])
        with progress(ui, "ToolUniverse installation"):
            config["command"] = str(ensure_python_tool("science-tooluniverse", ["tooluniverse==1.5.7"],
                                                       "tooluniverse", explicit=True, timeout=600))
    else:
        ui.show("PubMed uses the public third-party MCP at https://pubmed.caseyjhand.com/mcp. "
                "No local server dependency is needed. Approved future literature queries go to that service; "
                "it is not an NCBI-operated endpoint.")
    return config


def setup_defaults(cli, ui):
    import tempfile
    from pathlib import Path
    from sci_constants import get_sci_home
    from sci_cli.config import read_user_config_raw
    from sci_cli.native_profile_services import setup_mcp
    from sci_cli.native_profile_update import save_update
    from sci_cli.science_profiles_catalog import select_science_items
    from sci_cli.skill_add import Cancelled
    home = get_sci_home()
    original = read_user_config_raw(home / "config.yaml")
    missing = missing_defaults(original)
    chosen = select_science_items(ui, "Missing standard MCPs (existing connections/exclusions stay unchanged)",
                                  {n: "Optional setup; installation/connection approvals required" for n in missing})
    if not chosen:
        ui.show("No defaults added.")
        return
    services = []
    try:
        with tempfile.TemporaryDirectory(prefix="sci-mcp-review-") as scratch:
            for name in chosen:
                config = prepare_default(name, ui)
                service = setup_mcp(cli, ui, home, name, config, Path(scratch))
                if service:
                    services.append(service)
            if not services:
                ui.show("No connections saved.")
                return
            ui.choose("Save and enable for the next session?", ["Save and enable for the next session", "Cancel"])
            save_update(home, original, services=services, cli=cli)
        ui.show("Saved: " + ", ".join(s.name for s in services) + ". Enabled for a new conversation after restart. "
                "The current tools and prompt are unchanged.")
    except (Cancelled, KeyboardInterrupt, EOFError):
        ui.show("Setup cancelled. No connection saved; approved dependency downloads may remain.")


def disable_duplicate(home):
    """Retain the exact old entry in a private backup; refuse restricted-profile edits."""
    import json
    import os
    import tempfile
    from sci_cli.config import read_user_config_raw, atomic_config_write, _CONFIG_LOCK
    from sci_cli.plugins_state import _locked_plugin_state
    from sci_cli.native_profile_creation import profile_scope
    from plugins.boltzmann.auth import available
    if (home / "science-profile.json").exists():
        raise ValueError("Restricted profile requires a reviewed migration; duplicate left unchanged.")
    path = home / "config.yaml"
    with profile_scope(home), _locked_plugin_state(path), _CONFIG_LOCK:
        config = read_user_config_raw(path)
        entry = config.get("mcp_servers", {}).get("boltzmann")
        if not entry or not entry.get("enabled", True):
            return None
        if not available() or "boltzmann" not in config.get("plugins", {}).get("enabled", []):
            raise ValueError("Native Boltzmann plugin is not authorized/enabled; duplicate left unchanged.")
        # This helper handles only the known native connector's duplicate, not arbitrary servers.
        if not any(str(a).endswith("boltzmann_mcp_server.py") for a in entry.get("args", [])):
            raise ValueError("Unrecognized Boltzmann MCP implementation; review dependencies manually.")
        backup = home / "backups"
        backup.mkdir(mode=0o700, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix="boltzmann-mcp-", suffix=".json", dir=backup)
        with os.fdopen(fd, "w") as handle:
            json.dump(entry, handle, indent=2)
        entry["enabled"] = False
        atomic_config_write(path, config)
        return name
