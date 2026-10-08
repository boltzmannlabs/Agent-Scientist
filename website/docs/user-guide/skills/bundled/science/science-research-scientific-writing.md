---
title: "Scientific Writing — Draft scientific manuscripts with traceable evidence"
sidebar_label: "Scientific Writing"
description: "Draft scientific manuscripts with traceable evidence"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Scientific Writing

Draft scientific manuscripts with traceable evidence.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/science/research/scientific-writing` |
| Version | `2.1+sci.1` |
| Author | K-Dense Inc.; Sci adaptation for Agent Scientist |
| License | MIT |
| Platforms | linux |
| Tags | `science`, `research` |
| Related skills | [`citation-management`](../../bundled/science/science-research-citation-management.md), [`scientific-critical-thinking`](../../bundled/science/science-research-scientific-critical-thinking.md), [`scientific-visualization`](../../bundled/science/science-visualization-scientific-visualization.md), [`llm-wiki`](../../bundled/research/research-llm-wiki.md) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Scientific Writing Skill

Draft scientific manuscripts with traceable evidence. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): Python standard library or guidance only.
- Optional prerequisites: No additional service is required for the core workflow.
- Companion skills (check availability with `skills_list`): `citation-management`, `scientific-critical-thinking`, `scientific-visualization`, `llm-wiki`
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

- `scripts/audit_claims.py` — CLI
- `scripts/check_consistency.py` — CLI
- `scripts/check_references.py` — CLI
- `scripts/lint_manuscript.py` — CLI
- `scripts/scaffold_manuscript.py` — CLI
- `scripts/select_reporting_guidelines.py` — CLI
- `scripts/validate_authorship.py` — CLI
- `scripts/validate_manifest.py` — CLI

## Procedure

1. Confirm manuscript type, audience, available evidence, and reporting guidelines; scope checks to the requested draft or revision.
2. Build an evidence outline and preserve the supplied methods, numbers, units, uncertainty, limitations, and provenance. Never invent studies, results, approvals, or references.
3. Use the local consistency, claim, reference, and manifest tools where applicable; report unresolved evidence and retain human responsibility for authorship and submission.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
