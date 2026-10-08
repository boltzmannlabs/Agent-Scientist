"""Read-only, profile-scoped science selections; no discovery processes or network."""

from pathlib import Path
import re

SCIENCE_CATEGORIES = {"science", "life-sciences", "biology", "bioinformatics", "chemistry", "medicine", "clinical", "research"}
NON_SCIENCE_CATEGORIES = {"creative", "autonomous-ai-agents", "software-development", "productivity", "devops"}
SCIENCE_TOPIC = re.compile(r"(?i)\b(antibod\w*|protein\w*|molecul\w*|genom\w*|bioinformatic\w*|biolog\w*|chemistr\w*|clinical|pharma\w*|drug|rna|dna|sequenc\w*|pubmed)\b")

# Explicit workflow dependencies, not a wildcard grant to future server tools.
BOLTZMANN_WORKFLOW_TOOLS = (
    "boltzmann_submit", "boltzmann_status", "boltzmann_download",
    "boltzmann_upload", "boltzmann_fetch_tool_log",
)


def service_required_tools(server):
    normalized = re.sub(r"[^a-z0-9]", "", server.lower())
    return BOLTZMANN_WORKFLOW_TOOLS if "boltzmann" in normalized else ()


def select_service_tools(ui, server, tools, *, selected=None, verified=False):
    required = service_required_tools(server)
    if not required:
        return selected or select_science_items(ui, f"{server} tools", tools)
    missing = set(required) - set(tools)
    if missing and verified:
        raise ValueError(f"{server}: required Boltzmann workflow operations are missing: "
                         f"{', '.join(sorted(missing))}. Connection remains unconfigured; "
                         "update the server to expose the complete workflow, then retry setup.")
    ui.show(f"{server}: automatically included workflow operations: {', '.join(required)}. "
            "No individual selection needed. Upload/job approvals still apply.")
    if missing:
        ui.show("The cached tool list is incomplete or unavailable. These are saved requirements, "
                "not active permissions; setup must verify the complete workflow.")
    optional = {name: desc for name, desc in tools.items() if name not in required}
    extras = ([name for name in selected if name not in required] if selected is not None
              else select_science_items(ui, f"{server} additional tools (optional)", optional) if optional else [])
    return [*required, *extras]


def science_skills(home: Path):
    from agent.skill_utils import iter_skill_index_files, parse_frontmatter
    root = home / "skills"
    result = {}
    for skill in sorted(iter_skill_index_files(root, "SKILL.md")):
        if skill.is_symlink() or not skill.resolve().is_relative_to(root.resolve()):
            continue
        name = skill.parent.relative_to(root).as_posix()
        metadata, _ = parse_frontmatter(skill.read_text(encoding="utf-8-sig"))
        description = " ".join(str(metadata.get("description") or name.rsplit("/", 1)[-1]).split())
        category = name.split("/", 1)[0]
        if category in NON_SCIENCE_CATEGORIES:
            continue
        extra = metadata.get("metadata") or {}
        sci = extra.get("sci", {}) if isinstance(extra, dict) else {}
        sci = sci if isinstance(sci, dict) else {}
        tags = str(sci.get("category", "")) + " " + str(sci.get("tags", []))
        if category in SCIENCE_CATEGORIES or "science" in tags.lower() or SCIENCE_TOPIC.search(name + " " + description):
            result[name] = description
    return result


def select_science_items(ui, title, options):
    """Bounded toggle picker: Done is first even when there are thousands of tools."""
    if not options:
        ui.show(f"{title}: none available here. You can still create the profile.")
        return []
    selected, query, page = [], "", 0
    while True:
        matches = [key for key, desc in options.items() if query in (key + " " + desc).lower()]
        pages = max(1, (len(matches) + 3) // 4)
        page = min(page, pages - 1)
        rows = matches[page * 4:page * 4 + 4]
        labels = {f"{'[selected] ' if key in selected else ''}{key} — {options[key][:100]}": key for key in rows}
        controls = ["Done", *labels, "Search"]
        if query:
            controls.append("Clear search")
        if page + 1 < pages:
            controls.append("Next page")
        if page:
            controls.append("Previous page")
        controls.append("Cancel")
        choice = ui.choose(f"{title}: {len(selected)} selected; page {page + 1}/{pages}. Done continues.", controls)
        if choice == "Done":
            return selected
        if choice in labels:
            key = labels[choice]
            if key in selected:
                selected.remove(key)
                ui.show(f"Removed: {key}")
            else:
                selected.append(key)
                ui.show(f"Selected: {key}\n{options[key]}\nChoose Done to continue.")
            continue
        actions = {"Search": lambda: (ui.ask("Search by name or description:").lower(), 0),
                   "Clear search": lambda: ("", 0), "Next page": lambda: (query, page + 1),
                   "Previous page": lambda: (query, page - 1)}
        query, page = actions[choice]()


def configured_science_services(config):
    servers = config.get("mcp_servers", {})
    return {name: cfg for name, cfg in servers.items() if isinstance(cfg, dict)
            and any(term in re.sub(r"[^a-z0-9]", "", name.lower()) for term in ("tooluniverse", "boltzmann"))}


def cached_tools(server, config):
    from tools.mcp_schema_cache import config_fingerprint, get_cached_entry, tools_from_cache_entry
    entry = get_cached_entry(server, config_fingerprint(config))
    rows = tools_from_cache_entry(entry or {})
    if not rows:
        # Read an already connected server in this scope; never call discovery.
        from tools import mcp_tool
        from tools.mcp_tool_scope import _server_key
        live = mcp_tool._servers.get(_server_key(server))
        rows = [{"name": tool.name, "description": getattr(tool, "description", "")}
                for tool in getattr(live, "_tools", ())]
    return {row["name"]: str(row.get("description") or "Description unavailable")
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("name"), str) and row["name"]
            and not any(c in row["name"] for c in "*?[]")}
