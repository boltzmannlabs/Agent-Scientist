"""A changed wake phrase must reach detection, not just its UI label."""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools import wake_word as ww
from tools.wake_word_engines import _OpenWakeWordEngine, _SherpaKwsEngine


def test_default_phrase_reaches_open_vocabulary_engine(tmp_path, monkeypatch):
    from sci_cli.config_defaults import DEFAULT_CONFIG
    cfg = {**DEFAULT_CONFIG["wake_word"], "profile_routing": False}
    assert not cfg["enabled"] and ww._provider(cfg) == "sherpa"
    observed = {}
    for name in ("tokens.txt", "encoder-model.onnx", "decoder-model.onnx", "joiner-model.onnx"):
        (tmp_path / name).touch()

    def tokenize(phrases, **kwargs):
        observed["phrases"] = phrases
        return [p.split() for p in phrases]

    def spotter(**kwargs):
        observed["keywords"] = Path(kwargs["keywords_file"]).read_text()
        return SimpleNamespace(create_stream=lambda: object())

    monkeypatch.setitem(sys.modules, "sherpa_onnx", SimpleNamespace(text2token=tokenize, KeywordSpotter=spotter))
    engine = _SherpaKwsEngine.__new__(_SherpaKwsEngine)
    try:
        engine._build(cfg, {"model_dir": str(tmp_path)}, ww)
        assert observed["phrases"] == [ww.wake_phrase(cfg).upper(), *[p.upper() for p in cfg["aliases"]]]
        assert "@HEY_SCI" in observed["keywords"]
        assert "HEY_SCI" in engine._display_to_profile
        assert len(set(engine._display_to_profile.values())) == 1
        assert "@HEY_AGENT_SCIENTIST" in observed["keywords"]
        assert "@HEY_AGENT_SCI" in observed["keywords"]
    finally:
        engine.close()
    assert not Path(engine._keywords_file).exists()


def test_fixed_legacy_weights_cannot_masquerade_as_new_phrase(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("wrong acoustic model must not load")
    monkeypatch.setitem(sys.modules, "pyopen_wakeword", SimpleNamespace(
        OpenWakeWord=SimpleNamespace(from_model=forbidden),
        OpenWakeWordFeatures=SimpleNamespace(from_builtin=forbidden)))
    engine = _OpenWakeWordEngine.__new__(_OpenWakeWordEngine)
    with pytest.raises(ValueError, match="sherpa"):
        engine._build({"phrase": "hey sci"}, {}, ww)
