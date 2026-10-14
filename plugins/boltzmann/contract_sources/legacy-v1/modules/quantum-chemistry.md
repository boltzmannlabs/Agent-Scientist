<!-- canonical-contracts:start -->
> Request fields and catalog status: `../tool-contracts.v1.json`.
> File rules: `../file-input-contracts.v1.json`. Limits: `../input-limits.v1.json`.
> Missing detailed file rules mean partial validation, not a submission ban.
> Known invalid inputs and explicitly blocked tools still stop. Historical output
> verification is separate from request readiness; report uncertainty honestly.
<!-- canonical-contracts:end -->

# Quantum Chemistry

Domain: Density Functional Theory

This module was selected by the server. Use only the exact contracts below.

## 73. Geometry Optimization

Optimize a molecule's geometry with the selected DFT functional, basis set,
charge, spin multiplicity, and dispersion correction. The supplied submission
contract accepts one molecule file path or SMILES value at the user interface
and sends that same validated value in both `molecule_path` and `smiles`.

| Field | Value |
|-------|-------|
| **job_name** | `Geometry_Optimization` |
| **experimentName** | Required user-confirmed unique name; supplied example: `prime` |

**Required user inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `experiment_name` | string | yes | Unique name for the job. Pass it as the top-level `experimentName`; do not place it inside `experimentData`. |
| `molecule_path` | string | yes | One molecule file path (`.xyz`, `.cif`, `.sdf`, `.gjf`, or `.mol`) or a SMILES string. Upload a local file first and use the returned platform path. For the supplied wire contract, copy this exact value to both `molecule_path` and `smiles`. |
| `method` | string | yes | DFT functional. Allowed values: `B3LYP`, `PBE`, `PBE0`, `M06-2X`, `M06-L`, `wB97X-D`, `wB97X-D3`, `wB97M-V`, `HF`, `LDA`, `TPSS`, `TPSSh`, or `CAM-B3LYP`. |
| `basis` | string | yes | Allowed values: `def2-SVP`, `def2-TZVP`, `def2-TZVPP`, `def2-QZVP`, `cc-pVDZ`, `cc-pVTZ`, `cc-pVQZ`, `STO-3G`, `6-31G`, `6-31G*`, `6-311G**`, `aug-cc-pVDZ`, or `aug-cc-pVTZ`. |
| `charge` | integer | yes | Net molecular charge; use `0` for a neutral molecule and an explicit signed integer for an ion. |
| `spin_multiplicity` | integer | yes | `1` for singlet, `2` for doublet, or `3` for triplet. The supplied Geometry Optimization payload uses a number, unlike the older Single Point Energy string contract. |
| `dispersion` | string | yes | `D3`, `D3BJ`, or `D4`. |

**Execution settings** (confirm explicitly before submission):

| Parameter | Type | Supplied example | Notes |
|-----------|------|------------------|-------|
| `use_gpu` | boolean | `true` | Enable GPU acceleration. |
| `use_xtb_preopt` | boolean | `true` | Run xTB pre-optimization before DFT optimization. |
| `use_alchemi_prescreen` | boolean | `false` | Enable Alchemi conformer prescreening. |
| `n_conformers` | integer | `5` | Positive number of conformers. No upper bound was supplied; do not invent one. |
| `compute_resp` | boolean | `false` | Compute RESP charges. |

**Verified submit payload shape supplied for this contract:**

```json
{
  "experimentData": {
    "molecule_path": "O",
    "smiles": "O",
    "method": "B3LYP",
    "basis": "def2-SVP",
    "charge": 0,
    "spin_multiplicity": 1,
    "dispersion": "D3",
    "use_gpu": true,
    "use_xtb_preopt": true,
    "use_alchemi_prescreen": false,
    "n_conformers": 5,
    "compute_resp": false
  },
  "job_name": "Geometry_Optimization",
  "experimentName": "prime"
}
```

Call `boltzmann_submit` with `job_name="Geometry_Optimization"`, the
`experimentData` object as `experiment_data`, and the confirmed top-level name
as `experiment_name`. Submit exactly once, retain the returned `doc_id`, and
poll it with `boltzmann_status` using the same job name.

Before submitting, verify that charge and spin multiplicity are chemically
consistent with the supplied molecule. Do not silently convert
`spin_multiplicity` to a string, omit either molecule key, or replace the
selected functional, basis, dispersion, or execution settings with defaults.

