# Property Prediction

Domain: RNA Design

This module was selected by the server. Use only the exact contracts below.

## 58. mRNA Property Calculation

Compute mRNA objective/property metrics (e.g. CAI, GC content, MFE) for sequences in a FASTA file.

| Field | Value |
|-------|-------|
| **job_name** | `rna_property_calculation` |
| **watch_time** | ~30 s |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `input_fasta` | string (GCP path) | yes | FASTA of mRNA/CDS sequences. Upload the file via `file_upload` first, then pass the returned platform path here |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → **`mRNA_objectives.csv`** (a CSV, not a zip)
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

---

## 62. RNA Property Prediction — Mean Ribosomal Load

Predict mean ribosomal load (MRL) for 5'UTR sequences.

| Field | Value |
|-------|-------|
| **job_name** | `rna_property_prediction_mean_ribosomal_load` |
| **Mongo diagnostics collection** | `RNA_PROP_PRED` (verified sample record); pair with the returned experiment ID. |
| **watch_time** | Fast (seconds) |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `csv_file` | string (GCP path) | yes | CSV containing one or more **5'UTR** sequences with a header column named exactly **`Sequence`**. Upload via `file_upload` first, then pass the returned platform path here |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `predictions.csv`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

---

## 63. RNA Property Prediction — In-Cell Stability

Predict in-cell stability (half-life) for 3'UTR sequences.

| Field | Value |
|-------|-------|
| **job_name** | `rna_property_prediction_incell_stabilty` |
| **Mongo diagnostics collection** | `RNA_PROP_PRED` (verified sample record); pair with the returned experiment ID. |
| **watch_time** | Fast (seconds) |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `csv_file` | string (GCP path) | yes | CSV containing one or more **3'UTR** sequences with a header column named exactly **`Sequence`**. Upload via `file_upload` first, then pass the returned platform path here |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `predictions.csv`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

> ⚠️ The `job_name` is **intentionally misspelled** — `rna_property_prediction_incell_stabilty` (no second `i` in "stabilty"). Do NOT "correct" it to `..._stability`; the backend expects the misspelled string exactly.

---

## 64. siRNA Efficacy Prediction
Predict and rank on-target efficacy for candidate siRNAs against a target mRNA.

| Field | Value |
|---|---|
| **job_name** | `rna_siRNA_efficacy_pred` |
| **backend task** | `rna_siRNA_efficacy_pred` |
| **validation status** | **Verified working** |
| **observed terminal status** | `Success` |

### Inputs

Both fields are FASTA platform paths only:

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `sirna_fa` | platform path string | yes | Uploaded `.fa` or `.fasta` containing one or more candidate siRNA records. |
| `mrna_fa` | platform path string | yes | Uploaded `.fa` or `.fasta` containing the target mRNA record. |

If the user supplies raw sequences, create two distinct FASTA files. Candidate
siRNA records require unique IDs; the mRNA file should have a clear target ID.
Upload each file once and submit only the returned paths. If candidates come
from siRNA Generation, extract the chosen `siRNA` column into candidate FASTA
records; do not pass the generation CSV path as `sirna_fa`.

```python
sirna_fasta_path = create_fasta(sirna_records, local_sirna_fasta)
mrna_fasta_path = create_fasta(
    [("target_mrna", target_mrna_sequence)],
    local_mrna_fasta,
)

job_name = "rna_siRNA_efficacy_pred"
experiment_name = "siRNA efficacy prediction"
experiment_data = {
    "sirna_fa": sirna_fasta_path,
    "mrna_fa": mrna_fasta_path,
}
```

Use the live-proven job name `rna_siRNA_efficacy_pred`; do not replace it with
the stale product-sheet alias `siRNA_eff_pred`.

### Output instructions

Download the ZIP from `OutputData.outputFilePath.download_link`. The verified
archive contained:

- `sirna_eff.csv`, 16 ranked rows with columns `rank`, `name`, `siRNA_full`,
  `siRNA_core_19nt`, `sense_strand_19nt`, `efficacy`, `func_filter`, and
  `func_filter_desc`;
- `sirna_eff_unranked.csv`, the same 16 candidates without the `rank` column.

Use the ranked file for prioritization, retain the unranked file for input-order
traceability, and confirm candidate names/counts match `sirna_fa` before
reporting.

### Evidence

- The all-experiments CSV confirms both required FASTA path fields and their
  `.fa | .fasta` validation.
- The RNA product CSV confirms the OligoFormer prediction backend and both path
  inputs, despite an unrelated stale test-input cell.
- Live submission, terminal fetch, ZIP download, and both 16-row CSV parses
  succeeded.

