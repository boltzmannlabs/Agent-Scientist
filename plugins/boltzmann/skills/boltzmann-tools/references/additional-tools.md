# CSV-Backed Additional Tool Contracts

Read this reference when a request routes to one of the tools below. These contracts were
reconciled from the experiment inventory and the supplied BoltPro, BoltZyme, and BoltChem
product-feature CSVs. Exact backend spellings take precedence over human-readable titles.

Use the universal submission, polling, logging, confidentiality, and deduplication rules in
the parent `SKILL.md`. Upload file inputs first. Do not copy UI wrapper objects such as
`{label, value}` into the backend payload; pass their scalar `value` unless a tool explicitly
requires an object. An unverified output contract is not permission to invent an output key.

The inventory also names Create Library (`create_library`) and Fragments (`fragments`), but
the operator has marked both as intentionally ignored. Do not treat either as an active
coverage gap. Toxicophore Screening remains listed separately as on hold.

## 6. Genzyme Generation

Generate candidate enzyme structures conditioned on substrate and product SMILES.

| Field | Value |
|---|---|
| **job_name** | `Genzyme_Generation` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_substrate` | string | yes | Substrate SMILES |
| `input_product` | string | yes | Product SMILES |
| `num_structures` | integer | yes | Number of enzyme structures to generate |

**Output contract:** `OutputData.datainfo.outputFilePath` (product CSV); verify the terminal payload before downloading.

---

## 8. Sequence based peptide generation

Generate peptide candidates from an antigen or conditioning sequence.

| Field | Value |
|---|---|
| **job_name** | `Sequence_based_peptide_generation` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `sequence` | string | yes | Use the exact source field. |
| `num_peptides` | string | yes | Use the exact source field. |
| `seq_length` | string | yes | Use the exact source field. |

**Output contract:** Not documented in the supplied CSVs; inspect the first terminal payload.

---

## 10. Target-Aware CDR Designer / Epitope Conditioned Antibody Generation

Generate antigen- and epitope-conditioned antibody CDR backbones.

| Field | Value |
|---|---|
| **job_name** | `epitope_abgen` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `antigen_pdb_path` | string | yes | Uploaded antigen PDB |
| `antibody_pdb_path` | string | yes | Uploaded antibody-framework PDB |
| `mask_cdrs` | string | yes | `hcdr3`, `heavy_cdrs`, or `all_cdrs` |
| `heavy_chain_id` | string | no | Heavy-chain PDB identifier |
| `light_chain_id` | string | no | Light-chain PDB identifier |
| `antigen_chain_ids` | array[string] | no | Antigen chain identifiers |
| `epitope_residues` | string or array[string] | no | Residues such as `C:103,C:111` |
| `samples_per_task` | integer | no | 1-16; product source default is 4 |
| `seed` | integer | no | Product source default is 2026 |
| `max_tokens` | integer | no | 32-416 |

**Output contract:** `OutputData.datainfo.output_path` -> results archive (product CSV).

---

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

## 14. Enzymes

Predict enzyme properties selected from the supported property families.

| Field | Value |
|---|---|
| **job_name** | `Enzymes` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `dataPath` | string | yes | Uploaded CSV with sequence identifiers and sequences |
| `property_name` | array[string] | yes | Any of `pHPred`, `enzyme_solubility`, `tmPred_enzymes`, `function_prediction`, `substrate_pred` |

**Output contract:** `OutputData.datainfo.outputFilePath` (product CSV).

---

## 15. Vaccines

Screen peptide sequences for vaccine-related antigenicity, allergenicity, and toxicity.

| Field | Value |
|---|---|
| **job_name** | `Vaccines` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `dataPath` | string | yes | Uploaded CSV containing a `Sequence` column |
| `property_name` | array[string] | yes | Any of `Allergenicity`, `Antigenicity`, `Toxicity`, `Epitope` |
| `toxicity_reference` | number | no | Accepted by the API; product source says backend currently ignores it |
| `allergenicity_reference` | number | no | Accepted by the API; product source says backend currently ignores it |
| `antigenictiy_reference` | number | no | Preserve this backend misspelling; currently ignored |

**Output contract:** `OutputData.datainfo.outputFilePath` (product CSV).

---

## 17. Multimer Structure Prediction

Predict multimeric protein structures from paired or grouped sequences.

| Field | Value |
|---|---|
| **job_name** | `Multimer_Structure_Prediction` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_path` | string | yes | Use the exact source field. |

