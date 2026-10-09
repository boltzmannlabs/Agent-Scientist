# Property Prediction

Domain: Protein Engineering

This module was selected by the server. Use only the exact contracts below.

## 7. Peptide Property Prediction

| Field | Value |
|-------|-------|
| **job_name** | `Peptide_Property_Prediction` |
| **WARNING** | May return 404 — check API for valid collection name |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `dataPath` | string | yes | S3 path to CSV (upload first) |
| `property_name` | list[string] | yes | `["antigenicity"]`, `["allergenicity"]`, `["toxicity"]` |
| `antigenictiy_reference` | int | no | Default: 0 |
| `allergenicity_reference` | int | no | Default: 0 |
| `toxicity_reference` | int | no | Default: 0 |

**Input CSV columns:** `Sequence_ID, Sequence`

**Output CSV columns:** `Sequence, antigenicity, allergenicity, toxicity`

---

## 8. Peptiverse

Predict selected peptide-related properties for records supplied through an
uploaded CSV.

| Field | Value |
|---|---|
| **job_name** | `peptiverse` |
| **Mongo diagnostics collection** | `peptiverse` (operator-confirmed; sample not verified); pair with the returned experiment ID. |
| **backend task/collection** | `peptiverse` |
| **validation status** | **Input schema verified from backend validation; submission HTTP 200 verified; successful terminal result still requires inspection** |
| **observed submission cost** | 25 credits |

### Inputs

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `input_path` | string | yes | Current user's remote CSV, UTF-8/UTF-8-sig, exactly one column: `sequences` (aliases `sequence`, `seq`) OR `smiles` (alias `smile`). No extra columns. The byte guard downloads and validates current bytes; prior workers' upload receipts are not required. Named pasted data can be built into this CSV; never guess an ambiguous input kind. |
| `properties` | list[string] | yes | One or more exact identifiers: `hemolysis`, `nf`, `solubility`, `permeability_penetrance`, `halflife`. |
| `job_name` | string | no | Optional inner run label documented by the consolidated sample. This is distinct from the outer helper argument `job_name="peptiverse"`; omit it unless needed. |

```python
from nodeapi_helpers import (
    file_upload,
    prepare_peptiverse_input_csv,
    validate_peptiverse_input_csv,
)

# Preserve the original candidate manifest. Project only the accepted values
# into a separate upload file; P2SMI's ID/sequence/SMILES table must never be
# uploaded directly to Peptiverse.
peptiverse_csv = prepare_peptiverse_input_csv(
    source_csv=candidate_manifest_or_p2smi_csv,
    output_csv="peptiverse_smiles.csv",
    input_kind="smiles",
    source_column="Smiles",
)
validate_peptiverse_input_csv(peptiverse_csv)
uploaded_csv_path = file_upload(peptiverse_csv)

job_name = "peptiverse"
experiment_name = "Peptiverse property prediction"
experiment_data = {
    "input_path": uploaded_csv_path,
    "properties": [
        "hemolysis",
        "nf",
        "solubility",
        "permeability_penetrance",
        "halflife",
    ],
}
```

`input_path` is a path-only field. The uploaded CSV contract is fail-closed:

- exactly one column;
- the header is exactly lowercase `sequences` or lowercase `smiles`;
- at least one non-empty data row;
- no ID, peptide-name, index, annotation, or second column.

For sequence-native prediction, create `sequences` plus one peptide sequence
per row. For a P2SMI handoff, preserve the full identity manifest separately
and project only its SMILES column into a new one-column `smiles` CSV. Never
upload P2SMI's multi-column output directly. If a reference candidate must be
evaluated separately, create a separate one-row file using the same exact
schema. Keep the source manifest so returned values can be reconciled by the
exact submitted sequence/SMILES after count and order validation.

`submit_request` requires durable validation evidence written by the current
runtime's `file_upload`. A missing proof, an unknown historical path, a
multi-column header such as `Peptide,Smiles`, an empty value, or an unsupported
property blocks submission before workflow logging or credit-spending network
submission.

### Output instructions

Use the returned document ID with `fetch_status` and the exact job name
`peptiverse`. The supplied product sources do not define terminal output keys or
columns. Preserve and inspect the complete terminal payload and every returned
artifact before describing property values. Do not report completion from the
HTTP 200 submission response alone.

### Evidence

- The consolidated tool source confirms the exact job name, `input_path`, and
  `hemolysis`/`permeability_penetrance` property values.
- The accepted submission in `testing_tools.py` confirms HTTP 200 with all five
  property identifiers shown above.
- Backend validation observed on 2026-08-28 confirms that the CSV must contain
  exactly one column named `sequences` or `smiles`; it rejected
  `['peptide', 'smiles']` because extra columns are not allowed.
- A successful terminal output shape remains unverified and must still be
  preserved and inspected before property values are described.

---

## 10. Antibody Property Prediction

