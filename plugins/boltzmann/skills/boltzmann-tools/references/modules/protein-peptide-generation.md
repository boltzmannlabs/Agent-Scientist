# Peptide Generation

Domain: Protein Engineering

This module was selected by the server. Use only the exact contracts below.

## EvoBind

| Field | Value |
|---|---|
| **job_name** | `Evobind` |
| **contract status** | Documented; notebook payload and public API schema available. Not live-tested in this update. |

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `sequence` | string | yes | Target protein amino-acid sequence. |
| `a3m_file_path` | file | yes | Upload the corresponding A3M alignment. |
| `num_peptides` | integer | yes | Number of peptides to generate. |
| `seq_length` | integer | yes | Generated peptide length. |
| `target_residues` | string | yes | Comma-separated target residue positions. |
| `cyclic_offset` | string | yes | Exactly `"True"` or `"False"`, not a JSON boolean. |

Never invent an alignment or target residues. Download and verify the actual
backend outputs before describing the generated peptides. No durable Mongo
collection is inferred from this job name.

## 6. Structure-Based Peptide Generation

| Field | Value |
|-------|-------|
| **job_name** | `Structure_based_peptide_generation` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `sequence` | string | yes | Input peptide sequence |
| `num_structures` | int | yes | Number of structures |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]`

**CSV columns:** `Sequence_ID, Sequence, Score, Target, Length, Molecular_Weight, PI, Hydrophobic_Count, Acidic_count, Basic_count, Polar_Count, Others_Count, A..Y`

---

## 8. Sequence based peptide generation
Generate candidate peptide binders conditioned on a target protein sequence
using the target-based PepPrCLIP backend.

| Field | Value |
|---|---|
| **job_name** | `Sequence_based_peptide_generation` |
| **Mongo diagnostics collection** | `TARGET_PEP_GEN` (verified sample record); pair with the returned experiment ID. |
| **backend task/collection** | `TARGET_PEP_GEN` |
| **validation status** | **Verified working with requested-count mismatch** |
| **observed terminal status** | `Success` |

### Inputs

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `sequence` | string | yes | Target/conditioning protein sequence, not a peptide seed. |
| `num_peptides` | numeric string | yes | Requested candidate count, for example `"15"`. Preserve the plural field name. |
| `seq_length` | numeric string | yes | Desired peptide length. Documented supported range is 11–50 residues. |

Although some prose in the product sheet describes these controls as integers,
the client schema, backend API model, and successful payload use strings for
both `num_peptides` and `seq_length`. Send digit strings unless a later canary
proves another representation. Do not use the stale singular field
`num_peptide`.

```python
job_name = "Sequence_based_peptide_generation"
experiment_name = "Sequence-conditioned peptide generation"
experiment_data = {
    "sequence": target_protein_sequence,
    "num_peptides": "15",
    "seq_length": "11",
}
```

### Output instructions

The terminal result returns one directly downloadable CSV:

```python
result["OutputData"]["outputFilePath"]["path"]
result["OutputData"]["outputFilePath"]["download_link"]
```

The verified CSV contained:

```text
Sequence_ID,Sequence,Score,Target,Length,Molecular_Weight,PI,
Hydrophobic_Count,Acidic_count,Basic_count,Polar_Count,Others_Count,
A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y
```

Verify `Target`, `Length`, candidate uniqueness, and the actual row count before
reporting. Treat `Score` as the model-returned ranking score; do not present it
as calibrated affinity or an experimental measurement.

### Live count caveat

The live request asked for 15 peptides of length 11, but the backend returned
20 rows. All 20 peptide sequences were unique, every actual and reported length
was 11, and every row had a non-empty target. This proves scientific generation
and output integrity but also proves that `num_peptides` was not honored exactly
for this run. Report `requested=15` and `returned=20` truthfully. Do not discard
extra rows, create a top-up job, or claim that exactly 15 were generated.

### Evidence

- The all-experiments CSV confirms the three exact string fields and live sample
  values.
- The Boltpro product CSV confirms backend task `TARGET_PEP_GEN`, the 11–50
  length range, and the PepPrCLIP output family.
- Live submission, terminal fetch, direct CSV download, and CSV inspection all
  succeeded; row count, uniqueness, sequence lengths, targets, and score range
  were checked.

## 11. Cyclic Binder

Design cyclic peptide binders against a selected target chain.

| Field | Value |
|---|---|
| **job_name** | `cyclic_binder` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `pdb_path` | string | yes | Uploaded file: `.pdb` |
| `target_chain` | string | yes | Use the exact source field. |
| `binder_len` | string | yes | Use the exact source field. |

**Output contract:** `OutputData.datainfo.output_path` -> results archive (product CSV).

---
