# Protein sequence and structure recipes

Inspect current tool schemas before applying these recipes.

## Therapeutic antibody → separate domain calculations

1. Retrieve with `TheraSAbDab_get_therapeutic_sequences({"name": INN})`. Check `data.matched` and `data.therapeutic.inn_name`.
2. Use `heavy1` for VH and `light1` for VL. Preserve raw strings. Null `heavy2`/`light2` does not imply a missing primary pair.
3. For each sequence, separately call `ProtParam_calculate({"sequence": sequence})` and `Sequence_count_residues({"operation":"count_residues","sequence":sequence,"residue":"C"})`.
4. Map ProtParam `length`, `molecular_weight_da`, `isoelectric_point`, and `gravy` plus counter `count` into the table. Compare counter `sequence_length` with ProtParam `length`; cysteine positions are 1-based.
5. Identify the source field and unchanged input string for each row when provenance is requested.

Call these variable domains, not full-length chains: `Whole mAb` describes therapeutic format, not sequence-field extent. Preserve `struc100`, `struc99`, and `struc95to98` unchanged; their tiers describe identity to structural representatives, not percentages of intact-antibody coverage. Retain reported mass/pI conventions; do not interchange ProtParam average mass and Sequence_stats estimated monoisotopic mass.

## Reviewed protein search → canonical sequence → statistics

1. Use `UniProt_search` with gene, organism scope, and `reviewed:true`, such as `gene:ERBB2 AND taxonomy_id:9606 AND reviewed:true`. Check returned organism and gene identity.
2. Pass the selected `data.results[i].accession` into `UniProt_get_sequence_by_accession({"accession": accession})`; do not seed it from memory.
3. Pass the full returned sequence into `Sequence_stats({"operation":"stats","sequence":sequence})`. Omit `uniprot_id` so this exercises the sequence handoff rather than another retrieval.
4. Report retrieved accession/organism and calculated length, plus both handoffs. Prefix/suffix excerpts may identify a long sequence in the report, but disclose that the full string was submitted. Compare calculated and retrieved lengths when available.

## Protein sequence, localization, and functional annotations

1. Resolve the reviewed accession by gene and organism as above; verify organism, gene, and entry identity before presenting results.
2. For ToolUniverse retrieval, discover each missing capability separately and inspect its schema. `UniProt_get_function_by_accession` and `UniProt_get_subcellular_location_by_accession` accept `accession`; use the sequence operation above for the amino acid string. Do not substitute function prediction tools for existing curated annotations.
3. When the backend is unrestricted, a single GET of `https://rest.uniprot.org/uniprotkb/{accession}.json` can supply identity, `sequence`, `comments`, and processing `features`. Retain the raw response, but print only requested fields: complete feature arrays include extensive variants and structural annotations that swamp the output.
4. Extract FUNCTION and SUBCELLULAR LOCATION comments, including localization notes rather than only compartment names. Extract Signal, Propeptide, and Chain features when relevant; label the displayed sequence as precursor or mature chain and identify its isoform.
5. Verify `len(sequence["value"]) == sequence["length"]` programmatically and wrap the unchanged sequence at 60 residues for FASTA presentation. Return the full sequence when requested, not an excerpt. Prefer parsing the saved raw JSON over terminal transcripts; if recovering a JSON object followed by a log footer, use `json.JSONDecoder().raw_decode(text)` and inspect the remainder rather than treating the whole transcript as JSON.
6. Report accession and organism, complete sequence, localization, and concise functional annotations. Distinguish autocatalytic maturation from the mechanism acting on biological targets; membership in a protease family does not establish proteolytic cleavage of every target. Attribute annotations to the retrieved database and distinguish retrieval routes when more than one was used.

## PDB metadata and molecular composition

1. Retrieve method/resolution using `get_protein_metadata_by_pdb_id({"pdb_id": id})`. Avoid duplicate metadata calls unless fields are missing or independent verification was requested.
2. Use `pdbe_get_entry_molecules({"pdb_id": id})` for the molecular inventory, including protein chains, nonpolymers, and water. It returns a source URL and may normalize response keys to lowercase; retain the user's original identifier in the audit.
3. For detailed polymers, obtain IDs with `get_polymer_entity_ids_by_pdb_id`, then form returned `PDB_ENTITY` identifiers for `RCSBGraphQL_get_polymer_entity`. Match outputs by entity ID, not array order; batch results may reorder entities.
4. Use `RCSBData_get_nonpolymer_entity` only after discovering the relevant entity ID; do not guess IDs from polymer counts.
5. Distinguish Fab chains, intact antibody chains, and receptor extracellular domains. Include small molecules and solvent for complete composition; polymer counts alone omit components.
6. Disclose absent unit fields and other missing metadata. Neither a structure title nor its resolution provides quantitative affinity.
