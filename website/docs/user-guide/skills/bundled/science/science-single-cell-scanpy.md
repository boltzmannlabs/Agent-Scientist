---
title: "Scanpy — Analyze single-cell data with QC, clustering, and markers"
sidebar_label: "Scanpy"
description: "Analyze single-cell data with QC, clustering, and markers"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Scanpy

Analyze single-cell data with QC, clustering, and markers.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/science/single-cell/scanpy` |
| Version | `1.6+sci.1` |
| Author | K-Dense Inc.; Sci adaptation for Agent Scientist |
| License | BSD-3-Clause |
| Platforms | linux |
| Tags | `science`, `single-cell` |
| Related skills | [`anndata`](../../bundled/science/science-single-cell-anndata.md), [`pydeseq2`](../../bundled/science/science-transcriptomics-pydeseq2.md), [`pathway-enrichment`](../../bundled/science/science-bioinformatics-pathway-enrichment.md), [`get-available-resources`](../../bundled/science/science-computing-get-available-resources.md) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Scanpy Skill

Analyze single-cell data with QC, clustering, and markers. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): `scanpy==1.12.1`, `anndata==0.12.16`, `leidenalg==0.12.0`, `igraph==1.0.0`, `numpy==2.5.3`, `pandas==2.3.3`.
- Optional prerequisites: R and conversion packages for RDS/Seurat input; harmonypy or bbknn for their batch-correction methods; scvi-tools is an optional separate skill/package
- Companion skills (check availability with `skills_list`): `anndata`, `pydeseq2`, `pathway-enrichment`, `get-available-resources`
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

- `scripts/annotate.py` — CLI
- `scripts/batch_correct.py` — CLI
- `scripts/cluster.py` — CLI
- `scripts/convert.py` — CLI
- `scripts/find_markers.py` — CLI
- `scripts/inspect_data.py` — CLI
- `scripts/plot.py` — CLI
- `scripts/preprocess.py` — CLI
- `scripts/pseudobulk.py` — CLI
- `scripts/qc_analysis.py` — CLI
- `scripts/reduce_dimensions.py` — CLI
- `scripts/run_pipeline.py` — CLI
- `scripts/score_genes.py` — CLI
- `scripts/subset.py` — CLI

## Procedure

1. Inspect AnnData, sample hierarchy, metadata, and whether values are counts or transformed; preserve the raw-count layer.
2. Select and document QC, normalization, feature selection, reduction, and clustering choices for the dataset; do not silently repeat transformations.
3. Distinguish descriptive cell markers from sample-level inference; use biological-replicate pseudobulk when appropriate and verify annotations with independent evidence.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
