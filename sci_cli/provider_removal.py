"""Reviewed provider removal for /model; never changes a running agent or its history."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import shlex


class RemovalError(ValueError):
    """A safe-to-display refusal (never includes configuration values or credentials)."""


@dataclass
class Target:
    slug: str
    label: str
    aliases: set[str] = field(default_factory=set)
    urls: set[str] = field(default_factory=set, repr=False)


@dataclass
class Plan:
    target: Target
    home: Path
    everywhere: bool
    snapshots: dict = field(repr=False)
    desired: dict = field(repr=False)
    affected: list[str]


def _norm(value):
    return str(value or "").strip().lower()


def _definitions(config):
    for key, entry in (config.get("providers") or {}).items():
        if isinstance(entry, dict) and entry != {"enabled": False}:
            yield str(key), entry
    for entry in config.get("custom_providers") or []:
        if isinstance(entry, dict) and entry.get("name"):
            yield "", entry


def _aliases(key, entry):
    from sci_cli.providers import custom_provider_aliases
    return set(custom_provider_aliases(entry.get("name", ""), key))


def _url(entry):
    from sci_cli.route_identity import normalize_route_base_url
    return normalize_route_base_url(str(entry.get("base_url") or entry.get("api") or entry.get("url") or ""))


def _homes(home):
    from sci_constants import get_default_sci_root
    from sci_cli.profiles import _iter_named_profile_dirs
    root = get_default_sci_root(home=home)
    return list(dict.fromkeys([root, *_iter_named_profile_dirs(profiles_root=root / "profiles"), home]))


def _read(home):
    from sci_cli.config import require_readable_config_before_write
    path = home / "config.yaml"
    if home.is_symlink() or path.is_symlink():
        raise RemovalError(f"Refusing to modify linked configuration in {home.name}; unlink it explicitly first.")
    return require_readable_config_before_write(path)


def targets(home, rows=()):
    """Read local definitions and static identities only: no discovery, auth refresh or probes."""
    from sci_cli.models_catalog_static import CANONICAL_PROVIDERS
    from sci_cli.providers import ALIASES, custom_provider_slug
    from sci_constants import get_default_sci_root

    result = {p.slug: Target(p.slug, p.label, {p.slug}) for p in CANONICAL_PROVIDERS}
    for alias, canonical in ALIASES.items():
        if canonical in result:
            result[canonical].aliases.add(alias)
    for owner in dict.fromkeys([get_default_sci_root(home=home), home]):
        for key, entry in _definitions(_read(owner)):
            slug = key or custom_provider_slug(entry["name"])
            item = result.setdefault(slug, Target(slug, str(entry.get("name") or slug)))
            item.aliases.update(_aliases(key, entry))
            if _url(entry):
                item.urls.add(_url(entry))
    for row in rows:
        slug = row.get("slug", "")
        # Grouped custom rows can combine several separately named definitions.
        # Offer those actual definitions above, not an ambiguous synthetic identity.
        if (slug and not slug.startswith("custom:")
                and not any(_norm(slug) in item.aliases for item in result.values())):
            result[slug] = Target(slug, row.get("name") or slug, {slug})
    # Bare custom is a route, not a named provider; deleting it would affect unrelated endpoints.
    return sorted((v for k, v in result.items() if k not in {"custom", "moa"}), key=lambda t: t.label.lower())


def _matches(value, target):
    return _norm(value) in target.aliases


def _references(config, target, prefix=""):
    """Find defaults, auxiliary routes and fallback slots, not stored provider definitions."""
    if isinstance(config, dict):
        if _matches(config.get("provider"), target):
            yield prefix + ".provider"
        elif _norm(config.get("provider")) in {"", "custom", "auto"} and _url(config) in target.urls:
            yield prefix + ".base_url"
        for key, value in config.items():
            if not prefix and key in {"providers", "custom_providers", "model_catalog"}:
                continue
            yield from _references(value, target, f"{prefix}.{key}".lstrip("."))
    elif isinstance(config, list):
        for index, value in enumerate(config):
            yield from _references(value, target, f"{prefix}[{index}]")


def _check_managed(target):
    from sci_cli.config import is_managed
    from sci_cli.managed_scope import managed_config_keys
    keys = managed_config_keys()
    prefixes = {"custom_providers", "model_catalog.excluded_providers"}
    prefixes.update(f"providers.{alias}" for alias in target.aliases)
    if is_managed() or any(k == p or k.startswith(p + ".") for k in keys for p in prefixes):
        raise RemovalError("This provider configuration is managed by your administrator; it cannot be removed here.")


def prepare(home, target, *, everywhere, live_provider="", live_url=""):
    from sci_constants import get_default_sci_root
    from sci_cli.route_identity import normalize_route_base_url
    from sci_cli.providers import custom_provider_slug
    _check_managed(target)
    all_homes = _homes(home)
    root = get_default_sci_root(home=home)
    # Main's exclusions are shared; review every dependent profile even for a main-only hide.
    inspected = all_homes if everywhere or home == root else [home]
    snapshots, configs = {}, {}
    target = deepcopy(target)
    for owner in inspected:
        path = owner / "config.yaml"
        snapshots[path] = path.read_bytes() if path.exists() else None
        configs[owner] = _read(owner)
        if (path.read_bytes() if path.exists() else None) != snapshots[path]:
            raise RemovalError("Configuration changed while reading; reopen removal to review again.")
        for key, entry in _definitions(configs[owner]):
            if target.aliases.intersection(_aliases(key, entry)):
                if custom_provider_slug(entry.get("name", ""), key) != custom_provider_slug(target.slug):
                    raise RemovalError("Multiple provider definitions share this name/alias. Give them distinct names before removal; nothing changed.")
                target.aliases.update(_aliases(key, entry))
                if _url(entry):
                    target.urls.add(_url(entry))
    if _matches(live_provider, target) or (
        _norm(live_provider) in {"", "custom", "auto"} and normalize_route_base_url(live_url) in target.urls
    ):
        raise RemovalError("This conversation is using that provider. Select another provider with /model first, then retry removal.")
    blockers = [f"{('main' if owner == root else owner.name)}: {ref}"
                for owner, config in configs.items() for ref in _references(config, target)]
    if blockers:
        raise RemovalError("Provider is still selected in saved settings: " + "; ".join(blockers) +
                           ". Choose replacements first (/model <model> --provider <provider> --global for a profile default). Nothing changed.")
    desired = {}
    for owner in (inspected if everywhere else [home]):
        config = deepcopy(configs[owner])
        providers = config.setdefault("providers", {})
        for key, entry in list(providers.items()):
            if isinstance(entry, dict) and target.aliases.intersection(_aliases(key, entry)):
                if everywhere:
                    del providers[key]
                else:
                    entry["enabled"] = False
        if everywhere and "custom_providers" in config:
            config["custom_providers"] = [e for e in config["custom_providers"]
                                           if not isinstance(e, dict) or not target.aliases.intersection(_aliases("", e))]
        # Tombstones stop retained/shared logins from silently reintroducing the provider.
        for alias in sorted(target.aliases):
            providers.setdefault(alias, {})["enabled"] = False
        catalog = config.setdefault("model_catalog", {})
        catalog["excluded_providers"] = list(dict.fromkeys([
            *catalog.get("excluded_providers", []), *sorted(target.aliases)]))
        desired[owner / "config.yaml"] = config
    return Plan(target, home, everywhere, snapshots, desired,
                ["main" if p == root else p.name for p in inspected])


def apply(plan):
    """Recheck reviewed state, then atomically replace each file; report partial failure honestly."""
    from sci_cli.config import atomic_config_replace
    from sci_cli.config_backups import backup_config
    from sci_constants import get_default_sci_root
    _check_managed(plan.target)
    shared_scope = plan.everywhere or plan.home == get_default_sci_root(home=plan.home)
    if shared_scope and set(_homes(plan.home)) != {p.parent for p in plan.snapshots}:
        raise RemovalError("The profile list changed; reopen removal to review again. Nothing changed.")
    def unchanged(path):
        return (not path.parent.is_symlink() and not path.is_symlink()
                and (path.read_bytes() if path.exists() else None) == plan.snapshots[path])
    if not all(unchanged(p) for p in plan.snapshots):
        raise RemovalError("Configuration changed since review; reopen removal. Nothing changed.")
    saved, backups = [], []
    try:
        for path, config in plan.desired.items():
            if not unchanged(path):
                raise RemovalError("Configuration changed during saving.")
            backup = backup_config(path, "provider-removal")
            if backup:
                backups.append(str(backup))
            atomic_config_replace(path, config)
            saved.append(str(path))
    except Exception as exc:
        # Never echo YAML parsing errors: they can include literal credentials.
        raise RemovalError(f"Removal stopped ({type(exc).__name__}). Saved files: " +
                           (", ".join(saved) or "none") + ". Backups: " +
                           (", ".join(backups) or "none") + ". No rollback was attempted.") from exc
    return backups


def _available_targets(cli, home, rows):
    """Intersect removal identities with the model picker's active-profile inventory."""
    if rows is None:
        from sci_cli.inventory import load_picker_context, build_models_payload
        ctx = load_picker_context().with_overrides(
            current_provider=getattr(cli, "provider", "") or "",
            current_model=getattr(cli, "model", "") or "",
            current_base_url=getattr(cli, "base_url", "") or "")
        rows = build_models_payload(
            ctx, probe_custom_providers=False, probe_current_custom_provider=False,
            non_blocking_catalogs=True)["providers"]
    visible = {_norm(identity) for row in rows
               for identity in [row.get("slug", ""), *row.get("provider_aliases", [])] if identity}
    return [item for item in targets(home, rows) if item.aliases.intersection(visible)]


