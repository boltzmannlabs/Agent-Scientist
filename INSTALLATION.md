# Install Agent Scientist (SCI)

These instructions install this customized application, not another product.
Use a complete checkout from https://github.com/boltzmannlabs/Agent-Scientist.
No upstream repository is used as a fallback. Do not copy anyone else's `.sci`
directory or credentials.

## One-command installation: Linux / macOS

Run as your normal user, not with `sudo`. You need Git, Bash, `curl`, `tar`, `awk`, a
SHA256 verifier (`sha256sum` or `shasum`), internet access, and sufficient free
disk space for the managed runtime and dependencies. Full scientific models,
datasets, and optional container images need additional space and are not part
of this installation.

Clone and install:

```bash
git clone https://github.com/boltzmannlabs/Agent-Scientist.git
cd Agent-Scientist
bash ./install-sci.sh
```

The installer checks prerequisites, downloads checksum-verified managed tools,
installs the locked application dependencies, publishes `sci` and `agent-sci`
launchers, synchronizes bundled skills, and checks that the CLI starts. It does
not install developer/test dependency groups. In an interactive terminal it
then opens the existing provider setup wizard. Authenticate your chosen model
provider; SCI does not require a separate account with its original upstream.
Model charges and service usage remain subject to your providers' policies.

Fresh installations automatically use SCI's pink/magenta `neon-theme`, matching
the release palette in `assets/skins/neon-theme.yaml`. No manual skin-file copy
or theme command is needed. The classic gold default has been removed; older
`display.skin: default` settings resolve to neon. Existing custom theme choices
and user-authored skin files are preserved. The multicolor title and white
context-occupancy indicator are unchanged.

Optional model reasoning defaults to `medium`, with thinking text hidden
(`display.show_reasoning: false`). You can explicitly select another
effort with `/reasoning low`, `/reasoning medium`, or a level supported by your
model. Updates preserve existing saved effort choices and per-model overrides.

