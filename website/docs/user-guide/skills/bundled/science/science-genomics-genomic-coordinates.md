---
title: "Genomic Coordinates — Validate genomic intervals, assemblies, and conversions"
sidebar_label: "Genomic Coordinates"
description: "Validate genomic intervals, assemblies, and conversions"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Genomic Coordinates

Validate genomic intervals, assemblies, and conversions.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/science/genomics/genomic-coordinates` |
| Version | `1.1+sci.1` |
| Author | K-Dense Inc.; Sci adaptation for Agent Scientist |
| License | MIT |
| Platforms | linux |
| Tags | `science`, `genomics` |
| Related skills | [`pysam`](../../bundled/science/science-genomics-pysam.md), [`biopython`](../../bundled/science/science-bioinformatics-biopython.md) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Genomic Coordinates Skill

Validate genomic intervals, assemblies, and conversions. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): Python standard library or guidance only.
- Optional prerequisites: Reference FASTA for variant normalization
- Companion skills (check availability with `skills_list`): `pysam`, `biopython`
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

- `scripts/audit_intervals.py` — CLI
- `scripts/check_contigs.py` — CLI
- `scripts/convert_coords.py` — CLI
- `scripts/normalize_variant.py` — CLI

## Procedure

1. Declare reference assembly, contig naming, coordinate origin, interval closure, strand, and feature type.
2. Convert interval conventions explicitly; variants and transcript/protein positions require their own normalization or mapping rules.
3. Validate boundaries and joins against the same assembly. A format conversion does not perform assembly liftover.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