def run(cli, requested="", rows=None, *, ui=None):
    from sci_constants import get_sci_home, get_default_sci_root
    from sci_cli.skill_add import WizardUI, Cancelled
    ui = ui or WizardUI(cli)
    home = get_sci_home()
    try:
        if requested:
            items = targets(home, rows or ())
            matches = [item for item in items if _matches(requested, item)]
            exact = [item for item in matches if item.slug == requested]
            matches = exact or matches
            if len(matches) != 1:
                raise RemovalError("Provider name is unknown or ambiguous. Use /model remove and select its exact entry.")
            target = matches[0]
        else:
            items = _available_targets(cli, home, rows)
            if not items:
                ui.show("No available removable providers in this profile. Nothing changed.")
                return
            choices = {f"{item.label} [{item.slug}]": item for item in items}
            target = choices[ui.choose("Remove a provider and its model-list entries:", [*choices, "Cancel"])]
        hide = ("Hide from main's shared catalog" if home == get_default_sci_root(home=home)
                else "Hide in this profile only")
        scope = ui.choose("Choose removal scope:", [hide, "Delete provider definitions in main and all profiles", "Cancel"])
        live = [getattr(cli, "requested_provider", ""), getattr(cli, "provider", "")]
        plan = prepare(home, target, everywhere=scope.startswith("Delete"),
                       live_provider=next((p for p in live if _matches(p, target)), next((p for p in live if p), "")),
                       live_url=getattr(cli, "base_url", "") or "")
        ui.show(f"Provider: {target.label} [{target.slug}]\nScope: {scope}\n"
                f"Affected profiles: {', '.join(plan.affected)}\n"
                "All models from this provider disappear from the affected pickers. "
                "Built-in provider code and local model files are not uninstalled.\n"
                "Hiding main's shared catalog does not revoke independent profile overrides.\n"
                "Delete removes custom definitions and inline credentials; hide retains them. "
                "Saved keys in .env/auth.json and external logins are retained, not revoked. "
                "Use sci auth remove separately to manage saved credentials.\n"
                "Config backups may retain old definitions/inline keys. Conversations and running agents are not changed.")
        ui.choose("Confirm this provider change?", ["Confirm removal", "Cancel"])
        # A switch while the modal was open invalidates the approval's scope.
        if get_sci_home() != home:
            raise RemovalError("Active profile changed; restart removal. Nothing changed.")
        backups = apply(plan)
        ui.show(f"Provider {'removed' if plan.everywhere else 'hidden'}: {target.label}. "
                "Reopen /model to see the updated list. Existing conversations are unchanged; "
                "restart other running sessions to pick up the settings. Saved logins were retained.")
        if backups:
            ui.show("Config backups: " + ", ".join(backups))
    except Cancelled:
        ui.show("Provider removal cancelled. Nothing changed.")
    except RemovalError as exc:
        ui.show(str(exc))
    except Exception as exc:
        ui.show(f"Provider removal stopped ({type(exc).__name__}); no further work is running.")


def dispatch(cli, arguments, rows=None):
    """Return whether this is the reserved /model remove subcommand."""
    if arguments.split(None, 1)[:1] != ["remove"]:
        return False
    from cli import _cprint
    try:
        parts = shlex.split(arguments)
    except ValueError:
        _cprint("Unclosed quote. Usage: /model remove [provider]")
        return True
    if len(parts) > 2:
        _cprint('Usage: /model remove [provider] — quote names containing spaces.')
        return True
    from agent.memory_provider import spawn_context_thread
    args = (cli, parts[1] if len(parts) == 2 else "", rows)
    if getattr(cli, "_app", None):
        spawn_context_thread(run, name="provider-removal", args=args).start()
    else:
        run(*args)
    return True
