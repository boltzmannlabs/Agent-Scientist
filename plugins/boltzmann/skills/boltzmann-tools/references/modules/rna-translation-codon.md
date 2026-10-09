# Translation and Codon Optimization

Domain: RNA Design

This module was selected by the server. Use only the exact contracts below.

## 65. CodonRLBERT / Codon Optimization

Optimize / predict codon usage for a protein sequence (CodonRL + BERT).

| Field | Value |
|-------|-------|
| **job_name** | `CodonRLBERT` |
| **watch_time** | ~5 s to 5 min |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `fasta_file` | string (GCP path) | yes | FASTA of protein sequence(s). Upload via `file_upload` first, then pass the returned platform path here |
| `name` | string | yes | Run label placed **inside `experimentData`**; e.g. `"prime"` |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `predictions.csv`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

`Codon Optimization`, `Codon Optimisation`, and `CodonRLBERT` refer to this
same executable contract. The product CSV documents output columns
`optimized_mrna`, `optimized_dna`, `sequence_length`, `strategy`, `cai`, `csc`,
`gc`, `u_pct`, `mfe`, and `mrfp_expression`.

---

## 68. RNA Translation Prediction

Predict translation / expression properties for CDS sequences.

| Field | Value |
|-------|-------|
| **job_name** | `RNA_Translation` |
| **watch_time** | Actual run ~seconds; platform queue can be long — **credit-heavy** (a sample run billed 65 credits) |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `name` | string | yes | Run label placed **inside `experimentData`**; e.g. `"HBB_CDS_expression"` |
| `fasta_file` | string (GCP path) | yes | CDS FASTA to predict translation for. Upload via `file_upload` first, then pass the returned platform path here |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `predictions.csv`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

> Note: the sample submit response did not echo an `estimated_time`; rely on `fetch_status` polling. This is a credit-heavy tool — confirm intent before submitting large inputs.

---

## 72. RNA Translational Efficiency Prediction

Predict translational efficiency for sequences (organism-specific model).

| Field | Value |
|-------|-------|
| **job_name** | `transla_score` |
| **watch_time** | Fast (seconds; platform quotes ~1 min) |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `organism` | string | yes | `"human"` / `"mouse"` / `"ecole"` (string). Proven value: `"mouse"`. Note: source lists `"ecole"` — likely E. coli / `"ecoli"`; confirm the exact token on the first non-mouse/human run |
| `input_csv` | string (GCP path) | yes | CSV input for the prediction. Upload via `file_upload` first, then pass the returned platform path. The source requires a `Sequence` header. |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `results.zip`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`



# Quantum Chemistry (DFT)
