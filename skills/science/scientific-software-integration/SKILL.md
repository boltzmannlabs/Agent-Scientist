---
name: scientific-software-integration
description: Use when adding scientific software as agent tools.
version: 0.1.0
author: Sci Agent
license: MIT
platforms:
  - linux
  - macos
  - windows
metadata:
  sci:
    tags:
      - scientific-software
      - installation
      - tool-integration
      - molecular-visualization
    category: science
---

# Scientific Software Integration Skill

Install scientific applications and expose their verified capabilities to an agent. Keep application deployment, CLI invocation, native tool registration, and scientific output validation as separate deliverables.

## When to Use

- Add a molecular viewer, structure-analysis application, or other scientific executable to an agent's toolkit.
- Select between a standalone scientific application and a similarly named Python library.
- Establish a reproducible headless interface for an installed scientific program.

This skill covers deployment and integration, not interpretation of biological results or general-purpose debugging.

## Prerequisites

Application references describe prior integration work, not installations delivered by this skill. Plugins, binaries, and credentials must be separately installed, authorized, and verified on the current machine.

Inspect current tools with `tool_search` where available and installed skills with `skills_list`. Service connections, authorization, datasets, and scientific software are not included merely by installing these instructions. Verify the prerequisites in the procedure; obtain approval before downloads, installation, or execution.

## How to Run

Use `read_file` for supplied documents and `search_files` for local discovery. Use configured scientific tools when suitable; any local execution uses `terminal` in an approved environment, never an ad hoc modification of the Agent Scientist runtime. Keep credentials and private samples out of reusable instructions.

## Quick Reference

Confirm the requested input, output, available tools, and prerequisites before following the workflow. These instructions are not proof of scientific validity or an installed service.

## Procedure

1. Establish the requested integration surface before installing. Check whether the application is already present and whether the user needs CLI access, a reusable skill, or a registered agent tool. For a terse request, choose the least invasive reasonable default; ask one focused question only when the choice materially changes the implementation. State which surface is being delivered: a PATH entry does not register a native tool.

2. Verify product identity and distribution through the publisher. Retrieve the official download index and release metadata, then match OS, architecture, interpreter requirements, and required capabilities. Inspect package descriptions before rejecting a package based on its version number: a publisher's headless library and GUI application can have different release numbering. Do not infer Python compatibility from the interpreter being new; verify the supported versions or wheel tags.

3. Choose deployment based on capability and privileges. Prefer a publisher-supported package or bundled runtime when the application needs its own interpreter or GUI stack. If administrative access is unavailable, evaluate a user-local package extraction only when the application layout permits relocation. Resolve runtime dependencies before treating extraction as installation. Do not infer that all dependencies are present from the launcher's dependency list; plugins and rendering modules can load additional libraries later.

4. Acquire and validate the actual artifact. Follow the publisher's documented download flow. If an installer URL returns HTML, inspect the form or redirect instead of repeatedly downloading the same response under an installer extension. Present licensing choices and obtain authorization before accepting terms. Match the asset's architecture and exact byte size against publisher release metadata, inspect its file type, and verify a publisher checksum when supplied. Record the release tag, source commit, license, and locally measured SHA-256 separately; a locally measured hash is provenance, not proof of agreement with a publisher checksum. If an endpoint fails, return to the official index; one failed hostname does not establish a network allowlist.

5. Expose the application without disrupting existing configuration. Use the intended profile and installation scope. Inspect an executable with `file` before attempting a text read, because a launcher may be ELF or a symlink to a binary. Create a PATH wrapper or link only after locating the real executable. For a native Sci tool, load the Sci integration documentation and implement the appropriate supported extension; installing the executable or adding a skill alone does not satisfy registration.

6. Discover the interface before writing the functional probe. Read `--help`, advanced help when available, official scripting documentation, or the installed source for the relevant entry point. Separate the application's command language from its embedded Python interface. Read the injected script namespace before assuming convenience globals exist. Exercise the exact advertised invocation against a publisher fixture before encoding it in a wrapper: help text can omit runtime preconditions. If execution contradicts help, test a documented alternative and add a regression test for the working invocation. On an API or unknown-command error, inspect the named API or command registration before trying another guessed spelling; repeated guesses conceal a test bug as an installation problem.

7. Verify in increasing capability tiers, keeping each test independent:
   - Launch: the executable resolves and reports its version.
   - Data loading: a known input loads through the intended CLI or embedded API.
   - Analysis: a documented operation yields checked data or a machine-readable result.
   - Rendering, when requested: an image is written and its format, dimensions, and visible content are inspected.
   - Agent integration, when requested: the registered tool is discoverable and a real invocation exercises the application.
   Identify any scientific fixture from its source metadata before calling it an antibody, Fab, target, or control. Do not let an optional rendering test erase successful deployment, but do not mark rendering or integration complete based on launch alone.

8. Report the highest verified tier and any remaining requested tier. Give the executable or artifact path, exact capability verified, and blocker or pending work. When asked for status, answer with completed / failed / pending immediately rather than adding more exploratory calls. Keep progress messages to meaningful milestones and name the tools actually used; do not expose internal speculation or replay the debugging process.

### Application Reference

Read [ChimeraX deployment and scripting](references/chimerax.md) for official artifact discovery, the relocatable Debian layout, and source-backed scripting primitives. It deliberately does not claim a validated rendering workflow.

Read [BioToolsLLMAnnotate integration](references/biotoolsllmannotate.md) when installing its software-metadata annotation CLI or exposing it as native Sci tools. It covers isolated deployment, config-driven upload prevention, credential-safe snapshots, and distinguishing heuristic outputs from LLM assessments.

Read [biotoolsSchema integration](references/biotoolsschema.md) when exposing software-metadata JSON/XML validation or field inspection. It covers selecting stable schemas, duplicate-enum handling without source modification, isolated validators, safe XML parsing, and fresh-runtime native registry tests.

Read [Molecular docking deployment and probes](references/molecular-docking.md) when integrating receptor–ligand docking software. It covers publisher-asset selection, prepared PDBQT fixtures, the verified AutoDock Vina score-only autobox invocation, and separate gates for scoring, docking search, and native registration.

## Pitfalls

Do not treat installed instructions or historical integration notes as proof that software, service authorization, or scientific validation is available. Confirm prerequisites and report missing access before execution.

## Verification

Capture the application's own return code and complete log before filtering output. Prefer `terminal` output or log inspection through `read_file` over a trailing pipeline that reports a filter's exit code. Separate dependency failures from errors introduced by the verification script. Check the actual requested outputs; successful installation, a working import, and a native agent tool are distinct acceptance criteria.
