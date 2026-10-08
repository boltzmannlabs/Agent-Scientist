# Boltzmann connector for Agent Scientist

The custom Agent Scientist distribution includes this connector, **not a credential or a subscription**.
The default enables discovery of the setup command; it does not authorize the scientific tools.
Existing explicit plugin allowlists/denylists remain authoritative.

In the interactive CLI, run `/Add_boltz` (case-insensitive). Enter the key in the masked prompt,
not as an argument or a chat message. Validation makes one read-only request to
`https://nodeapis.boltzmann.co/api/get-projects`, with a 15-second timeout and no redirects.
On success the key is saved through Sci credential storage in the active profile; a
profile-and-key-bound activation receipt contains only a hash. No job is submitted by setup.

Restart `agent-sci` after success. All five operations (submit, status, download, upload,
fetch-tool-log) are enabled together. The ordinary setup command does not mutate the current
conversation's tools, skills, or prompt. Existing `--now` explicitly opts into immediate refresh.
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
