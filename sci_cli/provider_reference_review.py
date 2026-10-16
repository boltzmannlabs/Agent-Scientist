"""Review saved model routes affected by an explicit provider removal."""

from copy import deepcopy


def slots(config, target, path=()):
    from sci_cli.provider_removal import _matches, _norm, _url
    if isinstance(config, dict):
        if (_matches(config.get("provider"), target) or
                (_norm(config.get("provider")) in {"", "auto", "custom"} and _url(config) in target.urls)):
            yield path, config
        for key, value in config.items():
            if not path and key in {"providers", "custom_providers", "model_catalog"}:
                continue
            yield from slots(value, target, (*path, key))
    elif isinstance(config, list):
        for index, value in enumerate(config):
            yield from slots(value, target, (*path, index))


def apply_replacements(config, target, replacements):
    from sci_cli.provider_removal import RemovalError, _matches
    result = deepcopy(config)
    for path, slot in slots(result, target):
        if path not in replacements:
            raise RemovalError("Saved model references still need review; nothing changed.")
        replacement = replacements[path]
        if replacement is not None and (_matches(replacement.get("provider"), target) or
                                         not replacement.get("provider") or not replacement.get("model")):
            raise RemovalError("Choose a different provider and a model, or leave this route unconfigured.")
        # An explicit unconfigured route fails closed; auto would inherit another login.
        for key in ("provider", "default", "model", "base_url", "api_key", "key_env", "api_key_env", "api_mode", "api_key_cmd", "key_cmd"):
            slot.pop(key, None)
        slot["provider"] = replacement["provider"] if replacement else "unconfigured"
        if replacement:
            slot["default" if path == ("model",) else "model"] = replacement["model"]
    return result


def review(ui, configs, target, root):
    reviewed = {}
    for owner, config in configs.items():
        replacements = {}
        for path, _ in slots(config, target):
            label = ("main" if owner == root else owner.name) + ": " + ".".join(map(str, path))
            action = ui.choose(f"{label} uses {target.label}. After removal:",
                               ["Choose a replacement provider/model", "Leave unconfigured", "Cancel"])
            replacement = None
            if action.startswith("Choose"):
                replacement = {"provider": ui.ask("Replacement provider ID (as shown in /model):").strip(),
                               "model": ui.ask("Replacement model ID:").strip()}
            replacements[path] = replacement
        if replacements:
            reviewed[owner] = replacements
    return reviewed
