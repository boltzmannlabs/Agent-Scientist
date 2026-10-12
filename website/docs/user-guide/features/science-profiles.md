---
sidebar_label: Research profiles
---

# Native research profiles

The interactive Agent Scientist CLI creates ordinary native SCI profiles with
separate configuration, service credentials, selected skills, conversations,
memory, workspaces, and a scientific persona.

```text
/Create_profile "omics"
/profiles_list
/activate
/activate "omics" profile
/activate main
```

## Create and review

The wizard asks for a name, scientific skills, tools, service credentials, optional
sources, and final confirmation. Skills are copied with supporting files from main;
main's activation choices remain unchanged. The essential operating-manual skill
remains available through native skill synchronization. Missing capabilities can be
set up in main using `/Add_skill`, `/Add_tool`, and `/Add_mcp` first.

Tool choices come from main's installed plugins and configured MCP connections:

- Boltzmann: choose an existing main key or enter a masked new key. Its read-only
  authentication check requires approval and submits no scientific jobs. A successful
  save establishes a new profile-specific authorization receipt. All five helper
  operations are included together. This grants plugin-wide workflow access, not
  individual-workflow isolation. Without successful authorization, Boltzmann is omitted.
- MCP (including ToolUniverse): approve the connection check and any local process
  execution/package-runner download. After handshake/discovery, explicitly select
  tools. No business tools run during checking. The saved allowlist does not grant
  access to future server tools. Existing source allowlists remain an upper bound.
- Other installed plugins: review the complete plugin permission scope. Code is
  reused; updates or removal of that installation affect profiles using it. Only
  already-loaded integrations with known toolsets and no unreviewed dependency or
  custom-setting requirements can be reused. Credentialed plugins without a supported
  authentication checker require their native setup in the target profile, or an MCP
  connector. Metadata review is not an execution test.

Credentials are never displayed. Approved service keys are copied into the new
profile's private storage, not live-linked to main. Replacing a copy affects only
that profile; revocation at the service affects every copy of the revoked key.
OAuth connections require their normal, reviewed sign-in; only that connection's
staged credentials are saved. Cancelling can leave a remote OAuth grant or downloaded
package/image cache; these side effects are reported.

Existing shared LLM authentication uses SCI's native provider credential store.
The wizard does not copy main's entire `.env` or arbitrary service credentials.
Provider-specific authentication rules still apply; credentials available only as
shell variables or inline configuration are not automatically shared.

Review lists skills, tool counts, hidden credential choices, backend, workspace, and
source access. Creation stages the profile outside discovery and publishes it only
after confirmation. Duplicate names cannot overwrite existing profiles. After saving,
choose **Activate now** or **Stay in current profile**.

## Environment

No `/activate … --prepare` step is needed for new native profiles.

| Main's backend | New profile |
|---|---|
| Local | Same installed host software, separate workspace |
| Docker | Reviewed image pinned to its ID, separate container/workspace |
| SSH/cloud/other remote backend | Creation stops with guidance; a safe workspace/credential-copy adapter is required |

The local backend is profile separation, **not OS-level filesystem isolation**.
Docker covers terminal execution; trusted host plugins and local MCP processes are
not automatically containerized. Main's writable mounts, credential-file mounts,
and environment forwarding are not copied. Docker must already be installed/running;
a missing image requires download approval. There is no silent backend fallback.
Scientific dependencies, datasets, GPU support, and result validity remain separate
requirements; selecting a skill does not install its scientific software.

## Sources

Add a local file/folder or public HTTPS reference URL. Each source has a reviewed mode:

- **Reference only:** ask before reading or retrieving contents.
- **Allow local reading/processing:** ask before sending contents to a model or service.
- **Allow relevant contents to selected model:** permits that model, not arbitrary services.

Creation reads no source contents and does not download, upload, or index them.
Do not enter signed URLs or secrets. Approved Docker-local sources are mounted
read-only under `/sources/<index>`. Moving a referenced source breaks its location.
Source-access instructions guide the agent; on the local backend they are not an
OS sandbox or a substitute for filesystem permissions.

## Listing and activation

`/profiles_list` uses the same registry as `sci profile list`, including profiles
created outside this wizard. `/activate` presents a picker with the current profile
marked; a name activates it directly. The status bar's left label shows `[main]`,
`[omics]`, etc., shortened on narrow terminals.

Switching hands off to a fresh native CLI process after normal shutdown. It resumes
the destination's latest CLI session when one exists, otherwise starts a new one.
This switches slash commands as well as messages: `/Add_boltz`, `/Add_tool`,
`/Add_mcp`, and skill commands affect the selected profile. Finish or cancel running
work first. No live agent/toolset is transplanted between profiles, and activation
does not rewrite an existing cached system prompt.

Existing legacy science profiles also activate directly, without migration or setup
questions. Their saved files, credentials, history and isolation settings are preserved.
The native CLI applies their existing execution checks and permission gate before model
turns. A profile whose local setup was never completed still has no local execution;
activation neither prepares it nor grants new access. Invalid or changed legacy sandbox
configuration blocks execution with an error, not a setup wizard or host fallback.

`/Add_boltz` is always offered in the interactive CLI, including profiles that did
not select Boltzmann during creation. The command itself grants no tool access.
Successful masked-key validation enables the connector in the active profile for
the next session. Legacy isolated profiles add only the five Boltzmann operations
to their reviewed policy, retaining per-operation external-access approval and
all local execution restrictions. Their activation stays deferred even with `--now`.

In the creation tool picker, ToolUniverse and Boltzmann appear first when available.
Select entries to toggle them, then choose Done; the full description is printed
after selection even when its menu label was shortened.

## Optional routing and collaboration

Creation does not opt a profile into automatic routing or data sharing.

```text
/activate main
/profile_routing on
/profile_routing off
```

Choose eligible profiles and approve the displayed router model/destination.
Only the new request and profile-purpose metadata go to the router, not earlier
conversation history or project files. The router cannot grant tools or permissions.
Native routed turns use the profile's native configuration and provider; legacy
routed projects retain their restricted execution checks. Manual activation uses
the native CLI rather than this routing transport. Routing opt-in is session-local
and must be renewed after a native CLI restart.

Multi-profile steps run sequentially with bounded turn time and step count. Existing
directional sharing grants do not imply reverse grants. New or potentially sensitive
transfers require confirmation; detection is not exhaustive. Final aggregation also
requires approval before sending outputs to the coordinator. Provider charges apply.
Failures do not silently switch provider/profile or automatically retry. Cancellation
may retain completed outputs; owned-worker cleanup failures are reported.
