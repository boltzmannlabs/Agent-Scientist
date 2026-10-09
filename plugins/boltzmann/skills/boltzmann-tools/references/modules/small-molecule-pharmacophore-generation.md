# Pharmacophore Generation

Domain: Small Molecule Design

This module was selected by the server. Use only the exact contracts below.

## 30. Pharmacophore Hypothesis (phcore_gen)

| Field | Value |
|-------|-------|
| **job_name** | `Pharmacophore_Hypothesis` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pdb_path` | string | yes | S3 path to PDB (upload first) |
| `features` | list[string] | yes | See options |
| `ligand` | string | yes | Three-letter ligand residue code present in the PDB, not a SMILES string |

**Feature options:** `"hb acceptor"`, `"hb donor"`, `"aromatic ring"`, `"hydrophobicity"`, `"positive charge"`, `"negative charge"`

**Output CSV columns:** `features, features_length, ref_sdf_file, hypothesis_file`.
Use the returned `.posp` hypothesis artifact as the input to pharmacophore-based
generation or screening.

---

## 31. Pharmacophore-Based Generator (pgmg_molgen)

| Field | Value |
|-------|-------|
| **job_name** | `Pharmacophore_Based_Generator` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `posp_path` | string | yes | S3 path to .posp hypothesis file (from phcore_gen) |

**Output CSV columns:** `SMILES, QED, SA, TPSA, NUM_HDONORS, NUM_HACCEPTORS, Molecular Weight`

---


---

## Verified BoltChem contract overlay (2026-09-08)

The following section is the current verified BoltChem contract for this module. It overrides conflicting legacy text above. Do not submit until its required fields, exact enums, file headers, and validation rules pass.

### Pharmacophore-Based Generator and Receptor Pharmacophore Hypothesis

# Pharmacophore based generator
Tool display name:Pharmacophore based generator
Frontend route/screen:
Exact form fields:experimentName, posp_path
Required fields:experimentName, posp_path
Optional fields:null
Allowed choices and exact spelling:
Sample input file:CURRENT_USER_UPLOAD_PATH
Required file format:posp
Required column names:
Sample output file:/path/to/approved-input-or-output
output file format:csv
columns of output file: SMILES,QED,SA,TPSA,NUM_HDONORS,NUM_HACCEPTORS,Molecular Weight
Observed successful output envelope: `OutputData.pgmg_upload_path` containing a
generated CSV `path` and one or more signed `download_link` values. A verified
live response returned HTTP 200 with `status: Success`.
Observed artifact path pattern:
`.../Pharmacophore_Based_Generator/pharmacophore-generator/<run_id>.csv`.

Actual backend/network payload:
data = {
        "experimentData": {
            "posp_path": "CURRENT_USER_UPLOAD_PATH"
        },
        "job_name": "Pharmacophore_Based_Generator",
        "experimentName": "prime"
    }
Exact backend job name, if visible:Pharmacophore_Based_Generator
Known validation or failure messages:
- Treat HTTP 200 with `status: Success` and a non-empty
  `OutputData.pgmg_upload_path` artifact as terminal success.
- Verify the signed download, non-empty CSV, documented columns, and actual row
  count before reporting generated molecules.

# Receptor based Pharmacophore hypothesis
Tool display name:Receptor based Pharmacophore hypothesis
Frontend route/screen:
Exact form fields:pdb_path, features, ligand
Required fields:pdb_path, features, ligand
Optional fields:
fields details and options:
pdb_path: String,
"features": [
                "hb acceptor",
                "hb donor",
                "aromatic ring",
                "hydrophobicity",
                "positive charge",
                "negative charge"
            ],
ligand:String
Allowed choices and exact spelling:
Sample input file:/path/to/approved-input-or-output
Required file format:pdb
Required column names:
Sample output file:
Observed successful output envelope: `OutputData.zip_files` (generated ZIP),
`OutputData.outputFilePath` (generated CSV), and
`OutputData.default_hypothesis` (generated `.posp` hypothesis). A verified live
response returned HTTP 200 with `status: Success`.
Observed artifact path patterns:
- `.../Pharmacophore_Hypothesis/pharmacophore-hypothesis/<run_id>.zip`
- `.../Pharmacophore_Hypothesis/pharmacophore-hypothesis/<run_id>.csv`
- `.../Pharmacophore_Hypothesis/pharmacophore-hypothesis/<run_id>_default.posp`
The exact CSV columns from the live artifact still require inspection; do not
invent them from the HTTP envelope. The `.posp` file is reusable by downstream
pharmacophore generation or screening.
Actual backend/network payload:
data = {
        "experimentData": {
            "pdb_path": "CURRENT_USER_UPLOAD_PATH",
            "features": [
                "hb acceptor",
                "hb donor",
                "aromatic ring",
                "hydrophobicity",
                "positive charge",
                "negative charge"
            ],
            "ligand": "DUE"
        },
        "job_name": "Pharmacophore_Hypothesis",
        "experimentName": "prime"
    }
Exact backend job name, if visible:Pharmacophore_Hypothesis
Known validation or failure messages:
- Treat HTTP 200 with `status: Success` and all expected output keys
  (`zip_files`, `outputFilePath`, and `default_hypothesis`) as terminal success
  only after each signed download is verified.
- A missing or unreadable ZIP, CSV, or `.posp` artifact is unverified; do not
  claim hypothesis generation succeeded.
