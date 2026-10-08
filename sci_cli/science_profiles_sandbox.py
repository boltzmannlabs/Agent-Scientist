"""Fail-closed preflight for isolated research profiles; never installs Docker/images."""

import json
from pathlib import Path
import subprocess
import re


def docker_command(*args):
    from tools.environments.docker import find_docker
    executable = find_docker()
    if not executable:
        raise ValueError("Docker is required. Install/start Docker and retry; local execution is not a fallback.")
    result = subprocess.run([executable, *args], capture_output=True, text=True, timeout=15)
    if result.returncode:
        raise ValueError("Docker check failed. Start Docker and ensure the requested image is installed. No image was downloaded and no local fallback was used.")
    return result.stdout


def resolve_image(image: str) -> str:
    docker_command("version", "--format", "{{.Server.Version}}")
    records = json.loads(docker_command("image", "inspect", image))
    info = records[0]
    if info.get("Config", {}).get("Volumes"):
        raise ValueError("Choose an image without declared volumes; project mounts must be explicit.")
    return info["Id"]


def cleanup_owned_containers(profile: str, session: str):
    """Recover even after a hard-killed worker, without touching other sessions."""
    from tools.environments.docker import _sanitize_label_value
    ids = docker_command("ps", "-aq", "--filter", "label=sci-agent=1",
                         "--filter", f"label=sci-profile={_sanitize_label_value(profile)}",
                         "--filter", f"label=sci-task-id={_sanitize_label_value(session)}").split()
    if any(not re.fullmatch(r"[a-f0-9]{12,64}", cid) for cid in ids):
        raise ValueError("Unexpected Docker container identity; cleanup needs operator review.")
    if ids:
        docker_command("rm", "-f", *ids)


def validate_runtime(home: Path):
    from sci_cli.config import read_user_config_raw
    from sci_cli.science_profiles import read_spec, config_digest, regular_files
    spec = read_spec(home)
    config = read_user_config_raw(home / "config.yaml")
    if not spec.config_digest or config_digest(config) != spec.config_digest:
        raise ValueError("Reviewed model/sandbox settings changed. Recreate the profile to approve the new configuration; execution was blocked.")
    terminal = config.get("terminal", {})
    required = {"backend": "docker", "docker_image": spec.image, "docker_network": False,
                "docker_mount_cwd_to_workspace": False, "docker_extra_args": [],
                "docker_shared_container_key": "", "env_passthrough": [], "cwd": "/workspace",
                "container_persistent": False}
    if any(terminal.get(k) != v for k, v in required.items()):
        raise ValueError("Project sandbox settings changed. Review/recreate the profile; execution was blocked.")
    expected = [f"{home / 'workspace'}:/workspace:rw"]
    workspace = home / "workspace"
    if not workspace.is_dir() or workspace.resolve() != workspace.absolute():
        raise ValueError("Project workspace moved or became a symlink; execution was blocked.")
    for index, source in enumerate(spec.sources):
        if source.location.startswith("https://"):
            continue
        if not spec.allow_llm_sources:
            continue
        path = Path(source.location)
        if not path.exists() or path.is_symlink() or str(path.resolve()) != str(path):
            raise ValueError(f"Project source moved or became a symlink: {path}")
        regular_files(path)
        if spec.allow_llm_sources:
            expected.append(f"{path}:/sources/{index}:ro")
    if terminal.get("docker_volumes") != expected:
        raise ValueError("Project mounts differ from the reviewed sources; execution was blocked.")
    if config.get("plugins", {}).get("enabled") != []:
        raise ValueError("Host-loaded plugins are not isolated; execution was blocked.")
    for name, cfg in config.get("mcp_servers", {}).items():
        if name not in spec.mcp_tools or cfg.get("command") or not cfg.get("url", "").startswith("https://"):
            raise ValueError("Unreviewed/local MCP connection in isolated profile.")
        if cfg.get("tools", {}).get("include") != spec.mcp_tools[name]:
            raise ValueError("MCP permissions differ from the reviewed allowlist.")
    regular_files(home / "skills")
    if spec.setup_pending:
        if config.get("platform_toolsets", {}).get("cli") != ["skills", *spec.mcp_tools]:
            raise ValueError("Local tools cannot be enabled before isolated setup is approved.")
    else:
        resolve_image(spec.image)
    return spec
