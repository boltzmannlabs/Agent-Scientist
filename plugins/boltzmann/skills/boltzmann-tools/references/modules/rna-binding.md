# Binding Tools

Domain: RNA Design

This module was selected by the server. Use only the exact contracts below.

## 85. RNA_Binding_Specificity_Prediction

Predict ligand-binding specificity for an RNA sequence.

| Field | Value |
|---|---|
| **job_name** | `rna_bind_specificity_pred` |
| **contract status** | live-verified end to end |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `ligand_csv` | string | yes | Use the exact source field. |
| `rna_sequence` | string | yes | Use the exact source field. |
| `user_id` | string | yes | Use the exact source field. |

**Output contract:** Live-verified `OutputData.outputFilePath`; download and inspect the result archive.

The UI calls the sequence field `rnasequence`, but the accepted backend
field is `rna_sequence`. The verified archive contains `specificity_prediction.csv`
with `ligand_id`, `smiles`, `binding_probability`, and `uncertainty`, plus docked
complexes and RNA structure artifacts. Rank with probability and uncertainty
together rather than inferring quality from filenames.

---

## 86. RNA Pocket Prediction

Predict RNA binding pockets from one or more RNA structures.

| Field | Value |
|---|---|
| **job_name** | `rna_pocket_pred` |
| **contract status** | live-verified end to end |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_pdb` | string | yes | Use the exact source field. |
| `threshold` | number | yes | Use the exact source field. |
| `user_id` | string | yes | Use the exact source field. |

**Output contract:** Live-verified `OutputData.outputFilePath`; download and inspect the result archive.

Pass `input_pdb` as one scalar platform path even though the UI sample
wraps it in a list. The verified sample used `threshold=0.7`. The archive contains
`pocket_predictions.json` with `probs`, `binding_sites`, and `contacts`, plus one
pocket PDB per input structure.

---

## 87. Protein-RNA Interaction Prediction

Predict interaction between RNA and protein sequences supplied as FASTA files.

| Field | Value |
|---|---|
| **job_name** | `Rna_Inter_Pred` |
| **contract status** | submission accepted; output unverified |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `user_id` | string | yes | Use the exact source field. |
| `rna_file` | string | yes | Use the exact source field. |
| `protein_file` | string | yes | Use the exact source field. |

**Output contract:** Submission accepted but no terminal result was observed through 25 minutes; continue polling the original job and inspect the first terminal `OutputData`.

A live sample payload was accepted and remained pending through 25 minutes.
Acceptance proves the request schema, not successful execution. Do not resubmit;
continue polling the original job. Do not assume `outputFilePath` until a terminal
success exposes the real result key.

---
