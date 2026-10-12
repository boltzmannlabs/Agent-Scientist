"""Reuse a reviewed backend without inheriting main's writable mounts or secrets."""

from copy import deepcopy


def prepare_environment(config, destination, ui, cancel):
    from sci_cli.config import DEFAULT_CONFIG
    terminal = deepcopy(DEFAULT_CONFIG.get("terminal", {}))
    terminal.update(deepcopy(config.get("terminal", {})))
    backend = terminal.get("backend", "local")
    if backend not in {"local", "docker"}:
        raise ValueError(f"Backend {backend!r} needs a profile-specific remote workspace/credential review. "
                         "It cannot safely inherit main's remote writable workspace. Nothing was created; no host fallback.")
    # Preserve limits, shell options and backend identity, never arbitrary main
    # mounts, credential files, forwarded secrets or a shared mutable container.
    removed = []
    for key in ("docker_volumes", "docker_extra_args", "env_passthrough", "docker_forward_env",
                "credential_files"):
        if terminal.get(key):
            removed.append(key)
        terminal[key] = []
    for key in ("docker_env",):
        if terminal.get(key):
            removed.append(key)
        terminal[key] = {}
    terminal["docker_shared_container_key"] = ""
    terminal["temp_dir"] = ""
    terminal["docker_mount_cwd_to_workspace"] = False
    if removed:
        ui.show("Main's mount/credential forwarding settings are not copied: " + ", ".join(removed))
    if backend == "local":
        terminal["cwd"] = str(destination / "workspace")
        ui.show("Environment: existing host software, separate project workspace. "
                "This is profile separation, NOT OS-level filesystem isolation. No software will be installed.")
        return terminal
    from sci_cli.science_profiles_sandbox import resolve_image, docker_command
    from sci_cli.science_profiles_environment import run_preparation
    image = terminal.get("docker_image") or DEFAULT_CONFIG["terminal"]["docker_image"]
    ui.show(f"Environment: Docker image {image}; separate container/workspace; no main credential mounts.")
    docker_command("version", "--format", "{{.Server.Version}}")
    try:
        terminal["docker_image"] = resolve_image(image)
    except ValueError:
        ui.choose(f"Configured image {image} is unavailable. Download it? Cached layers may remain after cancellation.",
                  ["Approve image download", "Cancel"])
        try:
            run_preparation(["pull", image], ui, cancel, stage="Downloading configured image", timeout=900)
        finally:
            ui.show("Image download attempt ended; downloaded layers may remain. No scientific task ran.")
        terminal["docker_image"] = resolve_image(image)
    terminal["cwd"] = "/workspace"
    terminal["docker_volumes"] = [f"{destination / 'workspace'}:/workspace:rw"]
    terminal["container_persistent"] = False
    return terminal
