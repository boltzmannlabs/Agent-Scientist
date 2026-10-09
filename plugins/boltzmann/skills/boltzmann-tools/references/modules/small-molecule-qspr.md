# QSPR Modelling

Domain: Small Molecule Design

This module was selected by the server. Use only the exact contracts below.

## 23. Property Prediction (propinf)

| Field | Value |
|-------|-------|
| **job_name** | `Property_Prediction` |
| **validation status** | **Submission verified (HTTP 200)** |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `smiles` | string | yes | S3 path to CSV (upload first). A bare SMILES string is **rejected** (`"smiles file must be a uploaded .csv file containing smiles"`); it MUST be an uploaded CSV. All rows are predicted in one call. |
| `global_models` | list[string] | yes | Model names as **strings** (not objects, no thresholds). See format + names below. |
| `uncertainty` | integer or string flag | yes | Must be explicitly selected as `0` or `1`; string `"0"`/`"1"` remains source-backed. |
| `explainability` | integer or string flag | yes | Must be explicitly selected as `0` or `1`; string `"0"`/`"1"` remains source-backed. |

**There is NO `models` field.** Sending `models` (in any shape) makes the downstream service throw HTTP 500; sending object-form `global_models` (e.g. `{"name":...,"min_threshold":...}`) is rejected HTTP 400. Use name **strings** only.

**global_models format** — a JSON array of model-name strings:
```json
["Solubility", "BBB", "Bioavailability", "AMES", "DILI", "hERG", "Lipophilicity", "Cyp3a4 inh", "LD50", "Clearance"]
```

**Available global model names (50+):** `CaCo2 permeability`, `Clearance`, `Half Life`, `Hydration Free Energy`, `LD50`, `Lipophilicity`, `PPBR`, `rPPB`, `hPPB`, `Solubility`, `VDss`, `AMES`, `BBB`, `Bioavailability`, `HIA`, `PAMPA`, `PGP`, `PGP_inh`, `Carcinogenicity`, `Skin reaction`, `DILI`, `hERG`, `Cyp1a2 inh`, `Cyp2c9 inh`, `Cyp2c9 sub`, `Cyp2c19 inh`, `Cyp2d6 inh`, `Cyp2d6 sub`, `Cyp3a4 inh`, `Cyp3a4 sub`, plus Tox21-style `SR-*` / `NR-*` endpoints.

**Input CSV columns:** `SMILES`

**Output CSV columns:** `SMILES, <property_name>, <property_name>_uncertainty, <model_specific_columns>`

Submission-verified example:

```python
job_name = "Property_Prediction"
experiment_name = "Molecular property prediction"
experiment_data = {
    "smiles": uploaded_smiles_csv,
    "uncertainty": 1,
    "explainability": 1,
    "global_models": ["CaCo2 permeability"],
}
```

This exact payload returned HTTP 200 and a document ID. Terminal output for
this new canary has not yet been inspected.

## Property Prediction — Frontend clarification and preflight

The frontend describes this tool as **Property Prediction** under Small
Molecule Design → QSPR Modelling. It evaluates physicochemical,
pharmacokinetic, ADMET, and toxicity properties. It also exposes optional
custom property models for domain-specific endpoints such as pIC50, which can
be used as an activity estimate. These are computational predictions, not
experimental measurements.

### Compare the user's request with the input contract

Before submission, compare the received request and file against the schema and
tell the user both what is present and what is missing:

Required:
- one uploaded CSV path in `experimentData.smiles`;
- a non-empty `global_models` list of exact model-name strings;
- explicit `uncertainty` and `explainability` values (`0` or `1`);
- a CSV header exactly named `SMILES` (uppercase).

Optional:
- top-level `experimentName`;
- a selected `custom_models` entry when the current backend contract confirms
  the accepted model-ID and payload shape.

Do not demand output-only fields such as `ACTIVITY`, QED, TPSA, or molecular
descriptors in a new input file. The supplied example output contained 14 rows
with these observed columns:

