# Bundled wake-word models

`hey_sci.tflite` is the renamed bundled acoustic model. Its weights still
recognize the original phrase, "Hey Hermes"; the filename change did not retrain
it. It is retained only for explicitly configured legacy detection. New profiles
default to "Hey Sci" through the existing sherpa open-vocabulary engine, which
tokenizes the requested phrase; no renamed acoustic weights are used for that
phrase. See `website/docs/user-guide/features/wake-word.md`.

- **Engine:** [pyopen-wakeword](https://github.com/rhasspy/pyopen-wakeword)
  (rhasspy's maintained fork of openWakeWord; Apache-2.0). Runs TFLite via a
  bundled `tensorflowlite_c` library — no onnx, no runtime download.
- **Provenance:** trained with the openWakeWord training pipeline (synthetic
  TTS-generated speech), which produces the `.tflite` artifact. Redistribution
  is permitted under the openWakeWord license.
- **Label:** the model registers as `hey_sci` (matches the filename).
- **Runtime:** the `pyopen-wakeword` wheel includes the shared
  melspectrogram and embedding models. Starting this engine requires no
  model download. Identical model files alone do not establish identical
  scores across inference engines or platforms.

To use a different phrase, point `wake_word.openwakeword.model` at an
absolute path to a compatible `.tflite` model. Sci does not download
models by name, and this engine does not load `.onnx` files. See the
wake-word docs for the training guide and platform limits.
