"""Science-first project creation. Saving never depends on a runnable environment."""

import shlex
import threading

from sci_cli.skill_add import Cancelled, WizardUI
from sci_cli.science_profiles import ProfileSpec, Source, create, local_source
from sci_cli.science_profiles_catalog import (
    science_skills, configured_science_services, cached_tools, select_science_items,
    select_service_tools, service_required_tools,
)

PERSONA = ("You are a life-sciences research assistant. Follow the selected scientific skills, "
           "cite evidence, distinguish findings from hypotheses, disclose uncertainty, and ask "
           "about missing scientific parameters. Do not invent experimental results or claim an unrun tool succeeded.")


def choose_tools(home, ui):
    from sci_cli.config import read_user_config_raw
    services = configured_science_services(read_user_config_raw(home / "config.yaml"))
    for canonical in ("tooluniverse", "boltzmann"):
        if not any(canonical in name.lower().replace("-", "").replace("_", "") for name in services):
            ui.show(f"{canonical}: Setup required — no connection configured here. Use /Add_mcp later; profile creation can continue.")
    selected = select_science_items(ui, "Tool services", {
        name: "Required submit/status/download/upload/fetch operations included automatically; setup checked later"
        if service_required_tools(name) else "Choose tools for this project (setup checked later)"
        for name in services})
    pending = {}
    for name in selected:
        tools = cached_tools(name, services[name])
        if not tools and not service_required_tools(name):
            ui.show(f"{name}: Setup required — no current tool list is cached. Service preference saved; no tools granted. "
                    "Connection/authentication and tool discovery will need approval later.")
            pending[name] = []
            continue
        names = select_service_tools(ui, name, tools)
        if names:
            pending[name] = names
    return pending


def choose_sources(ui):
    sources = []
    while True:
        action = ui.choose(f"Project sources: {len(sources)} added (optional).", ("Done", "Add file or folder", "Add reference URL", "Cancel"))
        if action == "Done":
            return sources
        value = ui.ask("Paste the file/folder path:" if action == "Add file or folder" else "Paste the public HTTPS reference URL:")
        try:
            source = Source(value.strip().strip('"').strip("'"))
            if action == "Add reference URL" and not source.location.startswith("https://"):
                raise ValueError("Use a public HTTPS URL.")
            path = local_source(source)
            if path is not None:
                source.location = str(path)
            if source not in sources:
                sources.append(source)
            ui.show(f"Added reference: {source.location}. " + ("Original stays unchanged; content access needs approval later." if path else "URL saved only; not downloaded or indexed."))
        except (ValueError, OSError) as exc:
            ui.show(f"Source not added: {exc}. Choose another source or Done; your other selections are retained.")


def create_wizard(cli, command, ui=None):
    from sci_constants import get_sci_home
    from sci_cli.profiles import validate_profile_name
    ui = ui or WizardUI(cli)
    cli._science_cancel = threading.Event()
    try:
        args = shlex.split(command)[1:]
        if len(args) > 1:
            raise ValueError('Usage: /Create_profile ["project-name"]')
        home = get_sci_home()
        name = args[0] if args else ui.ask("Name your science project (for example antibody-project):")
        validate_profile_name(name)
        ui.show("Choose science skills, tools, and optional sources, then Create profile. "
                "No Docker setup, downloads, service connections, or model calls during creation. "
                "In each selection menu, Done is the first option.")
        skills = select_science_items(ui, "Science skills", science_skills(home))
        pending = choose_tools(home, ui)
        sources = choose_sources(ui)
        purpose = f"Life-sciences project {name}; selected capabilities: " + ", ".join([*skills, *pending])
        spec = ProfileSpec(name, purpose, PERSONA, "", skills=skills,
                           sources=sources, setup_pending=True, pending_tools=pending,
                           capability_source_home=str(home.resolve()))
        while True:
            ui.show(f"Review project: {spec.name}\n"
                    f"Science skills: {', '.join(skills) or 'none selected'} — instructions ready after save; software requirements not verified.\n"
                    f"Tool selections: {pending or 'none selected'} — Setup required before execution; no access granted yet.\n"
                    f"Sources: {', '.join(s.location for s in sources) or 'none'} — references only, not read/uploaded/indexed.\n"
                    "Scientific persona supplied automatically. Existing shared LLM login reused. "
                    "Manual activation by default; routing/collaboration are optional later. "
                    "Missing software does NOT prevent saving this project.")
            ui.choose("Save this science project?", ("Create profile", "Cancel"))
            if cli._science_cancel.is_set():
                raise Cancelled()
            try:
                destination = create(spec, home)
                break
            except FileExistsError:
                ui.choose(f"A profile named {spec.name} already exists. Nothing was overwritten.", ("Rename", "Cancel"))
                spec.name = ui.ask("New project name:")
                validate_profile_name(spec.name)
                spec.purpose = f"Life-sciences project {spec.name}; selected capabilities: " + ", ".join([*skills, *pending])
        ui.show(f'Created {spec.name}: {destination}\nReady: project conversation and saved skill instructions.\n'
                'Setup required: local execution and selected service connections; files/URLs are references only.\n'
                f'Use /activate "{spec.name}" profile. No environment preparation is required just to select it.\n'
                f'When local execution is needed: /activate "{spec.name}" --prepare. Existing conversation unchanged.')
    except (Cancelled, KeyboardInterrupt, EOFError):
        ui.show("Profile creation cancelled. Nothing was activated.")
    except Exception as exc:
        ui.show(f"Profile creation failed: {exc}. Nothing was activated.")
    finally:
        cli._science_cancel = None
