---
name: pathway-enrichment
description: Interpret gene sets with ORA and ranked enrichment.
version: 1.1+sci.1
author: K-Dense Inc.; Sci adaptation for Agent Scientist
license: MIT
platforms:
  - linux
metadata:
  version: '1.1'
  skill-author: K-Dense Inc.
  sci:
    category: science/bioinformatics
    tags:
      - science
      - bioinformatics
    related_skills:
      - pydeseq2
      - scanpy
      - bioservices
  upstream:
    url: https://github.com/K-Dense-AI/scientific-agent-skills
    revision: 49c6e97775eaa18ba791bebe23162a70ae601c18
---

# Pathway Enrichment Skill

Interpret gene sets with ORA and ranked enrichment. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): `gseapy==1.3.1`, `gprofiler-official==1.0.0`, `numpy==2.5.3`, `pandas==2.3.3`.
- Optional prerequisites: Network for remote Enrichr or g:Profiler queries; local GMT files support offline workflows
- Companion skills (check availability with `skills_list`): `pydeseq2`, `scanpy`, `bioservices`
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

- `scripts/run_enrichment.py` — CLI

## Procedure

1. Choose thresholded-list ORA versus ranked-list GSEA based on the question; establish organism, identifier namespace, gene universe, and gene-set version.
2. Preserve the measured/tested background, handle duplicate identifiers explicitly, and record thresholds, ranking statistic, seeds, and multiple-testing correction.
3. Report enrichment as association, not proof of pathway activation or causality. Keep directionality, overlap, and database coverage limitations explicit.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
