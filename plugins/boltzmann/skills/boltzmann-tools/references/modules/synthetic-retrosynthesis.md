# Retrosynthesis

Domain: Synthetic Chemistry

This module was selected by the server. Use only the exact contracts below.

## 47. Retrosynthesis

| Field | Value |
|-------|-------|
| **job_name** | `retrosynthesis` |
| **Mongo diagnostics collection** | `retrosynthesis` (verified sample record); pair with the returned experiment ID. |
| **watch_time** | ~60s |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `target_mol` | string | yes | Target molecule SMILES (NOT `target_smiles`) |
| `outname` | string | no | Default: `"scored_paths.json"` |
| `experiment_name` | string | no | Default: `"test_retro"` |

**Output:** JSON with scored retrosynthetic pathways.

**Output JSON keys:** `path, pathway_score, pathway_ranking_score, path_cost, scscore, sascore, starting_materials, index, num_steps`

---
