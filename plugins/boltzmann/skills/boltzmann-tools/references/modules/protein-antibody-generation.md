# Antibody Generation

Domain: Protein Engineering

This module was selected by the server. Use only the exact contracts below.

## 1. Random Antibody Generation

| Field | Value |
|-------|-------|
| **job_name** | `Random_Antibody_Generation` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `n_samples` | int | yes | Hard constraint: integer greater than 16 (minimum 17). The UI/sample value is 20 and is the recommended normal minimum. |
| `file_format` | string | yes | `"csv"` or `"fasta"`; user-facing alias `format`. These and `n_samples` are the only user input fields. |

**Output keys:**
- `result["OutputData"]["outputFilePath_H"]["download_link"]` — Heavy chain CSV/FASTA
- `result["OutputData"]["outputFilePath_L"]["download_link"]` — Light chain CSV/FASTA

**Pitfall — L-chain cap at ~16, verify counts after download:** Platform caps light chain output at ~16 sequences per job regardless of `n_samples`. Observed: n=21→16L, n=30→16L, n=24→16L, n=20→16L with 16H (whole job capped at 16 matched pairs). Heavy chain tracks `n_samples` more closely but can also fall short (n=30→24H). Always re-fetch the result and re-download to a fresh path to confirm row counts before reporting to the user. Report the returned heavy- and light-chain counts truthfully. Never submit a completion job unless the user explicitly requests a separate run.

**Signed URL refresh:** Output download URLs from the API are GCS signed URLs expiring in ~300s. If a download fails or the URL expires, re-poll `/api/result-2` with the same `docId` to get fresh signed URLs — the output persists on the Boltzmann server. Observation 2026-10-05: a re-poll returned the byte-identical cached signed URL (no refresh), so download immediately after the first Success poll; a second download after expiry fails with HTTP 400.

**CSV columns (format=csv):**
```
seq_id, Sequences, Length, Molecular_Weight, PI, Hydrophobic_Count, Acidic_count, Basic_count, Polar_Count, Others_Count, A, C, D, E, F, G, H, I, K, L, M, N, P, Q, R, S, T, V, W, Y
```

---

## 2. CDR Generator

| Field | Value |
|-------|-------|
| **job_name** | `CDR_Generator` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `sequence` | string | yes | Input antibody sequence (NOT `seq`) |
| `task_name` | string | yes | `"Mutagenesis"` |
| `file_format` | string | yes | `"csv"` only |
| `n_samples` | int | yes | Number of sequences |
| `scheme` | string | yes | `"imgt"`, `"kabat"`, `"chothia"` |
| `cdr_reg` | string | yes | `"HCDR1"`, `"HCDR2"`, `"HCDR3"` |
| `mode` | string | yes | `"H"` only; do not offer light-chain mode for CDR Generator. |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]`

**CSV columns:** `Sequence_ID, Sequence`

---

## 3. Backbone Generation

| Field | Value |
|-------|-------|
| **job_name** | `Backbone_Generation` |
| **Mongo diagnostics collection** | `BACKBONE_GENERATION` (verified sample record); pair with the returned experiment ID. |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `n_samples` | int | yes | Number of structures |
| `mode` | string | yes | `"H"` or `"L"` |

**Output keys:**
- `result["OutputData"]["outputFilePath_H"]["download_link"]` — Heavy chain PDB ZIP
- `result["OutputData"]["outputFilePath_L"]["download_link"]` — Light chain PDB ZIP

---

## 4. Antibody Backbone to Sequence Generation

| Field | Value |
|-------|-------|
| **job_name** | `Antibody_Backbone_to_Sequence_Generation` |
| **Mongo diagnostics collection** | `SEQ_PRED` (verified sample record); pair with the returned experiment ID. |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `dataPath` | string | yes | Platform-uploaded ZIP of PDB backbone files. Every backbone must contain chain A; the helper parses chain A for both H/L modes. |
| `mode` | string | yes | `"H"` or `"L"` |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]`

**CSV columns:** `Unnamed: 0, Sequence_ID, Sequence, Length, Molecular_Weight, PI, Hydrophobic_Count, Acidic_count, Basic_count, Polar_Count, Others_Count, A..Y`

---
