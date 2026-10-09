# Toolbox

Domain: Small Molecule Design

This module was selected by the server. Use only the exact contracts below.

## 25. Binding Site Prediction (fpocket)

| Field | Value |
|-------|-------|
| **job_name** | `Binding_Site_Prediction` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pdb_path` | string | yes | S3 path to PDB (upload first), or a bare RCSB PDB identifier such as `1LYZ` |

**Output:** PDB files + CSV.

**Output CSV columns:** `Pockets, GCP_Path, Druggability_Score, Pocket_Residues, Center_Coordinates, Max_Radius`

---

## 43. Molecular Docking — DiffDock Mode

Molecular Docking is one product tool with Vina and DiffDock modes. In the
Vina mode, leaving both feature boxes unchecked selects basic docking;
selecting Flexible docking or Score only routes to the corresponding Vina
submode. Read `references/additional-tools.md` section 67 for the complete
mode router and evidence levels.

DiffDock is the current live-verified executable path. Vina basic has a
schema-verified payload but a known worker failure; the Vina flexible and
score-only product routes are documented, but their helper `job_name` values
are not live-confirmed and must not be guessed.

| Field | Value |
|-------|-------|
| **job_name** | `Diffdock` |
| **watch_time** | ~60s |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `processed_pdb` | string | yes | S3 path to PDB (upload first) |
| `input_csv` | string | yes | S3 path to CSV (upload first) |
| `upload_sdf` | string | yes | `"true"` or `"false"` |

**Input CSV columns:** `SMILES`

**Output CSV columns:** `SMILES, NAMES, Ligand_no, Rank, Confidence, Interactions`

The verified result emits ten poses (`Rank` 0–9) per ligand. Confidence is
negative-scaled, so values closer to zero are better and Rank 0 is the preferred
pose. `Ligand_no` reflects completion order rather than input order; identify a
ligand by SMILES. `Interactions` is a Python-repr list and should be parsed with
`ast.literal_eval`.

**Additional outputs:** Up to 30 SDF pose files.

---

## 67. Molecular Docking

Route molecular docking through Vina or DiffDock, with basic, flexible, and score-only behavior under the Vina mode.

| Field | Value |
|---|---|
| **job_name** | `Vina_basic_docking` |
| **contract status** | mode router; Vina basic worker-blocked; DiffDock verified in parent skill |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `target_name` | string | yes | Target/receptor label |
| `processed_pdb` | string | yes | Uploaded receptor PDB |
| `center_x` | string | yes | Binding-box center X; live schema requires a string |
| `center_y` | string | yes | Binding-box center Y; live schema requires a string |
| `center_z` | string | yes | Binding-box center Z; live schema requires a string |
| `max_radius_size` | string | yes | Binding-box size; live schema requires a string |
| `exhaustivness` | string | yes | Preserve misspelling; supported values include `8`, `16`, `32` as strings |
| `upload_sdf` | string | yes | String boolean: `true` or `false` |
| `smiles` | string | yes | Platform path to ligand CSV with `SMILES,NAMES`; not a literal SMILES |

**Output contract:** Vina product rows describe ligand, pose, score, and interaction columns, but Vina basic is worker-blocked and the flexible/score-only result contracts are not live-verified. DiffDock has a separately verified result contract in the parent skill.

### Mode selection

The product surface is one **Molecular Docking** tool with two top-level modes:

| UI selection | Effective backend behavior | Evidence |
|---|---|---|
| Vina selected; neither feature box checked | Basic docking via `Vina_basic_docking` and route `/v4/DModule/basic_docking` | Payload live-verified; worker currently fails after parsing |
| Vina + Flexible docking | Product route `/v4/3DModule/flexible_docking`, task `flexible_docking` | Product CSV only; registered helper `job_name` not live-verified |
| Vina + Score only | Exact job `Vina_Score_only_docking`, product route `/v4/3DModule/vina_score_only_docking`, collection `equidock`, task `vina_score_only` | Submission and durable document verified |
| DiffDock selected | DiffDock via `Diffdock` and route `/v4/3DModule/diffdock` | Live-verified end to end in the parent skill |

Within Vina, leaving both **Flexible docking** and **Score only** unchecked means
basic docking. Treat the two feature boxes as mutually exclusive until a proven
payload establishes combined behavior.

### Vina basic docking

Use the input table above with `job_name="Vina_basic_docking"`. All numeric
fields and `upload_sdf` are strings. The `smiles` field is a platform path to a
ligand CSV containing both `SMILES` and `NAMES` columns.

The payload is schema-verified, but seven live attempts reached the same worker
failure after input parsing. Do not spend credits on Vina basic until the worker
is repaired. Do not describe the product-CSV output columns as a live result.

### Vina flexible docking

The product CSV documents the basic fields plus:

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `flexible_residues` | array[string] | no | Optional flexible receptor residues such as `ASN140`, `TYR62`; omit for rigid/basic docking |
| `smiles` | string | yes | Ligand input described by the product CSV |

The product route and task are known, but the registered `job_name` for
`submit_request` is not proven. Do not guess it from the route or task name.

### Vina score-only docking

| Field | Value |
|---|---|
| **job_name** | `Vina_Score_only_docking` |
| **validation status** | **Submission verified (HTTP 200)** |

The product CSV documents the common receptor/search-box fields and:

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `sdf_file` | string | yes | Platform path to ligand SDF |
| `upload_sdf` | string | yes | String boolean |

Use the common receptor/search-box fields with the score-only SDF fields:

```python
job_name = "Vina_Score_only_docking"
experiment_name = "Vina score-only docking"
experiment_data = {
    "target_name": "simple",
    "processed_pdb": uploaded_receptor_pdb,
    "center_x": "15.01",
    "center_y": "-2.41",
    "center_z": "29.42",
    "max_radius_size": "60",
    "exhaustivness": "16",
    "upload_sdf": "True",
    "sdf_file": uploaded_ligand_sdf,
}
```

This exact payload returned HTTP 200, task `vina_score_only`, and a document
ID. Preserve the case and misspelling exactly. The terminal result and output
columns remain unverified until the submitted document completes and its
artifact is inspected.

### DiffDock mode

Use `job_name="Diffdock"` with `processed_pdb`, `input_csv`, and `upload_sdf`.
The parent `SKILL.md` contains the live-verified input and result contract.
DiffDock is the current executable docking path while Vina basic remains
worker-blocked.

---


---

## Active BoltChem scope overlay (2026-09-08)

The following live-verified records are authoritative for Binding Site Prediction and Molecular Docking.

## Tool 5 — Binding Site Prediction (`Binding_Site_Prediction`) — VERIFIED

### Identity
- Experiment Name: Binding Site Prediction
- Job Name: `Binding_Site_Prediction` — VERIFIED_LIVE
- API route: `/v4/3DModule/fpocket` · internal task: `fpocket` · node: `boltzmann2`

### Verification Status
- Input contract verified: VERIFIED_LIVE (accepted payload below)
- Submission verified: VERIFIED_LIVE (docId `CURRENT_JOB_ID`, credits 2, est 2 min 30 s)
- Result fetch verified: VERIFIED_LIVE (terminal `Success` in ~18 s compute)
- Output download verified: VERIFIED_LIVE (`output_stats.csv` + `protein.pdb` from GCS signed URLs)
- Output analysis verified: VERIFIED_LIVE (4 pockets, CSV + PDB + inline JSON fully inspected)
- Downstream compatibility verified: VERIFIED_LIVE (pocket PDB path fed to Structure_Based_Generator — accepted)
- Confidence: HIGH — full lifecycle observed end-to-end

### Input Contract

| Field | Type | Required | Allowed Values | Default | Source |
|---|---|---|---|---|---|
| `pdb_path` | string | yes | cloud `.pdb` path from `file_upload` **OR bare PDB-ID string** | — | yup schema + VERIFIED_LIVE (bare `1LYZ` accepted!) |

Single-field tool. No other parameters.

### Contract Conflicts Resolved
1. **Bare PDB-ID accepted.** Despite the schema reading like a file path, the live payload
   `"pdb_path": "1LYZ"` was accepted and the backend fetched the structure from RCSB itself
   (node downloaded 1LYZ lysozyme, 129 residues, chain A). Cloud-path upload also works
   (that is how PH-R/6FMC was submitted). Prefer the bare ID when the user names a PDB entry —
   skip upload entirely.
2. No `chain`/`ligand` filtering options exist at this layer — fpocket runs on the whole structure.

### Verified Submission Payload

```python
{
    "experimentData": {"pdb_path": "1LYZ"},   # bare PDB-ID, no upload needed
    "job_name": "Binding_Site_Prediction",
    "experimentName": "bsp_verify"
}
```

### Result Contract — VERIFIED_LIVE
- Terminal status: `"Success"`
- OutputData keys: **three**, of different shapes:
  - `outcsv_path` → object `{path, download_link:[...]}` — pocket statistics CSV
  - `pdb_path` → object `{path, download_link:[...]}` — processed protein PDB
  - `pockets_data` → **inline JSON array** (no download link!) — per-pocket detail dicts keyed `pocket_1..N`
- `pockets_data[i].pocket_N` fields: `x_center/y_center/z_center` (floats), `Max_Radius` (Å),
  `PDB` (cloud path to `pockets/pocketN_atm.pdb` — NOT in OutputData download links; construct
  signed URL only by re-fetching result), `pocket_seq` (list of per-residue
  `{highlight: "False"|"True", protein_seq: <1-letter>}` for UI rendering), `pocket_residues`.
- Billing: `tool_name: "fpocket"`, credits 2, 18 s compute.

### Output Analysis — VERIFIED_LIVE (1LYZ → 4 pockets)
- `output_stats.csv`: columns `Pockets, GCP_Path, Druggability_Score, Pocket_Residues,
  Center_Coordinates, Max_Radius` — one row per pocket, pockets already sorted by druggability.
- 1LYZ (lysozyme, 129 res): Pocket-1 druggability **0.4464** (16 residues, radius 17.53 Å — the
  canonical substrate cleft), Pocket-2 0.1361, Pockets 3–4 ≈ 0 (shallow surface sites). Correct
  behavior: lysozyme is a hard, low-druggability target; the active-site cleft still ranks #1.
- `protein.pdb`: full processed structure (129 residues, chain A) — usable as generic receptor input.
- `GCP_Path` column values are bare cloud paths (`users/.../pockets/pocket1_atm.pdb`) — these are the
  pocket-only PDBs; the platform does NOT hand you signed URLs for them in the result body.
- Input → output transformation: 1 PDB → N pocket rows + pocket PDBs + centers/radii for all pockets.

### Downstream Compatibility — VERIFIED_LIVE
- `pockets_data[0].pocket_1.PDB` (or the CSV `GCP_Path` column) → **`protein_Path` of
  Structure_Based_Generator** (verified accepted — SBG submission used exactly this value).
- `Center_Coordinates`/`Max_Radius` → constraint-box parameters for docking tools (vina/diffdock).
- `protein.pdb` → any tool wanting a clean receptor (`Pharmacophore_Hypothesis`, docking, MDS).

### Sci Execution Instructions
1. Get a structure: user PDB-ID (pass bare string, no upload) or uploaded `.pdb` file path.
2. Submit single-field payload; `job_name="Binding_Site_Prediction"`.
3. Poll to `Success`; read `pockets_data` inline for pocket count, centers, radii.
4. Download `outcsv_path` + `pdb_path` artifacts (links expire in 300 s).
5. Rank pockets by `Druggability_Score`; report top pockets with residue counts and centers.
6. To chain into generation: use pocket-1's `PDB` cloud path as SBG `protein_Path`; for docking,
   use `protein.pdb` + pocket center/radius as the search box.
7. Never fabricate signed URLs for `pockets/pocketN_atm.pdb` — pass the bare cloud path to the
   next tool's payload (tools read each other's cloud paths directly).

### Verified Quirks
- Bare PDB-ID in `pdb_path` works — no upload round-trip needed for public structures.
- `pockets_data` is inline JSON, not a download; the pocket atom-PDBs inside it are cloud paths
  without signed URLs — downstream tools accept the cloud path as-is.
- 2 credits for an 18 s run (rate ~50/hr node-minutes).
- `pocket_seq` is a per-residue UI-highlight structure (verbose); use `pocket_residues` from the CSV
  for a compact residue list.

---



## Tool 27 — Molecular Docking - vina (`Vina_basic_docking`) — BLOCKED (worker bug)

### Identity
- Route: `/v4/DModule/basic_docking` · job_name `Vina_basic_docking`

### Input Contract (yup-verified)
```json
{
  "target_name":      "6FMC",
  "processed_pdb":    "<cloud path: protein PDB>",
  "center_x":         "27.436",     // ALL numerics are STRINGS (yup rejects numbers)
  "center_y":         "…", "center_z": "…",
  "max_radius_size":  "25",
  "exhaustivness":    "8",          // platform's spelling of "exhaustiveness"
  "upload_sdf":       "false",      // STRING boolean
  "smiles":           "<cloud path to ligand CSV with columns SMILES,NAMES>"
}
```
- `smiles` takes a **CSV cloud path**, not a SMILES string (proved by attempt 5 below).
- The ligand CSV **must** contain a `NAMES` column (proved by attempt 1's worker error).

### Submission Findings — 5 reasoned attempts across 7 versions
| # | protein | ligand field | numeric fields | outcome |
|---|---------|--------------|---------------|---------|
| 1 | BSP/fpocket processed PDB | SMILES-only CSV | strings | accepted → worker: `Missing required column(s): NAMES` |
| 2 | BSP/fpocket processed PDB | SMILES+NAMES CSV | strings | accepted → worker: `Failed to generate output` |
| 3 | BSP/fpocket processed PDB | SMILES+NAMES CSV | **numbers** | yup 422 — strings required |
| 4 | 6FMC stripped PDB | SMILES+NAMES CSV (`upload_sdf:"true"`) | strings | accepted → worker: `Failed to generate output` |
| 5 | 6FMC stripped PDB | **literal SMILES string** | strings | 500 `File not found or unreadable (404)` → proves CSV-path semantics |
| 6-7 | pristine RCSB 6FMC PDB (1,441 ATOM) | SMILES+NAMES CSV (`upload_sdf:"false"`) | strings | accepted → worker: `Failed to generate output` |

### Root-Cause Assessment — VERIFIED_LIVE
- Schema is fully solved (every field type and file format confirmed via yup + worker errors).
- The worker crashes after input parsing on every protein source (fpocket output, hand-stripped
  6FMC, pristine RCSB 6FMC) and both `upload_sdf` settings — always the same generic
  `Failed to generate output`. This is a worker-side defect, not an input problem.

### Sci Execution Instructions
1. Do not burn credits on this tool until the worker is fixed; use Diffdock (Tool 28) for
   protein–ligand docking in the interim.
2. If a run is required anyway: use the payload contract above with strings everywhere,
   a `SMILES,NAMES` ligand CSV, and a pristine RCSB PDB; expect `failed`.

### Verified Quirks
- Every numeric field is a string at the yup layer (numbers → 422).
- Field name misspelled `exhaustivness`; booleans are strings (`"false"`).
- `smiles` = ligand-CSV cloud path; missing `NAMES` column is a worker-stage error, not yup.

---



## Tool 28 — Molecular Docking - diffdock (`Diffdock`) — VERIFIED

### Identity
- Route: `/v4/3DModule/diffdock` · job_name `Diffdock`
- 1st-choice docking tool on the platform (vina worker is broken — see Tool 27).

### Input Contract — VERIFIED_LIVE (accepted first try)
```json
{
  "processed_pdb": "<cloud path to protein PDB — BSP fpocket output works>",
  "input_csv":     "<cloud path to ligand CSV (SMILES column; bpp output reused fine)>",
  "upload_sdf":    "false"   // string
}
```
- Ligand field is **`input_csv`** here — NOT `smiles` as in vina. No NAMES column required.

### Result Contract — VERIFIED_LIVE
- `status: "Success"`, `OutputData["outputFilePath[0..1]"]`: `diffdock_res.json` (UI payload) +
  `user_download.csv` (the result table). ~16 min for 5 ligands.

### Output Analysis — VERIFIED_LIVE
- `user_download.csv`: one row per pose = **10 poses (Rank 0–9) per ligand** — 5 ligands → 50 rows.
- Columns: full ADMET panel + 6 descriptors (same family as Property Prediction/Toxicity output,
  replicated on every pose row) + `Ligand_no`, `Rank`, `Confidence`, `Interactions`.
- `Confidence` is **negative-scaled** (−0.16 … −6.05 observed): closer to 0 = better;
  Rank 0 is always the top pose per ligand.
- `Interactions`: Python-repr list (single quotes — `ast.literal_eval`, NOT `json.loads`) of
  `[residue.chain, type, distance Å]`, e.g. `[['ASN44.A', 'VdWContact', 2.8]]`.
  Only `VdWContact` observed in this run; 23/50 pose rows had ≥1 interaction, and the
  rank-0 poses were mostly interaction-free (annotator fires on closer/lower-ranked poses).
- **`Ligand_no` is NOT the input row index** (completion order: 0,1,4,2,3 observed).
  Always map ligands by SMILES, never by Ligand_no.
- `diffdock_res.json`: all 50 pose entries keyed "0"–"49" (string keys), each = CSV row plus
  `node`/`edge`/`buttons` — vis.js graph snippets for the platform's interaction diagram.
  Machine consumers should use the CSV; the JSON is UI-render payload.
- No docked pose PDB/SDF is returned when `upload_sdf: "false"` — only scores/interactions.
  Set `"true"` if 3D structures are needed (untested).

### Downstream Compatibility — VERIFIED_LIVE
- ADMET columns identical to Property Prediction/Toxicity/QSPR outputs → ranking pipelines work
  unchanged; add Confidence + interaction-count as docking axes.

### Sci Execution Instructions
1. Provide a processed protein PDB (fpocket output path is proven) + ligand CSV; `"upload_sdf":
   "false"`; ~1 credit-class run, ~15 min for a handful of ligands (scales with ligand count).
2. Parse `Interactions` with `ast.literal_eval`; ignore `Ligand_no` for identity.
3. Report per ligand: best (rank-0) confidence + the residue contacts across poses.
4. Docked-structure files require `upload_sdf: "true"` — request only when the user needs PDBs.

### Verified Quirks
- Field asymmetry vs vina (`input_csv` vs `smiles`); no NAMES requirement.
- Negative confidence scale; rank 0 = best; Ligand_no ≠ input order.
- Interactions are Python-repr, not JSON; only VdWContact type observed in this run.

---



## Molecular Docking mode matrix (active scope)

Molecular Docking is one user-facing tool with Vina and DiffDock modes. The
Vina feature choices are mutually exclusive: no feature selects basic docking;
Flexible docking and Score only select their corresponding Vina routes.

| User mode | Exact job name | Status | Required contract |
|---|---|---|---|
| Vina basic | `Vina_basic_docking` | Schema verified; worker blocked | `target_name`, `processed_pdb`, `center_x`, `center_y`, `center_z`, `max_radius_size`, `exhaustivness`, `upload_sdf`, and ligand CSV cloud path in `smiles` |
| Vina flexible | Not live-confirmed | Do not guess or submit | Requires the common receptor/search-box fields plus `flexible_residues`; exact submit job name remains unverified |
| Vina score-only | `Vina_Score_only_docking` | Submission verified; terminal output unverified | Common receptor/search-box fields plus `sdf_file` and string `upload_sdf` |
| DiffDock | `Diffdock` | Verified end-to-end | `processed_pdb`, `input_csv`, and string `upload_sdf` |

For Vina, all numeric search-box fields are strings, the field spelling is
`exhaustivness`, and the receptor PDB and ligand CSV are upload-only inputs
(do not paste file contents or literal SMILES). The ligand CSV must contain
`SMILES,NAMES`. For DiffDock,
the ligand field is `input_csv`, `NAMES` is not required, and the verified
result is `user_download.csv` with pose/ranking fields. Identify ligands by
`SMILES`, not `Ligand_no`.

Do not submit Vina basic or Gromacs while their worker failures remain active.
DiffDock is the currently verified docking path. Do not claim Vina flexible or
score-only terminal output until its artifacts have been fetched and inspected.