```text
SMILES, ACTIVITY, CaCo2_permeability, QED, SA, TPSA,
NUM_HDONORS, NUM_HACCEPTORS, Molecular Weight
```

Those columns are evidence of one returned result, not additional universal
input requirements.

### Input-file rules

- Accept exactly one readable `.csv` molecule-library file.
- Require the exact uppercase header `SMILES`; no aliases are allowed for this
  contract. Additional columns are accepted by the live backend: it consumes
  `SMILES` and ignores unrelated columns. Preserve those columns and do not
  reject or silently project them away.
- Require at least one data row and a non-empty, chemically valid SMILES in
  every row.
- No hard row or byte limit is documented; do not invent one.
- The submitted `smiles` value must be the cloud path returned by upload, never
  a bare SMILES string, local path, or URL.

### Safe normalization and non-fabrication

Never overwrite the user's original file. A UTF-8 BOM may be ignored as an
encoding marker, but do not lowercase, trim, rename, or infer the `SMILES`
header. Do not silently delete, reorder, or rewrite molecule rows. Never
fabricate SMILES values, missing rows, model selections, flags, custom-model
IDs, or uploaded paths. A missing/incorrect header or value requires a corrected
file from the user.

### Clarification examples

If the file is present but required selections are missing:

> I received the CSV and verified the exact `SMILES` header. To run Property
> Prediction, please select at least one global property model and provide
> uncertainty and explainability values (`0` or `1`). `experimentName` and (if
> supported) a custom model such as pIC50 are optional.

If the header is wrong or missing:

> I cannot submit this CSV because the required header is exactly `SMILES` and
> no aliases are accepted. Please upload a corrected file; I will not invent the
> missing molecule column.

If a custom pIC50 model is requested:

> Please select the trained custom model and provide its model identifier. I
> will verify that the current backend accepts that custom selection before
> submitting.

### Submission, polling, and output

Upload the validated CSV, pass the returned path as `experimentData.smiles`,
include explicit `uncertainty` and `explainability` values, submit once with
`Property_Prediction`, and poll the same document with the same exact job name.
Pending/queued is not failure and is not a reason to duplicate a job. Validate
that `OutputData.output_path` is readable and that the returned rows correspond
to the submitted molecules before claiming success.

### External previous-result reuse

This is not an input field. A fresh worker may not have the previous local file,
so a follow-up can use the external continuity record to fetch the exact
completed result by job name and document ID. Say `I reused the previous
generated file` only after that exact fetch succeeds. Never use that phrase for
a local cache, conversation text, failed/pending result, or unreachable
platform.

### Failure handling

Missing required input, an invalid SMILES, a wrong header, an unsupported model,
or an invalid flag must stop submission and produce a specific clarification.
Do not fabricate missing data. Preserve the request on platform failure and
retry only after correcting the cause; a failed, pending, or unreachable prior
result must be reported as unavailable for reuse.

---

## 24. AutoML (Custom Property Model)

Current mode contract (public API form and operator video, 2026-09-24):
category selects the job; task independently selects regression/classification.
Do not route either category through the legacy `automl` name. The older
live examples below remain evidence for those combinations only.

| Category | Exact `job_name` | Current model selection |
|---|---|---|
| DL | `Custom_Property_Model_DL` | scalar `modelName="DL"`; regression or classification |
| ML | `Custom_Property_Model_Automl` | array of selected model names; regression or classification |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `property_name` | string | yes | Property label |
| `filepath` | string | yes | S3 path to CSV (upload first) |
| `modeltype` | string | yes | `"regression"` or `"classification"` |
| `features` | string | ML only | `descriptors` or `fingerprints`; absent for DL |
| `splittype` | string | ML only | `scaffoldsplit` or `randomsplit`; absent for DL |
| `modelName` | string or list[string] | yes | DL: scalar `DL`. ML: array using compiled task-specific choices; logistic/svm are classification-only. |
| `transformation` | string | no | Default: `"no"` |

