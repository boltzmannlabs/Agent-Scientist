# Toolbox Models

Domain: Protein Engineering

This module was selected by the server. Use only the exact contracts below.

## 14. Prodigy (Binding Affinity)
Estimate protein–protein binding affinity and identify interface residues for
selected chains in one PDB or a ZIP of PDB structures.

| Field | Value |
|---|---|
| **job_name** | `Prodigy` |
| **backend task/collection** | `prodigy` |
| **validation status** | **Verified working for chains A and B** |
| **observed terminal status** | `Success` |

### Inputs

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `input_path` | string | yes | Platform path to one `.pdb` or a `.zip` of PDB structures. |
| `chain_list` | list[string] | yes | Non-empty list containing the exact chain IDs whose interface will be evaluated. |

The UI accepts comma-separated chain IDs such as `A,B` and converts them to an
array. Sci must submit an actual JSON list:

```python
"chain_list": ["A", "B"]
```

Do not send the string `"A,B"`. Inspect the uploaded structure and derive the
real chain IDs before submission. For antibody–antigen analysis, include the
antigen and antibody chains needed to define the intended interface; otherwise
the tool can score an internal antibody interface instead. If a ZIP contains
structures with inconsistent chain IDs, split them into compatible runs.

The product sheet says an empty list can mean all chains, while the required UI
field and prior agent validation report that `[]` can yield no output. Use the
safe, live-proven rule: always send an explicit non-empty `chain_list`.

```python
uploaded_structure_path = file_upload(local_pdb_or_zip)

job_name = "Prodigy"
experiment_name = "Prodigy binding-affinity prediction"
experiment_data = {
    "input_path": uploaded_structure_path,
    "chain_list": ["A", "B"],
}
```

### Output instructions

The terminal result returns a directly downloadable CSV:

```python
result["OutputData"]["outputFilePath"]["path"]
result["OutputData"]["outputFilePath"]["download_link"]
```

Output headers depend on the submitted chain list. For `A` and `B`, the live
CSV contained:

```text
id,binding_affinity for AB,chain_A of AB,chain_B of AB
```

For another chain set, construct no hard-coded column names. Locate the column
starting with `binding_affinity for ` and the corresponding `chain_<ID> of `
interface-residue columns. The binding-affinity value is predicted Delta G in
kcal/mol; more negative values indicate stronger predicted binding under this
model.

The verified API output does not contain Kd, hydrogen-bond counts, salt-bridge
counts, or a separate total-contact count. Do not claim that Prodigy returned
those measurements unless a future output schema actually includes them.

### Evidence

- The all-experiments and Boltpro CSVs confirm exact job name `Prodigy`, PDB or
  ZIP input, and `chain_list` as a list of strings.
- The attached screenshot confirms `input_path` and `chain_list` are required
  in the current UI and that chain IDs are entered comma-separated.
- Live submission with `["A", "B"]`, terminal fetch, direct CSV download, and
  one-row parse all succeeded; the dynamic `AB` headers were observed.

## 15. Unconditional Sampling

| Field | Value |
|-------|-------|
| **job_name** | `Uncondtional_Sampling` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `samples_per_length` | int | no | Default: 10 |
| `seq_lengths` | list[int] | no | Default: `[70, 100, 200, 300]` |

**Output key:** `result["OutputData"]["outputFilePath"]["download_link"]` — ZIP with PDB files named `sample_0.pdb`, `sample_1.pdb`, etc.

---

## 16. Motif Scaffolding

| Field | Value |
|-------|-------|
| **job_name** | `Motiff_Scaffolding` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pdb_path` | string | yes | S3 path to PDB (upload first) |
| `contigs` | string | yes | Contig definition (e.g., `"A1-10"`) |
| `targets` | string | yes | Target chains |
| `min_lengths` | int | no | Minimum scaffold length |
| `max_lengths` | int | no | Maximum scaffold length |
| `samples_per_target` | int | no | Default: 2 |

**Output:** ZIP with designed PDB scaffolds.

---

## 17. Ligand MPNN

| Field | Value |
|-------|-------|
| **job_name** | `Ligand_MPNN` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `input_path` | string | yes | S3 path to PDB (upload first) |
| `num_sequences` | int | yes | Number of sequences to design |

**Output:** ZIP containing `backbones/` folder, `seqs/` folder, and CSV file.

**Output CSV columns:** `file_name, id, Sequence`

---

## 18. NetsolP (Solubility)

| Field | Value |
|-------|-------|
| **job_name** | `Netsolp` |
| **Mongo diagnostics collection** | `solubility_prediction` (verified sample record); pair with the returned experiment ID. |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `input_path` | string | yes | S3 path to CSV or FASTA (upload first) |
| `prediction_type` | string | no | `"S"` (solubility), `"U"` (usability), `"US"` (both). Default: `"S"` |

**Input CSV columns:** `Sequence_ID, Sequences`

**Output key:** `result["OutputData"]["output_path"]["download_link"]`

**Output CSV columns (solubility only):** `Sequence_ID, Sequence, predicted_solubility_model_0..4, predicted_solubility, Length, Molecular_Weight, PI, Hydrophobic_Count, Acidic_count, Basic_count, Polar_Count, Others_Count, A..Y`

---

## 19. Pep_Patch

| Field | Value |
|-------|-------|
| **job_name** | `Pep_Patch` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `input_path` | string | yes | S3 path to PDB (upload first) |

**Output CSV columns:** `type, npoints, area, cdr, main_residue`

---

## 20. Cat_Pred (Catalyst Prediction)
Predict enzyme catalytic rate from paired protein sequences and substrate
SMILES, including uncertainty estimates.

| Field | Value |
|---|---|
| **job_name** | `Cat_Pred` |
| **backend task** | `catpred` |
| **validation status** | **Verified working** |
| **observed terminal status** | `Success` |

### Inputs

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `input_path` | string | yes | Platform path to the input CSV returned by `file_upload`. |

The input CSV must contain these exact case-sensitive columns:

```text
Seq_id,Sequences,SMILES
```

Use one enzyme–substrate pair per row. `Sequences` is the protein sequence and
`SMILES` is the associated substrate representation. The input header is
plural `Sequences` (operator correction, 2026-09-23); output headers below
describe the observed output and are not input requirements.

```python
uploaded_csv_path = file_upload(local_csv_path)

