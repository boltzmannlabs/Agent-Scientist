"""Read-only scientific inventory shared by CLI catalog views and skill guidance."""

import json
import shlex
from pathlib import Path


def registry_path():
    from sci_cli.plugins_discovery import collect_directory_manifests, resolve_manifest_winners
    manifests = resolve_manifest_winners(collect_directory_manifests())
    manifest = manifests.get("boltzmann")
    root = Path(manifest.path) if manifest else Path(__file__).resolve().parents[1] / "plugins/boltzmann"
    refs = root / "skills/boltzmann-tools/references"
    canonical = refs / "tool-contracts.v1.json"
    # Older separately installed plugins have not necessarily been migrated yet.
    if canonical.is_file() and json.loads(canonical.read_text(encoding="utf-8-sig")).get("status") == "canonical":
        return canonical
    return refs / "module-registry.v1.json"


def catalog_rows(path=None, *, domain="", query=""):
    data = json.loads((path or registry_path()).read_text(encoding="utf-8-sig"))
    modules = {m["id"]: m for m in data["modules"]}
    rows = []
    tools = list(data["tools"].values()) if isinstance(data["tools"], dict) else data["tools"]
    for tool in [*tools, *data.get("unavailable_entries", [])]:
        if tool.get("status") in {"removed", "ignored"}:
            continue
        module = modules.get(tool.get("module_id"), {})
        row = {"domain": module.get("domain", "Unassigned"),
               "module": module.get("title", "Unassigned"), "name": tool["display_name"],
               "status": tool.get("status", "unknown")}
        searchable = " ".join([*row.values(), *tool.get("aliases", [])]).casefold()
        if domain.casefold() not in (row["domain"] + " " + row["module"]).casefold():
            continue
        if query.casefold() not in searchable:
            continue
        rows.append(row)
    return sorted(rows, key=lambda r: (r["status"] != "active", r["domain"], r["module"], r["name"]))


def authorization_summary():
    from plugins.boltzmann.auth import available
    from sci_cli.config import load_config_readonly
    from sci_constants import get_sci_home
    cfg = load_config_readonly()
    plugins = cfg.get("plugins", {})
    disabled = set(plugins.get("disabled", [])) | set(cfg.get("agent", {}).get("disabled_toolsets", []))
    selected = cfg.get("platform_toolsets", {}).get("cli")
    restricted = ("boltzmann" not in plugins.get("enabled", []) or "boltzmann" in disabled or
                  (selected is not None and "boltzmann" not in selected))
    legacy = (get_sci_home() / "science-profile.json").is_file()
    return ("Local authorization: " + ("present" if available() else "missing; use /add_boltzmann") +
            "; profile access: " + ("restricted/not selected" if restricted else "configured; execution gates still apply") +
            ("; legacy isolation policy applies" if legacy else "") +
            ". Catalog visibility is not execution permission, live entitlement, or readiness verification.")


def run_catalog(cli, command, ui=None):
    from sci_cli.skill_add import WizardUI, Cancelled
    ui = ui or WizardUI(cli)
    try:
        args = shlex.split(command)[1:]
        search = bool(args and args[0].lower() == "search")
        query, domain = (" ".join(args[1:]), "") if search else ("", " ".join(args))
        rows = catalog_rows(domain=domain, query=query)
        ui.show(authorization_summary())
        ui.show("Installed scientific catalog. Request, file-validation and output verification are separate. "
                "An active entry is not proof of live service readiness; explicit restrictions still apply.")
        page = 0
        while True:
            pages = max(1, (len(rows) + 19) // 20)
            ui.show(f"Boltzmann scientific tools — {len(rows)} matches; page {page + 1}/{pages}")
            previous = None
            for row in rows[page * 20:(page + 1) * 20]:
                group = (row["status"] != "active", row["domain"], row["module"])
                if group != previous:
                    ui.show(("Unavailable / on hold — " if group[0] else "") + f"{group[1]} → {group[2]}")
                    previous = group
                ui.show(f"  {row['name']}" + (f" [{row['status']}]" if group[0] else ""))
            controls = ["Done", "Search"]
            if page + 1 < pages:
                controls.append("Next page")
            if page:
                controls.append("Previous page")
            choice = ui.choose("Browse scientific catalog (no jobs are run)", controls)
            if choice == "Done":
                return
            if choice == "Search":
                rows = catalog_rows(query=ui.ask("Search scientific tools, domains, or modules:"))
                page = 0
            else:
                page += 1 if choice == "Next page" else -1
    except (Cancelled, KeyboardInterrupt, EOFError):
        ui.show("Catalog closed. Nothing changed.")
    except (ValueError, OSError, KeyError):
        ui.show("The installed Boltzmann catalog could not be read. No permissions changed.")