**Input CSV columns:** `SMILES, ACTIVITY`

**Output CSV columns:** `index, SMILES, Label, uncertainty_higher, uncertainty_lower, ACTIVITY, uncertainty`

Classification requires binary `ACTIVITY` labels with reasonable class balance;
regression requires continuous labels. Preserve each mode's exact payload shape.

---

## 44. Synergy Prediction

| Field | Value |
|-------|-------|
| **job_name** | `Synergy_Prediction` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `smile_1` | string | yes | Drug 1 SMILES |
| `smile_2` | string | no | Drug 2 SMILES |
| `cell_line_type` | string | yes | e.g., `"THYROID"`, `"PROSTATE"`, `"KIDNEY"`, `"OVARY"`, `"SKIN"`, `"SALIVARY_GLAND"` |

---

# Retrosynthesis (ReBolt)

## 72. global_ic50

Predict IC50 from a molecule, protein sequence, or uploaded batch.

| Field | Value |
|---|---|
| **job_name** | `global_ic50` |
| **contract status** | live-verified end to end |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `smiles` | string | yes | One ligand SMILES; the live-verified contract is scalar, not batch |
| `sequence` | string | yes | One target protein sequence in one-letter notation |
| `filepath` | uploaded CSV | alternative | CSV containing `SMILES,SEQUENCES`; use this batch mode instead of the scalar pair |

**Output contract:** Live-verified `results.csv` with `smiles`, `sequence`, `pIC50`, and `IC50_nM`.

The verified request is one ligand and one target per call. Although the
lower-level schema may accept empty fields, always supply both values: an empty
payload can be accepted while wasting a job. Interpret both reported scales;
`pIC50` is logarithmic while `IC50_nM` is the corresponding nanomolar value.

The clarification must offer both routes: the existing pasted `smiles` plus
`sequence` pair, and an uploaded CSV through `filepath` with exact headers
`SMILES,SEQUENCES`.

---


---

## Verified BoltChem contract overlay (2026-09-08)

The following section is the current verified BoltChem contract for this module. It overrides conflicting legacy text above. Do not submit until its required fields, exact enums, file headers, and validation rules pass.

### Property Prediction and IC50

# Property Prediction
Tool display name:
Property Prediction

Frontend route/screen:
Small Molecule Design → QSPR Modelling

Exact form fields:
- Molecule input / smiles
- Uncertainty
- Explainability
- Global Property Models
- Experiment name (optional)
- Custom property model (optional and backend-dependent)

Required fields:
- One uploaded CSV path in experimentData.smiles
- CSV header exactly: SMILES
- At least one global_models selection
- uncertainty: 0 or 1
- explainability: 0 or 1

Optional fields:
- experimentName
- custom_models with a real supported model ID

Allowed choices and exact spelling:
- uncertainty: 0, 1
- explainability: 0, 1
- global_models: exact backend model-name strings, including:
  CaCo2 permeability, Half Life, Solubility, VDss, GIA, Clearance,
  Hydration Free Energy, LD50, Lipophilicity, PPBR, rPPB, hPPB,
  BBB, Bioavailability, HIA, PAMPA, PGP_inh, AMES, Carcinogenicity,
  DILI, hERG, Cyp1a2 inh, Cyp2c9 inh, Cyp2c9 sub, Cyp2c19 inh,
  Cyp2d6 inh, Cyp2d6 sub, Cyp3a4 inh, Cyp3a4 sub, and documented
  NR-* / SR-* endpoints.
- `Cyp2d9` entries in the older document should not be trusted; the
  verified backend spelling is `Cyp2d6`.

Sample input file:
One CSV containing:

SMILES
CCO
CC(=O)O
c1ccccc1
CC(C)O
C1CCCCC1

Required file format:
Exactly one readable `.csv` molecule-library file.

Required column names:
Exactly `SMILES` in uppercase.

Sample output file:
bpp_6a8ffd076534fa00c1b79871.csv

