# Structure Prediction

Domain: Protein Engineering

This module was selected by the server. Use only the exact contracts below.

## 8. Boltz-2
Predict unified three-dimensional structures for complexes containing proteins,
DNA, RNA, and/or small-molecule ligands, with confidence and affinity outputs
when applicable.

| Field | Value |
|---|---|
| **job_name** | `Boltz2` |
| **backend task** | `boltz-structure-prediction` |
| **validation status** | **Verified working for one-protein plus one-ligand mode** |
| **observed terminal status** | `Success` |

### Inputs

Each molecular input is an array of strings. The four field names are exact and
case-sensitive:

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `Protein_Sequences` | list[string] | conditional | Protein amino-acid sequences, one sequence per list element. |
| `DNA_Sequences` | list[string] | conditional | DNA sequences, one sequence per list element. |
| `RNA_Sequences` | list[string] | conditional | RNA sequences, one sequence per list element. |
| `SMILES` | list[string] | conditional | Ligand SMILES, one ligand per list element. |

Provide at least the molecular entities needed for the requested complex. Empty
lists are valid for unused categories in the reference samples. The live
protein-plus-ligand canary also succeeded while omitting unused DNA and RNA
fields, but explicitly sending empty lists keeps the complete schema visible.

The web UI accepts comma-separated entries in each text field, then converts
them to arrays. Sci must send actual JSON lists. For example, if the UI text
is `protein_sequence_1,protein_sequence_2`, submit:

```python
"Protein_Sequences": [protein_sequence_1, protein_sequence_2]
```

Do not submit one literal comma-joined string inside a one-element list. Trim
whitespace and discard empty items when converting UI text. Sequence order is
meaningful because each list element becomes a distinct molecular chain/entity.
For an antibody–antigen complex, include antigen, heavy chain, and light chain
as three distinct `Protein_Sequences` entries; omitting the antigen models only
the antibody internal complex.

```python
job_name = "Boltz2"
experiment_name = "Boltz2 protein-ligand complex"
experiment_data = {
    "Protein_Sequences": [protein_sequence],
    "DNA_Sequences": [],
    "RNA_Sequences": [],
    "SMILES": [ligand_smiles],
}
```

### Boltz2 versus BoltzGen

The attached array-input screenshot and its code sample are for `Boltz2`, not
the separate `boltzgen` generation API. The user-confirmed BoltzGen UI rule is:
when that UI exposes a `protein` text field, enter multiple protein sequences in
that field separated by commas. Keep this as UI-format guidance. The currently
supplied BoltzGen backend CSV contract is structure/chain based (`file_path`,
`protein_id`, protocol, length, and design controls) and does not expose either
`protein` or `Protein_Sequences`; therefore, do not invent a BoltzGen backend
payload from the UI rule until a matching live submission schema is supplied
and verified.

### Output instructions

Boltz2 returns three separately downloadable output objects. Download and
inspect all three; do not stop after the PDB ZIP:

```python
result["OutputData"]["pdb_zip"]["download_link"]
result["OutputData"]["csv_path"]["download_link"]
result["OutputData"]["zip_path"]["download_link"]
```

- `pdb_zip` contains the predicted complex PDB file(s).
- `csv_path` is a direct CSV mapping inputs to structures. The live columns
  were `seq1`, `seq2_or_ligand`, and `filepath`.
- `zip_path` contains the complete prediction package: processed records,
  confidence/affinity JSON, PAE/PDE/pLDDT arrays, PDB predictions, MSA files,
  constraints, and run metadata.

The verified confidence JSON contained:

```text
confidence_score,ptm,iptm,ligand_iptm,protein_iptm,complex_plddt,
complex_iplddt,complex_pde,complex_ipde,chains_ptm,pair_chains_iptm
```

The verified affinity JSON contained:

```text
affinity_pred_value,affinity_probability_binary,
affinity_pred_value1,affinity_probability_binary1,
affinity_pred_value2,affinity_probability_binary2
```

Do not relabel the affinity values as kcal/mol, Kd, or another physical unit
unless an authoritative backend contract supplies that interpretation. Report
the original field names. Use the PDB for structure, confidence JSON for model
quality, and affinity JSON only when the submitted complex includes a ligand
and the file is present.

Before reporting, verify that the number and types of modeled entities match
the submitted arrays and that every downloaded structure is represented in the
mapping CSV.

### Evidence

- The all-experiments CSV and UI screenshot confirm the four array fields and
  the comma-separated UI-entry behavior.
- The Boltpro product CSV confirms backend task `boltz-structure-prediction`,
  multi-protein support, and the three output families.
- Live submission and terminal fetch succeeded for one protein plus one SMILES
  ligand. All three signed artifacts downloaded successfully; the PDB, mapping
  CSV, confidence JSON, affinity JSON, and supporting files were inspected.

## 12. Monomer Structure Prediction

