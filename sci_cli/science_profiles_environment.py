"""Guided sandbox preparation; metadata, download, and execution are separate grants."""

import json
from pathlib import Path
import re
import subprocess
import tempfile
import time
import uuid

from sci_cli.skill_add import Cancelled
from sci_cli.science_profiles_sandbox import docker_command, resolve_image

STANDARD = "Standard isolated workspace (recommended)"
ADVANCED = "Choose an installed environment (advanced)"


def requirements(home: Path, skills: list[str]):
    from agent.skill_utils import parse_frontmatter
    commands, notes = {"bash"}, []
    for name in skills:
        root = (home / "skills" / name).resolve(strict=True)
        if not root.is_relative_to((home / "skills").resolve()):
            raise ValueError("Skill requirements must come from the selected profile's skills.")
        metadata, _ = parse_frontmatter((root / "SKILL.md").read_text(encoding="utf-8"))
        prereqs = metadata.get("prerequisites") or {}
        prereqs = prereqs if isinstance(prereqs, dict) else {}
        declared = metadata.get("required_commands") or prereqs.get("commands") or []
        declared = [declared] if isinstance(declared, str) else declared
        if isinstance(declared, list):
            for item in declared:
                if isinstance(item, str) and re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.+-]{0,100}", item):
                    commands.add(item)
        notes.append({"skill": name, "declared_commands": declared, "dependencies": metadata.get("deps", []),
                      "prerequisites": prereqs, "compatibility": metadata.get("compatibility", "Not declared")})
    return sorted(commands), notes


def installed_images():
    docker_command("version", "--format", "{{.Server.Version}}")
    rows = docker_command("image", "ls", "--no-trunc", "--format", "{{json .}}")
    result = {}
    for line in rows.splitlines():
        row = json.loads(line)
        image_id = row["ID"]
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", image_id):
            raise ValueError("Docker returned an invalid environment identity.")
        tag = f"{row['Repository']}:{row['Tag']}"
        result.setdefault(image_id, []).append(tag)
    return result


def run_preparation(args, ui, cancel, *, stage, timeout):
    """Owned process, bounded wait, progress, and no pipe backpressure on image pulls."""
    from tools.environments.docker import find_docker
    executable = find_docker()
    if not executable:
        raise ValueError("The isolation service (Docker) is unavailable. Install/start it and retry; host execution will not be used.")
    if cancel.is_set():
        raise Cancelled()
    start, heartbeat = time.monotonic(), 0
    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8", errors="replace") as output:
        proc = subprocess.Popen([executable, *args], stdout=output, stderr=subprocess.STDOUT)
        try:
            while proc.poll() is None:
                elapsed = time.monotonic() - start
                if cancel.is_set():
                    raise Cancelled()
                if elapsed > timeout:
                    raise TimeoutError(f"{stage} exceeded {timeout} seconds; this attempt stopped.")
                if elapsed >= heartbeat:
                    ui.show(f"[Environment] {stage}: {elapsed:.0f}s elapsed. Ctrl+C cancels.")
                    heartbeat += 10
                try:
                    proc.wait(timeout=0.2)
                except subprocess.TimeoutExpired:
                    continue
            if cancel.is_set():
                raise Cancelled()
            if proc.returncode:
                raise ValueError(f"{stage} failed (exit {proc.returncode}). Check Docker, registry access, or the selected environment. No profile was created.")
            output.seek(0)
            return output.read(100_000)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)


def check_commands(image_id, commands, ui, cancel):
    # Execute only a fixed availability check, not user/skill-provided shell text.
    probe = "sci-profile-check-" + uuid.uuid4().hex
    script = 'for tool in "$@"; do command -v -- "$tool" >/dev/null 2>&1 || printf "%s\\n" "$tool"; done; true'
    args = ["run", "--rm", "--pull=never", "--name", probe, "--network=none", "--read-only",
            "--cap-drop=ALL", "--security-opt=no-new-privileges", "--pids-limit=64",
            "--memory=256m", "--cpus=1", "--entrypoint=/bin/bash", image_id,
            "--noprofile", "--norc", "-c", script, "requirements-check", *commands]
    try:
        output = run_preparation(args, ui, cancel, stage="Checking command availability", timeout=60)
        return [line for line in output.splitlines() if line in commands]
    finally:
        # --rm handles the normal case. A killed Docker client may leave its
        # container running; resolve only this attempt's unpredictable name.
        try:
            ids = docker_command("ps", "-aq", "--filter", f"name=^/{probe}$").split()
            if ids:
                if any(not re.fullmatch(r"[a-f0-9]{12,64}", cid) for cid in ids):
                    raise ValueError("Unexpected container identity")
                docker_command("rm", "-f", *ids)
        except Exception as exc:
            raise RuntimeError(f"The requirements check stopped, but cleanup could not be confirmed for {probe}. "
                               "Check Docker for that container. Downloaded image layers may remain.") from exc


