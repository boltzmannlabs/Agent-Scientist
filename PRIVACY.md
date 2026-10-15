# Data Privacy and Handling

Agent Scientist is maintained by Boltzmann Labs. This document describes data
handling in the self-hosted application; it is not a promise that all processing
stays on your machine or a certification of regulatory compliance.

Your deployment configuration, enabled integrations, and service-provider terms
determine where data goes. An organization hosting SCI for others should supply
its own approved privacy notice, retention rules, and responsible contact.

## What is stored locally

SCI stores application state in its configured home directory. The default on
Linux is `~/.sci`; installations and profiles can use other locations.
Project workspaces and execution backends may store files elsewhere.

Depending on enabled features, retained data can include:

| Data | Examples and purpose |
|---|---|
| Conversations | Messages, stored tool calls/results, session metadata, and summaries used for resume and context |
| Configuration | Model choices, enabled tools, profile settings, and source references |
| Credentials | API keys, saved logins, tokens, and authorization records used to access services |
| Research material | Downloaded files, generated outputs, uploaded-file copies, and workspace artifacts |
| Memory and skills | Saved preferences, reusable instructions, and information retained for later sessions |
| Diagnostics and caches | Logs, cached responses, large tool-output spillover, and troubleshooting artifacts |
| Backups and exports | Configuration backups, state snapshots, and exported conversations |

Treat these locations as sensitive. Logs, tool output, backups, and exports may
contain research data or secrets despite redaction safeguards. Local storage is
not a guarantee of encryption at rest; use appropriate filesystem permissions,
disk encryption, and organizational access controls.

## When information leaves the machine

| Destination | What may be sent |
|---|---|
| Selected model provider | Prompts, conversation context, relevant file content, tool results, and enabled tool descriptions |
| Auxiliary model services | Material needed for configured features such as vision, summarization, or embeddings |
| Web/search/browser services | Queries, requested URLs, page interactions, and data submitted to those services |
| MCP servers and plugins | Tool arguments, authentication material, and files or records required by the requested operation |
| Boltzmann services | Authorization requests, approved scientific inputs, job parameters, and job-management requests |
| Remote execution backends | Commands, mounted or transferred inputs, and generated outputs on the selected backend |
| Messaging and hosted interfaces | Messages and attachments handled by the connected platform or deployment operator |
| Package and update services | Requests for version information, source code, packages, and dependencies |

Services may also receive connection metadata such as IP addresses and request
times. A local model does not make web searches, remote tools, or other configured
integrations offline.

Provider retention, training use, processing location, and deletion practices are
governed by the provider's terms and your account agreement. SCI cannot guarantee
those policies or delete their records on your behalf.

## Permissions, profiles, and credentials

- Review destinations, requested access, and costs before connecting a service.
- Approval behavior depends on configuration. Do not assume every file read,
  network request, or command will always prompt for separate confirmation.
- A saved source reference does not itself upload or index that source. Later
  tool use can read or transmit relevant content according to configured access.
- Profiles separate application state and service configuration. They are not
  separate operating-system users or a complete security sandbox.
- Shared model authentication can be reused across profiles. Copying an approved
  service key into another profile creates another stored copy of that credential.
- Removing or disabling a provider does not necessarily delete its saved login.
  Read the operation's outcome and remove or revoke credentials separately when needed.
- Plugins and local processes can have substantial host access. Review their code
  and permissions; a terminal container does not automatically sandbox every plugin
  or MCP process. See [SECURITY.md](SECURITY.md).

Never put secrets in reusable skills, public repositories, issue reports, or
example commands. Use supported credential entry and storage mechanisms.

## Optional metrics and diagnostics

The repository defaults disable both shared-metrics collection and sending:

```yaml
telemetry:
  shared_metrics:
    enabled: false
    send: false
```

Collection and transmission are separate settings. Existing configurations can
differ from these defaults. Review the active profile and any observability
plugins before enabling metrics or exporting diagnostic traces.

**Current endpoint warning:** the shared-metrics default endpoint in
[`sci_cli/config_defaults.py`](sci_cli/config_defaults.py) is still
`https://telemetry.nousresearch.com/v1/telemetry`, an inherited third-party
destination, not a Boltzmann Labs endpoint. Sending is disabled by default.
Do not enable it without reviewing that destination and approving the transfer.

Disabling shared metrics does not disable ordinary model requests, tool traffic,
update checks, local logs, or independently configured third-party integrations.

## Retention, exports, and deletion

There is no single retention period covering every local artifact and external
service. Session storage, logs, caches, memories, outputs, and backups have
different lifecycles; operators should define and verify their own retention rules.

- Conversation compression reduces model context; it is **not** deletion of history.
- Hiding or archiving a conversation is not the same as deleting it.
- Review the [session-management guide](website/docs/user-guide/sessions.md) and
  command help before exporting or pruning records.
- Redaction options reduce accidental disclosure but do not guarantee removal of
  every secret or personal identifier. Inspect an export before sharing it.
- Deleting a session does not necessarily remove related memories, workspace
  outputs, logs, caches, backups, or copies held by external services.
- Revoke exposed credentials at the issuing service. Deleting a local key does
  not revoke the credential or remove copies from other profiles or backups.

Before maintenance, stop affected processes and identify the exact profile and
files involved. Do not delete the entire application home as a troubleshooting step.

## Scientific and sensitive data

Use public, synthetic, or approved de-identified fixtures for initial testing.
Do not submit identifiable patient data, restricted clinical records, confidential
sequences, unpublished research, or proprietary datasets without the necessary
authorization and an approved processing arrangement.

SCI's availability, input checks, and security scanning do not establish scientific
validity, clinical suitability, or compliance with an organization's data policies.

## Questions and incidents

For internal deployments, contact the Boltzmann Labs maintainer or organizational
administrator who supplied your installation through an existing private channel.
For suspected credential exposure or vulnerabilities, follow
[SECURITY.md](SECURITY.md). Do not post sensitive details in public issues.

**Before public release:** an approved privacy contact and private reporting
channel must be published. Neither should be inferred from an upstream project's
support address.
