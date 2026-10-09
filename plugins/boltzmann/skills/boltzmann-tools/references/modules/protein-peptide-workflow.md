# Peptide Workflow Handoffs

Domain: Protein Engineering

This module supports multi-stage peptide workflows that convert FASTA
sequences to SMILES, join property results, validate predicted structures, or
dock peptide structures. It provides local handoff rules and does not define a new Boltzmann platform job.

## Candidate identity

Create a stable manifest as soon as candidates exist. Preserve at least:

```text
candidate_id,sequence,role,generation_score,smiles,structure_path,
docking_result_path,status,warnings
```

Join independent outputs by `candidate_id` plus the exact sequence. Never join
independent tool outputs by row number alone. Keep requested, returned,
duplicate, invalid, and retained counts separate, and never fabricate missing
candidates or automatically submit a top-up job.

## FASTA to SMILES

Use the installed `p2smi==1.1.1` adapter at
`scripts/peptide_fasta_to_smiles.py`; never construct peptide SMILES manually.
The default output columns are `Sequence_ID,Sequence,SMILES`. Before upload,
verify that record counts and order match, IDs are unique, sequences are
unchanged, and every SMILES parses successfully. Preserve the raw `.p2smi`
output beside the CSV.

Peptiverse does not accept this multi-column identity table. Preserve it as the
candidate manifest, then call `prepare_peptiverse_input_csv` to create a
separate file with exactly one lowercase `smiles` column (or one lowercase
`sequences` column for a sequence-native run). Validate and upload that projected
file. Never drop the manifest: reconcile returned properties to candidates by
the exact submitted value after validating result count and order.

## Prioritization and structure handoff

Use only properties returned by a selected validated contract. State the
direction, weight, missing-value policy, and tie-breaker for every ranking
criterion. Preserve raw values and units.

Before downstream docking, verify each predicted structure for parseability,
coordinates, chain assignment, represented sequence, residue count, and its
associated confidence fields. Exclude invalid, truncated, mismatched, or empty
structures without hiding them from the audit manifest.

## Docking handoff

Never modify source structures in place. Create prepared copies and record the
source-to-prepared mapping. Compare docking scores only across runs with the
same backend, receptor preparation, ligand preparation, and configuration.
Preserve raw results and do not infer a ranking column or direction unless the
selected docking contract proves it.
