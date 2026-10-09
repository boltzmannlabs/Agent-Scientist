# Docking

Domain: Protein Engineering

This module was selected by the server. Use only the exact contracts below.

## 37. MegaDock
Run rigid protein–protein docking with the active MEGADOCK-GPU v2 backend.

| Field | Value |
|---|---|
| **job_name** | `MegaDock` |
| **Mongo diagnostics collection** | `megadock_gpu` (verified sample record); pair with the returned experiment ID. |
| **backend task** | `megadock_gpu` |
| **validation status** | **Verified working** |
| **observed terminal status** | `Success` |

### Inputs

Both input fields are path-only:

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `ligand_path` | platform path string | yes | Uploaded `.zip` containing one or more ligand protein PDB files. |
| `receptor_path` | platform path string | yes | Uploaded receptor `.pdb`. |

For the active v2 backend, ligand PDB filenames inside the ZIP must end in
`_l.pdb`, and the receptor filename must end in `_r.pdb`. Validate archive
members before upload. Do not pass a list, raw PDB text, local path, or raw
protein sequence. A user-supplied sequence requires an explicit upstream
structure-prediction step before MegaDock can run.

```python
ligand_zip_path = file_upload(local_ligand_zip)
receptor_pdb_path = file_upload(local_receptor_pdb)

job_name = "MegaDock"
experiment_name = "MEGADOCK rigid protein docking"
experiment_data = {
    "ligand_path": ligand_zip_path,
    "receptor_path": receptor_pdb_path,
}
```

### Output instructions

The verified response returned the docking archive under `outputFolderPath`,
not the older documented `outputFilePath`:

```python
result["OutputData"]["outputFolderPath"]["path"]
result["OutputData"]["outputFolderPath"]["download_link"]
```

The live archive contained the uploaded inputs, `visualisation_decoy_paths.txt`,
an `R-L.out` MEGADOCK result file, prepared ligand/receptor PDBs, ten ligand
pose PDBs, and ten combined `decoy.<rank>.pdb` complex structures. Use the
decoy-path manifest to locate visualization candidates and preserve `R-L.out`
with the structural results. Verify that each expected ligand produced a
docking folder before reporting completion.

### Evidence

- The all-experiments CSV confirms exact job name `MegaDock` and the two path
  fields.
- The active Boltpro v2 row confirms ZIP/PDB input conventions and task
  `megadock_gpu`; an older v1 row is inactive and must not override v2.
- Live submission, terminal fetch, archive download, ZIP validation, and member
  inspection all succeeded.

## 44. Placer
Place a named ligand in a protein structure, generate candidate poses, and
rank the poses by a supported confidence metric.

| Field | Value |
|---|---|
| **job_name** | `Placer` |
| **validation status** | **Transport/output verified; fresh payload-association canary required** |
| **accepted upload types** | `.pdb`, `.cif` |
| **observed terminal status** | `Success` |

### Inputs

All five fields below are required by the authoritative validation schema and
backend API model, even though an older generated module labels four optional.

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `input_file_path` | string | yes | Platform path returned by `file_upload`; filename must end in `.pdb` or `.cif`. |
| `rerank` | string enum | yes | Exact value `prmsd`, `plddt`, or `plddt_pde`. |
| `suffix` | string | yes | Ligand identifier appended to outputs; must match `^[A-Z]+-[A-Z]+-\d+$`, for example `D-LDP-501`. |
| `predict_ligand` | string | yes | Exact ligand identifier in the input structure, including chain ID, 3-letter ligand name, and residue number; same format as `suffix`. |
| `no_of_samples` | integer | yes | Number of poses; minimum 10 and maximum 100. Send an integer, not a string. |

`predict_ligand` must identify a ligand that actually exists in the uploaded
structure. Do not copy `D-LDP-501` into an unrelated PDB/CIF merely because it
is the reference sample.

```python
uploaded_structure_path = file_upload(local_structure_path)

job_name = "Placer"
experiment_name = "Placer - reference ligand pose generation"
experiment_data = {
    "input_file_path": uploaded_structure_path,
    "rerank": "prmsd",
    "suffix": "D-LDP-501",
    "predict_ligand": "D-LDP-501",
    "no_of_samples": 10,
}
```

### Output instructions

The terminal NodeAPI result exposed the same common archive envelope:

```python
result["OutputData"]["outputFilePath"]["path"]
result["OutputData"]["outputFilePath"]["download_link"]
```

The inspected ZIP contained:

- one ranked CSV with columns `label`, `model_idx`, `fape`, `lddt`, `rmsd`,
  `kabsch`, `prmsd`, `plddt`, and `plddt_pde`;
- one generated PDB model containing the placed ligand poses.

Sort and interpret the rows using the exact submitted `rerank` metric. Before
reporting, confirm the archive filenames, ligand label, and row count agree
with `predict_ligand`, `suffix`, and `no_of_samples`.

### Current validation caveat

The recorded Placer submission returned HTTP 200, and its document ID returned
HTTP 200 with terminal `Success`; the signed ZIP also downloaded and opened.
However, the archive contained the reference identifiers `4dtz` and
`D-LDP-501` with 10 rows, while the payload written beside that document ID in
`testing_tools.py` uses a different uploaded path/ligand identifier and requests
20 samples. This proves the endpoint and output shape, but not that the shown
payload produced that archive. Run one fresh, uniquely named canary and require
the ligand label and pose count to match before upgrading this contract to
**Verified working**.

### Evidence

- The all-experiments CSV defines the three fixed rerank values, both ligand
  identifier validations, and the inclusive 10–100 sample range.
- The Boltzyme product CSV confirms backend task/collection `placer`, exact
  input fields, PDB/mmCIF support, and the tabular `datainfo.outputFilePath`
  result model.
- The UI screenshot independently confirms `.pdb | .cif` uploads and the
  `prmsd | plddt | plddt_pde` fixed options.
- Live result transport and artifact readability are confirmed; payload-to-
  artifact identity remains deliberately unverified for the reason above.
