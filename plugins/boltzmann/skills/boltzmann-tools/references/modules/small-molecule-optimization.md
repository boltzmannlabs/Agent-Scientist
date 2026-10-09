# Molecule Optimization

Domain: Small Molecule Design

This module was selected by the server. Use only the exact contracts below.

## 40. Lead Generation — Reinvent

| Field | Value |
|-------|-------|
| **job_name** | `Lead_Generation_Reinvent` |
| **watch_time** | ~120s |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `n_mols` | int | yes | Number of molecules |
| `n_steps` | int | yes | Number of RL steps |
| `data_path` | string | yes | S3 path to CSV (upload first) |
| `name` | string | yes | Experiment name |
| `dataType` | string | yes | `"csv"` (required when finetune=false) |
| `reward` | string | no | Default: `"MWS"` |
| `model_path` | string | no | Pretrained model path |
| `finetune` | string | no | Default: `"false"` |
| `tar_seq` | string | no | Target sequence |
| `off_tar_seqs` | list[string] | no | Off-target sequences |
| `global_models` | list | yes | At least one model |
| `custom_models` | list | yes | At least one model (id must be valid MongoDB ObjectId) |

**Input CSV columns:** `SMILES`

---

## 41. Lead Generation — Augmented

| Field | Value |
|-------|-------|
| **job_name** | `Lead_Generation_Augmented` |
| **watch_time** | ~120s |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `method` | string | no | Default: `"smiles_aug_mem"` |
| `no_of_molecules` | int | yes | Number of molecules |
| `steps` | int | yes | Number of steps |
| `data_path` | string | yes | S3 path to CSV (upload first) |
| `name` | string | yes | Experiment name |
| `dataType` | string | yes | `"csv"` (required when finetune=false) |
| `global_models` | list | yes | At least one model |
| `custom_models` | list | yes | At least one model |

---
