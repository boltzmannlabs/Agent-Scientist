---
sidebar_label: Research profiles
---

# Isolated research profiles

The interactive Agent Scientist CLI supports scientist-defined profiles with separate
conversations, selected skills, tool permissions, sources, and a scientific persona.

```text
/Create_profile "antibody-project"
/activate "antibody-project" profile
```

Creation asks only for a name, science-related installed skills, configured ToolUniverse /
Boltzmann selections, and optional local file/folder paths or HTTPS reference URLs. Skill and
tool pickers have short searchable pages with **Done** always visible. An evidence-aware
scientific persona is supplied automatically. There are no Docker, persona, or routing
questions during creation, and no network requests or local software launches.

**Create profile** saves the project even if its scientific software is not ready. The
receipt distinguishes **Ready: conversation and skill instructions** from **Setup required:
local execution and service connections**. Tool names come from existing cached discovery;
if unavailable, a service preference is saved without granting access to its whole catalog.

Selecting Boltzmann automatically includes its shared submit, status, download, upload, and
fetch-tool-log operations as one explicit workflow bundle. They are not individual picker
options. Any additional tools remain optional; future server tools are not automatically
granted. Without a complete cached list these are saved requirements only. Connection setup
must discover all five before saving access. Uploads and job execution still require their
normal approvals; selection does not run a job or bypass authentication/isolation setup.

Local execution and supported service connections can be prepared later:

```text
/activate "antibody-project" --prepare
```

This optional flow offers a **Standard isolated workspace**: no Docker image name is needed.
It requests separate approvals for metadata inspection, downloading the existing default
sandbox image if missing, and an isolated requirements check. Manual image selection is
available under **Choose an installed environment (advanced)**. Setup cancellation or missing
software does not remove the saved project. Saving setup starts a new project conversation
on its next turn; it never rebuilds the main conversation's cached prompt.

The check uses Bash to locate declared commands; it does not run scientific tools or install
their dependencies. Missing commands block acceptance of that environment. Dependencies,
versions, datasets, GPU requirements, and requirements written only in prose still need review.
A standard workspace is not a ready-made antibody generator. Approved images are pinned by
immutable ID. Downloads show elapsed time, can be cancelled, and may leave cached image layers.
Docker itself must already be installed and running; there is no fallback to host execution.

Skills are selected from the current profile's installed skills and copied, with supporting
files, into the new profile. Add missing capabilities using the existing `/Add_skill`,
`/Add_tool`, or `/Add_mcp` workflow first, then create the profile. A setup request is not
proof that a tool was installed or scientifically validated.

Sources are initially references only: contents are not read, copied, indexed, or sent to a
model during creation. Moving a referenced file will make that reference unavailable, but
does not prevent saving or opening the project. Optional local setup separately asks whether
source contents may be processed by the LLM. Only approved local sources are mounted, read-only,
at `/sources/0`, `/sources/1`, etc. HTTPS references are recorded, **not automatically fetched**.
Private or uncertain source material requires confirmation before cross-profile transfer.

## Execution and credentials

Each active profile uses a separate Sci worker process and conversation. Before local
setup, it can converse and read skill instructions but has no terminal or file-operation
tools. It must not claim that pending software or services ran. After setup, local terminal
and file operations run in disposable Docker containers with network access disabled.
Outputs under `/workspace` persist in that profile's `workspace` directory. Containers are
removed after each turn; installed packages or other files outside the workspace do not
persist. Skill viewing does not execute inline shell, install host dependencies, capture
credentials, or forward skill-declared secrets. The trusted Sci controller and LLM
client still run on the host; Docker is not a guarantee against kernel vulnerabilities.

Existing shared provider authentication is reused through Sci's credential resolution;
the wizard does not copy the main profile's `.env`, credentials, histories, or unrelated
configuration. Provider credentials are not forwarded into Docker. Profile-specific
logins and custom endpoints still follow existing Sci provider rules.

ToolUniverse and Boltzmann selections can be saved regardless of connection readiness.
Current executable MCP support is **prepared, unauthenticated HTTPS connections**, with
explicit tool allowlists. Optional setup performs handshake/discovery after approval; each later
service call requires approval of its actual arguments. Host-loaded plugins, local/stdio
MCP processes, and authenticated MCP connections are not silently inherited: they require
a separately reviewed isolated deployment/credential workflow. A plain repository URL is
not an isolated runnable tool.

Changing a reviewed profile's configuration blocks execution until it is reviewed/recreated.
There is no fallback to local host execution. Selected image software and scientific
requirements remain the user's responsibility; sandbox checks do not establish scientific correctness.

## Automatic routing and collaboration

Creation does not opt a project into routing or cross-profile sharing. `/profile_routing on`
asks which profiles may route in this CLI session. Their project purpose and selected skills
provide the initial scope. Later-created profiles are not implicitly included. Existing
pre-approved sharing grants remain directional: antibody → molecule does not grant the reverse.
New profiles have no pre-approved transfers; additional sharing requires confirmation.

Enable routing explicitly in the current CLI:

```text
/activate main
/profile_routing on
```

The consent screen identifies the router model and endpoint. New requests and profile purpose
metadata are sent to it; the main conversation's earlier history and project files are not.
The router uses no executable tools and cannot grant permissions. Ambiguous requests ask for
clarification. An unmatched request continues in the main conversation.

For a request involving antibodies and small molecules, the router builds bounded steps for
the opted-in profiles. Each step gets an isolated worker and only its subtask plus approved
dependency outputs. Independent steps need not share any output; this version runs steps
sequentially. Pre-approved public collaboration runs automatically. New or potentially sensitive
transfers require confirmation. Optional final comparison separately asks before sending all
outputs to the coordinator model. Detection of sensitive information is not exhaustive.

The default limits are four pipeline steps, 300 seconds per profile turn, and 30 agent
iterations. Routing/model calls have a 60-second limit. Provider charges still apply.
Failures do not silently fall back to another profile/provider or launch automatic retries.
Cancelled runs may retain outputs from completed steps; cleanup failures are reported explicitly.

```text
/profile_routing off
/activate main
```

Manual activation takes priority over automatic routing. Switching A → B → A in one CLI
resumes each worker's separate conversation without modifying the main agent's cached prompt
or toolset. Histories are saved in their profile databases; reopening the CLI starts a new
project conversation rather than automatically resuming an old one.
