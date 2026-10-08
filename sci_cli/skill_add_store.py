"""Reviewed installation and next-session enablement; never clear prompt caches."""

from contextlib import contextmanager
from pathlib import Path
import shutil

from sci_cli.skill_add_sources import validate_bundle


def existing_skill(name: str) -> bool:
    from tools.skills_hub import HubLockFile
    from tools.skills_tool import _find_all_skills
    return (HubLockFile().get_installed(name) is not None
            or any(s.get("name") == name for s in _find_all_skills(skip_disabled=True)))


@contextmanager
def scanned_bundle(bundle):
    from tools.skills_hub_install import quarantine_bundle
    from tools.skills_guard import scan_skill
    validate_bundle(bundle)
    path = quarantine_bundle(bundle, unique=True)
    try:
        # Local rule scanner only: never send imports to an advisory LLM before consent.
        result = scan_skill(path, source="community")
        yield path, result
    finally:
        if path.exists():
            shutil.rmtree(path)


def enable_next_session(name: str) -> None:
    from sci_cli.config import atomic_config_write, read_user_config_raw
    from sci_constants import get_config_path
    from agent.skill_utils import parse_config_string_list

    config = read_user_config_raw()
    skills = config.get("skills", {})
    changed = False
    for section, key in ((skills, "disabled"), (skills.get("platform_disabled", {}), "cli")):
        values = parse_config_string_list(section.get(key))
        if name in values:
            section[key] = [v for v in values if v != name]
            changed = True
    if changed:
        atomic_config_write(get_config_path(), config)


def save_reviewed(bundle, staged: Path, scan):
    from tools.skill_manager_tool import _skill_mutation_lock
    from tools.skills_hub_install import install_from_quarantine
    from tools.skills_guard import should_allow_install

    if scan.verdict == "dangerous":
        raise ValueError("Dangerous skill blocked. Nothing was installed.")
    allowed, reason = should_allow_install(scan, force=True)
    if not allowed:
        raise ValueError(reason)
    with _skill_mutation_lock(bundle.name):
        if existing_skill(bundle.name):
            raise FileExistsError(f"A skill named {bundle.name} already exists. Choose a new name.")
        installed = install_from_quarantine(staged, bundle.name, "", bundle, scan, overwrite=False)
    try:
        enable_next_session(bundle.name)
    except Exception as exc:
        # Do not claim success or delete a successfully installed user's skill.
        return installed, f"Installed, but enablement failed ({type(exc).__name__}). Check skill settings; activation was not confirmed."
    return installed, "Enabled. Available automatically in your next session."