| Field | Value |
|-------|-------|
| **job_name** | `Protein_Structure_Prediction` |
| **Mongo diagnostics collection** | `monomer_structure_prediction` (verified sample record); pair with the returned experiment ID. |
| **watch_time** | Long (~5-15 min) |
| **validation status** | **Schema accepted, but backend dispatch failed** |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `input_csv` | string | yes | S3 path to CSV (upload first) |
| `property_name` | string | no | Default: `"monomer_structure_prediction"` |
| `experiment_name` | string | no | Experiment label |

The minimal accepted request contains only the uploaded CSV path:

```python
job_name = "Protein_Structure_Prediction"
experiment_name = "Monomer structure prediction"
experiment_data = {"input_csv": uploaded_sequence_csv}
```

NodeAPI returned HTTP 200 and a document ID, but the embedded `apiResponse`
was `status="error"` because Kubernetes manifest creation failed. This proves
the request schema reached dispatch, not that a scientific job queued or
completed. Do not retry automatically or report this tool as working until the
platform deployment error is repaired.

**Input CSV columns:** `seq_id, sequences` (lowercase)

**Output keys:**
- `result["OutputData"]["output_csv_path"]["download_link"]` — result CSV
- `result["OutputData"]["output_zip_path"]["download_link"]` — PDB structures ZIP

**Output CSV columns:** `Seq_id, pdb_filename, pLDDT, pTM` (note: `Seq_id` capitalized, input uses lowercase `seq_id`)

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

## ipSAE Generation
Score protein-protein interfaces across AlphaFold2-multimer or Boltz2 prediction
bundles using PAE, residue confidence, and inter-chain distance information.

Aliases: **ipSAE**, **IPSAE**, **ipSAE Generation**.

| Field | Value |
|---|---|
| **job_name** | `ipsae-protein` |
| **collection / backend task** | `ipsae` / `ipsae` |
| **validation status** | **Submission verified (HTTP 200); terminal result pending** |
| **accepted input** | uploaded `.zip` prediction bundle |
| **product status** | Active |

Use exact outer job name `ipsae-protein`. The lowercase worker request label
`ipsae` is not the NodeAPI job name.

### Inputs

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `model_type` | string enum | yes | Exact value `af2_multimer` or `boltz2`; choose it to match the archive producer. |
| `input_path` | platform path string | yes | Uploaded ZIP containing compatible prediction structures and their matching confidence/PAE files. A lone PDB is insufficient. |
| `pae_cutoff` | positive number | no | PAE threshold; worker default 10.0. |
| `dist_cutoff` | positive number | no | C-alpha contact-distance threshold; worker default 10.0. |

Validate the ZIP before upload: it must be a real archive, contain at least one
compatible predicted model, and include the confidence/PAE companion required
for every structure to be scored. Reject mixed producer formats and set
`model_type` from the actual files rather than guessing from the filename.

```python
uploaded_prediction_zip = file_upload(local_multimer_prediction_zip)

job_name = "ipsae-protein"
experiment_name = "ipSAE AF2 multimer scoring"
experiment_data = {
    "model_type": "af2_multimer",
    "input_path": uploaded_prediction_zip,
    "pae_cutoff": 10.0,
    "dist_cutoff": 10.0,
}
```

For Boltz2 outputs change only the producer enum when the archive contents are
actually Boltz2-compatible:

```python
experiment_data["model_type"] = "boltz2"
```

Do not add worker-managed `tokenid`, `experiment_id`, `user_id`, or inner
`job_name` fields to `experiment_data`.

### Output instructions

The product contract specifies one consolidated CSV with one row per predicted
model and flattened chain-pair/score results. The worker records the artifact
under `datainfo.outputFilePath`, but the outer NodeAPI envelope and exact CSV
columns have not yet been observed.

Use `fetch_status` with collection name `ipsae-protein`, download every signed
artifact it exposes, and parse the consolidated CSV. Verify the number of model
rows against compatible models in the input ZIP, then report chain-pair scores,
cutoffs, and any models skipped for missing/mismatched confidence files. Do not
invent column names before inspecting the first successful artifact.

The product estimate is approximately two minutes per model and one credit;
queue time may vary. Treat this as an estimate, not a guaranteed runtime.

### Evidence and live-test state

- The BoltPro source defines active endpoint `/v5/ProteinGeneration/ipsae`,
  collection/task `ipsae`, the two model enums, ZIP input, positive cutoffs,
  defaults, expected consolidated output, runtime estimate, and cost estimate.
- The consolidated tool-name source supplies exact outer job name
  `ipsae-protein` and a complete AF2-multimer sample payload.
- An AF2-multimer payload using numeric cutoffs of `10` returned HTTP 200,
  task `ipsae`, and a document ID.
- Submission is now verified. Do not mark terminal execution or output columns
  verified until result fetch, artifact download, and CSV inspection succeed.