**Output contract:** `OutputData.datainfo.outputFilePath` -> prediction archive (product CSV).

---

## 20. Antibody Numbering

Number antibody residues with a supported numbering scheme.

| Field | Value |
|---|---|
| **job_name** | `Antibody_Numbering` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `dataPath` | string | yes | Use the exact source field. |
| `scheme` | string | yes | values: `Kabat, Chothia, Aho` |
| `property_name` | string | yes | Use the exact source field. |

**Output contract:** Not documented in the supplied CSVs; inspect the first terminal payload.

---

## 21. RC Plot

Calculate and render a Ramachandran plot from protein structure coordinates.

| Field | Value |
|---|---|
| **job_name** | `RC_Plot` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `dataPath` | string | yes | Use the exact source field. |

**Output contract:** `OutputData.datainfo.outputFilePath` (product CSV).

---

## 22. IG Design

Design immunoglobulin sequences conditioned on an antigen-antibody complex structure.

| Field | Value |
|---|---|
| **job_name** | `igdesign` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `pdb_path` | string | yes | Uploaded file: `.pdb` |

**Output contract:** `OutputData.datainfo.output_path` (product CSV).

---

## 23. RF-Antibody

Generate antibody or nanobody sequences from antibody and antigen structures.

| Field | Value |
|---|---|
| **job_name** | `rfdiffusion_proteinmpnn` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `antibody_pdb_path` | mixed | yes | Use the exact source field. |
| `antigen_pdb_path` | mixed | yes | Use the exact source field. |
| `num_sequences` | number | yes | Use the exact source field. |

**Output contract:** `OutputData.datainfo.output_path` -> results archive (product CSV).

---

## 24. Antibody RFD3

Generate alternative antibody CDR backbone conformations while preserving the framework and antigen.

| Field | Value |
|---|---|
| **job_name** | `agcdr_diff` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `antibody_pdb_path` | mixed | yes | Use the exact source field. |
| `antigen_pdb_path` | mixed | yes | Use the exact source field. |
| `num_samples` | number | yes | Use the exact source field. |
| `num_steps` | number | yes | Use the exact source field. |

**Output contract:** `OutputData.datainfo.output_path` plus generated-structure metadata (product CSV).

---

## 28. Solublempnn

Design sequences for a supplied backbone with ProteinMPNN or its soluble-protein variant.

| Field | Value |
|---|---|
| **job_name** | `Solublempnn` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_path` | string | yes | Use the exact source field. |
| `model_type` | string | no | Use the exact source field. |
| `num_seq` | number | yes | Use the exact source field. |
| `fixed_residues` | string | no | Use the exact source field. |
| `invert_selection` | number | no | Use the exact source field. |

**Output contract:** `OutputData.datainfo.outputFilePath` (product CSV).

---

## 32. Thermal MPNN

Predict stability changes for protein point mutants with ThermoMPNN.

| Field | Value |
|---|---|
| **job_name** | `Thermal_MPNN` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `zip_path` | string | yes | Use the exact source field. |

**Output contract:** `OutputData.datainfo.output_path` -> CSV with mutation and ddG columns (product CSV).

---

## 34. TM Align

Structurally align one or more protein models to a reference structure.

| Field | Value |
|---|---|
| **job_name** | `tm_align` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_path` | string | yes | Uploaded file: `.pdb`, `.zip` |
| `wt_path` | string | yes | Uploaded file: `.pdb` |
| `task_name` | string | no | Use the exact source field. |

