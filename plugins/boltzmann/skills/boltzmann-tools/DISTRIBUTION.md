# Boltzmann workflow distribution

## Source and scope

Imported from the owner's authorized local Boltzmann plugin for this Agent
Scientist distribution. The executable connector, schemas, authorization and
onboarding were byte-identical to the repository version at review. This change
packages the missing knowledge, not a different execution or login system.

The registry describes 30 modules and 130 catalog entries at import time.
Entries include active, ignored, removed and on-hold states; active does not
mean scientifically validated, currently working, or authorized for an account.
Module-level blocked/parked/unverified constraints still take precedence.
The machine-contract scaffold explicitly retains `needs_audit` entries and is
not an executable payload specification. No fresh live research jobs were run
to certify the imported historical observations.

## Included and excluded

Included: the operative skill, every registered module, clarification catalogs,
file/limit contracts, public parameter evidence, collection mappings, BoltChem
contract overlay, status guidance, additional-tool descriptions, and the
referenced peptide FASTA-to-SMILES conversion script. The latter requires an
approved separate runtime with its documented dependencies; nothing executes
or installs merely because these files are present.

Excluded: credentials and authorization receipts; local config; caches; job
outputs; `.orig` backups; catalog-editing maintenance scripts; legacy monolithic
catalog and unreferenced local debugging/fallback/session-recovery notes.
These exclusions do not remove modules selected by the operative registry.

Historical user upload paths, local home paths, job/account IDs and signed
artifact URLs are replaced with clearly non-executable placeholders. Long
example biological sequences and public frontend sampleData/worker-route/output
path fields are omitted or replaced. Parameter names, enums, required flags,
job names, module routing and status restrictions are retained. Always use the
current user's validated inputs and job identifiers, never an example value.

## Authorization and activation

Only `/Add_boltz` successful key validation records authorization. A copied key
alone is insufficient. Another profile does not inherit the authorization
receipt. The five operations check authorization at execution time, including
cache reads/downloads; a rejected or unreachable validation fails closed.
Default activation takes effect in a fresh session, without altering the
current cached prompt. The existing explicit `--now` option is not the default.

## Known boundaries

This is application-level gating, not a sandbox against an operator who can
edit local code or issue independent API requests. Boltzmann enforces account
permissions, availability and billing. The imported documents are not a grant
to all backend jobs. Some historical snippets reference unavailable preparation
helpers: do not execute their imports or bypass the plugin; disclose missing
validation/runtime requirements and stop when required. No adapter or scientific
model installation is implied by the bundled knowledge.
