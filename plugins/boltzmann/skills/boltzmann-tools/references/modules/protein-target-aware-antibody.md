# Target-Aware Antibody Design

Domain: Protein Engineering

This module was selected by the server. Use only the exact contracts below.

## 10. Target-Aware CDR Designer / Epitope Conditioned Antibody Generation

Generate antigen- and epitope-conditioned antibody CDR backbones.

**Raw-mode execution warning: request contract incomplete.** Raw requests built
from the table below were rejected by the server with `Schema validation failed`:
heavy-chain ID, light-chain ID, and antigen-chain IDs are explicitly required,
plus an epitope-related requirement whose returned error was truncated. Their
accepted payload names/types are not established here. Block new raw-mode
submissions until the current server schema is verified; do not guess selector
keys or automatically resubmit. A rejection without a returned job ID is not a
queued or completed generation. Preserve prepared inputs and report the error.
This warning supersedes the source-backed status label below for raw mode.

| Field | Value |
|---|---|
| **job_name** | `epitope_abgen` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_path` | string | prepared mode | Prepared PT or ZIP of PTs; aliases feature_path/input_feature_path. Use canonical input_path. This route blocks until a safe feature-content validator exists. |
| `antigen_pdb_path` | string | raw mode | Antigen PDB, required together with antibody PDB instead of input_path. |
| `antibody_pdb_path` | string | raw mode | Antibody-framework PDB. |
| `mask_cdrs` | string | no | Default HCDR3; mask is an alias. Other allowed names are not verified by the operator packet. |
| `complex_id` | string | no | Default platform-assigned experiment_id; never invent that ID. |
| `epitope_residues` | string or array[string] | no | Residues such as `C:103,C:111` |
| `samples_per_task` | integer | no | 1-16; product source default is 4 |
| `seed` | integer | no | 0-4294967295; default 2026 |
| `max_tokens` | integer | no | 32-416; default 384 |
| `task_id` | string | no | Single prepared feature only. |
| `mask_type` | string | no | Default None. |
| `complex_pdb_path` | string | no | Optional complex PDB for one feature lacking Atom14 labels; pdb_path is an alias. |
| `min_finite_coordinate_rate` | number | no | Default 1.0. |
| `allow_cpu` | boolean | no | Strict boolean; default false. |

Choose one input route, not both. Do not ask for raw PDBs when a prepared-feature
path is supplied. Completeness does not override the prepared-feature validation
block. Platform/auth fields are not user inputs. These operator-confirmed rules
supersede the former raw-PDB-only mask table.

**Output contract:** `OutputData.datainfo.output_path` -> results archive (product CSV).

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

## AntiBMPNN
Generate structure-conditioned antibody sequence variants for selected chains
or residue positions in an antibody or antibody-antigen structure.

| Field | Value |
|---|---|
| **job_name** | `AntiBMPNN` |
| **collection / backend task** | `antibmpnn` / `antibmpnn` |
| **validation status** | **Submission verified (HTTP 200); terminal output pending** |
| **accepted structure input** | uploaded `.pdb` or `.zip` of PDB files |
| **product status** | Active |

The outer Sci/NodeAPI `job_name` is case-sensitive `AntiBMPNN`. The
lowercase `antibmpnn` value in the worker API is an internal request label and
must not replace the outer job name passed to `submit_request` or
`fetch_status`.

### Inputs

| Parameter | Type | Required | Validation and meaning |
|---|---|---|---|
| `input_path` | platform path string | yes | Uploaded single `.pdb` antibody/complex structure or one `.zip` containing PDB structures. Raw sequences and local paths are invalid. |
| `chains_to_design` | list of strings | yes | Non-empty list of one-character PDB chain IDs, for example `['H', 'L']`. Every chain must exist in every applicable input structure. |
| `residue_positions_to_design` | object mapping string to string | no | Designed-chain IDs mapped to one-based residue selections such as `101-106,115,119-123`. Omit or send `{}` for full-chain design. |
| `generation_count` | integer | yes | Sequences to generate per PDB; accepted range 1–10000. Use a small count for validation. |

Before submission, inspect the PDB chain IDs and residue numbering. Reject an
empty chain list, chain IDs absent from the structure, malformed ranges,
descending ranges, and residue-map keys not present in `chains_to_design`.
Preserve PDB residue numbering; do not reinterpret residue selections as
zero-based sequence indexes.

For a single uploaded PDB and full-chain design:

```python
uploaded_structure_path = file_upload(local_antibody_or_complex_pdb)

job_name = "AntiBMPNN"
experiment_name = "AntiBMPNN minimal validation"
experiment_data = {
    "input_path": uploaded_structure_path,
    "chains_to_design": ["B"],
    "residue_positions_to_design": {},
    "generation_count": 1,
}
```

For targeted design, include only explicitly selected positions:

```python
experiment_data = {
    "input_path": uploaded_structure_path,
    "chains_to_design": ["B", "C"],
    "residue_positions_to_design": {
        "B": "101-106,115,119-123",
        "C": "108-114",
    },
    "generation_count": 2,
}
```

The supplied live submission record verifies this ZIP-based H/L-chain payload
shape:

```python
job_name = "AntiBMPNN"
experiment_name = "AntibMPNN_test"
experiment_data = {
    "input_path": "users/<uid>/<timestamp>/ppiflow_output.zip",
    "chains_to_design": ["H", "L"],
    "residue_positions_to_design": {
        "H": "5-6,11-15,11-21",
        "L": "14-16,7-9,10-12",
    },
    "generation_count": 2,
}
```

That request returned HTTP 200 with `task_name="AntiBMPNN"`, status `queued`,
and a document ID. This verifies submission acceptance only; it does not prove
terminal success, downloaded artifact structure, generated counts, or mutation
contents.

Do not add worker-managed fields such as `tokenid`, `experiment_id`, or
`user_id` to `experiment_data`; the NodeAPI/Sci layer supplies platform
identity and tracking fields.

### Output instructions

The product worker records a generated design path as `datainfo.output_path`,
but the outer NodeAPI terminal envelope and artifact contents have not yet been
observed. Use `fetch_status` with exact collection name `AntiBMPNN`, preserve
the complete terminal response, and inspect every downloaded file before
documenting output columns or sequence counts. Do not assume the worker key is
exposed unchanged as `OutputData.output_path`.

For each result, verify that the source structure, designed chains, requested
residue selection, and requested generation count correspond to the submitted
payload. Report actual generated counts and mutation positions; never infer
them from the request alone.

### Evidence and live-test state

- The BoltPro source defines the active `/v5/Toolbox/AntiBMPNN` product,
  collection/task `antibmpnn`, all four experiment fields, position syntax,
  and generation range 1–10000.
- The consolidated tool-name source identifies exact outer job name
  `AntiBMPNN`; the product source explicitly distinguishes it from the lowercase
  local worker label.
- A supplied live canary used `ppiflow_output.zip`, designed chains `H` and
  `L`, explicit per-chain residue ranges, and `generation_count=2`. NodeAPI
  returned HTTP 200, queued task `AntiBMPNN`, a task job identifier, and a
  document ID.
- No terminal fetch or downloaded artifact inspection accompanies that canary,
  so the result schema and scientific output remain unverified.
