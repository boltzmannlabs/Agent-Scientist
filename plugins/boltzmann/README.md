# Boltzmann connector for Agent Scientist

The custom Agent Scientist distribution includes this connector, **not a credential or a subscription**.
The CLI setup command is available even when this plugin is not enabled in a profile.
Seeing `/Add_boltz` does not authorize any scientific tools. Successful explicit setup enables
only Boltzmann, preserving unrelated plugin selections.

In the interactive CLI, run `/Add_boltz` (case-insensitive). Enter the key in the masked prompt,
not as an argument or a chat message. Validation makes one read-only request to
`https://nodeapis.boltzmann.co/api/get-projects`, with a 15-second timeout and no redirects.
On success the key is saved through Sci credential storage in the active profile; a
profile-and-key-bound activation receipt contains only a hash. No job is submitted by setup.

Restart `agent-sci` after success. All five operations (submit, status, download, upload,
fetch-tool-log) are enabled together. The ordinary setup command does not mutate the current
conversation's tools, skills, or prompt. Existing `--now` explicitly opts into immediate refresh
for native profiles. Legacy isolated science profiles always defer activation until the next
session; their reviewed policy adds only the five Boltzmann operations, with per-call external
access approval. Local sandbox restrictions and pending local setup remain unchanged.
Missing, changed, removed, rejected, or revoked credentials block execution, including cached
status reads and signed-file downloads. Service outages also fail closed. A saved key alone
does not authorize the connector: `/Add_boltz` must complete in each owning profile.

The optional stdio MCP adapter uses the same gate. It must run with the owning profile's
`SCI_HOME` and the Sci runtime with MCP support. Nothing here creates a remote MCP
service or copies credentials into isolated scientific project containers.

This is application-level gating, not a sandbox against someone who can edit local Python or
state files. The Boltzmann service remains responsible for actual account permissions and billing.
Other independent MCP servers are responsible for their own authentication.

The connector was brought forward from this project's existing local Boltzmann plugin.
Its prior workflow helpers and schemas are preserved; authorization and profile isolation were
updated. No private `.env`, configuration, API keys, results, or local sample data are bundled.

## Packaged workflow knowledge

The authorized `boltzmann:tools` skill includes the module registry, scientific
references, clarification/file/limit contracts, collection mappings and the
optional peptide conversion script. These files ship with Git checkouts and
Python package data; no private local plugin directory is needed. They are
instructions and contracts, not additional model tools or installed scientific
runtimes. The same five tools execute jobs.

Read `skills/boltzmann-tools/DISTRIBUTION.md` for provenance, sanitization,
historical verification limits, and excluded private/maintenance material.
Installing this knowledge never grants access: authorization remains profile-
and-key-bound, and every operation revalidates against the service.

## Scientific execution routing

For an authorized profile, the plugin supplies a session-frozen prompt section
that points to `boltzmann:tools` before generic generation skills. Plugin skills
are intentionally absent from the ordinary system-prompt skill index; deferred
tools remain discoverable through the existing tool-search bridge. This policy
does not add a core tool, perform a network check, or rebuild a live prompt.

Matching verified scientific workflows use Boltzmann by default. Missing inputs
need clarification; missing session tools need setup/restart guidance. Failed
authentication or blocked contracts do not authorize a silent local/other-provider
fallback. Alternative scientific execution requires an explicit request or informed
approval. Random-antibody generation must use the installed antibody contract and
report actual heavy/light output counts; it must not promise 20 pairs merely
because 20 samples were requested. These are model-routing instructions, not an
OS sandbox or a guarantee that an arbitrary model obeys every instruction.

Existing user-installed plugins with the same name can override the bundled
plugin. Inspect the discovered plugin location when updating an existing
machine; do not overwrite a user's plugin automatically. Fresh installations
without an override use this repository's bundled connector.
