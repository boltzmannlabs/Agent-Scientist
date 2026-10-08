# BioToolsLLMAnnotate integration

## Scope

BioToolsLLMAnnotate annotates bioinformatics software metadata for the bio.tools registry. It does not annotate protein or nucleotide sequences. Separate a working CLI, native tool registration, offline pipeline verification, online LLM scoring, and Pub2Tools discovery as distinct acceptance tiers.

## Installation and interface

- Inspect the repository's pyproject.toml and installed --help before choosing an interface. Install the source in a dedicated user-local virtual environment, not the Sci runtime. Expose biotools-annotate on PATH through a link to that environment.
- Invoke `biotools-annotate --custom-pub2tools-json FILE --offline`; despite stale examples containing `run`, the verified single-command Typer entry point accepts options directly.
- Prefer a user-local native plugin with typed arguments, an isolated subprocess, a process-group timeout, and profile-safe `plugin_data_dir` outputs. Enable through `sci plugins enable`, then check the configured platform toolset and fresh-runtime registry.

## Safety and provenance

- Generate the entire upstream config from `DEFAULT_CONFIG_YAML` in the tool's isolated interpreter; partial configs are not automatically merged with defaults.
- Disable both CLI upload and `pipeline.upload.enabled`. Merely omitting --upload does not prevent a config-enabled upload.
- Never accept API-key literals as arguments. Use `ollama.api_key_env`, preserve only the explicitly selected credential variable, and keep `ollama.api_key` null so config snapshots do not contain a key. Clear ambient BIOTOOLS_CONFIG, BIOTOOLS_ANNOTATE_INPUT and BIOTOOLS_ANNOTATE_JSON overrides.
- Reject missing or malformed candidate files before executing. The upstream CLI can exit zero and write an empty result when a supplied path does not exist.
- Treat offline output as heuristics, not LLM evidence. The online scorer can also fall back to heuristics without a failing process exit. Parse the actual CSV model column to report model provenance and LLM-assessed counts.
- Distinguish dry_run from offline: dry_run skips payload writing but can still fetch evidence and call inference services.
- Use new UUID run directories to avoid upstream fixed-name outputs overwriting earlier runs.

## Optional dependencies and verification

Online scoring requires an Ollama service or an OpenAI-compatible chat/completions endpoint; the Sci chat subscription is not automatically forwarded. Date-based discovery additionally requires Java and Pub2Tools. Do not install a large model or publish registry entries without user direction.

For local candidate input, verify `out/custom_tool_set/reports/assessment.csv` and, unless dry_run, `out/custom_tool_set/exports/biotools_payload.json`. The tested upstream version emits CSV but not necessarily assessment.jsonl: inspect actual files instead of assuming JSONL from an older test or class. Count CSV rows and validate payload JSON. Label example.org/sample candidates as synthetic upstream test fixtures, not real discovered resources.

Run `sci plugins doctor PLUGIN --ci`; exercise registered handlers through a fresh Sci runtime, not only direct module imports. Report pending online inference/discovery separately from the verified offline integration, and tell the user when a new session is needed to load tool schemas.