## 71. siRNA Property Prediction
Score siRNA candidates for sequence, duplex, thermodynamic, transcriptome, and
miRNA off-target properties, then filter them by GC limits and composite rules.
This tool is also labeled siRNA off-target prediction in parts of the inventory.

| Field | Value |
|---|---|
| **job_name** | `siRNA_obj_pred` |
| **backend task** | `siRNA_obj_pred` |
| **validation status** | **Verified working** |
| **observed terminal status** | `Success` |

### Inputs

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `input_csv` | platform path string | yes | Uploaded CSV with the exact columns below. |
| `min_gc` | number | yes | Inclusive minimum GC percentage, from 0 through 100. |
| `max_gc` | number | yes | Inclusive maximum GC percentage, from 0 through 100 and not less than `min_gc`. |

The input CSV headers must be exactly:

```text
id,transcript_id,target_position,guide_sequence,passenger_sequence
```

If the user supplies candidate values rather than a file, create this CSV,
validate unique IDs and the required sequence/position values, upload it once,
and submit only the returned path. Do not create FASTA for `input_csv`.

```python
uploaded_csv_path = file_upload(local_sirna_csv)

job_name = "siRNA_obj_pred"
experiment_name = "siRNA property and off-target prediction"
experiment_data = {
    "input_csv": uploaded_csv_path,
    "min_gc": 20,
    "max_gc": 80,
}
```

### Output instructions

Download the ZIP from:

```python
result["OutputData"]["outputFilePath"]["path"]
result["OutputData"]["outputFilePath"]["download_link"]
```

The archive contains `sirna_all.csv` for every scored candidate and
`sirna_pass.csv` for candidates that passed the filters. The verified files
used these columns:

```text
id,transcript_id,position,guide_sequence,passenger_sequence,gc_content,
asymmetry_score,paired_fraction,mfe,duplex_stability_dg,
duplex_stability_score,dg_5p,dg_3p,delta_dg_end,melting_temp_c,
off_target_count,off_target_penalty,transcriptome_hits_total,
transcriptome_hits_0mm,transcriptome_hits_1mm,transcriptome_hits_2mm,
transcriptome_hits_seed_0mm,mirna_hits_total,mirna_hits_0mm_seed,
mirna_hits_1mm_seed,mirna_hits_high_risk,transcript_hit_count,
transcript_hit_fraction,composite_score,passes_filters,guide_overhang,
guide_modifications,passenger_overhang,passenger_modifications,variant_mode,
allele_specific,targeted_alleles,overlapped_variants
```

The input header `target_position` becomes output header `position`. Use
`sirna_pass.csv` for the filtered candidate set and retain `sirna_all.csv` for
audit. In the live sample, both files contained seven rows because every tested
candidate passed; never assume the counts will always match.

### Organism-specific off-target boundary

This backend has no `organism`, taxonomy, genome, transcriptome, or reference
file field. Its verified payload is limited to `input_csv`, `min_gc`, and
`max_gc`. Never add named organisms to the payload or claim that the returned
off-target columns were evaluated against a user-selected species.

When a request names organisms, route it to the RNA platform-tool lane and load
this contract, but pause before species-specific off-target execution. Explain
that generation and general property scoring can run, then ask for a separately
supported organism-aware tool contract or explicit confirmation to proceed only
with the available non-species-selectable scoring. Do not silently switch the
request to Omics and do not fabricate reference-transcriptome analysis.

### Evidence

- The all-experiments and RNA CSVs confirm the exact job name, path field, GC
  bounds, and ordering constraint.
- Existing RNA validation supplies the exact five-column input template.
- Live submission, terminal fetch, ZIP download, and both seven-row CSV parses
  succeeded.

## 88. CDS Property Prediction

Calculate selected coding-sequence properties with the CodonRLBERT property
workflow. Product surfaces also call this contract **mRNA Property Prediction**;
that name is an alias, not a separate backend.

| Field | Value |
|---|---|
| **job_name** | `CodonRLBERTPropPred` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `user_id` | string | yes | Use the exact source field. |
| `fasta_file` | string | yes | Uploaded file: `.fasta`, `.fa` |
| `selected_properties` | array[string] | yes | Select at least one of `cai`, `csc`, `gc`, `u_pct`, `mfe`, `mrfp_expression`, `mrna_stability`, `riboswitch`, `vaccine_degradation`. |

The all-experiments UI sample uses the stale key `RNA_properties`; the backend
model and product payload use `selected_properties`. Submit the latter only.
The source does not document a terminal result path or CSV columns; inspect the
first terminal payload and artifact before reporting values.

---
