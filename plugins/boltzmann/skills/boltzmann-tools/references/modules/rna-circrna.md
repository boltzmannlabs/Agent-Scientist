# Circular RNA

Domain: RNA Design

This module was selected by the server. Use only the exact contracts below.

## 66. Circular RNA Evaluation

Evaluate circular RNA constructs (properties / quality scoring).

| Field | Value |
|-------|-------|
| **job_name** | `CircRNAEvaluate` |
| **watch_time** | Fast (seconds; platform may not quote an estimated time) |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `fasta_file` | string (GCP path) | yes | FASTA of circRNA sequence(s). Upload via `file_upload` first, then pass the returned platform path here |
| `name` | string | yes | Run label placed **inside `experimentData`**; e.g. `"hh"` |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

Upload-only input: `.fasta`, `.fa`, or `.txt` containing headed, non-empty RNA
FASTA records. Plain unheaded text and SMILES are not inputs to this tool.
The byte-level rules are in `../file-input-contracts.v1.json` (`CircRNAEvaluate`).

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `evaluate.csv`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

---

## 67. Circular RNA Design / CircRNA Generate

Design and generate circular RNA constructs from an input FASTA (circRNA generation).

| Field | Value |
|-------|-------|
| **job_name** | `CircRNA` |
| **watch_time** | Platform quotes ~5.5 min; actual run is ~tens of seconds (may queue longer under load) |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `name` | string | yes | Run label placed **inside `experimentData`**; e.g. `"HBB_circRNA_design"` |
| `fasta_file` | string (GCP path) | yes | Protein FASTA used to design circRNA candidates. Upload via `file_upload` first, then pass the returned platform path here |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

Upload-only input: `.fasta`, `.fa`, or `.txt` containing headed, non-empty protein
FASTA records. Preserve a supplied platform path across clarification turns;
ask only for missing settings. Do not offer Paste SMILES. Inspect the file's
bytes before submission using `../file-input-contracts.v1.json` (`CircRNA`).
Missing internal file metadata is a configuration defect, not a request for
the user to upload the same file again.

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `evaluate.csv`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

> Disambiguation: **CircRNA Generate**, **CircRNA Generation**, and **CircRNA
> Design** are names for this one executable contract (`job_name` `CircRNA`,
> backend task `circrna_generate`). It is distinct from `CircRNAEvaluate`
> (`job_name` `CircRNAEvaluate`, task `circrna_evaluate`), which evaluates
> existing RNA FASTA records. Pick by design/generate versus evaluate intent.

---