Keep the checkout in its installed location: the launchers refer to it. On
completion, open a new terminal, or update this terminal's PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
agent-sci
```

The installer can be rerun after an interrupted installation. It uses managed
package state rather than installing Python packages into your system Python.
An error stops the installation and names the failed stage; do not interpret
a stopped installer as successful. Existing credentials and research profiles
are not distributed by this process.

### Unattended server installation

```bash
git clone https://github.com/boltzmannlabs/Agent-Scientist.git
cd Agent-Scientist
bash ./install-sci.sh --non-interactive
export PATH="$HOME/.local/bin:$PATH"
sci setup
agent-sci
```

The `--non-interactive` installation installs software only. It does not configure model access,
invent credentials, approve scientific jobs, or open a public network port.
Run `sci setup` later in an interactive terminal before chatting.

## Windows

From a complete checkout in PowerShell:

```powershell
git clone https://github.com/boltzmannlabs/Agent-Scientist.git
cd Agent-Scientist
.\setup-sci.ps1
sci setup
agent-sci
```

The Bash installer does not target native Windows. Native installers and desktop
packaging are separate build products; source support is not a claim that signed
Windows/macOS release packages have been produced or tested on this Linux host.
From CMD in a complete checkout, `scripts\install.cmd` runs the same local
`setup-sci.ps1` script. It does not download another application's installer.

## Check the installation

```bash
sci --help
sci doctor
agent-sci
```

Inside SCI, use `/help`, then send a simple greeting. A model response requires
your own working provider authentication; software installation alone does not
provide free model credits. Exit and restart with `agent-sci` to test a fresh
session after saving new tools or skills.

## First-time use

1. Complete `sci setup`: select your model provider and authenticate using its
   supported login or your own API key. The installer does not include anyone
   else's account, service access or credits. Use `sci model` later to review
   or change the selected provider/model.
2. Start `agent-sci`. Enter `/help` to see the commands and `/skills` to review
   the installed skill instructions.
3. Try a simple conversation first, for example: `Explain the difference
   between antibody affinity and specificity.` A successful response confirms
   model access, not scientific-service readiness.
4. Add the services and material your research needs using the commands below.
   Review requested permissions and installation/execution actions. Restart
   `agent-sci` after saving capabilities that take effect next session.

For a research project, enter these commands inside the running CLI, not in
your operating-system shell:

```text
/Create_profile
/activate "antibody-project"
/activate main
```

During creation, name the project `antibody-project` (or use your own name),
choose suitable science skills/service tools, and optionally provide downloaded
source-file paths or reference URLs. `/activate` selects its separate project
conversation; `/activate main` returns to the main conversation. Source paths
and URLs are references until explicitly read or processed. Project creation
does not automatically install scientific software or grant service permissions.

Type `/exit` to leave the CLI. To start it again in a later terminal:

```bash
agent-sci
```

## Data, credentials, and scientific services

User settings, conversations, skills, and profiles default to `~/.sci`.
`SCI_HOME=/absolute/path agent-sci` selects a different state home. The managed
tool store is shared by your account; it is not an independent runtime copied
into every research profile. Never run the installer with another person's
home or copy private state into this repository.

Bundled science skills are instructions, not proof that their software is
installed or that a result is scientifically correct. Their supporting
references/scripts are shipped; optional skills remain opt-in. Existing users'
activation choices are preserved. External services use their own credentials.

```text
/Add_boltz
/Add_skill
/Add_tool <request or official URL>
/Add_mcp <request or documented MCP endpoint/configuration>
/Create_profile
```

Boltzmann tools remain locked until a valid API key is authorized through
`/Add_boltz`. ToolUniverse, PubMed, and other MCP services require their own
documented server setup and permissions; a website URL is not necessarily an
MCP endpoint. New capabilities normally become available in the next session.
Never put API keys in chat, the repository, or screenshots.

For OAuth-protected MCP services, dynamic registration or a service-registered
client remains supported. CIMD-only services require your team's approved
hosted identity document in `oauth.client_metadata_url`; SCI does not borrow
another application's client identity. A template is included under
`examples/mcp/client-metadata.json.example`.

## Web dashboard and desktop: optional builds

The installer prepares the core CLI. Frontend bundles and native packages are
built separately from this same checkout, with the root npm workspace lock:

```bash
npm ci
npm run build --workspace web
sci dashboard
```

Keep the dashboard bound to localhost unless you deliberately configure
authentication, a secure proxy, and network access controls. For the Electron
desktop source build:

```bash
npm run build --workspace apps/desktop
npm run start --workspace apps/desktop
```

Electron may require OS-provided desktop libraries. On a headless server, use
the CLI/dashboard instead. Native release packaging also requires each target
platform's signing credentials and release configuration; no inherited update
host or installer is used as a substitute. Application artwork is intentionally
neutral pending an approved SCI logo.

## Maintenance and troubleshooting

For an installed Git checkout, check and apply source updates deliberately:

```bash
sci update --check
sci update
```

Alternatively, enter `/update` inside the CLI. Startup update recommendations
normally use a 24-hour cache and do not install anything automatically. Only
reviewed source pushed to this repository's `main` branch is delivered. Back up
your `~/.sci` state before maintenance; keep local code edits on a separate branch.

- Command not found: open a new terminal or export the PATH shown above. The
  checkout-local launcher is also available at `.sci/bin/agent-sci`.
- Interrupted download/dependency build: rerun `bash ./install-sci.sh`; read
  the stage/error before retrying. Do not work around it using system `pip`.
- Provider/authentication problem: run `sci setup` or `sci model`. Do not share
  secrets in an issue report. SCI does not silently switch providers.
- Missing scientific dependency: follow that tool's documented environment
  requirements; installing a skill does not install its models or datasets.
- Container execution: Docker must be separately installed and a suitable
  sandbox image built/configured. See `docker/sandbox-desktop.Dockerfile`.
- Moving the source checkout: reinstall from its new location so launchers are
  republished. Back up your state before maintenance.
- Source updates are enabled for Git installations from the approved SCI
  repository. Use `sci update --check`, then `sci update` (or `/update` inside
  the CLI). Startup recommendations normally cache checks for 24 hours; they
  do not automatically install software. Every new commit on `main` can be
  recommended, so maintainers should publish only tested source changes.
- Promoted stable/canary releases and native installer/desktop feeds still
  require separate publication, signing and qualification. These paths remain
  guarded. Source updates do not create those releases or change their settings.

For developer setup and tests, use `CONTRIBUTING.md` and `source ./activate`;
these deliberately include tools that ordinary end users do not need.
