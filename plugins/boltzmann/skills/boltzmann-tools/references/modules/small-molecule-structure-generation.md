# Structure-Based Generation

Domain: Small Molecule Design

This module was selected by the server. Use only the exact contracts below.

## 26. Structure-Based Generator
Generate small molecules for an uploaded protein binding-pocket structure,
optionally filtering the generated molecules with selected property models.

| Field | Value |
|---|---|
| **job_name** | `Structure_Based_Generator` |
| **backend task** | `structurebasedgen` |
| **validation status** | **Verified working for a thresholded global-model submission** |
| **accepted structure input** | uploaded `.pdb` platform path |
| **observed terminal status** | `Success` |

### Inputs

The three generation fields are compulsory. Model selection is optional and
must obey the conditional schema below.

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `protein_Path` | platform path string | yes | Uploaded binding-pocket or protein `.pdb` path. Raw sequence, local paths, PDB text, and HTTP URLs are invalid. |
| `no_of_shapes` | integer | yes | Number of shapes to generate; minimum 1. Send an integer, not a string. |
| `no_of_decodings` | integer | yes | Number of decodings; minimum 1. Send an integer, not a string. |
| `model_category` | string | no | Optional model category. The verified sample used exact value `ML`. |
| `global_models` | list of objects | conditional | Optional. Omit it or send `[]` when no global property model is selected. When selected, every item requires `name`, `min_threshold`, and `max_threshold`. |
| `custom_models` | list | no | Optional. Omit it or send `[]` when no custom model is selected. A non-empty custom-model item schema has not yet been live-verified, so do not invent one. |

`protein_Path` follows the shared path-only invariant. Upload an existing valid
PDB with `file_upload` and submit only the returned platform path. A raw protein
sequence cannot be converted directly into a valid pocket PDB. If the user has
only a sequence, run an explicitly requested structure-prediction and, when
needed, binding-site/pocket-extraction workflow before this tool.

### Conditional model-selection contract

Apply these cases exactly:

| Selection state | Payload representation | Validity |
|---|---|---|
| No property model selected | Omit `global_models` and `custom_models` | Valid; observed submission response HTTP 200. |
| No property model selected | Send both as empty lists | Valid; observed submission response HTTP 200. |
| Global model selected as a bare string, for example `"global_models": ["QED"]` | List of strings | **Invalid**; observed submission response HTTP 500. Do not retry the identical payload. |
| Global model selected with thresholds | List of objects containing `name`, `min_threshold`, and `max_threshold` | Valid; thresholded LD50 sample returned HTTP 200 and reached terminal `Success`. |

For every selected global model:

- require a non-empty `name`;
- require both `min_threshold` and `max_threshold`;
- accept the threshold values in the API-proven string representation;
- validate that both thresholds are numeric and
  `max_threshold >= min_threshold` before submission;
- never transform a model name into a bare string-list item.

The requirement is conditional: thresholds are compulsory **per selected
global model**, but `global_models` itself is not compulsory when no model is
selected.

### Valid payloads

Without property filtering, either omit the model arrays:

```python
uploaded_pocket_path = file_upload(local_pocket_pdb)

job_name = "Structure_Based_Generator"
experiment_name = "Structure-based generation without property filtering"
experiment_data = {
    "protein_Path": uploaded_pocket_path,
    "no_of_shapes": 3,
    "no_of_decodings": 4,
    "model_category": "ML",
}
```

or represent the absence of selections explicitly:

```python
experiment_data = {
    "protein_Path": uploaded_pocket_path,
    "no_of_shapes": 3,
    "no_of_decodings": 4,
    "model_category": "ML",
    "global_models": [],
    "custom_models": [],
}
```

With a selected global model, submit an object with thresholds:

```python
job_name = "Structure_Based_Generator"
experiment_name = "Structure-based generation with LD50 filtering"
experiment_data = {
    "protein_Path": uploaded_pocket_path,
    "no_of_shapes": 3,
    "no_of_decodings": 4,
    "model_category": "ML",
    "global_models": [
        {
            "name": "LD50",
            "min_threshold": "1",
            "max_threshold": "5",
        }
    ],
    "custom_models": [],
}
```

