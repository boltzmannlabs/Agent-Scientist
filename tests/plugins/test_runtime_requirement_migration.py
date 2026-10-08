"""External metadata cannot bypass the runtime version gate after rebranding."""
from sci_cli import plugins_manifest


def test_external_and_sci_constraints_both_apply(monkeypatch):
    monkeypatch.setattr(plugins_manifest, "running_sci_version", lambda: "0.21.5")
    assert plugins_manifest.requires_sci_error({"requires_hermes": ">=99.0"})
    assert plugins_manifest.requires_sci_error({"requires_sci": ">=0.20", "requires_hermes": ">=99.0"})
    assert plugins_manifest.requires_sci_error({"requires_sci": ">=0.20", "requires_hermes": "<1.0"}) is None