Observed output columns:
SMILES, ACTIVITY, CaCo2_permeability, QED, SA, TPSA,
NUM_HDONORS, NUM_HACCEPTORS, Molecular Weight

These are observed output columns, not universal input requirements.

Actual backend/network payload:
{
  "experimentData": {
    "smiles": "<cloud path returned by file_upload>",
    "uncertainty": 1,
    "explainability": 1,
    "global_models": ["CaCo2 permeability"]
  },
  "job_name": "Property_Prediction",
  "experimentName": "property_prediction_sample"
}

Exact backend job name:
Property_Prediction

Known validation or failure messages:
- Bare SMILES or a local path is rejected; smiles must be an uploaded CSV path.
- Wrong or missing header is rejected because it must be exactly SMILES.
- Empty global_models is invalid.
- uncertainty and explainability must be explicitly 0 or 1.
- Object-form global_models is invalid; use a list of strings.
- Sending an unsupported models field can produce HTTP 500.
- Missing model artifacts can produce signed-URL download errors such as HTTP 404.
- “Failed to generate output” is a terminal backend failure, not a valid result.
# IC50
Tool display name:Global IC50
Frontend route/screen:Small Molecule Design → QSPR Modelling
Exact form fields:
- `filepath` — uploaded CSV path for multiple molecule/sequence pairs.
- `smiles` — one ligand SMILES for the single-pair mode.
- `sequence` — one target protein sequence for the single-pair mode.
Required fields:
- Exactly one input mode is required:
  - Batch mode: `filepath` containing multiple paired rows.
  - Single-pair mode: both `smiles` and `sequence`.
- `experimentData` must contain the selected mode and must not mix an uploaded
  `filepath` with scalar values unless the backend contract explicitly requires
  both.
Optional fields:
- `experimentName` — optional experiment label.
Allowed choices and exact spelling:
- No enumerated model or flag choices are defined.
- `smiles` values must be non-empty, valid ligand SMILES strings.
- `sequence` values must be non-empty protein sequences in one-letter amino-acid
  notation.
- For batch mode, preserve the exact CSV headers `SMILES,SEQUENCES`.
- The backend wire key is singular `sequence`; the sample CSV header is plural
  `SEQUENCES` and must not be silently renamed without evidence.
Sample input file:/path/to/approved-input-or-output
Required file format:csv
Required column names:SMILES,SEQUENCES
Sample output file:/path/to/approved-input-or-output
output file column names: smiles,sequence,pIC50,IC50_nM
Actual backend/network payload:
data = {
        "experimentData": {
            "filepath": "CURRENT_USER_UPLOAD_PATH"
        },
        "job_name": "global_ic50",
        "experimentName": "prime"
    }

data = {
        "experimentData": {
            "smiles": "O=C1CCCC2=C1C1(CCS(=O)(=O)C1)NC(Nc1nc3ccccc3o1)=N2",
            "sequence": "USER_SUPPLIED_PROTEIN_SEQUENCE"
        },
        "job_name": "global_ic50",
        "experimentName": "global_ic50_test"
    }
Exact backend job name, if visible:global_ic50
Known validation or failure messages:
- A missing `filepath` in batch mode, or a missing `smiles`/`sequence` value in
  single-pair mode, is incomplete and must be clarified before submission.
- An unreadable, empty, malformed, or incorrectly headed CSV must be rejected
  before upload.
- Do not submit raw CSV text, a local filesystem path, or an HTTP URL as
  `experimentData.filepath`; use the cloud path returned by `file_upload()`.
- Do not treat a pending or queued result as a failure and do not duplicate the
  job while polling.
- A terminal result without `smiles`, `sequence`, `pIC50`, and `IC50_nM` is
  unverified and must not be reported as a successful prediction.

Submission instructions:
1. If the user supplies multiple pairs, validate one CSV with exact headers
   `SMILES,SEQUENCES`, upload it, and pass the returned cloud path as
   `experimentData.filepath`.
