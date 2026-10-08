# AGENT-SCIENTIST

Agent Scientist (SCI), built by **Boltzmann Labs**, is a scientific assistant
for literature research, data analysis, and approved computational workflows.

Start it with **`agent-sci`**. Application state defaults to **`~/.sci`**.
This README and the local `sci-agent` operating-manual skill describe this
customized application. No external product website is needed for SCI help.

## Install from this repository

Repository: https://github.com/boltzmannlabs/Agent-Scientist

After the initial source commit is pushed, obtain the complete checkout below.
Native release installers and SCI update feeds are not published yet. Do not
use another product's installer or update channel: it will not contain SCI's
customizations.

On Linux/macOS, from the checkout:

```bash
git clone https://github.com/boltzmannlabs/Agent-Scientist.git
cd Agent-Scientist
bash ./install-sci.sh
export PATH="$HOME/.local/bin:$PATH"
agent-sci
```

The installer provisions the managed runtime and dependencies; first setup may take
time and require downloads. It opens normal provider setup to authenticate your
chosen model. Credentials are personal and are not distributed in the repository.
For unattended servers, use `bash ./install-sci.sh --non-interactive`, then run
`sci setup` interactively. See [INSTALLATION.md](INSTALLATION.md) for prerequisites,
verification, dashboard/desktop builds, and troubleshooting.

On Windows, run `.\setup-sci.ps1`, then `sci setup` and `agent-sci`.
Native Windows/macOS packaging is not yet verified for this customized build.
Self-update remains blocked until this project has compatible release endpoints.
The bootstrap scripts deliberately have no default repository. Maintainers using
them must provide `SCI_REPO_URL` for their approved SCI source; normal users with
a checkout can use `bash ./install-sci.sh` above. No Termux package is advertised.

## Start and configure

```bash
agent-sci
SCI_HOME="$HOME/.sci" agent-sci
sci --help
sci model
sci tools
sci doctor
```

`SCI_HOME` selects the state directory; it does not migrate or delete another
directory. Settings live in `config.yaml`, secrets in the profile's protected
credential store or `.env`, and persona instructions in `SOUL.md`.
Never paste passwords or API keys into a chat or commit them to Git.

Use `/help` inside the CLI for the current command list. Use `/new` for a
fresh conversation after deferred skill/tool changes. Changing a file does not
rewrite the system prompt of a conversation already in progress.

## Scientific tools and Boltzmann

The included Boltzmann connector is locked until you authorize it:

```text
/Add_boltz
```

Enter your own key in the masked prompt. Successful validation grants this
profile access for the next session. Restart `agent-sci` after saving.
Never assume that a shipped connector or selected tool is ready to execute.

Scientific requests use suitable available tools first. Authorized Boltzmann
workflows are preferred when their verified contracts match the inputs and
outputs. Local scripts are a fallback when no suitable tool exists, or when
explicitly requested. Authentication failures must not cause silent provider
switching, and pending jobs must not be duplicated.

See the local `plugins/boltzmann/README.md` for the authorization implementation.

## Add skills, tools and services

- `/Add_skill`: import a link or local file/folder, or describe a workflow;
  review the draft and scan result before saving.
- `/Add_tool <request or URL>`: send a tool-addition request to the ordinary
  agent. Inspect requirements and approve external actions before installation
  or execution. A repository is not automatically an agent tool.
- `/Add_mcp <request or URL>`: ask the agent to connect an existing MCP service.
  Supply its actual endpoint or documented server configuration. An ordinary
  website or REST endpoint is not automatically an MCP server.
- `/skills`: inspect skills; `sci mcp --help`: inspect MCP administration.

Approved additions become available in a new session. Review permissions,
dependencies, and scientific limitations. A security scan is not a scientific
validation. Service credentials are separate from your model-provider login.

### Skills included with a fresh installation

The `skills/` tree includes the science workflows and their supporting scripts,
references, templates, and upstream license notices. Installing instructions does
not install scientific Python environments, model weights, service connections,
or API keys. Each workflow checks those prerequisites separately.
Platform restrictions still apply; Linux-specific scientific helpers are not
advertised as runnable on Windows or macOS just because their files are shipped.

Fresh setup uses the disabled-skill selection in `cli-config.yaml.example`;
the template-free first-save path uses `sci_cli/config_skill_defaults.py`.
Keep those lists in sync when changing release defaults. They are a **disabled
list**, not an allowlist: future bundled additions may become available unless
disabled. `sci-agent` is the essential operating-manual skill and stays enabled.

Existing configurations are not overwritten or silently assigned this selection.
The existing bundled-skill synchronizer can deliver newly bundled files on a later
startup while preserving user-edited bundles and existing enable/disable choices.
`optional-skills/` remains opt-in. Use `/skills` to review your own choices.
Personal credentials, sessions, profiles, usage history, and local dependency
environments are not part of this distribution.

## Research projects

```text
/Create_profile
/activate "antibody-project"
/activate main
```

Choose science skills, supported service tools, and optional source files/URLs.
Sources are references until explicitly read or processed. A project can be
saved before software/environment preparation. Local execution may require
`/activate "antibody-project" --prepare`; there is no silent host fallback.

Project conversations remain separate. Existing shared model login can be reused;
service permissions remain profile-scoped. Automatic routing or collaboration
must be explicitly configured; new permissions and sensitive transfers still
require review.

## Other surfaces

```bash
sci dashboard
sci gateway setup
sci desktop
```

The dashboard includes this manual locally. Messaging and desktop require their
own configuration. Desktop packaging and native platform checks remain pending;
availability in the source tree is not a claim of release readiness.

## Troubleshooting

If startup stalls, interrupt the foreground process with Ctrl+C and capture the
last visible stage. Do not delete your state directory or repeatedly reinstall.
Run `sci doctor` and inspect redacted logs in the active home's `logs/` directory.

The `sci-agent` skill is a local setup/troubleshooting manual, not a science
workflow and not needed for greetings. Detailed references are under
`skills/autonomous-ai-agents/sci-agent/references/` in the checkout and the
corresponding installed skills directory. Local implementation and CLI help
take precedence if inherited technical references disagree with this fork.
Do not fetch upstream documentation or installers as SCI instructions.

## Development and release status

The approved source repository is `boltzmannlabs/Agent-Scientist`. The initial
SCI commit uses fresh history; the inherited history is retained in a private
backup outside this repository. Automatic release lookup has no upstream
fallback, and release publishing remains blocked by
`sci-unpublished-distribution` until SCI-owned destinations are approved.
GitHub automation requires the approved `SCI_REPOSITORY` and the explicit
`SCI_RELEASES_ENABLED` opt-in; container and skills-index destinations must also
be configured for the workflows that use them. Plugin-validation callers must
provide `sci-repository`. Installer tests must supply SCI installer URLs.

Use `scripts/run_tests.sh` for Python tests. Source-level engineering guidance
is in `AGENTS.md` and its area-specific files. See `SCI_MIGRATION.md` for
migration verification and outstanding platform checks.

Before public release, configure SCI documentation, installers, support channels,
and update endpoints, then test them. A source push alone does not publish
native installers or activate CLI self-update. The source clone above becomes
available only after the initial push.

The `sci-unpublished-distribution` marker blocks source replacement and the release
entrypoint's publishing actions. Canary, stable, desktop release and website
deployment entry jobs additionally require the repository variable
`SCI_RELEASES_ENABLED=true`. Do not enable publication or remove the marker until
the release destinations, credentials, signing, and clean-install tests are reviewed.

Original copyright and license notices remain in `LICENSE` and source headers.
They are legal attribution, not SCI's product identity or an instruction to
contact an upstream service.
