"""Profile inventory from local metadata and the existing conversation; never probes."""

import shlex


def inventory(cli):
    from sci_constants import get_sci_home
    from sci_cli.config import load_config_readonly
    from sci_cli.plugins_discovery import collect_directory_manifests, resolve_manifest_winners
    from sci_cli.science_integrations import missing_defaults
    from agent.skill_utils import iter_skill_index_files, get_disabled_skill_names
    from tools.registry import registry
    cfg = load_config_readonly()
    agent = getattr(cli, "agent", None)
    live = {t.get("function", {}).get("name") for t in getattr(agent, "tools", []) or []}
    selected = cfg.get("platform_toolsets", {}).get("cli")
    excluded = set(cfg.get("agent", {}).get("disabled_toolsets", []))
    rows = []

    def add(kind, name, enabled, in_session=None, detail=""):
        state = "enablement not verified" if enabled is None else "enabled" if enabled else "disabled"
        current = ("available" if in_session else "not listed") if in_session is not None else "not verified"
        pending = ("; pending next-session activation" if kind == "MCP" and name in
                   getattr(cli, "_science_deferred_mcp", {}) else
                   "; may require a new session or setup" if enabled and in_session is not True else "")
        rows.append((kind, name, f"configured/installed; {state}; conversation: {current}{pending}. {detail}"))

    for name in registry.get_all_tool_names():
        entry = registry.get_entry(name)
        if entry:
            enabled = entry.toolset not in excluded and (selected is None or entry.toolset in selected)
            add("tool", name, enabled, name in live if "tool_search" not in live else
                (True if name in live else None), "Deferred tools require discovery; no readiness probe performed.")
    for name, value in cfg.get("mcp_servers", {}).items():
        if not isinstance(value, dict):
            continue
        enabled = value.get("enabled", True) and name not in excluded and (selected is None or name in selected)
        add("MCP", name, enabled, None, "Connection/authentication not probed. "
            f"Explicit allowlist: {len(value.get('tools', {}).get('include', []))} entries." if
            "include" in value.get("tools", {}) else "No explicit allowlist; review permissions.")
    plugins = cfg.get("plugins", {})
    manifests = resolve_manifest_winners(collect_directory_manifests())
    from agent.secret_scope import build_profile_secret_scope
    secrets = build_profile_secret_scope(get_sci_home())
    for name in sorted(set(manifests) | set(plugins.get("enabled", []))):
        manifest = manifests.get(name)
        enabled = (name in plugins.get("enabled", []) and name not in plugins.get("disabled", []) and
                   name not in excluded)
        detail = "Plugin-wide permissions; dependencies/authentication not verified."
        if manifest is None:
            detail = "Configured plugin installation/manifest is missing; setup required."
        elif manifest.kind != "standalone":
            enabled = None
            detail = "Category-managed plugin; consult its provider/backend configuration."
        else:
            required = [item if isinstance(item, str) else item.get("name", "") for item in manifest.requires_env]
            missing = [key for key in required if key and not secrets.get(key)]
            if missing:
                detail += " Missing credential/environment slots: " + ", ".join(missing) + "."
        if name == "boltzmann":
            from sci_cli.science_catalog_view import authorization_summary
            detail = (authorization_summary() + " Scientific inventory: /boltzmann_tools. "
                      "Inspect request schemas through tool discovery; this view does not test live execution.")
        visible = True if manifest and set(manifest.provides_tools) & live else None
        add("plugin", name, enabled, visible, detail)
    disabled = get_disabled_skill_names("cli")
    home = get_sci_home()
    for path in iter_skill_index_files(home / "skills", "SKILL.md"):
        name = path.parent.relative_to(home / "skills").as_posix()
        from sci_cli.science_profiles_catalog import skill_identifiers
        add("skill", name, not skill_identifiers(name, path.parent) & disabled,
            None, "Saved instructions; this conversation's cached skill index is not refreshed.")
    for name in missing_defaults(cfg):
        rows.append(("default MCP", name, "available to set up; not configured; no permissions granted. /capabilities setup"))
    return sorted(rows, key=lambda r: (r[0], r[1]))


def run(cli, command, ui=None):
    from sci_cli.skill_add import WizardUI, Cancelled
    from sci_cli.native_profile_session import profile_label
    ui = ui or WizardUI(cli)
    try:
        args = shlex.split(command)[1:]
        if args == ["setup"]:
            from sci_cli.science_integrations import setup_defaults
            return setup_defaults(cli, ui)
        query = " ".join(args[1:] if args[:1] == ["search"] else args).casefold()
        rows = inventory(cli)
        page = 0
        while True:
            matches = [r for r in rows if query in " ".join(r).casefold()]
            pages = max(1, (len(matches) + 7) // 8)
            ui.show(f"Capabilities [{profile_label()}] — {len(matches)} matches; page {page + 1}/{pages}. "
                    "Local metadata only; no service or scientific tool executed.")
            for kind, name, state in matches[page * 8:(page + 1) * 8]:
                ui.show(f"{kind}: {name}\n  {state}")
            controls = ["Done", "Search", "Set up missing defaults"]
            if page + 1 < pages:
                controls.append("Next page")
            if page:
                controls.append("Previous page")
            action = ui.choose("Browse capabilities", controls)
            if action == "Done":
                return
            if action == "Set up missing defaults":
                from sci_cli.science_integrations import setup_defaults
                return setup_defaults(cli, ui)
            if action == "Search":
                query, page = ui.ask("Search capabilities:").casefold(), 0
            else:
                page += 1 if action == "Next page" else -1
    except (Cancelled, KeyboardInterrupt, EOFError):
        ui.show("Capabilities closed. Any separately approved downloads may remain.")
    except Exception:
        ui.show("Capabilities/setup could not complete. No success is confirmed. "
                "Approved installations or staged credentials may remain; existing conversation unchanged.")