2. If the user supplies one pair, pass both scalar `smiles` and `sequence` in
   `experimentData` as shown in the verified payload.
3. Submit once using the exact job name `global_ic50` and keep
   `experimentName` top-level when supplied.
4. Poll the returned document ID with the same exact job name and verify the
   downloaded output before reporting values.

Polling and timeout behavior:
- Continue polling while the job is queued, pending, or running.
- A client-side polling timeout does not prove that the job failed; do not
  resubmit until the original job's absence or terminal failure is established.
- Retry only transient status/download failures through the existing helper
  behavior, never by creating a duplicate experiment.

Output verification:
- The verified output columns are exactly `smiles,sequence,pIC50,IC50_nM`.
- Verify that returned molecule/sequence pairs correspond to the submitted
  input and that both numeric result columns are populated before claiming
  success.
- `pIC50` is logarithmic; `IC50_nM` is the corresponding nanomolar estimate.



---

## Active BoltChem scope overlay (2026-09-08)

The following records retain historical live evidence. The mode contract above
and compiled catalog govern current forms; these examples do not restrict ML
to regression or DL to classification. The observed `DNN_Classification` token
remains accepted for legacy DL classification payloads, but new forms show `DL`.

## Tool 2 — Custom Property Model - Classification (`Custom_Property_Model_DL`) — VERIFIED

### Identity
- Experiment Name: Custom Property Model - Classification
- Job Name: `Custom_Property_Model_DL` ⚠ (NOT `Custom_Property_Model_DNN_Classification`) — VERIFIED_LIVE
- API route: `/v4/proppred/dl` · internal task: `dlproptrain` · node: `boltzmann15`

### Verification Status
- Input contract verified: VERIFIED_LIVE (after 1 job-name correction)
- Submission verified: VERIFIED_LIVE (docId `CURRENT_JOB_ID`, 4 credits, est 3 min 21 s)
- Result fetch verified: VERIFIED_LIVE (terminal `Success`, 3 min 50 s compute / 636 s lifetime)
- Output download verified: VERIFIED_LIVE (train/test CSVs + **431 MB `.pt` model**)
- Output analysis verified: VERIFIED_LIVE (CSV passthroughs + torch checkpoint inspected)
- Downstream compatibility: VERIFIED_PRODUCT_FEATURES (model path feeds Property Prediction
  `custom_models` — not yet chained live)
- Confidence: HIGH — full lifecycle observed end-to-end

### Input Contract

| Field | Type | Required | Allowed | Default | Source |
|---|---|---|---|---|---|
| `property_name` | string | yes | becomes output filename stem | — | VERIFIED_LIVE |
| `filepath` | string (cloud CSV) | yes | uploaded training CSV | — | VERIFIED_LIVE |
| `modeltype` | string | yes | `"classification"` (this tool) | — | VERIFIED_LIVE |
| `modelName` | string | yes | `"DNN_Classification"` observed; grover is the actual backend | — | VERIFIED_LIVE |
| `transformation` | string | yes | `"no"` (Morgan/other transforms exist) | — | VERIFIED_LIVE |

Training CSV: header `SMILES,ACTIVITY`; ACTIVITY = class 0/1 (also accepts continuous for regression twin).

```python
{
    "experimentData": {
        "property_name": "logp_class",
        "filepath": "users/<userId>/<ts>/train_cls.csv",   # 32 rows
        "modeltype": "classification",
        "modelName": "DNN_Classification",
        "transformation": "no"
    },
    "job_name": "Custom_Property_Model_DL",
    "experimentName": "cpmc_verify"
}
```

### Submission Findings
- First attempt used job_name `Custom_Property_Model_DNN_Classification` → rejected
  (no such collection). Probed with empty payload → **`Custom_Property_Model_DL`** is the
  collection key. Corrected resubmit accepted.

