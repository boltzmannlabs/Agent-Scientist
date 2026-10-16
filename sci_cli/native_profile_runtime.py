"""Native conversation setup for opted-in routing; transport owns only lifecycle."""

import json

from sci_cli.native_profile_creation import PROJECT


def routing_spec(home):
    from sci_cli.science_profiles import ProfileSpec, Source, MANIFEST
    if (home / MANIFEST).is_file():
        from sci_cli.science_profiles_sandbox import validate_runtime
        return validate_runtime(home)
    data = json.loads((home / PROJECT).read_text(encoding="utf-8-sig")) if (home / PROJECT).is_file() else {}
    from sci_cli.config import read_user_config_raw
    terminal = read_user_config_raw(home / "config.yaml").get("terminal", {})
    return ProfileSpec(home.name, data.get("purpose") or f"Native profile {home.name}",
                       "Native profile persona", terminal.get("docker_image", ""),
                       setup_pending=terminal.get("backend", "local") != "docker",
                       skills=data.get("skills", []),
                       sources=[Source(s["location"]) for s in data.get("sources", [])],
                       routing_terms=data.get("routing_terms", []), collaborators=data.get("collaborators", []))


def build_native_cli(home, spec):
    from cli import SciCLI, CLI_CONFIG
    from sci_cli.tools_config import _get_platform_tools
    # Same configuration resolver as the interactive native CLI, not a custom
    # list that strips plugin/deferred operations. Router turns are new sessions.
    return SciCLI(toolsets=sorted(_get_platform_tools(CLI_CONFIG, "cli")),
                  run_budget=spec.max_seconds)