**Output contract:** `OutputData.datainfo.outputFilePath` (product CSV).

---

## 37. MegaDock

Dock a ligand structure against a receptor with MEGADOCK-GPU.

| Field | Value |
|---|---|
| **job_name** | `MegaDock` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `ligand_path` | string | yes | Use the exact source field. |
| `receptor_path` | string | yes | Use the exact source field. |

**Output contract:** `OutputData.datainfo.outputFilePath` and `outputFolderPath` (product CSV).

---

## 38. ActSeek

Compare candidate structures with an active-site-annotated reference.

| Field | Value |
|---|---|
| **job_name** | `act_seek` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_path` | string | yes | Uploaded file: `.pdb`, `.zip` |
| `reference_path` | string | yes | Uploaded file: `.pdb` |
| `active_sites` | string | yes | Use the exact source field. |

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

## 41. BoltzGen

Generate protein, nanobody, or antibody designs with optional ligand and structural constraints.

| Field | Value |
|---|---|
| **job_name** | `boltzgen` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `protocol` | string | yes | values: `protein, nanobody, antibody` |
| `file_path` | mixed | yes | Use the exact source field. |
| `protein_id` | string | yes | Use the exact source field. |
| `sequence_len` | number | yes | Use the exact source field. |
| `num_designs` | number | yes | Use the exact source field. |
| `budget` | number | yes | Use the exact source field. |
| `cyclic` | string | yes | values: `true, false` |
| `ligand_id` | string | no | Use the exact source field. |
| `use_ccd` | boolean | no | Use the exact source field. |
| `ccd` | string | no | Use the exact source field. |
| `smiles` | string | no | Use the exact source field. |
| `ligand_binding_types` | string | no | Use the exact source field. |
| `advanced` | boolean | no | Use the exact source field. |
| `secondary_structure` | string | no | Use the exact source field. |
| `include_chains_id` | string | no | Use the exact source field. |
| `include_chains_res_index` | string | no | Use the exact source field. |
| `atom1_list` | array | no | Use the exact source field. |
| `atom2_list` | array | no | Use the exact source field. |
| `total_len` | object | no | Use the exact source field. |

**Output contract:** `OutputData.datainfo.output_path` (product CSV).

---

## 42. PX Design Infer

Run PXDesign backbone inference or the full binder-design pipeline.

| Field | Value |
|---|---|
| **job_name** | `pxdesigninfer` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `task_name` | string | yes | `pxdesign-infer` or `pxdesign-pipeline` |
| `cif_path` | string | yes | Uploaded target CIF path |
| `chain` | string | yes | Target chain identifier |
| `binder_length` | integer | yes | 10-300 |
| `n_samples` | integer | yes | 1-10000 |
| `crop` | string | no | Optional residue range, e.g. `17-145` |
| `hotspots` | string | no | Comma-separated target residue numbers |

**Output contract:** `OutputData.datainfo.output_files` and `config_yaml` (product CSV).

---

## 43. PPI Flow Monomer

Generate unconditional or motif-conditioned monomer structures with PPIFlow.

| Field | Value |
|---|---|
| **job_name** | `ppiflowmonomer` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `task_name` | string | yes | values: `monomer` |
| `samples_min_length` | number | yes | Use the exact source field. |
| `samples_max_length` | number | yes | Use the exact source field. |
| `samples_num` | number | yes | Use the exact source field. |
| `length_subset` | string | no | Use the exact source field. |
| `motif_csv` | mixed | yes | Use the exact source field. |
| `motif_names` | string | no | Use the exact source field. |

**Output contract:** `OutputData.datainfo.output_path` (product CSV).

---

## 44. Placer

Place and rerank ligands in PDB or mmCIF structures.

| Field | Value |
|---|---|
| **job_name** | `Placer` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_file_path` | string | yes | Uploaded file: `.pdb`, `.cif` |
| `rerank` | string | no | Use the exact source field. |
| `suffix` | string | no | Use the exact source field. |
| `predict_ligand` | string | no | Use the exact source field. |
| `no_of_samples` | number | no | Use the exact source field. |

