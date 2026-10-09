# Structure Prediction

Domain: RNA Design

This module was selected by the server. Use only the exact contracts below.

## 59. RNA Tertiary Structure Prediction

Predict the 3D structure of an RNA from its sequence (RhoFold).

| Field | Value |
|-------|-------|
| **job_name** | `rna_structure_prediction` |
| **watch_time** | ~30 s |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `input_fasta` | string (GCP path) | yes | FASTA containing the RNA sequence. Upload via `file_upload` first, then pass the returned platform path here |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `prediction.zip`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

---

## 92. Secondary Structure Prediction

Predict RNA secondary structure from a nucleotide sequence.

| Field | Value |
|---|---|
| **job_name** | `sec_struct_pred` |
| **contract status** | submission accepted; output unverified |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `sequence` | string | yes | Use the exact source field. |

**Output contract:** Submission accepted but no terminal result was observed through 25 minutes; continue polling the original job and inspect the first terminal `OutputData`.

Pass only `sequence` inside `experiment_data`; do not duplicate `job_name`
inside the payload. A live sample alternated between `pending` and `No Output Found`
through 25 minutes. Treat that evidence as unresolved, not success, and do not
invent dot-bracket, CT, or image output formats.

---