**Fetch/output contract not yet supplied:** Inspect the terminal status payload
before identifying output keys or downloads. Do not claim an optimized
structure, convergence, RESP charges, or a conformer count until the returned
artifacts and metadata confirm them.

---

## HOMO-LUMO & Reactivity Descriptors

Calculate global HOMO-LUMO/reactivity descriptors and optionally atom-local
Fukui descriptors for one molecule.

| Field | Value |
|---|---|
| **job_name** | `Reactivity_Descriptors_Combined` |
| **experimentName** | Required user-confirmed unique name, passed at the top level |
| **task selector** | Exact `TASK_NAME` value: `homo_lumo_combined` |
| **input status** | Exact supplied UI/API schema documented; terminal output remains unverified |

Pass these fields inside `experimentData`:

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `TASK_NAME` | string | yes | Must be exactly `homo_lumo_combined`. Preserve uppercase field spelling. |
| `molecule_path` | string | yes | One uploaded molecule file path (`.xyz`, `.cif`, `.sdf`, or `.gjf`) or one validated SMILES string. Do not add a separate `smiles` key. |
| `method` | string | yes | `B3LYP`, `PBE`, `PBE0`, `M06-2X`, `M06-L`, `wB97X-D`, `wB97X-D3`, `wB97M-V`, `HF`, `LDA`, `TPSS`, `TPSSh`, or `CAM-B3LYP`. |
| `basis` | string | yes | `def2-SVP`, `def2-TZVP`, `def2-TZVPP`, `def2-QZVP`, `cc-pVDZ`, `cc-pVTZ`, `cc-pVQZ`, `STO-3G`, `6-31G`, `6-31G*`, `6-311G**`, `aug-cc-pVDZ`, or `aug-cc-pVTZ`. |
| `charge` | number | yes | Net molecular charge. Ask the user; values shown in the recording are not defaults. |
| `spin_multiplicity` | number | yes | Exact choice: `1`, `2`, or `3`. Confirm chemical consistency with charge and electron count. |
| `calculate_local` | boolean | yes | `true` requests local Fukui descriptors; `false` requests only the non-local result set. |
| `dispersion` | string | yes | Exact choice: `D3`, `D3BJ`, or `D4`. |

Call `boltzmann_submit` with
`job_name="Reactivity_Descriptors_Combined"`, the reviewed fields above as
`experiment_data`, and the user-confirmed name as `experiment_name`. Submit
once, retain the returned `doc_id`, and poll with `boltzmann_status` using the
same job name.

The recording establishes the exact input schema but not terminal artifacts or
columns. Inspect the complete terminal payload before reporting HOMO, LUMO,
gap, global reactivity, or Fukui values. A completed calculation does not by
itself establish method suitability, convergence, or experimental validity.

---

## 74. Single Point Energy

Calculate a molecule's electronic energy and electronic properties at a fixed
geometry without optimizing or moving its atoms. The platform uses
GPU-accelerated GPU4PySCF for rapid single-point DFT calculations. Use this
tool for energy ranking, conformer comparison, electronic-property profiling,
reaction-intermediate screening, charge/dipole analysis, method benchmarking,
or validation of an already optimized structure.

| Field | Value |
|-------|-------|
| **job_name** | `Single_Point_Energy` |
| **Mongo diagnostics collection** | `Single_Point_Energy` (verified sample record); pair with the returned experiment ID. |
| **experimentName** | Proven value: `Single_Point_Energy_test` |

