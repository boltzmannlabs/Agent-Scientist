---
title: "Get Available Resources — Check effective compute limits before heavy workloads"
sidebar_label: "Get Available Resources"
description: "Check effective compute limits before heavy workloads"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Get Available Resources

Check effective compute limits before heavy workloads.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/science/computing/get-available-resources` |
| Version | `1.3+sci.1` |
| Author | K-Dense Inc.; Sci adaptation for Agent Scientist |
| License | MIT |
| Platforms | linux |
| Tags | `science`, `computing` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Get Available Resources Skill

Check effective compute limits before heavy workloads. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): `psutil==7.2.2`.
- Optional prerequisites: GPU management CLIs for optional read-only probes
- Companion skills (check availability with `skills_list`): None required.
- Other skills named in upstream references are optional and may be absent. Use `skills_list` before loading one; a Python package is not a skill dependency.

## How to Run

Replace `<science-python>` in the examples with the verified interpreter path; it is a placeholder, not a shell command. Resolve `SCI_SKILL_DIR`, where used, to this installed skill directory. Check current tools first: prefer an authorized matching scientific tool, including Boltzmann when applicable. Use local execution only when appropriate or explicitly requested, and explain any fallback.

Use Sci `read_file` and `search_files` for inspection and `terminal` for execution. Read `references/upstream-workflow.md` and the relevant API reference before implementing an unfamiliar operation.

Run helpers with the verified interpreter and the absolute skill directory supplied by Sci:

```bash
"<science-python>" "${SCI_SKILL_DIR}/scripts/<helper>.py" --help
```

Choose an actual helper from the list below; the placeholder is not a command to execute. For Python snippets in references, use the same interpreter. Shell examples assume the skill directory as their working directory; use absolute task input/output paths and write artifacts to the task workspace, never into the installed package. Do not use bare `python`, automatic `uv run` environment creation, or upstream installation examples in place of the verified interpreter.

## Quick Reference

- `scripts/accelerator_diagnostics.py` — CLI
- `scripts/detect_resources.py` — CLI
- `scripts/plan_workload.py` — CLI
- `scripts/snapshot_tools.py` — CLI

## Procedure

1. Run resource detection only when requested or when the planned workload needs it; start with the redacted stdout snapshot.
2. Distinguish host inventory from affinity, cgroup limits, scheduler allocations, and actual framework access; a visible GPU is not proof it is usable.
3. Use the planner to bound workers and memory. Report unknowns and partial probes, and avoid stress tests or driver changes.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
