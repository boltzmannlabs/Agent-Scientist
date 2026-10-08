---
title: "Scientific Critical Thinking — Assess evidence quality, bias, confounding, and claims"
sidebar_label: "Scientific Critical Thinking"
description: "Assess evidence quality, bias, confounding, and claims"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Scientific Critical Thinking

Assess evidence quality, bias, confounding, and claims.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/science/research/scientific-critical-thinking` |
| Version | `1.3+sci.1` |
| Author | K-Dense Inc.; Sci adaptation for Agent Scientist |
| License | MIT license |
| Platforms | linux |
| Tags | `science`, `research` |
| Related skills | [`experimental-design`](../../bundled/science/science-data-analysis-experimental-design.md), [`statistical-analysis`](../../bundled/science/science-data-analysis-statistical-analysis.md), [`grounded-citations`](../../bundled/research/research-grounded-citations.md) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Scientific Critical Thinking Skill

Assess evidence quality, bias, confounding, and claims. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): Python standard library or guidance only.
- Optional prerequisites: No additional service is required for the core workflow.
- Companion skills (check availability with `skills_list`): `experimental-design`, `statistical-analysis`, `grounded-citations`
- Other skills named in upstream references are optional and may be absent. Use `skills_list` before loading one; a Python package is not a skill dependency.

## How to Run

Replace `<science-python>` in the examples with the verified interpreter path; it is a placeholder, not a shell command. Resolve `SCI_SKILL_DIR`, where used, to this installed skill directory. Check current tools first: prefer an authorized matching scientific tool, including Boltzmann when applicable. Use local execution only when appropriate or explicitly requested, and explain any fallback.

Use Sci `read_file` and `search_files` for inspection and `terminal` for execution. Read `references/upstream-workflow.md` and the relevant API reference before implementing an unfamiliar operation.

Run Python API examples with `<science-python>` through `terminal`. This skill has no bundled command-line helpers. Keep input data unchanged and write generated artifacts in the task workspace. Historical installation examples do not authorize package installation. Never modify the Agent Scientist runtime environment.

## Quick Reference

Use the Python API examples in the detailed workflow.

## Procedure

1. Separate the reported observation, its interpretation, and the strength of the causal claim.
2. Evaluate design, sampling, controls, measurement validity, confounding, statistical methods, and replication; apply an evidence framework appropriate to the study.
3. Give specific strengths, limitations, alternative explanations, and what additional evidence would change the conclusion. Do not mistake missing information for a demonstrated flaw.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
