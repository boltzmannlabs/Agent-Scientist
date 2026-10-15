"""Removal is a reviewed config operation, never a live-model switch or a credential purge."""

from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from sci_cli import provider_removal as removal
from sci_cli.config import atomic_config_replace, read_user_config_raw
from sci_cli.native_profile_creation import profile_scope


@pytest.fixture
def homes(tmp_path, monkeypatch):
    main = tmp_path / "sci"
    a, b = main / "profiles" / "a", main / "profiles" / "b"
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(main))
    for home in (main, a, b):
        home.mkdir(parents=True)
        atomic_config_replace(home / "config.yaml", {
            "model": {"provider": "openrouter", "default": "fixture-model"},
            "terminal": {"cwd": str(home / "workspace")},
            "skills": {"disabled": ["private-fixture"]},
            "mcp_servers": {"private": {"url": "https://research.invalid"}},
            "custom_providers": [{"name": "keep", "base_url": "http://localhost:54322/v1", "models": ["keep-model"]}],
        })
        (home / ".env").write_text("LAB_KEY=private-fixture\nBOLTZMANN_API_KEY=research-fixture\n")
        (home / "auth.json").write_text('{"credential_pool": {"lab": [{"access_token": "private-fixture"}]}}')
        (home / "sessions").mkdir()
        (home / "sessions" / "fixture.json").write_text('{"messages": [{"role": "user", "content": "keep history"}]}')
    # Catalog discovery is never needed by removal. Real picker reads are cache-only
    # here; unexpected external I/O fails instead of touching production providers.
    monkeypatch.setattr("agent.models_dev.fetch_models_dev", lambda **kw: {})
    from sci_cli import model_switch_providers as picker
    monkeypatch.setattr(picker, "_build_curated_lists", lambda *a, **kw: {})
    monkeypatch.setattr(picker, "_collect_authed_provider_slugs", lambda *a, **kw: [])
    monkeypatch.setattr(picker, "_lap_overlay_rows", lambda *a: None)
    monkeypatch.setattr(picker, "_lap_canonical_rows", lambda *a: None)
    monkeypatch.setattr(picker, "_discover_endpoint_models", lambda *a, **kw: (None, False))
    return main, a, b


def _seed(home, kind):
    cfg = read_user_config_raw(home / "config.yaml")
    entry = {"name": "lab", "base_url": "http://localhost:54321/v1", "api_key": "inline-private", "models": ["lab-model"]}
    if kind == "legacy":
        cfg["custom_providers"].append(entry)
    else:
        cfg["providers"] = {"lab": entry}
    atomic_config_replace(home / "config.yaml", cfg)


def _snapshot(homes):
    return {p: p.read_bytes() for home in homes for p in (
        home / "config.yaml", home / ".env", home / "auth.json", home / "sessions" / "fixture.json")}


@pytest.mark.parametrize("kind", ["legacy", "keyed"])
@pytest.mark.parametrize("scope", ["local", "shared", "everywhere"])
def test_removal_scopes_preserve_credentials_history_and_other_settings(homes, kind, scope):
    from sci_cli.inventory import load_picker_context, build_models_payload
    from sci_cli.runtime_provider import resolve_runtime_provider
    from agent.secret_scope import set_multiplex_active

    main, a, b = homes
    _seed(main, kind)
    _seed(b, kind)  # an independent local definition with the same identity
    before = _snapshot(homes)
    original = {h: read_user_config_raw(h / "config.yaml") for h in homes}
    owner = main if scope == "shared" else a
    set_multiplex_active(True)
    try:
        with profile_scope(owner):
            target = next(t for t in removal.targets(owner) if t.slug == ("custom:lab" if kind == "legacy" else "lab"))
            plan = removal.prepare(owner, target, everywhere=scope == "everywhere", live_provider="openrouter")
            assert _snapshot(homes) == before
            removal.apply(plan)
            for path, contents in before.items():
                if path.name != "config.yaml":
                    assert path.read_bytes() == contents
        for home in (a, b, a, main):
            with profile_scope(home):
                ctx = load_picker_context()
                rows = build_models_payload(ctx, probe_custom_providers=False)["providers"]
                hidden = scope != "local" or home == a
                assert any(r["name"] == "lab" for r in rows) is not hidden
                assert any(r["name"] == "keep" for r in rows)
                if hidden and not (scope == "shared" and home == b):
                    with pytest.raises(ValueError, match="disabled"):
                        resolve_runtime_provider(requested="custom:lab")
                else:
                    assert resolve_runtime_provider(requested="custom:lab")["base_url"] == "http://localhost:54321/v1"
    finally:
        set_multiplex_active(False)
    for home in homes:
        config = read_user_config_raw(home / "config.yaml")
        for key in ("model", "terminal", "skills", "mcp_servers"):
            assert config[key] == original[home][key]
        if scope == "everywhere":
            assert "inline-private" not in (home / "config.yaml").read_text()
        elif home != owner:
            assert (home / "config.yaml").read_bytes() == before[home / "config.yaml"]


class UI:
    def __init__(self, answers):
        self.answers = iter(answers)
        self.messages = []

    def show(self, message):
        self.messages.append(message)

    def choose(self, question, choices):
        from sci_cli.skill_add import Cancelled
        answer = next(self.answers)
        assert answer in choices
        if answer == "Cancel":
            raise Cancelled()
        return answer