**Output contract:** `OutputData.datainfo.outputFilePath` (product CSV).

---

## 46. Create Dataset

Create a small-molecule dataset from a target, measurement type, and assay type.

| Field | Value |
|---|---|
| **job_name** | `dataset_creation` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `scrap_id` | string | no | Use the exact source field. |
| `data_type` | string | no | Use the exact source field. |
| `assay_type` | string | no | Use the exact source field. |

**Output contract:** Not documented in the supplied CSVs; inspect the first terminal payload.

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

## 60. QSPR Screening

Screen a SMILES library with custom property models and filters.

| Field | Value |
|---|---|
| **job_name** | `QSPR_Screening` |
| **contract status** | live-verified end to end |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `path` | string | yes | Uploaded CSV containing a `SMILES` column |
| `custom_models` | array[object] | yes | Required but may be empty; custom property models with thresholds |
| `filters` | array[object] | yes | Use live-verified UI objects such as `{"value":"BBB","type":"Permeable"}` |

**Output contract:** Live-verified CSV containing the input rows plus one PASS/FAIL verdict column per selected filter.

The verified payload uses `filters` entries with the keys `value` and `type`;
do not replace them with guessed `prop_name` or `label` keys. The output preserves
all input rows and appends a verdict column for each selected filter.

---

## 62. Toxicophore Screening

Screen a molecular library for toxicophore alerts. This tool is on hold by operator decision.

| Field | Value |
|---|---|
| **job_name** | `toxic_screening` |
| **contract status** | on hold; name-only; do not submit |

**Inputs**

No request fields are defined in the supplied sources. Do not submit this tool.

**Output contract:** On hold: no request or output contract is present in the supplied CSVs; do not submit.

---

## 67. Molecular Docking

Route molecular docking through Vina or DiffDock, with basic, flexible, and score-only behavior under the Vina mode.

| Field | Value |
|---|---|
| **job_name** | `Vina_basic_docking` |
| **contract status** | mode router; Vina basic worker-blocked; DiffDock verified in parent skill |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `target_name` | string | yes | Target/receptor label |
| `processed_pdb` | string | yes | Uploaded receptor PDB |
| `center_x` | string | yes | Binding-box center X; live schema requires a string |
| `center_y` | string | yes | Binding-box center Y; live schema requires a string |
| `center_z` | string | yes | Binding-box center Z; live schema requires a string |
| `max_radius_size` | string | yes | Binding-box size; live schema requires a string |
| `exhaustivness` | string | yes | Preserve misspelling; supported values include `8`, `16`, `32` as strings |
| `upload_sdf` | string | yes | String boolean: `true` or `false` |
| `smiles` | string | yes | Platform path to ligand CSV with `SMILES,NAMES`; not a literal SMILES |

**Output contract:** Vina product rows describe ligand, pose, score, and interaction columns, but Vina basic is worker-blocked and the flexible/score-only result contracts are not live-verified. DiffDock has a separately verified result contract in the parent skill.

### Mode selection

The product surface is one **Molecular Docking** tool with two top-level modes:

| UI selection | Effective backend behavior | Evidence |
|---|---|---|
| Vina selected; neither feature box checked | Basic docking via `Vina_basic_docking` and route `/v4/DModule/basic_docking` | Payload live-verified; worker currently fails after parsing |
| Vina + Flexible docking | Product route `/v4/3DModule/flexible_docking`, task `flexible_docking` | Product CSV only; registered helper `job_name` not live-verified |
| Vina + Score only | Product route `/v4/3DModule/vina_score_only_docking`, collection `equidock`, task `vina_score_only` | Durable collection verified from Mongo document |
| DiffDock selected | DiffDock via `Diffdock` and route `/v4/3DModule/diffdock` | Live-verified end to end in the parent skill |

