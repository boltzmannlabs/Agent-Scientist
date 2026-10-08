---
title: "Exploratory Data Analysis — Inspect datasets, missingness, leakage, and distributions"
sidebar_label: "Exploratory Data Analysis"
description: "Inspect datasets, missingness, leakage, and distributions"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Exploratory Data Analysis

Inspect datasets, missingness, leakage, and distributions.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/science/data-analysis/exploratory-data-analysis` |
| Version | `1.2+sci.1` |
| Author | K-Dense Inc.; Sci adaptation for Agent Scientist |
| License | MIT |
| Platforms | linux |
| Tags | `science`, `data-analysis` |
| Related skills | [`statistical-analysis`](../../bundled/science/science-data-analysis-statistical-analysis.md), [`scientific-visualization`](../../bundled/science/science-visualization-scientific-visualization.md) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Exploratory Data Analysis Skill

Inspect datasets, missingness, leakage, and distributions. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): `numpy==2.5.3`, `pandas==2.3.3`, `h5py==3.16.0`, `biopython==1.87`, `pillow==12.3.0`, `tifffile==2026.9.20`.
- Optional prerequisites: polars for alternate table processing
- Companion skills (check availability with `skills_list`): `statistical-analysis`, `scientific-visualization`
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

- `scripts/capability_manifest.py` — CLI
- `scripts/distribution_sensitivity.py` — CLI
- `scripts/eda_analyzer.py` — CLI
- `scripts/image_inspector.py` — CLI
- `scripts/missingness_leakage_audit.py` — CLI
- `scripts/report_scaffold.py` — CLI
- `scripts/sequence_inspector.py` — CLI
- `scripts/tabular_profile.py` — CLI

## Procedure

1. Identify the observation unit, provenance, units, missing codes, groups, and data split before interpreting summaries.
2. Run the capability manifest before the narrowest supported inspector. Respect its file-size and format limits; reference-only formats require domain tooling.
3. Report scanned scope, truncation, missingness, and sensitivity to outliers; preserve raw inputs and keep exploratory claims separate from confirmatory inference.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
