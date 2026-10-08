# Paired-antibody evidence and integration workflow

Use for comparing existing therapeutic antibodies through curated sequences, executable calculations, deposited structures, and primary literature. This is not de novo antibody generation or experimental validation.

## 1. Retrieve and identify the antigen reference

Discover tools by biological function and inspect schemas before execution. A molecular-entity retrieval capability such as `pdbe_get_entry_molecules({"pdb_id": PDB_ID})` can return entity IDs, molecule names, organisms, sequences, lengths, and chains.

Identify the receptor separately from its ligand using returned molecule names and entity IDs. Report database-returned sequence lengths as retrieved metadata, not as calculations or counts of resolved residues. Do not call molecular records downloaded coordinates. Do not relabel a receptor–ligand structure as an antibody–receptor complex.

## 2. Retrieve exact therapeutic pairs

Use a curated therapeutic-record capability such as `TheraSAbDab_get_therapeutic_sequences({"name": INN})`. Require the returned `matched` and `therapeutic.inn_name` to match the requested therapeutic; stop that antibody branch if the match is absent or different.

Assign stable sequence references per antibody and field, for example `A-VH = data.therapeutic.heavy1` and `A-VL = data.therapeutic.light1`. Keep them paired and preserve the strings exactly. The therapeutic's Whole mAb format does not make these variable-domain fields full-length chains. Retain target and raw structural-coverage tokens, including which source identity tier supplied each token.

## 3. Transfer sequences to executable calculations

For each returned VH and VL, execute a protein physicochemical calculator and a cysteine-counting operation separately. Validated operation shapes, subject to freshly inspected schemas, are:

- `ProtParam_calculate({"sequence": S})`
- `Sequence_count_residues({"operation":"count_residues", "residue":"C", "sequence": S})`

Pass the actual sequence, not an accession that triggers an independent refetch. Compare every submitted `sequence` argument against its labeled upstream field; disclose any normalization and do not silently trim or concatenate domains. Parallelize independent chain calculations while preserving their labels. Cross-check the tools' reported lengths and cysteine counts, but do not treat matching lengths as proof of sequence equality. Claim machine-verified equality or a checksum only if such verification actually ran.

Report one row per antibody/domain: source field, length, molecular weight in Da, pI, GRAVY, cysteine count, and 1-based positions. Preserve unavailable fields as missing. Cysteine counts do not confirm disulfide connectivity; pI, GRAVY, and instability index do not establish measured solubility, melting temperature, or developability.

## 4. Select and verify structural evidence

Extract candidate PDB IDs from the curated structural tokens by taking the substring before the chain delimiter. Preserve the source tier separately; do not promote a 99% reference to an exact match. Verify the actual receptor and antibody rather than automatically choosing the highest-identity reference, which may be an unbound antibody.

Retrieve metadata and molecular annotations with compatible independent capabilities, such as:

- `RCSBGraphQL_get_structure_summary({"pdb_ids": comma_separated_ids})`
- `pdbe_get_entry_molecules({"pdb_id": returned_id})`

Match returned metadata rows by PDB ID, not array position. Verify antibody identity through returned molecule names and receptor identity through its annotations. Report Fab or domain constructs distinctly from intact therapeutics and distinguish antigen constructs of different lengths.

Keep author-chain IDs (`in_chains`) separate from structural asymmetry IDs (`in_struct_asyms`); mixing these namespaces can assign the wrong heavy, light, or antigen chain. Do not infer which antigen copy contacts which Fab merely from lists of chains. Preserve pairing annotations when supplied by the curated reference.

If an optional annotation source errors or returns HTML instead of structured data, report the actual error and stop that branch. Independently retrieved metadata remains usable; never fabricate missing CDR or affinity annotations. Do not persist a transient endpoint failure as a permanent tool limitation.

## 5. Transfer structural citations to literature

Read `citation_pubmed_id` from the row matched to the selected PDB ID and pass that exact returned identifier to `PubMed_get_article`. Verify the returned PMID. Retrieve metadata and abstracts before summarizing findings; label full text unperformed unless it was actually retrieved. Preserve disagreements between current structural metadata and publication abstracts, including resolution differences, without inventing an explanation or silently replacing one value.

## 6. Compare and audit

Separate retrieved facts, executable calculations, interpretation, and missing evidence. Finish with a chain-property table, structure/literature evidence table, and explicit input/output handoffs. Do not rank binding strength from pI, GRAVY, crystal resolution, or source identity tier. Explain mutation-specific findings within the scope of the retrieved abstract rather than presenting them as universal superiority.

For capability-only stages, inspect definitions without invoking scientific execution. Distinguish existing CDR/PTM/affinity annotations from new sequence annotation or prediction, single-protein folding from antibody–antigen complex prediction, and package information or deposited trajectories from MD execution. Report required inputs and untested access honestly. Say not found in these searches rather than confirmed unavailable; never replace protein operations with small-molecule tools.
