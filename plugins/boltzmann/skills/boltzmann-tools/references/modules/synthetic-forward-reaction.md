# Forward Reaction

Domain: Synthetic Chemistry

This module was selected by the server. Use only the exact contracts below.

## 48. Forward Reaction Prediction

| Field | Value |
|-------|-------|
| **job_name** | `forward_reaction` |
| **Mongo diagnostics collection** | `forward_reaction` (live-verified 2026-09-25); pair with the returned experiment ID. The previous `retrosynthesis` mapping did not contain the verified forward-reaction record. |
| **watch_time** | ~30s |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `target_mol` | string | yes | SMILES of reactants (NOT `reactants`) |
| `intermediates` | string | no | Optional SMILES of known intermediates |

**Output:** JSON with predicted products.

**Output keys:** `predictions: [{SMILES: str, score: float}, ...]`

---

## 49. Impurity Prediction

| Field | Value |
|-------|-------|
| **job_name** | `impurity_prediction` |
| **Mongo diagnostics collection** | `impurities` (verified sample record); pair with the returned experiment ID. |
| **watch_time** | ~30s |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `session_id` | string | yes | Session identifier |
| `reactants` | string | yes | Reactant SMILES |
| `products` | string | yes | Expected product SMILES |
| `experiment_name` | string | no | Default: `"test"` |

**Output keys:** `impurities: [{prd_smiles, feasibility_score, similarity_to_product}, ...]`

---

## 50. Atom Mapping

| Field | Value |
|-------|-------|
| **job_name** | `atom_mapping` |
| **Mongo diagnostics collection** | `atommapping` (verified sample record); pair with the returned experiment ID. |
| **watch_time** | ~30s |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `session_id` | string | yes | Session identifier |
| `reactants` | string | yes | Reactant SMILES |
| `products` | string | yes | Product SMILES |
| `experiment_name` | string | no | Default: `"test"` |

**Output keys:** `mapped_rxn, confidence, atom_map_details, source_rxn_smiles`

---

## 51. Condition Recommendation

| Field | Value |
|-------|-------|
| **job_name** | `condition_recommendation` |
| **Mongo diagnostics collection** | `condition_recommendation` (verified sample record); pair with the returned experiment ID. |
| **watch_time** | ~30s |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `session_id` | string | yes | Session identifier |
| `reactants` | string | yes | Reactant SMILES |
| `products` | string | yes | Product SMILES |
| `experiment_name` | string | no | Default: `"test"` |

**Output keys:** `ranked_conditions: {top0: {solvent1, catalyst, reagent1, expected_yield}, ...}, confidence_scores`

---

# RNA / mRNA Design
