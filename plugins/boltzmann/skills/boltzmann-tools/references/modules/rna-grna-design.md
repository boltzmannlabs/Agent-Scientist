# gRNA Design

Domain: RNA Design

This module was selected by the server. Use only the exact contracts below.

## 57. CRISPR Base Editing
Design guide RNAs for adenine or cytosine base editing of a target gene.

| Field | Value |
|---|---|
| **job_name** | `crispr_base_editing` |
| **validation status** | **Verified working** |
| **live sample** | `gene_id="HPRT1"`, `editor_type="ABE"` |
| **observed terminal status** | `Success` |

### Inputs

Pass only these tool fields inside `experimentData`:

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `gene_id` | string | yes | A target gene identifier/symbol. The live test used `HPRT1`. |
| `editor_type` | string enum | yes | Exact value `ABE` or `CBE`; do not send labels, objects, lowercase variants, or invented editor names. |

`experiment_name` is the separate top-level argument to `submit_request`; it
does not belong inside `experiment_data`.

```python
job_name = "crispr_base_editing"
experiment_name = "CRISPR base editing - HPRT1 ABE"
experiment_data = {
    "gene_id": "HPRT1",
    "editor_type": "ABE",
}
```

### Output instructions

The successful result used:

```python
result["OutputData"]["outputFilePath"]["path"]
result["OutputData"]["outputFilePath"]["download_link"]
```

The verified ZIP contained one CSV named from the requested gene and editor,
for example `HPRT1_abe_base_editing_guides.csv`. The live sample contained
4,476 guide rows with these columns:

```text
guide_id,input_gene_id,gene_symbol,entrez_id,editor_type,chromosome,
gene_strand,guide_strand,protospacer,pam,edit_window,editable_base,
edited_base,editable_positions,editable_genomic_positions,target_base_count,
original_sequence,edited_sequence,protospacer_genomic_start,
protospacer_genomic_end,pam_genomic_start,pam_genomic_end
```

Use the CSV rows as the scientific result. Confirm `input_gene_id` and
`editor_type` match the submitted values before summarizing or ranking guides.
Do not infer that `CBE` was live-tested merely because it is a valid fixed UI
option; the current live canary used `ABE`.

### Evidence

- The all-experiments CSV defines `gene_id` and `editor_type` as required and
  supplies the HPRT1/ABE sample.
- The RNA product CSV confirms exact job name `crispr_base_editing`, task name
  `gRNA_base_editing`, and the `ABE | CBE` restriction.
- Live submission returned HTTP 200, result lookup returned HTTP 200 with
  terminal `Success`, and the signed ZIP downloaded and opened successfully.
- The archive filename and CSV content matched the submitted HPRT1/ABE inputs.

## CRISPR Bystander Effect Prediction

Predict unintended bystander edits for base-editing targets supplied in an
uploaded FASTA file.

| Field | Value |
|---|---|
| **job_name** | `BE_bystander_prediction` |
| **backend task** | `bystander_prediction` |
| **validation status** | **Submission verified (HTTP 200, queued)** |

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `fasta` | platform path string | yes | Uploaded FASTA. Use this exact field; not `input_fasta`. |
| `editor_kind` | string | yes | Live-proven value `ABE`. |
| `base_editor` | string | yes | Live-proven value `ABE`. |
| `celltype` | string | yes | Live-proven value `HEK293T`. |

The product documentation describes one 50-nucleotide DNA record spanning
positions -19 through +30 around the protospacer: positions 1-20 are the spacer
and positions 21-23 are the NGG PAM. Validate that layout before upload. The UI
documentation names `ABE`, `CBE`, and `CGBE` editor families and `mES` and
`HEK293(T)` cell contexts, but it does not provide the complete compatible
`base_editor` matrix. Only the exact `ABE`/`ABE`/`HEK293T` combination below is
submission-verified; do not guess other payload tokens from their display labels.