| Field | Value |
|-------|-------|
| **job_name** | `Antibody_Prediction` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `dataPath` | string | yes | S3 path to CSV (upload first) |
| `scheme` | string | yes | `"imgt"`, `"kabat"`, `"chothia"` |
| `property_name` | list[string] | yes | See options below |

**property_name options:** `"Thermal_Stability_Protbert"`, `"Thermal_Stability_ESM"`, `"Solubility_ESM"`, `"Antigen_Antibody_binding"`, `"CDR_Prediction"`

**Input CSV columns:** `seq_id, Heavy_chain, Light_chain`

**Output key:** `result["OutputData"]["output_path"]["download_link"]`

**Output CSV columns:** `Unnamed: 0, seq_id, Heavy_chain, Light_chain, Thermal_stab_protbert` (only requested properties appear; values are strings like `"[49.32897]"`)

---

## 14. Enzymes
Predict one or more supported properties for enzyme sequences supplied in a
CSV file.

| Field | Value |
|---|---|
| **job_name** | `Enzymes` |
| **backend task/collection** | `ENZ_PROP` |
| **validation status** | **Verified working for four selected categories** |
| **observed terminal status** | `Success` |

### Inputs

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `dataPath` | string | yes | Platform path to the input CSV returned by `file_upload`. Preserve the capital `P`. |
| `property_name` | list[string] | yes | One or more exact backend property identifiers from the fixed mapping below. |

Use this exact UI-label-to-payload mapping:

| UI category | Value in `property_name` | Live-tested in current canary |
|---|---|---|
| pH prediction | `pHPred` | yes |
| Enzyme solubility | `enzyme_solubility` | yes |
| thermostability | `tmPred_enzymes` | yes |
| Function prediction | `function_prediction` | yes |
| Substrate prediction | `substrate_pred` | no; source- and UI-backed |

The current UI screenshot exposes exactly these five categories. A stale
product-sheet cell also mentions `Catalytic_site_pred`, but it is absent from
both the UI options and the product sheet's accepted option list. Do not submit
`Catalytic_site_pred` until a later live canary proves it.

The safest verified input CSV headers are:

```text
Seq_id,Sequences
```

The product sheet also documents `Sequence_ID` as an accepted identifier-header
variant, but `Seq_id` is the form preserved in the successful output. Keep one
enzyme sequence per row.

```python
uploaded_csv_path = file_upload(local_csv_path)

job_name = "Enzymes"
experiment_name = "Enzyme property prediction"
experiment_data = {
    "dataPath": uploaded_csv_path,
    "property_name": [
        "pHPred",
        "enzyme_solubility",
        "tmPred_enzymes",
        "function_prediction",
    ],
}
```

### Output instructions

The terminal result returns a directly downloadable CSV, not a ZIP:

```python
result["OutputData"]["outputFilePath"]["path"]
result["OutputData"]["outputFilePath"]["download_link"]
```

The live output had one row and these columns:

```text
Seq_id,Sequences,pHPred,enzyme_solubility,tmPred_enzymes,function_prediction
```

Only requested properties should be expected as prediction columns. Verify the
identifier and sequence columns and confirm every requested property appears
before reporting completion. The current canary did not request
`substrate_pred`, so its output-column behavior remains unverified.

### Evidence

- The Boltzyme product CSV confirms `dataPath`, `property_name`, task
  `ENZ_PROP`, the five accepted identifiers, and the input CSV shape.
- The UI screenshot confirms the five human-facing category labels.
- Live submission, terminal fetch, direct CSV download, and CSV parsing all
  succeeded. All four requested property columns were present.

## 15. Vaccines

Screen peptide sequences for vaccine-related antigenicity, allergenicity, and toxicity.

| Field | Value |
|---|---|
| **job_name** | `Vaccines` |
| **Mongo diagnostics collection** | `PEP_PROP` (verified sample record); pair with the returned experiment ID. |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `dataPath` | string | yes | Uploaded CSV containing a `Sequences` column |
| `property_name` | array[string] | yes | Any of `Allergenicity`, `Antigenicity`, `Toxicity`, `Epitope` |
| `toxicity_reference` | number | no | Accepted by the API; product source says backend currently ignores it |
| `allergenicity_reference` | number | no | Accepted by the API; product source says backend currently ignores it |
| `antigenictiy_reference` | number | no | Preserve this backend misspelling; currently ignored |

**Output contract:** `OutputData.datainfo.outputFilePath` (product CSV).

---

## 39. Kcatnet

Predict enzyme turnover values from protein sequences and substrate SMILES.

| Field | Value |
|---|---|
| **job_name** | `kcatnet` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_path` | string | yes | Uploaded file: `.csv` |

**Output contract:** `OutputData.datainfo.outputFilePath` (product CSV).

---

## 40. Kinetic Kcat

Predict enzyme kcat or Km values from sequence-substrate pairs.

| Field | Value |
|---|---|
| **job_name** | `kcat_km` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_path` | mixed | yes | Use the exact source field. |
| `prediction_type` | string | yes | values: `kcat, km` |

**Output contract:** `OutputData.datainfo.outputFilePath` -> CSV (product CSV).

---