### Result Contract — VERIFIED_LIVE
- Terminal status: `"Success"`
- OutputData keys (three): `TrainFile`, `TestFile` (split CSVs) and `outputFilePath` (**the trained
  model**) — each `{path, download_link:[...]}`
- Naming: `<property_name>_<backend>_<role>.csv` / `<property_name>_<backend>_model.pt`
  → observed `logp_class_grover_*` (backend is **grover** regardless of `modelName=DNN_Classification`)
- Path pattern: `users/<userId>/Custom_Property_Model_DL/property-predictors/<docId>/…`
- billing: `tool_name: "dlproptrain"`, 4 credits, rate 50/hr.

### Output Analysis — VERIFIED_LIVE
- TrainFile: 32 rows `SMILES,ACTIVITY` — exact passthrough of my upload (28× class 0, 4× class 1).
- TestFile: 4 rows — internal validation split.
- Model: **torch zip checkpoint, 431,511,849 bytes, 119 tensor entries.** `model/data.pkl` carries
  the training args: `parser_name: finetune`, `data_path: dl_data/frameworks/grover/logp_class/train.csv`,
  `batch_size: 32`, `gpu: 0` → it is a **GROVER fine-tune** checkpoint, self-contained (loads with
  `torch.load` without the platform).
- Input → output transformation: training CSV + property name → (a) split artifacts, (b) a portable
  pretrained-then-finetuned property model keyed by property name.

### Downstream Compatibility
- The model cloud path is the `path` field of `outputFilePath` → Property Prediction
  `custom_models: [{name: <property_name>, path: <path>, model_type: …, …}]` (contract from product
  features; chaining not yet run live — scheduled follow-up).
- The `.pt` downloads and loads anywhere torch exists — models are NOT platform-locked.

### Sci Execution Instructions
1. User supplies labeled data: `SMILES,ACTIVITY` CSV, classes 0/1. Check class balance locally;
   warn below ~10% minority.