```python
job_name = "BE_bystander_prediction"
experiment_name = "Base-editing bystander prediction"
experiment_data = {
    "fasta": uploaded_target_fasta,
    "editor_kind": "ABE",
    "base_editor": "ABE",
    "celltype": "HEK293T",
}
```

The exact string-valued payload returned HTTP 200, queued task
`bystander_prediction`, and a document ID. Do not send selector objects for
these three strings. Terminal artifacts remain unverified. Product documentation
expects run metadata plus `num_predicted_outcomes`,
`total_predicted_probability`, `top_predicted_frequency`, `top_edit_outcome`,
and `top_genotype`; treat those as expected rather than verified until the
terminal artifact is downloaded and inspected.

## CRISPR Base-Editing Efficacy Prediction

Predict editing efficiency for base-editing targets supplied in an uploaded
FASTA file.

| Field | Value |
|---|---|
| **job_name** | `BE_efficacy_pred` |
| **backend task** | `efficiency_prediction` |
| **validation status** | **Submission verified (HTTP 200, queued)** |

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `fasta` | platform path string | yes | Uploaded FASTA. Use this exact field; not `input_fasta`. |
| `editor_kind` | string | yes | Live-proven value `ABE`. |
| `base_editor` | string | yes | Live-proven value `ABE`. |
| `celltype` | string | yes | Live-proven value `HEK293T`. |

```python
job_name = "BE_efficacy_pred"
experiment_name = "Base-editing efficacy prediction"
experiment_data = {
    "fasta": uploaded_target_fasta,
    "editor_kind": "ABE",
    "base_editor": "ABE",
    "celltype": "HEK293T",
}
```

The exact string-valued payload returned HTTP 200, queued task
`efficiency_prediction`, and a document ID. Terminal artifacts and output
columns remain unverified.

## 61. CRISPR gRNA Design

Design SpCas9 knockout guide RNAs for a target gene.

| Field | Value |
|-------|-------|
| **job_name** | `gRNA_design` |
| **watch_time** | ~1 to 7 min |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_id` | string | yes | Real human gene symbol; e.g. `"HBB"` |
| `experiment_name` | string | yes | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `results.zip`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

> The `job_name` MUST be exactly `"gRNA_design"`.

---

## 69. CRISPR IndelShift Prediction

Predict CRISPR indel / frameshift outcomes for guide RNAs (Lindel-based on-/off-target model).

| Field | Value |
|-------|-------|
| **job_name** | `crispr_fs_score` |
| **watch_time** | ~2 min |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `input_csv` | string (GCP path) | yes | CSV of guide RNAs. Upload via `file_upload` first, then pass the returned platform path. Headers MUST be exactly: `grna_id, chromosome, genomic_position, strand, protospacer, pam` |
| `aligner` | string | yes | Aligner used to map guide-RNA spacers and locate target/off-target sites; proven value `"biostrings"` (lowercase) |
| `mismatches` | int | yes | Number of allowed mismatches for off-target mapping — INTEGER (e.g. `5`) |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `results.zip`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

> ⚠️ Follow the input CSV headers **exactly**: `grna_id`, `chromosome`, `genomic_position`, `strand`, `protospacer`, `pam`.

---

## 70. CRISPR Off-Target Prediction

Predict CRISPR on-/off-target activity scores for guide RNAs (Azimuth-based model).

| Field | Value |
|-------|-------|
| **job_name** | `crispr_score` |
| **watch_time** | ~20 s |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `input_csv` | string (GCP path) | yes | CSV of guide RNAs. Upload via `file_upload` first, then pass the returned platform path. Headers MUST be exactly: `grna_id, chromosome, genomic_position, strand, protospacer, pam` |
| `aligner` | string | yes | Aligner for mapping guide spacers; proven value `"biostrings"` (lowercase) |
| `mismatches` | int | yes | Number of allowed mismatches — INTEGER (e.g. `5`) |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `results.zip`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

> Same input CSV shape as `## 68` (the sample run reuses the identical input file). Headers must be followed **exactly**: `grna_id`, `chromosome`, `genomic_position`, `strand`, `protospacer`, `pam`.

---
