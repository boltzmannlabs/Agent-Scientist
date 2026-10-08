"""Explicit offline migration of an existing user home to SCI.

The original is never modified. Stop all writers first. Credentials and stored
conversation data are copied, not globally search/replaced. Dependency generations
and disposable caches are rebuilt by PM, not transplanted into the new runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import shutil
import stat

from scripts.sci_namespace_migration import replace_names, rewrite

REBUILD = {"installs", "cache", "backups", "state-snapshots"}
EPHEMERAL = {"gateway.pid", "gateway.lock", "gateway.sock", "gateway_state.json",
             "processes.json", "spawn-ledger.json"}
CODE_ROOTS = {"skills", "plugins", "hooks", "skins"}
RUNTIME_ROOTS = {"bin", "venvs", "science-env", "science-bioservices-env", "tools", "node", "lsp"}


def relative_root(path: Path) -> str:
    parts = path.parts
    return parts[2] if len(parts) > 2 and parts[0] == "profiles" else parts[0]


def rebase(value: str, source: Path, destination: Path) -> str:
    """Replace an exact home path, never arbitrary occurrences in credential values."""
    if value == str(source):
        return str(destination)
    return value.replace(str(source) + "/", str(destination) + "/").replace(
        "/venvs/hermes-dev/", "/venvs/sci-dev/")


def settings(value, source: Path, destination: Path, path: tuple = ()):
    if isinstance(value, dict):
        result = value.copy()
        result.clear()
        for key, item in value.items():
            new_key = "SCI_" + key[7:] if isinstance(key, str) and key.startswith("HERMES_") else key
            if path == ("plugins", "entries"):
                new_key = replace_names(key)
            # Inline secrets are not branding. Even a value containing the old
            # product name must survive intact.
            secret = isinstance(key, str) and re.search(r"(?i)password|secret|token|api_key|authorization", key)
            reference = isinstance(item, str) and re.fullmatch(r"\$\{HERMES_[A-Z0-9_]+\}", item)
            result[new_key] = item if secret and not reference else settings(item, source, destination, (*path, key))
        return result
    if isinstance(value, list):
        return [settings(item, source, destination, path) for item in value]
    if isinstance(value, str):
        identifier = (path == ("skills",) or
                      len(path) == 2 and (path[0] == "platform_toolsets" or
                      path[0] in {"skills", "plugins"} and path[1] in {"enabled", "disabled"}))
        if identifier:
            value = replace_names(value)
        value = rebase(value, source, destination)
        value = re.sub(r"\$\{HERMES_([A-Z0-9_]+)\}", r"${SCI_\1}", value)
        if value in {"hermes", "hermes-cli", "hermes-cron", "hermes-agent"} or value.startswith("hermes_cli."):
            value = replace_names(value)
    return value


def _check_stopped(source: Path):
    marker = source / "gateway.pid"
    if marker.is_file():
        try:
            pid = int(marker.read_text().strip())
        except ValueError as exc:
            raise ValueError("Unrecognized gateway PID marker; inspect running processes first") from exc
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        raise RuntimeError("A gateway PID is still live; stop it before migrating")


def _files(source: Path):
    for directory, dirs, names in os.walk(source, followlinks=False):
        parent = Path(directory).relative_to(source)
        dirs[:] = [d for d in dirs if d != "__pycache__" and not (
            relative_root(parent / d) in REBUILD)]
        for name in [*names, *(d for d in dirs if (Path(directory) / d).is_symlink())]:
            relative = parent / name
            if name in EPHEMERAL or name.endswith((".lock", ".pid", ".sock", ".pyc")):
                continue
            yield relative


def _code_text(text: str, relative: Path, source: Path, destination: Path) -> str:
    # Never edit plugin Git objects or third-party runtime package sources.
    if ".git" in relative.parts:
        return text
    root = relative_root(relative)
    if relative.name in {"facts.json", "active.json", "install-stamp.json", ".install-metadata.json"}:
        return json.dumps(settings(json.loads(text), source, destination), indent=2) + "\n"
    if relative.name == "SOUL.md":
        return rewrite(rebase(text, source, destination), str(relative))
    if root in CODE_ROOTS and relative.suffix in {".py", ".md", ".yaml", ".yml", ".json", ".sh", ".toml"}:
        return rewrite(rebase(text, source, destination), str(relative))
    runtime_entry = root in RUNTIME_ROOTS and (
        "bin" in relative.parts or relative.name == "pyvenv.cfg" or relative.suffix == ".pth"
        or "__editable__" in relative.name or any("hermes_agent" in p for p in relative.parts))
    if runtime_entry:
        text = rebase(text, source, destination)
        owned = "hermes" in relative.name or any("hermes_agent" in p for p in relative.parts)
        return replace_names(text) if owned else text
    return text


def _reviewed_profile(home: Path, new_home: Path, source: Path, destination: Path):
    from sci_cli.config import read_user_config_raw, atomic_config_replace
    from sci_cli.science_profiles import config_digest

    needs_review = False
    config = home / "config.yaml"
    if config.is_file():
        old = read_user_config_raw(config)
        new = settings(old, source, destination)
        atomic_config_replace(new_home / "config.yaml", new)
        manifest = home / "science-profile.json"
        if manifest.is_file():
            spec = json.loads(manifest.read_text())
            needs_review = bool(spec.get("config_digest")) and not hmac.compare_digest(spec["config_digest"], config_digest(old))
            spec = settings(spec, source, destination)
            if spec.get("config_digest") and not needs_review:
                spec["config_digest"] = config_digest(new)
            (new_home / manifest.name).write_text(json.dumps(spec, indent=2) + "\n")

    # Carry a grant ONLY when the previous receipt matches this profile and key.
    # A key alone never becomes authorization as a side effect of migration.
    from agent.secret_scope import load_env_file
    from sci_cli.plugins_manifest import _portable_skill_namespace
    key = (load_env_file(home / ".env").get("BOLTZMANN_API_KEY") or "").strip()
    receipt = Path("plugin-data") / _portable_skill_namespace("boltzmann") / "state.json"
    path = home / receipt
    if key and path.is_file():
        state = json.loads(path.read_text())
        fingerprint = lambda directory: hashlib.sha256(f"{directory.resolve()}\0{key}".encode()).hexdigest()
        if isinstance(state.get("authorization"), str) and hmac.compare_digest(state["authorization"], fingerprint(home)):
            state["authorization"] = fingerprint(new_home)
            (new_home / receipt).write_text(json.dumps(state, indent=2) + "\n")
            (new_home / receipt).chmod(0o600)
    return needs_review


def migrate(source: Path, destination: Path) -> dict:
    source, destination = source.resolve(strict=True), destination.absolute()
    if destination.exists() or destination.is_symlink() or destination.is_relative_to(source):
        raise ValueError("Destination must be a new directory outside the old home")
    homes = [source]
    if (source / "profiles").is_dir():
        homes.extend(p for p in (source / "profiles").iterdir() if p.is_dir() and not p.is_symlink())
    for home in homes:
        _check_stopped(home)
    names = list(_files(source))
    mapped = {name: (name if ".git" in name.parts else Path(replace_names(str(name)))) for name in names}
    if len(set(mapped.values())) != len(mapped):
        raise ValueError("Home filename collision; migration has not started")
    needed = sum((source / name).lstat().st_size for name in names)
    if shutil.disk_usage(destination.parent).free < needed + 2 * 1024**3:
        raise ValueError("Insufficient disk space for a separate recoverable home")
    destination.mkdir(mode=0o700)
    # A failed migration stays inspectable but must never look ready.
    marker = destination / ".sci-migration-incomplete"
    marker.touch(mode=0o600)
    for directory, dirs, _ in os.walk(source, followlinks=False):
        parent = Path(directory).relative_to(source)
        dirs[:] = [d for d in dirs if d != "__pycache__" and relative_root(parent / d) not in REBUILD]
        for name in dirs:
            old_dir = Path(directory) / name
            if not old_dir.is_symlink():
                new_dir = destination / replace_names(str(parent / name))
                new_dir.mkdir(parents=True, exist_ok=True)
                shutil.copystat(old_dir, new_dir)
    count = 0
    for relative in names:
        old, new = source / relative, destination / mapped[relative]
        new.parent.mkdir(parents=True, exist_ok=True)
        mode = old.lstat().st_mode
        if stat.S_ISLNK(mode):
            link = os.readlink(old)
            target = Path(os.path.abspath(old.parent / link))
            if target.is_relative_to(source):
                mapped_target = destination / replace_names(str(target.relative_to(source)))
                link = os.path.relpath(mapped_target, new.parent)
            new.symlink_to(link)
        elif stat.S_ISREG(mode):
            shutil.copy2(old, new)
            if old.name == ".env":
                text = old.read_text()
                new.write_text(re.sub(r"(?m)^(\s*(?:export\s+)?)HERMES_([A-Z0-9_]+)(\s*=)", r"\1SCI_\2\3", text))
                new.chmod(0o600)
            elif old.stat().st_size < 10 * 1024**2:
                data = old.read_bytes()
                if b"\0" not in data:
                    try:
                        text = data.decode("utf-8")
                    except UnicodeDecodeError:
                        continue
                    updated = _code_text(text, relative, source, destination)
                    if updated != text:
                        new.write_text(updated)
            count += 1
            if count % 10000 == 0:
                print(f"Copied {count} files; original home unchanged.", flush=True)
        else:
            raise ValueError(f"Unsupported special file: {relative}")
    needs_review = []
    for home in homes:
        if _reviewed_profile(home, destination / replace_names(str(home.relative_to(source))), source, destination):
            needs_review.append(home.name)
        _check_stopped(home)
    marker.unlink()
    report = {"source": str(source), "destination": str(destination), "files": count,
              "original_modified": False, "runtime_rebuild_required": True,
              "existing_profiles_requiring_review": needs_review}
    (destination / "sci-migration.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(migrate(args.source, args.destination), indent=2))