Never submit this invalid representation:

```python
experiment_data = {
    "protein_Path": uploaded_pocket_path,
    "no_of_shapes": 3,
    "no_of_decodings": 4,
    "model_category": "ML",
    "global_models": ["QED"],  # Invalid: thresholds are missing.
    "custom_models": [],
}
```

An HTTP 500 from that bare-string representation is a payload-schema failure,
not evidence that the tool is unavailable. Correct the model item to the
threshold object form before making a new submission.

### Output instructions

The verified terminal result used this envelope:

```python
result["OutputData"]["rawdata_path"]["path"]
result["OutputData"]["rawdata_path"]["download_link"]
```

`download_link` was a list even though the canary exposed one file, so handle
both list and string forms. The downloaded `rawdata.csv` contained 10 generated
molecules with these columns:

```text
SMILES,QED,SA,TPSA,NUM_HDONORS,NUM_HACCEPTORS,Molecular Weight
```

Validate that the CSV is non-empty, parse every `SMILES`, and report the actual
row count rather than assuming it equals `no_of_shapes * no_of_decodings`.
When property models are selected, verify the returned columns and values from
the artifact instead of assuming that every requested filter produces a named
output column.

### Evidence

- The all-experiments source defines the compulsory PDB path,
  `no_of_shapes`, and `no_of_decodings` fields and their minimum values.
- The BoltChem product source identifies backend task `structurebasedgen` and
  documents raw and filtered generation outputs.
- The thresholded `LD50` object payload returned HTTP 200; its existing result
  record returned HTTP 200 with terminal `Success`.
- The signed artifact downloaded successfully and parsed as a 10-row CSV with
  the seven columns listed above.
- The no-model omitted-array case, no-model empty-array case, and invalid bare
  string-list case are recorded as observed API behavior; keep them as explicit
  regression cases when this contract is promoted.

## 27. Substructure-Based Generation (subgen)

| Field | Value |
|-------|-------|
| **job_name** | `Substructures` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `filePath` | string | yes | S3 path to CSV (upload first) |
| `max_atoms` | int | yes | Maximum atoms |
| `prop_model_category` | string | no | Default: `"ML"` |
| `global_models` | list | yes | At least one model |
| `custom_models` | list | yes | At least one model |

**Input CSV columns:** `SMILES`

**Output CSV columns:** `SMILES, rationales, num_atoms, reward, QED, SA, TPSA, NUM_HDONORS, NUM_HACCEPTORS, Molecular Weight`

---

## 28. Merge Substructure

| Field | Value |
|-------|-------|
| **job_name** | `Merge_Substructure` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `rationale_path_1` | string | yes | S3 path (from subgen output) |
| `rationale_path_2` | string | yes | S3 path (from subgen output) |
| `prop_model_category` | string | no | Default: `"ML"` |
| `global_models` | list | yes | At least one model |
| `custom_models` | list | yes | At least one model |

---

## 29. Fragment-Based Generation Inference (gflowinf)

| Field | Value |
|-------|-------|
| **job_name** | `Fragment_based_generation_Inference` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `model_name` | string | yes | Model name |
| `gen_model_path` | string | yes | S3 path to trained model |
| `num_samples` | int | yes | Number of molecules |
| `prop_model_category` | string | no | Default: `"ML"` |
| `global_models` | list | yes | At least one model |
| `custom_models` | list | yes | At least one model |

**Output CSV columns:** `SMILES, QED, SA, TPSA, NUM_HDONORS, NUM_HACCEPTORS`

---


---

## Verified BoltChem contract overlay (2026-09-08)

The following section is the current verified BoltChem contract for this module. It overrides conflicting legacy text above. Do not submit until its required fields, exact enums, file headers, and validation rules pass.

### Structure-Based Generator