def test_removal_menu_only_lists_active_profile_inventory(homes):
    from sci_cli.inventory import load_picker_context, build_models_payload

    main, a, b = homes
    _seed(main, "legacy")
    config = read_user_config_raw(b / "config.yaml")
    config["model_catalog"] = {"excluded_providers": ["custom:lab"]}
    atomic_config_replace(b / "config.yaml", config)
    cli = SimpleNamespace(provider="openrouter", model="fixture-model", base_url="")
    for home in (main, a, b, a):
        with profile_scope(home):
            rows = build_models_payload(load_picker_context(), probe_custom_providers=False)["providers"]
            expected = {"custom:keep"} if home == b else {"custom:keep", "custom:lab"}
            # Both the existing picker action and standalone /model remove use
            # the same availability filter, not the complete static catalog.
            for source_rows in (rows, None):
                items = removal._available_targets(cli, home, source_rows)
                assert {item.slug for item in items} == expected
            ui = UI([])
            before = (home / "config.yaml").read_bytes()
            removal.run(cli, rows=[], ui=ui)
            assert ui.messages == ["No available removable providers in this profile. Nothing changed."]
            assert (home / "config.yaml").read_bytes() == before


@pytest.mark.parametrize("kind", ["legacy", "keyed"])
def test_grouped_available_provider_exposes_only_its_actual_definitions(homes, kind):
    from sci_cli.inventory import load_picker_context, build_models_payload

    main, a, b = homes
    config = read_user_config_raw(main / "config.yaml")
    entries = [{"name": f"Lab — {model}", "base_url": "http://localhost:54323/v1", "models": [model]}
               for model in ("one", "two")]
    if kind == "legacy":
        config["custom_providers"].extend(entries)
        expected = {"custom:lab-—-one", "custom:lab-—-two"}
    else:
        config["providers"] = dict(zip(("lab-one", "lab-two"), entries))
        expected = {"lab-one", "lab-two"}
    atomic_config_replace(main / "config.yaml", config)
    with profile_scope(a):
        rows = build_models_payload(load_picker_context(), probe_custom_providers=False)["providers"]
        group = next(row for row in rows if row["name"] == "Lab")
        cli = SimpleNamespace(provider="openrouter", model="fixture-model", base_url="")
        assert {item.slug for item in removal._available_targets(cli, a, [group])} == expected


@pytest.mark.parametrize("case", ["cancel", "active", "active-auto", "default", "auxiliary", "ambiguous", "managed", "stale", "new-profile", "partial", "save"])
def test_review_refusals_and_atomic_save_report_actual_outcome(homes, monkeypatch, case):
    main, a, b = homes
    _seed(main, "legacy")
    if case in {"default", "auxiliary"}:
        cfg = read_user_config_raw(b / "config.yaml")
        cfg["model" if case == "default" else "auxiliary"] = {"provider": "custom:lab", "default": "lab-model"}
        atomic_config_replace(b / "config.yaml", cfg)
    if case == "ambiguous":
        cfg = read_user_config_raw(b / "config.yaml")
        cfg["providers"] = {"different-account": {"name": "lab", "base_url": "https://other.invalid"}}
        atomic_config_replace(b / "config.yaml", cfg)
    if case == "managed":
        monkeypatch.setattr("sci_cli.managed_scope.managed_config_keys", lambda: {"model_catalog.excluded_providers"})
    before = _snapshot(homes)
    cli = SimpleNamespace(provider="custom:lab" if case.startswith("active") else "openrouter",
                          requested_provider="auto" if case == "active-auto" else "",
                          base_url="", model="fixture-model", conversation_history=[{"role": "user", "content": "hello"}],
                          agent=SimpleNamespace(system_prompt="byte-stable", tools=["existing"]))
    live = deepcopy(vars(cli))
    ui = UI(["Delete provider definitions in main and all profiles", "Cancel" if case == "cancel" else "Confirm removal"])
    real_apply = removal.apply

    def apply(plan):
        if case == "stale":
            config = read_user_config_raw(b / "config.yaml")
            config["display"] = {"skin": "fixture"}
            atomic_config_replace(b / "config.yaml", config)
        if case == "new-profile":
            extra = main / "profiles" / "new"
            extra.mkdir()
            atomic_config_replace(extra / "config.yaml", {"model": {"provider": "custom:lab"}})
        return real_apply(plan)

    monkeypatch.setattr(removal, "apply", apply)
    if case == "partial":
        def fail_second(path, config):
            if path.parent == a:
                raise OSError("private-fixture MUST NOT BE LOGGED")
            atomic_config_replace(path, config)
        monkeypatch.setattr("sci_cli.config.atomic_config_replace", fail_second)
    with profile_scope(a):
        removal.run(cli, "lab", ui=ui)
    assert vars(cli) == live
    text = "\n".join(ui.messages)
    assert "inline-private" not in text and "private-fixture" not in text
    assert "Provider removed" in text if case == "save" else "Provider removed" not in text
    if case in {"cancel", "active", "active-auto", "default", "auxiliary", "ambiguous", "managed"}:
        assert _snapshot(homes) == before
    elif case in {"stale", "new-profile"}:
        assert "changed" in text
        assert (main / "config.yaml").read_bytes() == before[main / "config.yaml"]
    elif case == "partial":
        assert "No rollback was attempted" in text and str(main / "config.yaml") in text
        assert (b / "config.yaml").read_bytes() == before[b / "config.yaml"]
    else:
        assert "Saved keys in .env/auth.json and external logins are retained" in text