def choose_environment(home, skills, mcp_tools, ui, cancel):
    from sci_cli.config_defaults import DEFAULT_SANDBOX_IMAGE
    commands, notes = requirements(home, skills)
    ui.show("Your tools and skills are selected. Next, prepare their isolated workspace. "
            "A standard workspace is a general starting point, not an antibody generator or a guarantee "
            "that specialist scientific software is installed. Remote MCP tools run at their service, not inside this workspace.\n"
            f"Selected remote tools: {sum(len(v) for v in mcp_tools.values())}.\n"
            "Declared skill requirements (untrusted metadata; never installation commands):\n" + json.dumps(notes, indent=2))
    while True:
        mode = ui.choose("How should we prepare the isolated workspace?", (STANDARD, ADVANCED, "Cancel"))
        ui.choose("Check which isolated environments are available on this computer? Metadata only; no download or execution.",
                  ("Check available environments", "Cancel"))
        images = installed_images()
        if mode == STANDARD:
            image = next((i for i, tags in images.items() if DEFAULT_SANDBOX_IMAGE in tags), None)
            if image is None:
                ui.show(f"The standard workspace is not installed. Download source: Docker registry image {DEFAULT_SANDBOX_IMAGE}. "
                        "This may use substantial disk space and bandwidth. It will not run software or upload research files. "
                        "Downloaded layers may remain if you cancel later.")
                choice = ui.choose("Download the standard workspace?", ("Approve download", ADVANCED, "Cancel"))
                if choice == ADVANCED:
                    mode = ADVANCED
                else:
                    try:
                        run_preparation(["pull", DEFAULT_SANDBOX_IMAGE], ui, cancel, stage="Downloading standard workspace", timeout=900)
                    finally:
                        ui.show("Download attempt ended. Downloaded/cached image layers may remain on this computer; no profile has been created yet.")
                    image = DEFAULT_SANDBOX_IMAGE
        if mode == ADVANCED:
            labels = {f"{', '.join(tags)} ({image_id[7:19]})": image_id for image_id, tags in images.items()}
            choice = ui.choose("Choose an installed environment, or enter its name (advanced).",
                               (*labels, "Enter an installed image name", "Back", "Cancel"))
            if choice == "Back":
                continue
            image = ui.ask("Installed Docker image name or ID:") if choice == "Enter an installed image name" else labels[choice]
        image_id = resolve_image(image)
        checks = sorted(set(commands) | ({"python3"} if mode == STANDARD else set()))
        ui.show(f"Environment: {image_id}\nCheck: Bash 'command -v' for {', '.join(checks)}. "
                "This starts a temporary container with no network, credentials, or project files, and removes it afterward. "
                "It does not run the scientific tools, install dependencies, or check scientific correctness.")
        ui.choose("Run this isolated requirements check?", ("Approve check", "Cancel"))
        missing = check_commands(image_id, checks, ui, cancel)
        if missing:
            ui.show("Missing commands: " + ", ".join(missing) + ". Choose a prepared environment containing them. "
                    "No installation commands will be invented or run, and this profile has not been saved.")
            ui.choose("The selected environment cannot meet the declared requirements.", ("Choose another environment", "Cancel"))
            continue
        ui.show("Declared command-availability checks passed. Dependencies, versions, datasets, GPU requirements, "
                "and requirements written only in prose are not verified. No scientific task has run.")
        if ui.choose("Review the skill requirements above. Continue with this workspace?", ("Use this workspace", "Choose another environment", "Cancel")) == "Use this workspace":
            return image_id
