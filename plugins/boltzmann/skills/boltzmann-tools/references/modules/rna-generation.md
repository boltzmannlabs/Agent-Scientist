# RNA Generation

Domain: RNA Design

This module was selected by the server. Use only the exact contracts below.

## 52. RNA CDS Generation

Generate coding DNA sequence (CDS) variants for a protein sequence (GEMORNA model). Each CDS encodes the input protein.

| Field | Value |
|-------|-------|
| **job_name** | `rnagen_cds` |
| **watch_time** | Fast (typically a few seconds; platform may quote up to ~10 min) |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `Protein_sequence` | string | yes | Amino-acid sequence to back-translate into CDS variants |
| `n_gen` | string | yes | Number of CDS variants — pass as a STRING (`"5"`), not an int |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`); e.g. `"prime"` |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `results.zip`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

---

## 53. RNA mRNA Generation

Generate a full mRNA construct — CDS plus 5'UTR and 3'UTR variants — for a protein sequence (GEMORNA model).

| Field | Value |
|-------|-------|
| **job_name** | `rnagen_cds_mrna-gen` |
| **watch_time** | Fast (typically seconds; platform may quote up to ~3 min) |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `Protein_sequence` | string | yes | Protein amino-acid sequence to encode |
| `n_cds_gen` | string | yes | Number of CDS variants — pass as a STRING (`"5"`) |
| `n_5utr_gen` | string | yes | Number of 5'UTR variants — pass as a STRING (`"5"`) |
| `n_3utr_gen` | string | yes | Number of 3'UTR variants — pass as a STRING (`"3"`) |
| `utr_len` | string | yes | `"short"` / `"medium"` / `"long"` |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`); e.g. `"prime"` |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `results.zip`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

> ⚠️ The UTR-length field here is **`utr_len`** — NOT `utr_length` (which the standalone 3'UTR/5'UTR tools below use). These are different field names for different tools; do not normalize them.

---

## 54. RNA 3'UTR Generation

Generate 3'UTR sequence variants (GEMORNA model).

| Field | Value |
|-------|-------|
| **job_name** | `rnagen_3utr` |
| **watch_time** | Fast (typically seconds; platform may quote up to ~3 min) |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `n_gen` | string | yes | Number of UTR variants — pass as a STRING (`"5"`) |
| `utr_length` | string | yes | `"short"` / `"medium"` / `"long"` |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`); e.g. `"prime"` |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `results.zip`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

---

## 55. RNA 5'UTR Generation

Generate 5'UTR sequence variants (GEMORNA model).

| Field | Value |
|-------|-------|
| **job_name** | `rnagen_5utr` |
| **watch_time** | Fast (typically seconds) |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `n_gen` | string | yes | Number of UTR variants — pass as a STRING (`"5"`) |
| `utr_length` | string | yes | `"short"` / `"medium"` / `"long"` |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`); e.g. `"prime"` |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `results.zip`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

---

## 60. siRNA Generation
Generate and rank candidate siRNAs from a target RNA/mRNA FASTA sequence using
the OligoFormer generation backend.

| Field | Value |
|---|---|
| **job_name** | `rna_siRNA_gen` |
| **backend task** | `rna_siRNA_gen` |
| **validation status** | **Verified working** |
| **observed terminal status** | `Success` |

### Inputs

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `input_fasta` | platform path string | yes | Uploaded target RNA/mRNA `.fa` or `.fasta`. Raw sequence is not accepted in this field. |

When the user supplies a raw target sequence, create a valid single-record
FASTA such as `>target_mrna`, validate its RNA alphabet, upload it with
`file_upload`, and place only the returned platform path in `input_fasta`.

```python
target_fasta_path = create_fasta(
    [("target_mrna", target_mrna_sequence)],
    local_target_fasta,
)

job_name = "rna_siRNA_gen"
experiment_name = "siRNA generation"
experiment_data = {
    "input_fasta": target_fasta_path,
}
```

Use the live-proven job name `rna_siRNA_gen`. A product-sheet `Job Name` cell
contains the stale alias `siRNA_gen`; do not use it for submission or polling.

### Output instructions

Download the ZIP from `OutputData.outputFilePath.download_link`. The verified
archive contained three CSVs with identical columns:

```text
pos,sense,siRNA,efficacy,func_filter,filter
```

- `RNA_sequence.csv`: all 39 generated candidates;
- `RNA_sequence_ranked.csv`: the same 39 candidates in ranked form;
- `RNA_sequence_ranked_filtered.csv`: 16 ranked candidates passing filters.

Use the ranked filtered file for prioritization while retaining the full and
ranked tables. Verify counts from the actual archive. The live result omitted a
`billing` block; terminal `status`, `time_taken`, and inspected outputs still
proved completion.

### Evidence

- The all-experiments CSV confirms `.fa | .fasta` validation and exact job name
  `rna_siRNA_gen`.
- The RNA product CSV confirms the `input_fasta` backend field and OligoFormer
  generation task.
- Live submission, terminal fetch, ZIP download, and all three CSV parses
  succeeded.

## 102. BiomambaRna

Analyze an RNA sequence with the BiomambaRna workflow.

| Field | Value |
|---|---|
| **job_name** | `BiomambaRna` |
| **contract status** | live-verified end to end |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `user_id` | string | yes | Use the exact source field. |
| `sequence` | string | yes | Use the exact source field. |

**Output contract:** Live-verified `OutputData.outputFilePath`; download and inspect the result archive.

The UI calls the sequence field `rnasequence`, but the accepted backend
field is `sequence`. The verified archive contains `sequence_1_top_similar.csv`
with 100 ranked `sequence` and `similarity_score` rows, plus `manifest.json` with
run-level result inventory.

---

<!-- csv-additional-tools:end -->
