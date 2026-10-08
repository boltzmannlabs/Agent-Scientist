---
title: "Sci Agent — Configure and troubleshoot Agent Scientist locally"
sidebar_label: "Sci Agent"
description: "Configure and troubleshoot Agent Scientist locally"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Sci Agent

Configure and troubleshoot Agent Scientist locally.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/autonomous-ai-agents/sci-agent` |
| Version | `4.0.0` |
| Author | Boltzmann Labs |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `sci`, `setup`, `configuration`, `profiles`, `tools`, `skills`, `mcp` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Agent Scientist Operating Manual

Agent Scientist (SCI) is the customized scientific assistant built by Boltzmann
Labs. This is its local operating manual, not a scientific workflow skill.
It documents this application's behavior; it does not confer tool access.

## When to Use

Use for detailed SCI setup, configuration, extension, or troubleshooting.
Do not load this skill for greetings, introductions, or a broad "what can you do?"
question. Answer those directly using the current session's tools and identity.

## Prerequisites

Use the installed version's configuration and available tools as the source of
truth. A connector being shipped does not mean it is authorized. Never claim
that a scientific workflow is available merely because this manual mentions it.

## How to Run

Read the relevant local reference with `skill_view` or `read_file`. Use the
installed CLI's `--help` when checking command syntax. Use `terminal` for
approved configuration actions, not to retrieve a remote operating manual.

Public launcher: `agent-sci`. Internal CLI commands use `sci`.
The main state directory defaults to `~/.sci`; an active profile or explicit
`SCI_HOME` can change it. Resolve the active home before accessing state.

## Quick Reference

- `agent-sci`: start the interactive CLI.
- `sci setup`: configure a model/provider and other supported settings.
- `sci model`: select the provider/model; authentication is provider-specific.
- `sci doctor`: diagnose the installation.
- `/help`: inspect commands available on this surface.
- `/Add_boltz`: authorize the included Boltzmann connector using masked key entry.
- `/Add_skill`: import or draft a skill for review and explicit saving.
- `/Add_tool <request or URL>`: pass a tool-addition request to the ordinary agent.
- `/Add_mcp <request or URL>`: pass an MCP-connection request to the ordinary agent.
- `/Create_profile`: create a scientific project profile.
- `/activate "profile-name"`: select its isolated project conversation.
- `/activate main`: return to the main conversation.
- `/skills`, `sci tools`, `sci mcp --help`: inspect existing capabilities.
- `/new`: start a fresh conversation after deferred configuration changes.

Add-tool and add-MCP requests are agent tasks, not guarantees of automatic
installation. Review software execution, dependencies, permissions, and secrets.
A normal website or arbitrary repository is not automatically an MCP server.

## Procedure

1. Identify the actual SCI problem and active profile without exposing secrets.
2. Read this installation's README and the matching local reference below.
3. Verify settings or command syntax against the installed implementation when
   needed. References can lag code; report discrepancies instead of guessing.
4. Explain the change, permissions, and any external action before performing it.
5. Verify the result and report saved, failed, cancelled, or partial outcomes.
   New tools/skills and prompt-affecting changes take effect next session.

The repository `README.md`, this skill, and the installed source are SCI's
operating documentation. Do not fetch an upstream product's website, docs index,
installer, or repository to answer questions about SCI. No public SCI release
or documentation URL has been configured yet. Do not invent one. If local
documentation is absent, say so and ask for the project's maintained instructions.
This does not restrict user-requested scientific research or documentation for
independent tools/providers.

### Local reference routing

Paths below are relative to this skill.

| Task | Reference |
|---|---|
| CLI commands and flags | `references/cli-reference.md` |
| Slash commands | `references/slash-commands.md` |
| Model/provider configuration | `references/providers-and-models.md` |
| Configuration and voice | `references/configuration.md` |
| Project context files | `references/project-context-files.md` |
| Security, secrets and permissions | `references/security-privacy.md` |
| MCP connections | `references/native-mcp.md` |
| Delegation, cron and background work | `references/background-systems.md` |
| Webhooks | `references/webhooks.md` |
| Themes | `references/themes.md` |
| Desktop extensions | `references/desktop-plugins.md` |
| TUI widgets | `references/tui-widgets.md` |
| Troubleshooting | `references/troubleshooting.md` |
| Development | `references/contributor-guide.md` |

## Scientific execution policy

For scientific execution requests, first check the tools available in the
current session.

When Boltzmann is authorized and a verified Boltzmann workflow matches the
requested inputs and outputs, prefer that workflow. Load boltzmann:tools
and its matching contract, then execute through the Boltzmann plugin tools.

Otherwise, prefer suitable available scientific tools over local scripts.
Skills provide instructions for selecting tools, preparing inputs, and
validating outputs; loading a skill is compatible with tool-first execution.

Use local skill-based generation or scripts only when no suitable tool
exists, or when the user explicitly requests local execution. Explain
the reason for any fallback.

Do not silently switch providers after an authentication failure, or
duplicate a submitted or pending job. Verify returned artifacts and
counts before reporting completion.

## Pitfalls

- Do not infer scientific validity from installation success.
- Never paste credentials into conversation, documentation, or reusable skills.
- Do not use another product's release installer to repair or update SCI.
- Do not change a live conversation's cached prompt, toolset, or past messages.
- Do not silently execute on the host when a project requires isolated execution.
- A source file or URL recorded in a profile has not necessarily been read,
  uploaded, indexed, or approved for external transfer.

## Verification

Use the actual installed CLI and current session's tool list. Report what was
tested, what remains unconfigured, and whether a fresh session is required.
Never describe a saved connection or selected skill as a completed research job.