2. Pick a short snake_case `property_name` (it becomes the model's identifier everywhere).
3. Upload CSV; submit payload above with `job_name="Custom_Property_Model_DL"`; budget 4 credits
   and ~4 min compute + queue.
4. Download all three artifacts (the model is ~431 MB — disk-space aware).
5. Store the model cloud path: it is the handle for future predictions via Property Prediction
   custom_models, or load the .pt directly in local torch.
6. Do not resubmit to "improve" — a new run trains from scratch and re-bills.

### Verified Quirks
- Job-name ≠ product name (`Custom_Property_Model_DL`, not `…_DNN_Classification`).
- `modelName: "DNN_Classification"` is a UI label; the backend always runs GROVER fine-tuning
  (visible in checkpoint args and output filenames).
- Model file is huge (431 MB) relative to a 32-row train set — it's the pretrained GROVER backbone;
  download time can exceed training time.
- With a tiny imbalanced set (28/4) training still completes cleanly — no minimum-data guard.

---



## Tool 3 — Custom Property Model - Regression (`Custom_Property_Model_Automl`) — VERIFIED

### Identity
- Experiment Name: Custom Property Model - Regression
- Job Name: `Custom_Property_Model_Automl` — VERIFIED_LIVE
- API route: `/v4/proppred/automl` · internal task: `automl` · node: `boltzmann3-hp-z6-g4-workstation`

### Verification Status
- Input contract verified: VERIFIED_LIVE (after 3 corrections — see Submission Findings)
- Submission verified: VERIFIED_LIVE (docId `CURRENT_JOB_ID`, 1 credit, est 39 s)
- Result fetch verified: VERIFIED_LIVE (terminal `Success`, 57 s compute)
- Output download verified: VERIFIED_LIVE (train/test CSVs)
- Output analysis verified: VERIFIED_LIVE (predictions + applicability-domain columns)
- Downstream compatibility: VERIFIED_PRODUCT_FEATURES only — **no model artifact is exposed**,
  so unlike the DL variant nothing user-portable is returned
- Confidence: HIGH on the observed contract

### Input Contract

| Field | Type | Required | Allowed | Source |
|---|---|---|---|---|
| `property_name` | string | yes | filename stem (`clogp`) | VERIFIED_LIVE |
| `filepath` | string (cloud CSV) | yes | `SMILES,ACTIVITY` (continuous labels) | VERIFIED_LIVE |
| `modeltype` | string | yes | `"regression"` | VERIFIED_LIVE |
| `features` | string | yes | `"descriptors"` observed (fingerprints likely) | VERIFIED_LIVE |
| `splittype` | string | yes | **`"randomsplit"`** (not `"random"`) | VERIFIED_LIVE |
| `modelName` | array | yes | `["automl"]` — array, lowercase | VERIFIED_LIVE |
| `transformation` | string | yes | `"no"` | VERIFIED_LIVE |

```python
{
    "experimentData": {
        "property_name": "clogp",
        "filepath": "users/<userId>/<ts>/train_reg.csv",
        "modeltype": "regression",
        "features": "descriptors",
        "splittype": "randomsplit",
        "modelName": ["automl"],
        "transformation": "no"
    },
    "job_name": "Custom_Property_Model_Automl",
    "experimentName": "cpmr_verify"
}
```

### Submission Findings (3 rejections before accept — richest correction chain of the batch)
1. `splittype: "random"` → rejected; enum is **`randomsplit`**.
2. `modelName: ""` → rejected; must be an **array**.
3. `modelName: ["AutoML"]` → rejected "Invalid ML regression model"; must be **lowercase `["automl"]`**.
Accepted on 4th attempt.

### Result Contract — VERIFIED_LIVE
- Terminal status: `"Success"`
- OutputData keys: only `TestFile` and `TrainFile` — **no model file key** (contrast: DL variant
  returns a 431 MB `.pt`). The trained AutoML model is not downloadable.
- Naming: `<property_name>_<model>_<features>_train/test.csv` → `clogp_rf_descriptors_*.csv`
  (rf = the AutoML-selected random forest).
- billing: `tool_name: "automl"`, 1 credit, 57 s compute, cheap node.

### Output Analysis — VERIFIED_LIVE
- TrainFile: `Label,ACTIVITY` — my input values plus slight perturbation (Label = input truth?
  ACTIVITY = model fit). 42 rows.
- TestFile (8 rows): `Label, ACTIVITY, distances, applicability_domain` —
  **the only custom-model tool that reports applicability domain**: `distances` = distance to
  training manifold, `applicability_domain` = Yes/No flag. One point at distance 1,325 → still
  flagged "Yes" (threshold appears lenient or absolute-scaled).
- Fit quality on the toy set: |Label−ACTIVITY| ≈ 0.01–0.17 across 8 test points — good on
  trivial data (clogp from SMILES is an easy descriptor task).
- Input → output transformation: labeled CSV → trained (server-side) regressor + validation
  split with per-point predictions and AD flags.

### Downstream Compatibility
- Nothing portable leaves the platform (no model file). If the user needs to run predictions
  later, the path is Property Prediction with `custom_models` — whether the AutoML backend
  supports that hook is UNVERIFIED; recommend the DL variant when portability matters.
- TestFile is self-contained (truth + prediction + AD) — directly reportable to users.

### Sci Execution Instructions
1. Build `SMILES,ACTIVITY` CSV with **continuous** labels; upload.
2. Submit with the exact enums above (`randomsplit`, lowercase `["automl"]`); 1 credit; ~1 min.
3. Download both CSVs; report test metrics from Label vs ACTIVITY, flag points where
   `applicability_domain` is No.
4. Warn the user: no downloadable model artifact from this variant.

### Verified Quirks
- Strict enums: `randomsplit` not `random`; `automl` lowercase array.
- No model artifact in OutputData — the DL variant (`Custom_Property_Model_DL`) is the one that
  returns a portable `.pt`.
- AutoML picks the model (rf here); the chosen model surfaces only in the output filename.

---
