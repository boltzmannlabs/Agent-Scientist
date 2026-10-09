# Enumeration and Dataset Creation

Domain: Small Molecule Design

This module was selected by the server. Use only the exact contracts below.

## 32. R-Group Enumeration

| Field | Value |
|-------|-------|
| **job_name** | `Molecule_Enumeration` |
| **validation status** | **Submission verified (HTTP 200)** |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `building_blocks_file` | platform path string | yes | Uploaded fragments CSV. |
| `input_scaffolds_file` | string | yes | Scaffold containing R-group placeholders such as `[R1]` and `[R2]`; the live submission accepted a literal scaffold, not a file path. |
| `global_models` | list[string] | yes | Property model names as strings; the live submission used `CaCo2 permeability`. |

```python
job_name = "Molecule_Enumeration"
experiment_name = "Molecule enumeration"
experiment_data = {
    "building_blocks_file": uploaded_fragments_csv,
    "input_scaffolds_file": "N2([R1])CCN([R2])C1=CC=CC=C1C2",
    "global_models": ["CaCo2 permeability"],
}
```

This exact shape returned HTTP 200 and a document ID. The terminal artifact has
not yet been inspected, so preserve and inspect the complete first result
instead of inventing output columns. Do not use the stale `models` field.

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


---

## Verified BoltChem contract overlay (2026-09-08)

The following section is the current verified BoltChem contract for this module. It overrides conflicting legacy text above. Do not submit until its required fields, exact enums, file headers, and validation rules pass.

### Molecule Enumeration

# Molecule Enumeration
Tool display name:Molecule Enumeration
Frontend route/screen:
Exact form fields:building_blocks_file,input_scaffolds_file,global_models
Required fields:building_blocks_file,input_scaffolds_file,global_models
building_blocks_file:CSV input fragements generated via boltzmann's fragment extraction.
Fragments,Num_Atoms,Parent_Molecule_count,Parent_Molecules,Mol_wt,numHacceptors,numHdonors,clogp,rotatable_bonds
input_scaffolds_file:Input scaffold with R's at its position where the enumeration can be done.[THIS NEED NOT BE A PATH EVERY TIME IT WE CAN EVEN TYPE SMILES DIRECTLY, CHECK THE WORKING PAYLOAD ONCE]
globals_models:string"options are:
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
Optional fields:null
Allowed choices and exact spelling:
Sample input file:/path/to/approved-input-or-output
Required file format:csv
Required column names:Fragments,Num_Atoms,Parent_Molecule_count,Parent_Molecules,Mol_wt,numHacceptors,numHdonors,clogp,rotatable_bonds
Sample output file:/path/to/approved-input-or-output
Actual backend/network payload:
data = {
        "experimentData": {
            "building_blocks_file": "CURRENT_USER_UPLOAD_PATH",
            "input_scaffolds_file": "CC(CNC(C1:C2CC(CCN:2:N:C:1)([R1]))=O)(C)C",
            "global_models": [
                "CaCo2 permeability"
            ]
        },
        "job_name": "Molecule_Enumeration",
        "experimentName": "Molecule_Enumeration_test"
    }
Exact backend job name, if visible:Molecule_Enumeration
Known validation or failure messages:
