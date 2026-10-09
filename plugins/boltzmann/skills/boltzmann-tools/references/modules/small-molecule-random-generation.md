# Random Generation

Domain: Small Molecule Design

This module was selected by the server. Use only the exact contracts below.

## 22A. Random Generation — Training

Fine-tune a molecular generator on a user-supplied SMILES library. The trained
checkpoint becomes a private **Custom Generator** option in Random Generation —
Inference. Training supports **VAE and CharRNN only**. TransVAE is inference-only
in the current product and must never be sent to this training job.

Product page: `https://app.boltzmann.co/small-molecule/experiments/random-generation-training`

| Field | Value |
|-------|-------|
| **job_name** | `Random_based_generation_training` |
| **API route** | `/v4/generators/customgen` |
| **backend task** | `customgen` |
| **contract status** | VAE request, submit, terminal fetch, checkpoint download, and checkpoint inspection verified live |

### Training inputs

Pass these fields inside `experimentData`. `experiment_id` and `tokenid` shown
in the lower-level product CSV are injected by the platform; do not add them
when using `submit_request()`.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `dataPath` | string | yes | Uploaded `.csv` path. The CSV header must be exactly `SMILES`. |
| `num_epochs` | int | yes | Fine-tuning epochs. Product guidance suggests 20–100 and starting near 40; use a small value only for an explicit smoke test. |
| `num_samples` | int | yes | Molecules sampled per epoch. Product source maximum: 5000. The web UI currently sends 1000; the live API also accepted 100. |
| `model_name` | string | yes | Exact API tokens: `"vae"` or `"CharRNN"`. The UI label `VAE` is converted to lowercase `"vae"`; sending `"VAE"` directly was rejected live. |
| `model_filePath` | string | yes | Base checkpoint. Global defaults are `globalgenerators/vae_alldata.ckpt` for VAE and `globalgenerators/CharRNN_60Ldata.ckpt` for CharRNN. A prior compatible checkpoint may be used for further specialization. |
| `model_category` | string | yes | Use `"ML"`; the lower-level CSV calls this optional, but it was present in the verified submission. |
| `global_models` | list[object] | conditional | Global property rewards in `{name,min_threshold,max_threshold}` form. |
| `custom_models` | list[object] | conditional | Custom property rewards in `{id,min_threshold,max_threshold}` form. Required when `global_models` is empty. Do not confuse these property models with the generator checkpoint. |

At least one global or custom property model is required by the current schema.
Every selected property requires numeric minimum and maximum thresholds.

**Input CSV**

```csv
SMILES
CCO
CC(=O)OC1=CC=CC=C1C(=O)O
```

Validate that the file contains a non-empty `SMILES` column before uploading.
Do not rename it to `smiles`, `canonical_smiles`, or `Molecule`.

### Training examples

VAE:

```python
job_name = "Random_based_generation_training"
experiment_data = {
    "num_epochs": 40,
    "num_samples": 1000,
    "model_name": "vae",
    "model_filePath": "globalgenerators/vae_alldata.ckpt",
    "dataPath": uploaded_smiles_csv,
    "model_category": "ML",
    "global_models": [
        {"name": "Solubility", "min_threshold": -6.0, "max_threshold": 0.0}
    ],
}
doc_id = submit_request(
    experiment_data, job_name, "random_generation_vae_training",
    token=bearer_token, conv_id=conv_id,
)
result = fetch_status(
    job_name, doc_id, token=bearer_token, conv_id=conv_id,
    output_folder=str(result_dir),
)
```

CharRNN uses the same contract with only these changes:

```python
experiment_data["model_name"] = "CharRNN"
experiment_data["model_filePath"] = "globalgenerators/CharRNN_60Ldata.ckpt"
```

### Training result and handoff

- Verified output key: `result["OutputData"]["outputFilePath"]`.
- The artifact is a fine-tuned `.ckpt`, not a molecule CSV.
- A verified VAE run produced a 67.9 MB PyTorch-Lightning checkpoint.
- Preserve the returned cloud `path`; inference consumes that exact path through
  `model_filePath`. Do not substitute the short-lived signed download URL.
- The trained model is private to the user who trained it and appears in the
  UI's Custom Generator selector after successful completion.

Training is fine-tuning, not training from scratch: it starts from
`model_filePath`, learns the uploaded chemical space, and applies the selected
property rewards. Never claim that a target name in the prose prompt is a
conditioning input unless it is represented by an actual selected property
model or the training dataset.

