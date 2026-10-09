# Optimization

Domain: Protein Engineering

This module was selected by the server. Use only the exact contracts below.

## Stability-Binding DDG

| Field | Value |
|---|---|
| **job_name** | `stability-binding-ddg` |
| **Mongo diagnostics collection** | `stabddg` (product mapping; not the submit job name) |
| **contract status** | Documented form; live execution not verified in this change |

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `pdb_path` | file | no | Upload `.pdb` coordinates; no pasted SMILES, sequence, or bare PDB ID. |
| `sequence` | string | yes | Protein sequence for the selected chain. |
| `chain` | string | yes | One uppercase letter; if a PDB is supplied, that chain must exist in it. |
| `mutations` | array | yes | Positive residue positions or ascending position ranges, e.g. `[1, 2, "8-15"]`. Integers and documented range strings are preserved. |
| `num_mutations` | string | yes | Requested mutation count; the API payload uses a string. |

The experiment name belongs to top-level `experimentName` through the existing
submission helper, not `experimentData.job_name`. The backend job is always
`stability-binding-ddg`, never the sample experiment label or `stabddg`.

Evidence: public submit-job form and operator recording
`Screen Recording 2026-09-25 045410.mp4`. The current form marks PDB upload
optional, superseding the older New_skills.md required-PDB description for
clarification. Do not impose a two-chain requirement absent from that form.
The random PDB-ID example in the recording is not evidence of ID support.
When a PDB is provided, the compulsory byte guard validates actual coordinates
and chain membership. No coordinate or sequence content is invented.

Product documentation advertises a CSV containing `id`, `Sequences`, and
`DDG_values`; inspect the real terminal payload and downloadable files before
claiming results. Use collection `stabddg` plus the returned experiment ID for
durable diagnostics. No output JSON key or scientific sign convention is
assumed from the input demo.

## 11. Random Controlled Mutagenesis

| Field | Value |
|-------|-------|
| **job_name** | `Random_Controlled_Mutagenesis` |

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `seq` | string | yes | Input sequence (string, NOT list) |
| `n_samples` | int | yes | Number of mutants |
| `file_format` | string | yes | `"csv"` only |
| `task_name` | string | yes | `"Mutagenesis"` |
| `indices` | array[int] | yes | Positions to mutate (e.g., `[5, 10]`) — must be array, not string |
| `mutaions_per_epoch` | int | yes | Number of mutations per round. **API TYPO: spell it `mutaions_per_epoch` (missing the "t")** — the backend rejects the correct spelling `mutations_per_epoch` with `Schema validation failed: Mutations per epoch is required`. The skill docs and most reference files will say `mutations_per_epoch` but the live API only accepts the misspelled form. |

**Output CSV columns:** `Unnamed: 0, Sequence_ID, Sequence, Length, Molecular_Weight, PI, Hydrophobic_Count, Acidic_count, Basic_count, Polar_Count, Others_Count, A..Y`

**Pitfall — per-sequence job, not batch:** `seq` is a single string. To produce N mutants for M parents, submit M separate jobs (one per parent). Each job returns `n_samples` mutant rows. A list in `seq` is rejected.

**Pitfall — tool can fail with "Failed to generate output" on some parents:** Means the parent sequence produced an invalid mutant (e.g., the round produced a residue not in the 20-AA alphabet, or hit a degeneracy). Expect ~1-10% failure rate across a batch. The doc_id is still returned — check `status` for `failed` and re-submit those parents individually (do NOT use local mutagenesis).

**Pitfall — platform queue is heavily loaded for this tool:** Jobs may stay `pending`, `queued`, or `running` for several minutes if the Boltzmann compute nodes are saturated. `fetch_status` checks every 5 seconds and continues until a terminal status arrives. Do not bypass the helper or automatically re-submit the job.

---

## 13. Directed Evolution (MLDE)

| Field | Value |
|-------|-------|
| **job_name** | `Insilico_Directed_Evolution` |
| **Mongo diagnostics collection** | `mlde` (verified sample record); pair with the returned experiment ID. |
| **returned task_name** | `mlde` — response metadata only; never use this value as `job_name` |
| **watch_time** | Long |

Use machine-learning-guided directed evolution to generate a focused mutant
library around selected residue positions and evaluate each sequence's
physicochemical properties.

**Inputs:**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `property_name` | string | yes | Exact enum: `Thermal_Stability_Protbert`, `Thermal_Stability_ESM`, `Solubility_ESM`, `Antigen_Antibody_binding`, or `CDR_Prediction` |
| `fasta_path` | string | yes | Protein input reference accepted by the NodeAPI. For a file, upload it first and pass the returned path. The UI also exposes Dataset, File, and Sequence modes, but alternate JSON field names for those modes are not yet verified. |
| `positions` | string | yes | Space-separated residue-position tokens, e.g. `"I61 N40"` or `"A187 G190"`. Do not convert this to an integer array or comma-separated numeric indexes. |
| `experiment_name` | string | yes | Pass as the third argument to `submit_request`; it becomes top-level `experimentName`, not a member of `experimentData`. |

**Verified submit pattern:**

```python
job_name = "Insilico_Directed_Evolution"
experiment_data = {
    "property_name": "Thermal_Stability_Protbert",
    "fasta_path": uploaded_fasta_path,
    "positions": "I61 N40",
}
doc_id = submit_request(
    experiment_data,
    job_name,
    "prime",
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

A successful submission returns HTTP 200 with `success: true`, a `docId`, and
`apiResponse: {task_name: "mlde", status: "queued", ...}`. Queued is not a
completed result; continue through `fetch_status` using the submit
`job_name` and returned `docId`.

**Expected result content from the product UI:** generated sequences plus
length, molecular weight, pI, hydrophobic, acidic, basic, polar, and other
residue counts; analysis includes aggregate length/hydrophobicity and a
multiple-sequence alignment.

**Fetch/output contract not yet verified:** Do not invent an `OutputData` key,
file extension, or download shape from the UI documentation. Inspect the first
terminal fetch payload and use only its actual `download_link` field. A sample
completed fetch response is required before hard-coding this tool into the
Output Data Key Reference.

---

## 38. ActSeek

Compare candidate structures with an active-site-annotated reference.

| Field | Value |
|---|---|
| **job_name** | `act_seek` |
| **contract status** | source-backed request contract |

**Inputs**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `input_path` | string | yes | Uploaded file: `.pdb`, `.zip` |
| `reference_path` | string | yes | Uploaded file: `.pdb` |
| `active_sites` | string | yes | Comma-separated residue identifiers, e.g. `105_A,224_A,187_A`; every identifier must exist in the reference/seed PDB. Never choose or invent sites. |

The design input may be one PDB or a ZIP of PDB structures; the reference is
one PDB. The submission guard validates coordinates and reference residues.

**Output contract:** `OutputData.datainfo.outputFilePath` (product CSV).

---
