<!-- canonical-contracts:start -->
> Request fields and catalog status: `../tool-contracts.v1.json`.
> File rules: `../file-input-contracts.v1.json`. Limits: `../input-limits.v1.json`.
> Missing detailed file rules mean partial validation, not a submission ban.
> Known invalid inputs and explicitly blocked tools still stop. Historical output
> verification is separate from request readiness; report uncertainty honestly.
<!-- canonical-contracts:end -->

# Molecular Dynamics

Domain: Molecular Dynamics

This module was selected by the server. Use only the exact contracts below.

## MDS OpenMM

Run a molecular-dynamics simulation with the platform's OpenMM workflow.

| Field | Value |
|---|---|
| **job_name** | `MDS_openMM` |
| **experimentName** | Required user-confirmed unique name, passed at the top level |
| **input status** | Supplied schema documented; terminal result remains unverified |

### Inputs

Pass these fields inside `experimentData`. Field names and capitalization are
part of the API contract and must be preserved exactly.

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `Complex_pdb` | string | conditional | Platform storage path for an uploaded complex PDB. Use this instead of separate protein and ligand PDBs. |
| `Protein_PDB_file_name` | string | conditional | Platform storage path for an uploaded `.pdb` protein file. Required with `Ligand_PDB_file_name` when `Complex_pdb` is not supplied. |
| `Ligand_PDB_file_name` | string | conditional | Platform storage path for an uploaded `.pdb` ligand file. Required with `Protein_PDB_file_name` when `Complex_pdb` is not supplied. |
| `Pressure` | number | yes | Simulation pressure in bar. Ask the user; do not copy a sample value. |
| `Temperature` | number | yes | Simulation temperature in kelvin. Ask the user; do not copy a sample value. |
| `Time` | number | yes | Production time in nanoseconds. Ask the user; do not copy a sample value. |
| `Water_type` | string | yes | Exact value: `TIP3P` or `OPC`. |
| `Force_field` | string | yes | Exact value: `ff19SB` or `ff14SB`. |
| `Ions` | string | yes | Exact value: `K+` or `Cl-`. Preserve this spelling and case. |
| `Ligand_Force_field` | string | no | Optional ligand force-field value supplied by the user. No enum was supplied; do not invent one. |
| `dcd_file` | string | yes | Exact value: `YES` or `NO`. |
| `Force_constant` | number | yes | User-confirmed restraint force constant. No unit or valid range was supplied; do not infer either. |

The three structure inputs form two supported alternatives: one uploaded
complex PDB, or an uploaded protein PDB plus an uploaded ligand PDB. Never send
local filesystem paths; upload the selected file and use the returned platform
storage path. Do not fabricate a ligand, split a complex, or silently choose an
input alternative.

The following lower-level form keys are not this submission contract and must
not be sent in `experimentData`: `uploadpdb`, `uploadligandpdb`,
`productiontime`, `forcefield`, `ions`, `forceconstant`, `trajectory`, and
`watertypeopenmm`.

### Submission

Call `boltzmann_submit` with `job_name="MDS_openMM"`, the reviewed fields above
as `experiment_data`, and the user-confirmed top-level name as
`experiment_name`. Submit exactly once, retain the returned `doc_id`, and poll
with `boltzmann_status` using the same job name. The existing OpenMM timeout is
conservative because runtime depends on the system and requested production
time.

### Output and scientific guardrails

The supplied schema establishes the input contract only. Inspect the terminal
status payload and downloaded artifacts before reporting completion. Do not
claim that a trajectory, equilibrated structure, energy trace, or requested
simulation duration exists until the returned files and metadata confirm it.

Before submission, confirm that the selected force field, water model, ions,
thermodynamic settings, restraint force constant, and ligand parameterization
are suitable for the system. A successfully accepted or completed job does not
establish physical validity, equilibration, convergence, or reproducibility.

---

## MDS Gromacs

Run a protein-ligand molecular-dynamics simulation with the platform's Gromacs
workflow.

| Field | Value |
|---|---|
| **job_name** | `MDS_Gromacs` |
| **experimentName** | Required user-confirmed unique name, passed at the top level |
| **input status** | Supplied schema documented; earlier live attempts reached a worker failure, so terminal results remain unverified |

### Inputs

Pass these exact fields inside `experimentData`. Preserve capitalization,
spaces, and the backend typo `temparature`.

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `force_field` | string | yes | Exact value: `amber` or `charmm36`. |
| `Protein_PDB_file` | string | yes | Platform storage path returned after uploading a protein `.pdb` file. |
| `Ligand_PDB_file` | string | yes | Platform storage path returned after uploading a ligand `.pdb` file. |
| `Stream_str_file` | string | conditional | Platform storage path for the uploaded STR file required when `force_field` is `charmm36`; omit for `amber` unless the platform explicitly requires it. |
| `Time` | number | yes | Total production time in picoseconds. Ask the user; do not copy a screenshot value. |
| `XTC Trajectory File` | string | no | Exact value: `YES` or `NO`. The spaces and capitalization are part of the supplied wire key. |
| `temparature` | number | yes | Simulation temperature. Preserve the backend misspelling; do not send `temperature`. |
| `pressure` | number | yes | Simulation pressure. Ask the user; do not copy a screenshot value. |
| `water_type` | string | yes | Exact value: `TIP3P`, `SPC`, `TIP4P`, `TIP5P`, or `TIP4PEW`. |
| `snaptime` | number | yes | Snapshot interval in picoseconds. Ask the user; do not copy a screenshot value. |

Never send local filesystem paths. Upload every selected input and use the
returned platform storage path. Confirm that the protein and ligand structures
belong to the same prepared complex. Do not silently choose thermodynamic
settings, simulation duration, snapshot interval, water model, or force field.

Call `boltzmann_submit` with `job_name="MDS_Gromacs"`, the reviewed fields as
`experiment_data`, and the user-confirmed top-level `experiment_name`. Submit
exactly once, retain the returned `doc_id`, and poll with `boltzmann_status`
using the same job name.

### Verification status and guardrails

Earlier live submissions were accepted but ended with `Failed to generate
output`. The supplied schema corrects and documents the request shape, but does
not prove that the worker has been repaired. Warn the user before a
credit-spending submission and do not retry automatically. Inspect terminal
status and returned artifacts before claiming a completed trajectory or
simulation duration.

Confirm force-field compatibility and ligand parameterization before running.
A completed job does not establish equilibration, convergence, physical
validity, or reproducibility.