Within Vina, leaving both **Flexible docking** and **Score only** unchecked means
basic docking. Treat the two feature boxes as mutually exclusive until a proven
payload establishes combined behavior.

### Vina basic docking

Use the input table above with `job_name="Vina_basic_docking"`. All numeric
fields and `upload_sdf` are strings. The `smiles` field is a platform path to a
ligand CSV containing both `SMILES` and `NAMES` columns.

The payload is schema-verified, but seven live attempts reached the same worker
failure after input parsing. Do not spend credits on Vina basic until the worker
is repaired. Do not describe the product-CSV output columns as a live result.

### Vina flexible docking

The product CSV documents the basic fields plus:

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `flexible_residues` | array[string] | yes | Flexible receptor residues such as `ASN140`, `TYR62` |
| `smiles` | string | yes | Ligand input described by the product CSV |

The product route and task are known, but the registered `job_name` for
`submit_request` is not proven. Do not guess it from the route or task name.

### Vina score-only docking

The product CSV documents the common receptor/search-box fields and:

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `sdf_file` | string | yes | Platform path to ligand SDF |
| `upload_sdf` | string | yes | String boolean |

The collection is `equidock` and the task is `vina_score_only`, but a live
Sci submission has not confirmed which exact value the submit endpoint
accepts as `job_name`. Do not guess.

### DiffDock mode

Use `job_name="Diffdock"` with `processed_pdb`, `input_csv`, and `upload_sdf`.
The parent `SKILL.md` contains the live-verified input and result contract.
DiffDock is the current executable docking path while Vina basic remains
worker-blocked.

---

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

**Output contract:** Live-verified `results.csv` with `smiles`, `sequence`, `pIC50`, and `IC50_nM`.

The verified request is one ligand and one target per call. Although the
lower-level schema may accept empty fields, always supply both values: an empty
payload can be accepted while wasting a job. Interpret both reported scales;
`pIC50` is logarithmic while `IC50_nM` is the corresponding nanomolar value.

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

## 88. CDS Property Prediction

Calculate selected coding-sequence properties with the CodonRLBERT property workflow.

| Field | Value |
|---|---|
| **job_name** | `CodonRLBERTPropPred` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `user_id` | string | yes | Use the exact source field. |
| `fasta_file` | string | yes | Uploaded file: `.fasta`, `.fa` |
| `selected_properties` | array | no | Use the exact source field. |

**Output contract:** Not documented in the supplied CSVs; inspect the first terminal payload.

---

## 92. Secondary Structure Prediction

Predict RNA secondary structure from a nucleotide sequence.

| Field | Value |
|---|---|
| **job_name** | `sec_struct_pred` |
| **contract status** | submission accepted; output unverified |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `sequence` | string | yes | Use the exact source field. |

**Output contract:** Submission accepted but no terminal result was observed through 25 minutes; continue polling the original job and inspect the first terminal `OutputData`.

Pass only `sequence` inside `experiment_data`; do not duplicate `job_name`
inside the payload. A live sample alternated between `pending` and `No Output Found`
through 25 minutes. Treat that evidence as unresolved, not success, and do not
invent dot-bracket, CT, or image output formats.

---

## 102. BiomambaRna

Analyze an RNA sequence with the BiomambaRna workflow.

| Field | Value |
|---|---|
| **job_name** | `BiomambaRna` |
| **contract status** | live-verified end to end |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `user_id` | string | yes | Use the exact source field. |
| `sequence` | string | yes | Use the exact source field. |

**Output contract:** Live-verified `OutputData.outputFilePath`; download and inspect the result archive.

The UI calls the sequence field `rnasequence`, but the accepted backend
field is `sequence`. The verified archive contains `sequence_1_top_similar.csv`
with 100 ranked `sequence` and `similarity_score` rows, plus `manifest.json` with
run-level result inventory.

---