job_name = "Cat_Pred"
experiment_name = "CatPred catalytic-rate prediction"
experiment_data = {
    "input_path": uploaded_csv_path,
}
```

### Output instructions

The terminal result returns a directly downloadable CSV through:

```python
result["OutputData"]["outputFilePath"]["path"]
result["OutputData"]["outputFilePath"]["download_link"]
```

The verified 14-row output contained these exact columns:

```text
Seq_id,SMILES,Sequence,Prediction_(s^(-1)),Prediction_log10,
SD_total,SD_aleatoric,SD_epistemic
```

`Prediction_(s^(-1))` is the predicted catalytic rate and `Prediction_log10`
is its log10 representation. Preserve the three uncertainty columns; do not
rank solely by the point prediction when uncertainty materially differs.

The old skill incorrectly lists lowercase `sequence` and a `pdbpath` column.
The live output contains capitalized `Sequence` and no `pdbpath`; use the live
schema above.

### Evidence

- The all-experiments and Boltzyme CSVs confirm exact job name `Cat_Pred`,
  backend task `catpred`, `input_path`, and the required paired sequence/SMILES
  input.
- Live submission, terminal fetch, direct CSV download, and parsing succeeded
  for all 14 rows.

## 21. Clean (Enzyme Classification)

| Field | Value |
|-------|-------|
| **job_name** | `Clean` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `input_path` | string | yes | S3 path to CSV (upload first) |

**Input CSV columns:** `Seq_id, Sequences` — both capitalized

**Output CSV columns:** `Seq_id, EC_pred, pred_probability, Sequences, SMILES`

---

# Small Molecule (BoltChem)

## 20. Antibody Numbering

Number antibody residues with a supported numbering scheme.

| Field | Value |
|---|---|
| **job_name** | `Antibody_Numbering` |
| **Mongo diagnostics collection** | `AbNumber` (verified sample record); pair with the returned experiment ID. |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `dataPath` | string | yes | Use the exact source field. |
| `scheme` | string | yes | values: `Kabat, Chothia, Aho` |
| `property_name` | string | yes | `AbNumber` only; preserve the capital N in the backend value. |

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
| `zip_path` | string | yes | Remote ZIP containing PDB files, including nested directories (not nested ZIPs). |
| `chain` | string | no | Empty/omitted: first chain in each PDB. An explicit chain must exist in each structure. |
| `model_path` | string | no | Omit for backend default `${PRODUCT_BASE}/models/thermompnn/models/thermoMPNN_default.pt`. Never submit that placeholder. Custom PT content validation is not implemented, so custom model files remain blocked. |

**Output contract:** `OutputData.datainfo.output_path` -> CSV with mutation and ddG columns (product CSV).

---

## 34. TM Align
Structurally align one protein model, or a ZIP of protein models, against one
reference PDB and report TM-scores, RMSD, and structure lengths.

| Field | Value |
|---|---|
| **job_name** | `tm_align` |
| **backend task/collection** | `tmalign` |
| **validation status** | **Verified working** |
| **observed terminal status** | `Success` |

### Inputs

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `input_path` | string | yes | At least one design PDB, directly or in a ZIP. First chain used from each structure. |
| `wt_path` | string | yes | Exactly one reference/wild-type PDB. First chain used. |

Upload local files once with `file_upload`. `wt_path` is a scalar string. A
stale UI sample wraps it in a list, but the validation schema, backend model,
and successful live payload all require a string. Do not add the client-only
optional `task_name` field; the exact Sci/NodeAPI routing identity is the
top-level `job_name="tm_align"`.

```python
design_path = file_upload(local_design_pdb_or_zip)
reference_path = file_upload(local_reference_pdb)

job_name = "tm_align"
experiment_name = "TM-align structural comparison"
experiment_data = {
    "input_path": design_path,
    "wt_path": reference_path,
}
```

### Output instructions

The terminal result returns one directly downloadable CSV:

```python
result["OutputData"]["outputFilePath"]["path"]
result["OutputData"]["outputFilePath"]["download_link"]
```

The verified output contained:

```text
wt_file,design_file,tm_score_norm_wt,tm_score_norm_design,rmsd,
wt_length,design_length
```

TM-align reports two normalized scores because normalization by the reference
length and by the design length can differ. Preserve both; never collapse them
into one unlabeled `TM-score`. Use `rmsd` together with both TM-scores, and keep
the associated filenames and lengths when comparing multiple designs.

### Evidence

- The all-experiments CSV confirms `.pdb | .zip` for `input_path`, `.pdb` for
  `wt_path`, and exact job name `tm_align`.
- The Boltzyme product CSV confirms backend task `tmalign` and the two scalar
  input paths.
- Live submission, terminal fetch, direct CSV download, and one-row CSV parse
  all succeeded.