**Planning estimate:** the product inventory gives
`8 + attributes + (epochs × 6) + (epochs × samples × 0.0002)` seconds and an
example of 61 seconds / 2 credits for 3 properties, 10 epochs, and 100 samples.
Treat this as a planning estimate only: the live 2-epoch verification was billed
1 credit and reported 2 minutes 30 seconds of compute, excluding queue time.

---

## 22B. Random Generation — Inference

Generate chemically valid, diverse ligand-like molecules from either a global
pretrained generator or a private fine-tuned generator. The product exposes
three global models—**VAE, CharRNN, and TransVAE**—but TransVAE uses a different
job and payload. Route by model before submitting.

Product page: `https://app.boltzmann.co/small-molecule/experiments/random-generation-inference`

### Inference routing matrix

| User selection | Exact job_name | Exact `model_name` | Generator checkpoint |
|---|---|---|---|
| Global VAE | `Random_based_generation_nontrans` | `"vae"` | Omit `model_filePath` or use the global VAE checkpoint |
| Global CharRNN | `Random_based_generation_nontrans` | `"CharRNN"` | Omit `model_filePath` or use the global CharRNN checkpoint |
| Custom Generator trained as VAE/CharRNN | `Random_based_generation_nontrans` | Reuse the training result's model token | Set `model_filePath` to the prior training result's `.ckpt` cloud path |
| Global TransVAE | `Random_based_generation_Inference_transvaegen` | `"transvae"` | TransVAE has its own backend; do not send it to the nontrans job |

The UI labels are `VAE`, `CharRNN`, and `TransVAE`/`Transvae`; the payload
tokens and job names in the table are case-sensitive.

### VAE, CharRNN, and custom-generator contract

| Field | Value |
|-------|-------|
| **job_name** | `Random_based_generation_nontrans` |
| **API route** | `/v4/generators/randomgen` |
| **backend task** | `randomgen` |
| **contract status** | Global VAE full lifecycle verified live; CharRNN and checkpoint handoff are schema/product-backed |

