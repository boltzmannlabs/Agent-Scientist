"""Unsupported private imports fail clearly; public-context plugins still load."""
from pathlib import Path

from sci_cli.config import atomic_config_write
from sci_cli.plugins import PluginManager
from sci_cli.plugin_validate import ValidationReport, _check_requires_sci


def test_external_requirement_validation_and_private_import_remedy(tmp_path, monkeypatch):
    report = ValidationReport()
    _check_requires_sci(report, {"requires_hermes": "invalid"})
    assert not report.ok
    home = tmp_path / ".sci"
    plugin = home / "plugins/old-private-import"
    plugin.mkdir(parents=True)
    (plugin / "plugin.yaml").write_text("name: old-private-import\nversion: 1.0.0\ndescription: fixture\n")
    (plugin / "__init__.py").write_text("from hermes_constants import get_hermes_home\ndef register(ctx): pass\n")
    atomic_config_write(home / "config.yaml", {"plugins": {"enabled": ["old-private-import"]}})
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(home))
    bundled = tmp_path / "empty-bundled"
    bundled.mkdir()
    monkeypatch.setenv("SCI_BUNDLED_PLUGINS", str(bundled))
    manager = PluginManager()
    try:
        manager.discover_and_load()
        plugin = manager._plugins["old-private-import"]
        assert "SCI-compatible release" in plugin.error
        assert "sci_constants" in plugin.error
        assert not plugin.tools_registered
    finally:
        manager.unload()
