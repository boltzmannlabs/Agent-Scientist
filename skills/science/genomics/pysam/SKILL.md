---
name: pysam
description: Inspect and process sequencing files with pysam.
version: 2.1+sci.1
author: K-Dense Inc.; Sci adaptation for Agent Scientist
license: MIT
platforms:
  - linux
metadata:
  version: '2.1'
  skill-author: K-Dense Inc.
  sci:
    category: science/genomics
    tags:
      - science
      - genomics
    related_skills:
      - genomic-coordinates
      - biopython
  upstream:
    url: https://github.com/K-Dense-AI/scientific-agent-skills
    revision: 49c6e97775eaa18ba791bebe23162a70ae601c18
---

# Pysam Skill

Inspect and process sequencing files with pysam. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): `pysam==0.24.0`.
- Optional prerequisites: Matching reference FASTA and indexes for CRAM or indexed queries
- Companion skills (check availability with `skills_list`): `genomic-coordinates`, `biopython`
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

- `scripts/alignment_qc.py` — CLI
- `scripts/filter_alignments.py` — CLI
- `scripts/inspect_hts.py` — CLI
- `scripts/variant_summary.py` — CLI

## Procedure

1. Identify SAM/BAM/CRAM/VCF/FASTA format, reference assembly, sort order, and index availability.
2. Keep zero-based half-open Python intervals separate from one-based region strings; verify reference contigs and CRAM reference identity.
3. Stream bounded summaries or write derived outputs without overwriting source data; validate sort/index requirements and report filters and counts.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