**Inputs** (passed inside `experimentData`):

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `task_name` | string | yes | User-defined task label. Proven value: `"testing"`. This belongs inside `experimentData`; do not confuse it with the response's platform task metadata. |
| `molecule_path` | string | yes | Platform path to the fixed input geometry. Proven input is an uploaded XYZ path. UI-supported file extensions: `.xyz`, `.gjf`, `.cif`, and `.sdf`. Upload a local file first and pass the returned platform path. |
| `method` | string | yes | DFT functional. Proven value: `"B3LYP"`. UI options: `B3LYP`, `PBE`, `PBE0`, `M06-2X`, `wB97X-D`, `wB97M-V`, `HF`, `LDA`, `TPSS`, and `CAM-B3LYP`. |
| `basis` | string | yes | Basis set. Proven value: `"def2-TZVP"`. Documented options: `def2-SVP`, `def2-TZVP`, `def2-TZVPP`, `def2-QZVP`, `cc-pVDZ`, `cc-pVTZ`, `cc-pVQZ`, `STO-3G`, `6-31G`, `6-31G*`, `6-311G**`, `aug-cc-pVDZ`, and `aug-cc-pVTZ`. |
| `charge` | int | yes | Total formal charge of the whole modeled species. Proven value: `0`. Use `0` for neutral species and explicit positive/negative integers for ions. |
| `spin_multiplicity` | string | yes | **The verified API payload uses a string.** Proven value: `"1"`. Use `"1"` for singlet, `"2"` for doublet, or `"3"` for triplet; set radicals and metal systems explicitly. |
| `dispersion` | string | yes | Proven value: `"D3BJ"`. Exact UI options: `D3`, `D3BJ`, `D4`, or `None`. |
| `experiment_name` | string | yes | Pass as the third argument to `submit_request`; it becomes the top-level `experimentName`. Proven value: `"Single_Point_Energy_test"`. |

The UI also displays a SMILES input tab, but the supplied verified API schema
contains only `molecule_path`. Do not invent or send a `smiles` field until a
successful SMILES-mode submission payload is captured.

**Verified submit pattern:**

```python
job_name = "Single_Point_Energy"
experiment_data = {
    "task_name": "testing",
    "molecule_path": molecule_path,
    "method": "B3LYP",
    "basis": "def2-TZVP",
    "charge": 0,
    "spin_multiplicity": "1",
    "dispersion": "D3BJ",
}
doc_id = submit_request(
    experiment_data,
    job_name,
    "Single_Point_Energy_test",
    token=bearer_token,
    conv_id=conv_id,
)
result = fetch_status(
    job_name,
    doc_id,
    token=bearer_token,
    conv_id=conv_id,
    output_folder=str(result_dir),
)
```

**Method-selection guidance:**

- General neutral organics: `B3LYP` or `PBE0`.
- Noncovalent complexes: `wB97X-D` or `wB97M-V`.
- Reaction energetics/barriers: `M06-2X`, `PBE0`, or `wB97X-D`.
- Charge-transfer/orbital-sensitive cases: `CAM-B3LYP` or `wB97X-D`.
- Very large screens: `PBE` or `B3LYP`, then refine selected candidates.
- Treat `HF` as a reference/rough comparison and `LDA` as a legacy baseline.

**Basis-selection guidance:**

- Fast routine screening: `def2-SVP`.
- Final ranking of selected candidates: `def2-TZVP`.
- Higher-accuracy small-system refinement: `def2-TZVPP`.
- Anions/diffuse density: `aug-cc-pVDZ` or `aug-cc-pVTZ`.
- Use `STO-3G` only for sanity checks; reserve quadruple-zeta choices for
  small benchmark calculations.

**Comparison rules:** Compare total energies only across calculations using
the same functional, basis, charge, and comparable spin multiplicity. Use a
consistent protocol across conformers or reaction intermediates. Absolute
energies alone are less informative than consistently calculated relative
energies.

**Expected result content from the product documentation:** total energy in
Hartree, eV, kcal/mol, and kJ/mol; HOMO and LUMO energies and their gap;
Mulliken and Hirshfeld atomic charges; dipole moment and optional
polarizability; SCF convergence, iteration count, wall time, molecule formula,
atom/electron/basis-function counts, charge, functional, and basis set. The UI
shows the unchanged fixed geometry and supports JSON, CSV, XYZ, and SDF
exports. Although the UI screenshot labels the viewer “Optimized Structure,”
Single Point Energy must not be described as performing geometry optimization.

Interpretation guardrails:

- Lower total energy generally indicates greater relative stability only for
  consistently computed comparable structures.
- HOMO and LUMO trends describe donating/accepting tendencies; a smaller gap
  often suggests greater reactivity, but is not a standalone stability proof.
- Atomic charges and dipoles are method-dependent descriptors.
- Always verify SCF convergence before interpreting the results.
- Do not claim optimized stability unless the supplied input geometry was
  independently optimized and that provenance is available.

**Fetch/output contract not yet verified:** No submit response or completed
fetch payload was supplied. Do not invent an `OutputData` key or download
shape. Poll with `job_name="Single_Point_Energy"` and the returned `docId`,
then inspect the first terminal payload before adding this tool to the Output
Data Key Reference.

---

<!-- csv-additional-tools:start -->

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
