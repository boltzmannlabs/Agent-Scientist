# RNA Inverse Folding

Domain: RNA Design

This module was selected by the server. Use only the exact contracts below.

## 56. RNA 2D Inverse Folding

Design RNA sequences that fold into a target secondary structure (inverse folding).

| Field | Value |
|-------|-------|
| **job_name** | `rna_inverse_fold` |
| **watch_time** | ~20 s to 2 min |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `n_gen` | int | yes | Number of candidate sequences — pass as an INTEGER (`5`), **not** a string (differs from other RNA tools) |
| `struct_name` | string | yes | Structure template label; e.g. `"vienna_simple_hairpin"` |
| `second_struct` | string | yes | Target secondary structure in dot-bracket notation; e.g. `"(((.(((....))).)))"` |
| `target_seq` | string | yes | Seed / target RNA sequence; e.g. `"GGGGGGGAAAACCCACCC"` |
| `experiment_name` | string | no | Experiment label (top-level, not inside `experimentData`) |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — a **list** of signed URLs → `results.zip`
**Path key:** `result["OutputData"]["outputFilePath"]["path"]`

---

## 84. RNA Tertiary Folding

Run tertiary RNA folding for a supplied PDB identifier.

| Field | Value |
|---|---|
| **job_name** | `TertiaryFolding` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `pdb_id` | string | yes | Use the exact source field. |

**Output contract:** Not documented in the supplied CSVs; inspect the first terminal payload.

---
