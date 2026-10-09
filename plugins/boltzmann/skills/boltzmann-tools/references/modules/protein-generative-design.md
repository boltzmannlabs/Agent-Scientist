# Generative Protein Design

Domain: Protein Engineering

This module was selected by the server. Use only the exact contracts below.

For a generic PPI Flow or PXDesign request, ask which documented task the user
wants rather than selecting one silently. PPI Flow has monomer, protein,
antibody, and nanobody jobs. PXDesign has infer and pipeline jobs. Preserve
the selected job and its matching `task_name` throughout clarification.

## 41. BoltzGen

Generate protein, nanobody, or antibody designs with optional ligand and structural constraints.

| Field | Value |
|---|---|
| **job_name** | `boltzgen` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `protocol` | string | yes | `protein`, `nanobody`, `antibody`, `peptide`, `protein-small_molecule` |
| `file_path` | mixed | yes | Use the exact source field. |
| `protein_id` | string | yes | Use the exact source field. |
| `sequence_len` | number | yes | Use the exact source field. |
| `num_designs` | number | yes | Use the exact source field. |
| `budget` | number | yes | Use the exact source field. |
| `cyclic` | boolean | yes | JSON `true` or `false` |
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

## PPI Flow Antibody

Generate antibody structures against an antigen using uploaded antigen and
framework PDBs, explicit chain identities, CDR-length ranges, and optional
antigen hotspots.

| Field | Value |
|---|---|
| **job_name** | `ppiflowantibody` |
| **backend task** | `antibody` |
| **validation status** | **Submission verified (HTTP 200)** |

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `task_name` | string | yes | Exact value `antibody`. |
| `antigen_pdb` | platform path string | yes | Uploaded antigen PDB. |
| `framework_pdb` | platform path string | yes | Uploaded antibody framework PDB. |
| `antigen_chain` | string | yes | Antigen chain identifier. |
| `heavy_chain` | string | yes | Framework heavy-chain identifier. |
| `light_chain` | string | yes | Framework light-chain identifier. |
| `cdr_length` | string | no | Optional comma-separated CDR names and inclusive length ranges. |
| `samples_per_target` | integer | yes | Number of designs; the accepted canary used `5`. |
| `specified_hotspots` | string | no | Comma-separated antigen chain/residue identifiers. |

```python
job_name = "ppiflowantibody"
experiment_name = "PPI Flow antibody design"
experiment_data = {
    "task_name": "antibody",
    "antigen_pdb": uploaded_antigen_pdb,
    "framework_pdb": uploaded_framework_pdb,
    "antigen_chain": "A",
    "heavy_chain": "H",
    "light_chain": "L",
    "cdr_length": "CDRH1,5-6,CDRH2,11-15,CDRH3,11-21,CDRL1,14-16,CDRL2,7-9,CDRL3,10-12",
    "samples_per_target": 5,
    "specified_hotspots": "A19,A23,A26,A54,A56,A58,A66,A113,A115,A117,A119,A120,A121,A122,A123,A124,A125",
}
```

This exact payload returned HTTP 200 and a document ID. The terminal archive
has not yet been inspected; report it as submission-verified, not completed.

---

## 42. PX Design Infer

Run PXDesign backbone inference. The full pipeline uses the separate job below.

| Field | Value |
|---|---|
| **job_name** | `pxdesigninfer` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `task_name` | string | yes | `pxdesign-infer` only; alias `task`. |
| `cif_path` | string | yes | Uploaded target CIF path |
| `chain` | string | yes | Target chain identifier |
| `binder_length` | integer | yes | 10-300 |
| `n_samples` | integer | yes | 1-10000 |
| `crop` | string | no | Optional residue range, e.g. `17-145` |
| `hotspots` | string | no | Comma-separated target residue numbers |

**Output contract:** `OutputData.datainfo.output_files` and `config_yaml` (product CSV).

---

## 43. PPI Flow Monomer

For an unspecified PPI Flow request, ask for `task_name` first: `monomer`,
`protein`, `antibody`, or `nanobody`. Each choice routes to its own job below;
never combine all four modes' required fields in one form. An explicit job or
mode already supplies task_name. Mode changes rebuild the draft, preserve only
compatible common values, and never reuse an old submitted job as new approval.

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
| `motif_csv` | file | no | Required only for motif scaffolding; not used for unconditional monomer generation. |
| `motif_names` | string | no | Use the exact source field. |

`length_subset` is a string containing an integer list, e.g. `"[100, 150]"`.
The monomer `generation_mode` clarification selector distinguishes
`unconditional` from `motif_scaffolding`; it is not a backend field.

## PPI Flow Protein

| Field | Value |
|---|---|
| **job_name** | `ppiflowprotein` |

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `task_name` | string | yes | `protein` |
| `input_pdb` | file | yes | Upload target/complex PDB. |
| `target_chain` | string | yes | Target chain in the uploaded structure. |
| `binder_chain` | string | no | Binder chain present in that PDB; alternatively use specified_hotspots. |
| `samples_min_length` | integer | yes | Minimum design length. |
| `samples_max_length` | integer | yes | Maximum design length. |
| `samples_per_target` | integer | yes | Number of designs. |
| `specified_hotspots` | string | no | Target hotspot residues. |

## PPI Flow Nanobody

| Field | Value |
|---|---|
| **job_name** | `ppiflownanobody` |

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `task_name` | string | yes | `nanobody` |
| `antigen_pdb` | file | yes | Upload antigen PDB. |
| `framework_pdb` | file | yes | Upload nanobody framework PDB. |
| `antigen_chain` | string | yes | Antigen chain ID. |
| `heavy_chain` | string | yes | Nanobody chain ID; there is no light_chain input. |
| `cdr_length` | string | no | Optional CDR length specification. |
| `samples_per_target` | integer | yes | Number of designs. |
| `specified_hotspots` | string | no | Optional antigen hotspots. |

## PX Design Pipeline

| Field | Value |
|---|---|
| **job_name** | `pxdesignpipeline` |

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `task_name` | string | yes | `pxdesign-pipeline` only; alias `task`. |
| `cif_path` | file | yes | Upload the target CIF structure. |
| `chain` | string | yes | Target chain; alias `target_chain`. |
| `binder_length` | integer | yes | 10-300. |
| `n_samples` | integer | yes | 1-10000. |
| `crop` | string | no | Optional residue range, e.g. `17-145`. |
| `hotspots` | string | no | Optional comma-separated target residues. |

These added mode contracts come from the public submit-job documentation and
the supplied experiment notebook. Schema coverage is not a live execution or
terminal-output claim. Do not guess a diagnostics collection for a new job.

**Output contract:** `OutputData.datainfo.output_path` (product CSV).

---