**Inputs** (inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `num_samples` | int | yes | Positive number of molecules requested. Sampling is nondeterministic. |
| `model_name` | string | yes | Exact API token `"vae"` or `"CharRNN"`. Never send `"VAE"`, `"charRNN"`, or `"TransVAE"` to this job. |
| `prop_model_category` | string | yes | Use `"ML"`. |
| `model_filePath` | string | custom generator only | Fine-tuned `.ckpt` cloud path returned by Random Generation — Training. Omit for the default global generator. |
| `global_models` | list[object] | yes | Threshold-object dialect. The array itself is required; use up to three selected reward properties. |
| `custom_models` | list[object] | conditional | Custom property rewards. If no global properties are supplied, at least one custom property model is required. |

**Do not confuse the two meanings of “custom”:**

- `model_filePath` chooses a **custom molecular generator checkpoint**.
- `custom_models` chooses **custom property/reward models** used to score and
  constrain generated molecules.

Custom-generator inference must reuse the prior training result's exact
`model_name` and `OutputData.outputFilePath.path`. If that historical result is
unavailable, failed, or not a `.ckpt`, stop and report it; do not silently use a
global generator.

### Property reward format

```json
{"name": "hERG", "min_threshold": 0.0, "max_threshold": 0.5}
```

- Both thresholds must be numeric for every selected reward property.
- Never mix a numeric threshold with `""` for the same property.
- Use no more than three reward properties, as documented by the product UI.
- Confirm each model's scale and direction before converting qualitative goals
  such as “low hERG” into thresholds.
- Avoid unrealistically narrow ranges: a live Solubility range of `-4` to
  `0.4` yielded zero accepted molecules, whereas a permissive verification
  range produced the requested output.

**Exact global property-model names exposed by the current product:**

```text
CaCo2 permeability, Half Life, Solubility, VDss, GIA, Biodegradability,
Cyp2d9 inh, Cyp2d9 sub, PGP sub, Endocrine disrupting, Eye corrosive,
Genotoxicity, Clearance, Hydration Free Energy, LD50, Lipophilicity, PPBR,
rPPB, hPPB, Nephrotox_v3, BBB, Bioavailability, HIA, PAMPA, PGP_inh,
Cyp1a2 inh, Cyp2c9 inh, Cyp2c9 sub, Cyp2c19 inh, Cyp2d6 inh, Cyp2d6 sub,
Cyp3a4 inh, Cyp3a4 sub, AMES, Carcinogenicity, DILI, hERG, Skin reaction,
ClinTox, NR-AR, NR-AR-LBD, NR-AhR, NR-Aromatase, NR-ER, NR-ER-LBD,
NR-PPAR-gamma, SR-ARE, SR-ATAD5, SR-HSE, SR-MMP, SR-p53
```

Preserve these names exactly, including `CaCo2 permeability`, `Cyp2d9 inh`,
`Cyp2d9 sub`, `PGP sub`, and `PGP_inh`. Do not “correct” apparent naming drift.

### Global-generator example

```python
job_name = "Random_based_generation_nontrans"
experiment_data = {
    "num_samples": 25,
    "model_name": "vae",
    "prop_model_category": "ML",
    "global_models": [
        {"name": "hERG", "min_threshold": 0.0, "max_threshold": 0.5}
    ],
}
doc_id = submit_request(
    experiment_data, job_name, "random_generation_vae_inference",
    token=bearer_token, conv_id=conv_id,
)
result = fetch_status(
    job_name, doc_id, token=bearer_token, conv_id=conv_id,
    output_folder=str(result_dir),
)
```

For global CharRNN, change `model_name` to `"CharRNN"`.

### Custom-generator example

```python
training_output = prior_training_result["OutputData"]["outputFilePath"]
checkpoint_path = training_output["path"]

job_name = "Random_based_generation_nontrans"
experiment_data = {
    "num_samples": 100,
    "model_name": prior_training_model_name,  # "vae" or "CharRNN"
    "model_filePath": checkpoint_path,
    "prop_model_category": "ML",
    "global_models": [
        {"name": "Solubility", "min_threshold": -6.0, "max_threshold": 0.0}
    ],
}
doc_id = submit_request(
    experiment_data, job_name, "random_generation_custom_inference",
    token=bearer_token, conv_id=conv_id,
)
result = fetch_status(
    job_name, doc_id, token=bearer_token, conv_id=conv_id,
    output_folder=str(result_dir),
)
```

### Standard inference result

- Verified output key:
  `result["OutputData"]["save_gen_mols_path"]`.
- On a real success this is an object with `path` and `download_link`.
- **Soft-failure trap:** terminal status may still be `Success` while
  `save_gen_mols_path` is the literal string `"No molecules obtained"`. Always
  type-check it. Report that zero molecules passed the constraints; do not
  claim success or try to access `.path` on the string.
- Do not depend on the lower-level response's inline `smiles` list; the product
  source says it may be removed.

The generated CSV contains:

```text
SMILES, <selected property-model columns>, QED, SA, TPSA,
NUM_HDONORS, NUM_HACCEPTORS, Molecular Weight
```

Validate SMILES, count and deduplicate rows, and verify that selected-property
columns match the requested models before scientific interpretation. A live
verification observed a property-column label mismatch, so never infer column
identity only from its position.

### TransVAE inference contract

| Field | Value |
|-------|-------|
| **job_name** | `Random_based_generation_Inference_transvaegen` |
| **API route** | `/v4/generators/transvaegen` |
| **backend task / collection** | `transvaegen` / `transvae-generator` |
| **contract status** | Product UI, frontend payload, and BoltChem inventory backed; terminal lifecycle not yet verified in this workspace |

TransVAE does **not** use `Random_based_generation_nontrans`. Pass these fields
inside `experimentData`:

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `num_epochs` | int | yes | Send `0`; TransVAE is inference-only here. |
| `num_samples` | int | yes | Number of accepted molecules requested. |
| `model_name` | string | yes | Send `"transvae"`. |
| `dataPath` | string | yes | Current frontend sends `""`; no input dataset is required. |
| `model_category` | string | yes | Use the exact choice `"model_inference"`. GraphDTA is not an available choice in this mode. |
| `mode` | int | yes | `0` for regression. Product source also mentions classification modes 7, 8, or 9. |
| `global_models` / `custom_models` | list[object] | conditional | Selected reward/property models; the platform converts them to the lower-level `attribute` list. |

The product inventory lists eight installed TransVAE checkpoints spanning
`trans1x`/`trans4x`, latent sizes `128`/`256`, and PubChem/ZINC training sets:
`trans1x-128_pubchem`, `trans1x-128_zinc`, `trans1x-256_pubchem`,
`trans1x-256_zinc`, `trans4x-128_pubchem`, `trans4x-128_zinc`,
`trans4x-256_pubchem`, and `trans4x-256_zinc`. These are backend inventory
details, not verified public request parameters; do not invent a checkpoint
selector field unless the API exposes one.

```python
job_name = "Random_based_generation_Inference_transvaegen"
experiment_data = {
    "num_epochs": 0,
    "num_samples": 25,
    "model_name": "transvae",
    "dataPath": "",
    "model_category": "model_inference",
    "uniprot_id": "",
    "mode": 0,
    "global_models": [
        {"name": "Solubility", "min_threshold": -6.0, "max_threshold": 0.0}
    ],
}
doc_id = submit_request(
    experiment_data, job_name, "random_generation_transvae_inference",
    token=bearer_token, conv_id=conv_id,
)
result = fetch_status(
    job_name, doc_id, token=bearer_token, conv_id=conv_id,
    output_folder=str(result_dir),
)
```

The lower-level product schema reports `outputFilePath` pointing to a CSV with
`SMILES`, `Flow`, selected property values, and the standard descriptors. Since
this terminal wrapper has not yet been live-verified, inspect the first
completed `OutputData` payload before hard-coding a download expression.

### Inference output interpretation

- `SA`: 1 is easier and 10 is harder to synthesize; prefer `SA < 5` as a
  practical screening heuristic.
- `TPSA`: values below 90 Å² often support oral absorption; values above
  140 Å² often indicate poor membrane penetration.
- Hydrogen-bond donors/acceptors: Lipinski guidance is donors ≤ 5 and
  acceptors ≤ 10.
- Molecular weight: below 500 Da is commonly preferred for oral drug-like
  molecules; below 300 Da is common in fragment-oriented design.
- `QED`: 0–1, with `QED > 0.6` a useful prioritization heuristic.

These are screening heuristics, not proof of efficacy, safety, target binding,
or synthesizability. QED, SA, TPSA, donors, acceptors, and molecular weight are
default output descriptors—not verified reward-model names. Apply those
filters after download unless an exact supported property reward exists.

The standard payload contains no target sequence, protein structure, known hit,
or binding-affinity field. A disease or target named only in the user prompt is
context, not target-conditioned generation. Use a verified custom property
model, TransVAE GraphDTA mode, or a downstream target-specific tool before
claiming target relevance.

**Planning estimate:** for standard VAE/CharRNN inference, the product inventory
gives `3 + (attributes × 0.3) + (samples × 0.007)` seconds and an example of
10.7 seconds / 2 credits for 3 properties and 1000 samples. Actual billing,
runtime, and queue delay are authoritative; do not promise the formula as an
ETA. The inventory does not provide a reliable TransVAE time or cost estimate.

---

## 51. Random based generation training

Fine-tune a VAE or CharRNN molecular generator on a SMILES dataset.

| Field | Value |
|---|---|
| **job_name** | `Random_based_generation_training` |
| **contract status** | VAE live-verified end to end; CharRNN schema/product-backed |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `dataPath` | string | yes | Uploaded CSV containing a `SMILES` column |
| `model_filePath` | string | yes | Base-model checkpoint path |
| `model_name` | string | yes | Exact API token `vae` or `CharRNN`; uppercase `VAE` was rejected live |
| `num_epochs` | integer | yes | Fine-tuning epochs |
| `num_samples` | integer | yes | Samples per epoch; product source states maximum 5000 |
| `model_category` | string | yes | Use `ML` |
| `global_models` | array[object] | conditional | Threshold objects `{name,min_threshold,max_threshold}` |
| `custom_models` | array[object] | conditional | Custom property-model threshold objects; required when `global_models` is empty |

**Output contract:** Live-verified `OutputData.outputFilePath` -> private fine-tuned `.ckpt`; preserve its cloud `path` for inference.

Training is fine-tuning from `model_filePath`, not training from scratch.
The uploaded CSV header must be exactly `SMILES`, and at least one global or custom
property model is required. The verified VAE base checkpoint was
`globalgenerators/vae_alldata.ckpt`. Reuse the returned checkpoint's cloud `path`
with the matching model token during random-generation inference; never substitute
the short-lived signed download URL.

---


---

## Verified BoltChem contract overlay (2026-09-08)

The following section is the current verified BoltChem contract for this module. It overrides conflicting legacy text above. Do not submit until its required fields, exact enums, file headers, and validation rules pass.

### Random Generation — Inference

# Random based generator-inference
Tool display name:Random based generation-inference
Frontend route/screen:
Exact form fields:num_samples,model_name,prop_model_category,global_models
Required fields:num_samples,model_name,prop_model_category,global_models
fields details and options: num-samplesintegrer(Total number of molecules to be generated that satisfy the given property profile.),
model_name:string[CharRNN,vae]
prop_model_category:string[ML]
globals_models:list of threshold objects; at least one global model is required
                ["CaCo2 permeability",
                "Half Life",
                "Solubility",
                "VDss",
                "GIA",
                "Biodegradability",
                "Cyp2d9 inh",
                "Cyp2d9 sub",
                "PGP sub",
                "Endocrine disrupting",
                "Eye corrosive",
                "Genotoxicity",
                "Clearance",
                "Hydration Free Energy",
                "LD50",
                "Lipophilicity",
                "PPBR",
                "rPPB",
                "hPPB",
                "Nephrotox_v3",
                "BBB",
                "Bioavailability",
                "HIA",
                "PAMPA",
                "PGP_inh",
                "Cyp1a2 inh",
                "Cyp2c9 inh",
                "Cyp2c9 sub",
                "Cyp2c19 inh",
                "Cyp2d6 inh",
                "Cyp2d6 sub",
                "Cyp3a4 inh",
                "Cyp3a4 sub",
                "AMES",
                "Carcinogenicity",
                "DILI",
                "hERG",
                "Skin reaction",
                "ClinTox",
                "NR-AR",
                "NR-AR-LBD",
                "NR-AhR",
                "NR-Aromatase",
                "NR-ER",
                "NR-ER-LBD",
                "NR-PPAR-gamma",
                "SR-ARE",
                "SR-ATAD5",
                "SR-HSE",
                "SR-MMP",
                "SR-p53"
            ]
Optional fields:
  `model_filePath`: optional fine-tuned generator checkpoint path. Use only the
  exact `.ckpt` path returned by a verified Random Generation Training result,
  together with that result's exact `model_name`.
  "custom_models": [
                {
                    "id": "",
                    "min_threshold": "",
                    "max_threshold": ""
                }]
Allowed choices and exact spelling:
- `model_name` must be the exact backend token `vae` or `CharRNN`; do not send
  UI labels such as `VAE`, `charRNN`, or `TransVAE` to this non-TransVAE job.
- `prop_model_category` must be the verified value `ML`.
- `global_models` is compulsory and must contain at least one object. Every
  selected model object must include `name`, `min_threshold`, and
  `max_threshold`.
- Whenever a global model is selected, both threshold values are mandatory and
  must be explicitly supplied by the user. The agent must never invent,
  infer, default, or choose either threshold.
- Thresholds must be numeric and `max_threshold >= min_threshold`; do not mix
  a numeric threshold with an empty string.
- Use no more than three total reward/property models when the backend applies
  the documented cardinality limit.
Sample input file:null
Required file format:null
Required column names:null
Sample output file:
Actual backend/network payload:
data = {
        "experimentData": {
            "num_samples": 3,
            "model_name": "CharRNN",
            "prop_model_category": "ML",
            "global_models": [
                {
                    "name": "Clearance",
                    "min_threshold": "3",
                    "max_threshold": "11"
                }
            ]
        },
        "job_name": "Random_based_generation_nontrans",
        "experimentName": "prime"
    }
Exact backend job name, if visible:Random_based_generation_nontrans
Known validation or failure messages:
- Missing `num_samples`, `model_name`, `prop_model_category`, or
  `global_models` is incomplete and must be clarified before submission.
- A global model without user-supplied `min_threshold` and `max_threshold`
  must be rejected before submission; never fill either value automatically.
- A bare-string global model such as `{"global_models": ["QED"]}` is invalid;
  use threshold objects instead.
- A missing, failed, or non-`.ckpt` `model_filePath` from a prior training
  result cannot be reused; report it and do not silently fall back to a global
  generator.
- A terminal `Success` with `save_gen_mols_path` equal to
  `"No molecules obtained"` means zero molecules passed the constraints, not
  a populated successful result.

Submission instructions:
1. Collect `num_samples`, exact `model_name`, and `prop_model_category="ML"`.
2. Require at least one selected global model and ask the user for both
   thresholds for every selected model.
3. Submit threshold objects, not bare model-name strings, using the exact job
   name `Random_based_generation_nontrans`.
4. For a custom generator, use only the verified prior training `.ckpt` path
   and matching model token.
5. Poll the returned document ID and verify `OutputData.save_gen_mols_path`.

Polling and output verification:
- Pending, queued, and running are not failures; continue polling the same
  document with the same job name and never duplicate the request.
- The successful output is an object containing `path` and `download_link`;
  handle the signed link through the existing download helper.
- The generated CSV should be non-empty, contain valid `SMILES`, and be
  checked for the selected property columns and actual row count.
