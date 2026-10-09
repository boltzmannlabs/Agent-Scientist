# Quantum Chemistry

Domain: Density Functional Theory

This module was selected by the server. Use only the exact contracts below.

## 73. Single Point Energy

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