# Structure-Based Generator
Tool display name: Structure-Based Generator
Frontend route/screen: Small Molecule Design → Structure-Based Generation
Purpose: Generate small molecules for an uploaded protein binding-pocket
structure, optionally filtering the generated molecules with selected property
models.
Exact form fields:
- `protein_Path`
- `no_of_shapes`
- `no_of_decodings`
- `model_category` (optional)
- `global_models` (optional/conditional)
- `custom_models` (optional)
Required fields:
- `protein_Path`: uploaded `.pdb` platform path.
- `no_of_shapes`: integer, minimum `1`.
- `no_of_decodings`: integer, minimum `1`.
Optional fields:
- `model_category`; the verified sample used exact value `ML`.
- `global_models`; omit it or send `[]` when no property filter is selected.
- `custom_models`; omit it or send `[]` when no custom model is selected.
Allowed choices and exact spelling:
- `model_category`: verified sample value `ML`.
- Each selected global model must be an object containing exactly the relevant
  model name and numeric threshold bounds:
  `{ "name": "LD50", "min_threshold": "1", "max_threshold": "5" }`.
- If any global model is selected, both thresholds are mandatory and must be
  explicitly supplied by the user. Never invent, infer, default, or choose
  `min_threshold` or `max_threshold`.
- Threshold values may use the API's verified string representation, but must
  be numeric and `max_threshold >= min_threshold`.
- A selected global model must never be sent as a bare string such as
  `"global_models": ["QED"]`.
Sample input file: uploaded protein binding-pocket `.pdb` file (local sample
path not supplied in this packet).
Required file format: `.pdb`.
Required column names: not applicable to the PDB input.
Sample output file: verified `rawdata.csv` artifact.
Output file column names:
`SMILES,QED,SA,TPSA,NUM_HDONORS,NUM_HACCEPTORS,Molecular Weight`
Actual backend/network payload:
```python
uploaded_pocket_path = file_upload(local_pocket_pdb)

experiment_data = {
    "protein_Path": uploaded_pocket_path,
    "no_of_shapes": 3,
    "no_of_decodings": 4,
    "model_category": "ML",
    "global_models": [
        {"name": "LD50", "min_threshold": "1", "max_threshold": "5"}
    ],
    "custom_models": [],
}
job_name = "Structure_Based_Generator"
experiment_name = "Structure-based generation with LD50 filtering"
```
Exact backend job name, if visible: `Structure_Based_Generator`
Backend task: `structurebasedgen`
Validation status: verified working for a thresholded global-model submission;
terminal status was `Success`.
Known validation or failure messages:
- Raw sequence, PDB text, local paths, and HTTP URLs are invalid for
  `protein_Path`; upload an existing `.pdb` and use the returned platform path.
- `no_of_shapes` and `no_of_decodings` must be integers greater than or equal
  to `1`.
- With no property filtering, omitting both model arrays or sending both as
  empty arrays was observed valid (HTTP 200).
- Bare-string global models such as `global_models: ["QED"]` were observed
  invalid (HTTP 500); do not retry that identical payload.
- A non-empty custom-model item schema is not live-verified; do not invent it.
- A terminal output without a readable, non-empty CSV is unverified.

Submission instructions:
1. Confirm that the user has an existing valid binding-pocket/protein `.pdb`.
2. Upload it with `file_upload()` and use the returned path as
   `experimentData.protein_Path`.
3. Require integer `no_of_shapes >= 1` and `no_of_decodings >= 1`.
4. If global models are selected, require threshold objects with `name`,
   `min_threshold`, and `max_threshold` for every selected model. Ask the
   user for both threshold values when either is missing; never supply them
   on the user's behalf.
5. Submit once with `Structure_Based_Generator`.
6. Poll the returned document ID with the same job name and verify the
   downloaded artifact before reporting generated molecules.

Polling and timeout behavior:
- Continue polling while the job is queued, pending, or running.
- A client-side timeout does not prove failure; do not create a duplicate job
  until the original job's terminal state or absence is established.
- Retry transient status/download errors only through the existing helper
  behavior.

Output verification:
- Read the path from `OutputData.rawdata_path.path` and the download link from
  `OutputData.rawdata_path.download_link`.
- Handle `download_link` as either a list or a string.
- Verify the downloaded CSV is non-empty and parse every returned `SMILES`.
- Report the actual row count; do not assume it equals
  `no_of_shapes * no_of_decodings`.
- When property filters are selected, verify returned columns and values from
  the artifact instead of assuming every filter creates a named column.
