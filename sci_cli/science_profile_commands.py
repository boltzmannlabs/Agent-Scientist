"""Profile activation and explicit routing consent; parent conversations stay intact."""

import shlex

from sci_cli.skill_add import WizardUI, Cancelled


def activate(cli, command, ui=None):
    from sci_cli.science_profiles import available_profiles
    from sci_cli.science_profiles_sandbox import validate_runtime
    from sci_cli.profiles import get_profile_dir
    from sci_constants import sci_home_key
    ui = ui or WizardUI(cli)
    try:
        args = shlex.split(command)[1:]
        prepare = "--prepare" in args
        args = [arg for arg in args if arg != "--prepare"]
        if len(args) == 2 and args[1].lower() == "profile":
            args.pop()
        if len(args) != 1:
            ui.show('Usage: /activate "profile-name" [profile] [--prepare] | /activate main')
            return
        name = args[0]
        if name == "main":
            cli._science_active = (sci_home_key(), None)
            ui.show("Main conversation selected. Profile conversations remain separate.")
            return
        profiles = available_profiles()
        if name not in profiles:
            raise ValueError("Unknown research profile. Create one with /Create_profile first.")
        home = get_profile_dir(name)
        if prepare:
            from sci_cli.science_profiles_setup import prepare_profile
            prepare_profile(cli, home, ui)
        spec = validate_runtime(home)
        cli._science_active = (sci_home_key(), name)
        ui.show(f"Activated {name}. Your next message runs in its isolated profile conversation. "
                "Use /activate main to return. No toolset or prompt was changed in the main conversation.")
        if spec.setup_pending or spec.pending_tools:
            pending = (["local execution"] if spec.setup_pending else []) + list(spec.pending_tools)
            ui.show(f'Project ready for conversation and skill instructions. Setup required for '
                    f'{", ".join(pending)}. '
                    f'When needed: /activate "{name}" --prepare. No host-execution fallback.')
    except (Cancelled, KeyboardInterrupt, EOFError):
        ui.show("Activation cancelled. Current selection unchanged.")
    except Exception as exc:
        ui.show(f"Activation failed: {exc}. Current selection unchanged.")


def routing(cli, command, ui=None):
    """Session-local opt-in: no surprise routing just because a profile exists."""
    from sci_constants import sci_home_key
    from sci_cli.science_profiles import available_profiles
    ui = ui or WizardUI(cli)
    try:
        args = shlex.split(command)[1:]
        if args == ["off"]:
            cli._science_routing = None
            cli._science_routing_names = None
            ui.show("Automatic profile routing is off for this CLI.")
            return
        if args not in ([], ["on"]):
            raise ValueError("Usage: /profile_routing [on|off]")
        from sci_cli.science_profiles_catalog import select_science_items
        profiles = available_profiles()
        if not profiles:
            raise ValueError("Create a research profile with /Create_profile first.")
        names = select_science_items(ui, "Profiles allowed to route automatically in this CLI",
                                     {n: s.purpose for n, s in profiles.items()})
        if not names:
            ui.show("No profiles selected. Routing settings unchanged.")
            return
        opted = {n: profiles[n].purpose for n in names}
        from sci_cli.skill_add_draft import prepare_route
        route = prepare_route(cli)
        try:
            identity = (route.provider, route.model, route.endpoint)
        finally:
            route.close()
        ui.show(f"Router model: {identity[0]} / {identity[1]} at {identity[2]}. New user requests and opted-in profile purposes go to this model, without your earlier conversation or files.\nEligible profiles: {opted}\nMatching profiles can collaborate within approved sharing permissions; additional or sensitive data transfers require confirmation. Provider charges apply.")
        ui.choose("Enable automatic routing in this CLI?", ("Enable routing", "Cancel"))
        cli._science_routing = (sci_home_key(), cli.provider, cli.model, getattr(cli, "base_url", None))
        cli._science_router_identity = identity
        cli._science_routing_names = (sci_home_key(), tuple(names))
        ui.show("Automatic routing enabled. Manual activation takes priority. /profile_routing off disables routing.")
    except (Cancelled, KeyboardInterrupt, EOFError):
        ui.show("Routing setup cancelled.")
    except Exception as exc:
        ui.show(f"Routing setup failed: {exc}")
