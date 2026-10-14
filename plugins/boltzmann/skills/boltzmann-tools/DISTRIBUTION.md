# Boltzmann workflow distribution

The owner's Boltzmann connector ships with the authorized Agent Scientist
distribution. It does not include credentials, a subscription, or scientific runtimes.

## Runtime knowledge

- `references/tool-contracts.v1.json`: exact jobs, request schemas, input kinds,
  module routing, recorded examples and diagnostic mappings.
- `references/file-input-contracts.v1.json`: documented file checks.
- `references/input-limits.v1.json`: documented bounds.
- `references/modules/`: generated instructions from those three definitions.
- `references/tool-status-fetch.md`: read-only diagnostic protocol.
- The optional conversion script requires its own approved runtime; nothing runs
  or installs merely because the script is packaged.

The catalog is the inventory authority; counts are not hardcoded here.
An active entry means a declared request, not a guaranteed backend result.
Unavailable entries state the missing request information instead of fabricated
payloads. File rules and limits are optional supplements, not separate job allowlists.

Historical, overlapping catalogs and developer audits are retained under the
plugin's `contract_sources/`, outside the runtime skill and Python package data.
They must not be loaded as competing execution instructions.

## Private material and evidence

Credentials, local configuration, authorization receipts, caches, outputs and
private samples are not bundled. Public-source account/job identifiers and
historical upload references are not reusable examples; active knowledge uses
non-executable placeholders instead. Shape templates are not validated scientific
samples or default parameters. Preserve the current user's values and actual
upload/job references.

Static contract checks and localhost connector tests are distinct from live
scientific verification. No packaging change authorizes a production experiment
or establishes scientific correctness.

## Authorization and activation

Successful `/Add_boltz` setup records profile-and-key-bound authorization.
Another profile does not inherit that receipt merely by possessing the same key.
Every connector operation checks authorization; failed authentication does not
permit a silent provider fallback.

Start a fresh process/conversation to load updated code and skill instructions.
Existing conversation prompts and toolsets are not rewritten. Runtime receipts
bind file checks to the owning profile, credential fingerprint, input context and
validation rules; substantive rule changes may require revalidation.

This is application-level access control, not an OS sandbox against someone who
can modify local code. Service permissions, availability and billing remain the
platform's responsibility. Unsupported serialized executable files and unsafe
archives are not authorized by approving incomplete scientific checks.
