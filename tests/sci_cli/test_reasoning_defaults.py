"""Fresh installations hide thoughts without disabling model reasoning."""

import pytest

from sci_cli.cli_config_load import _cli_config_defaults
from sci_cli.config import load_config_readonly, seed_config_file
from sci_constants import resolve_reasoning_config


@pytest.mark.parametrize("template", [True, False])
def test_fresh_reasoning_default_and_explicit_override(tmp_path, monkeypatch, template):
    monkeypatch.setenv("SCI_HOME", str(tmp_path))
    seed_config_file(tmp_path / "config.yaml", None if template else tmp_path / "missing-template")
    config = load_config_readonly()
    assert resolve_reasoning_config(config) == {"enabled": True, "effort": "medium"}
    assert config["display"]["show_reasoning"] is False
    assert _cli_config_defaults()["display"]["show_reasoning"] is False
    assert resolve_reasoning_config(_cli_config_defaults()) == resolve_reasoning_config(config)
    assert resolve_reasoning_config({}) is None  # Raw absent config defers to provider defaults.
    config["agent"]["reasoning_effort"] = "xhigh"
    assert resolve_reasoning_config(config) == {"enabled": True, "effort": "xhigh"}
    config["agent"]["reasoning_overrides"] = {"qwen3.8-27b": "none"}
    assert resolve_reasoning_config(config, "qwen3.8-27b") == {"enabled": False}
