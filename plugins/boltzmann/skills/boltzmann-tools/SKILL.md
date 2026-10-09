---
name: boltzmann-tools
description: Run authenticated Boltzmann scientific workflows.
metadata:
  sci:
    tags: [boltzmann, protein, chemistry, rna, drug-discovery]
    category: science
---

# Boltzmann Tools Skill

Use the authenticated `boltzmann` plugin for protein, small-molecule,
synthesis, RNA, and quantum-chemistry workflows. This installation is strictly
for `platform_tools`; never route a request into Omics mode or use Omics
contracts, logging, collections, or endpoints.

## Distribution notes

This packaged catalog preserves workflow contracts, not private account data.
Example upload paths, job IDs and artifact URLs are placeholders; obtain current
values only from this authorized workflow. Historical VERIFIED observations are
not a new service certification. A registry entry marked active does not override
a blocked, parked, unverified, or incomplete contract. Missing requirements stop
execution; never use the incomplete machine-contract scaffold as a payload.
Supporting local converters require separate dependencies and execution approval;
they do not install software or authorize Boltzmann calls.
Reference code snippets illustrate payloads, not permission to import internal
HTTP helpers or run them in terminal/execute_code. Map historical helper names
to the five registered plugin tools and their current schemas. Never pass a key.
Some historical references name preparation/validation helpers not included in
this connector. Check availability first; stop and explain a missing required
validator instead of inventing it or claiming validation happened. The generic
submission tool does not itself validate every scientific workflow contract.

## When to Use

Use this skill when the user asks to generate, predict, dock, optimize, screen,
or analyze a scientific design with a workflow represented in
`references/module-registry.v1.json`.

Do not use it for general literature search, general coding, or omics analysis.

## Prerequisites

- If not connected, ask the user to run `/add_boltz` in the Sci CLI and
  enter the key in its secure prompt. `/add_boltz --now` activates tools in the
  current conversation; without it, restart Sci. Never collect keys in chat.
- This bundled skill is discovered as `boltzmann:tools` after authorization.
- The profile-local `boltzmann` plugin must be enabled.
- `BOLTZMANN_API_KEY` must exist in the active Sci profile.
- The available execution tools are `boltzmann_submit`, `boltzmann_status`,
  `boltzmann_download`, `boltzmann_upload`, and
  `boltzmann_fetch_tool_log`.
- Authentication stays inside the plugin. Never ask for, display, or pass an
  API key, bearer token, `conv_id`, signed URL, or internal filesystem path in
  user-visible text.

## Contract Selection

1. Read `references/module-registry.v1.json` and match the user intent to one
   module.
2. Read that module file completely before asking questions or calling a tool.
3. For BoltPro tools, also read
   `references/tool-clarification-contracts.v1.json` when the module requires a
   mode-dependent or clarification contract.
4. For verified BoltChem tools, read the matching section of
   `references/boltchem_tools.md`.
5. Use only exact names, fields, enums, types, limits, and output keys present
   in the selected contract. Never infer a backend name or payload from memory.
6. A record marked `unverified`, blocked, or parked is not executable. Explain
   the limitation and stop.

## Execution Protocol

### 1. Resolve all inputs

- Preserve every valid value the user supplied.
- Treat required parameters as required even if an example shows a value.
- Defaults and recommendations are guidance, not permission to choose.
- `experiment_name` requires user confirmation. You may propose a descriptive
  name, but do not silently assign it at submission time.
- For an enum, offer only documented choices.
- Do not offer an open-ended “Other” choice for closed enums.
- Optional omissions never enter the missing-required list.

When anything is missing or invalid, respond:

```text
To run <tool>, I received: <provided fields/files>.
Required: <all required fields and file/schema requirements>.
Missing or invalid: <specific items>.
Optional: <optional fields and allowed choices>.
Please provide/confirm <next values>. Nothing has been submitted yet.
```

### 2. Validate files and handoffs

- Validate the actual documented format, required columns, non-empty values,
  biological alphabet, archive members, and documented limits before upload.
- A sequence is not a PDB/CIF structure. Text is not a storage path.
- Never fabricate coordinates, missing scientific values, labels, units, IDs,
  trained models, rows, or pairings.
- Preserve the source artifact. Create a separate derived input only for an
  explicitly documented, deterministic conversion.
- Do not use `boltzmann_upload` until validation succeeds.
- This installation does not expose `boltzmann_build_inputs`. Do not
  hallucinate that tool or replace it with an improvised scientific parser.

### 3. Obtain plan approval when required

For multiple tools, multiple stages, multiple candidate files, or ambiguous
file-to-tool mappings, show the ordered plan, file mapping, and expected
outputs. Obtain explicit approval before the first submission.

A single-tool request may proceed after all required values and the experiment
name have been explicitly supplied or confirmed.

### 4. Submit exactly once

Call `boltzmann_submit` with:

```json
{
  "job_name": "<exact contract job_name>",
  "experiment_data": {"<exact documented fields>": "<supplied values>"},
  "experiment_name": "<confirmed name>"
}
```

Retain the returned `job_name` and `doc_id` as one pair. Never invent, alter,
search for, or reuse an ID from another conversation.

### 5. Poll the same job

Call `boltzmann_status` with exactly the submitted `job_name` and returned
`doc_id`. Pending, queued, running, and pending approval are not failures.

- Continue polling the existing job within the tool contract.
- Never create a duplicate job because polling timed out.
- After an ambiguous submission timeout, do not resubmit until the absence of
  the original job is proven.
- A success response without populated required output is a propagation race;
  poll the same job again.

### 6. Retrieve and verify outputs

- Use `boltzmann_download` only with a signed URL returned for the current job. Arguments: `download_url` (the signed URL from the status response) and `output_folder` (local destination directory; the artifact keeps its original file name). `download_link`/`path` are rejected with "Missing required arguments: download_url, output_folder".
- If a signed URL expires, poll the same job for refreshed output metadata.
- Verify every required result key and artifact before reporting success.
- Check returned counts and formats against the request and report partial
  results truthfully.
- Never automatically submit a completion or top-up job.

### 7. Diagnose terminal results when needed

The live `boltzmann_status` response is the status authority. When a terminal
result needs durable diagnostic detail, resolve the exact collection through
`references/tool-collection-inventory.csv` and call:

```json
{
  "collection": "<verified collection>",
  "experiment_id": "<current doc_id>"
}
```

with `boltzmann_fetch_tool_log`. If the mapping is blank, ambiguous, or
source-only, do not guess it. A missing durable record does not by itself mean
the scientific job failed.

## Hard Rules

1. Use only the `boltzmann` plugin tools for execution. Never call Boltzmann
   HTTP endpoints directly and never replace a platform workflow with a local
   script.
2. Never expose credentials, backend-only identifiers, raw signed URLs,
   internal helper names, or internal filesystem paths.
3. Never submit until every required value is explicit and valid.
4. Submit once. Poll and retry status/download operations against the same job.
5. Do not execute blocked or unverified contracts.
6. Do not enter Omics mode or use `workflow-omics`.
7. Do not claim success until required output keys and artifacts are present.
8. Do not fabricate a result when authentication, status, or durable lookup is
   unavailable.

## Verification

Before the final answer, confirm:

- The selected module and exact `job_name` matched the user intent.
- Required inputs and the experiment name were explicit.
- Only one submission occurred.
- Status used the returned document ID.
- Required artifacts were downloaded and inspected when applicable.
- Returned counts, failures, warnings, and limitations are reported exactly.
