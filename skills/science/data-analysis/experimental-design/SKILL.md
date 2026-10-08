---
name: experimental-design
description: Plan controls, replication, randomization, and blocking.
version: 1.2+sci.1
author: K-Dense Inc.; Sci adaptation for Agent Scientist
license: MIT license
platforms:
  - linux
metadata:
  version: '1.2'
  skill-author: K-Dense Inc.
  sci:
    category: science/data-analysis
    tags:
      - science
      - data-analysis
    related_skills:
      - statistical-power
      - statistical-analysis
      - scientific-critical-thinking
  upstream:
    url: https://github.com/K-Dense-AI/scientific-agent-skills
    revision: 49c6e97775eaa18ba791bebe23162a70ae601c18
---

# Experimental Design Skill

Plan controls, replication, randomization, and blocking. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): `numpy==2.5.3`, `pandas==2.3.3`, `pyDOE3==1.6.2`.
- Optional prerequisites: No additional service is required for the core workflow.
- Companion skills (check availability with `skills_list`): `statistical-power`, `statistical-analysis`, `scientific-critical-thinking`
- Other skills named in upstream references are optional and may be absent. Use `skills_list` before loading one; a Python package is not a skill dependency.

## How to Run

Replace `<science-python>` in the examples with the verified interpreter path; it is a placeholder, not a shell command. Resolve `SCI_SKILL_DIR`, where used, to this installed skill directory. Check current tools first: prefer an authorized matching scientific tool, including Boltzmann when applicable. Use local execution only when appropriate or explicitly requested, and explain any fallback.

Use Sci `read_file` and `search_files` for inspection and `terminal` for execution. Read `references/upstream-workflow.md` and the relevant API reference before implementing an unfamiliar operation.

Run Python API examples with `<science-python>` through `terminal`. This skill has no argparse command-line helpers; import its documented functions where provided. Keep input data unchanged and write generated artifacts in the task workspace. Historical installation examples do not authorize package installation. Never modify the Agent Scientist runtime environment.

## Quick Reference

- `scripts/doe_designs.py` — Python module; import its functions
- `scripts/randomization.py` — Python module; import its functions

## Procedure

1. Define the question, estimand, experimental unit, treatment factors, and feasible measurement structure before data collection.
2. Separate biological from technical replication; choose randomization, blocking, controls, and allocation so effects are identifiable.
3. Record the seed and allocation procedure, check balance and confounding, and justify sample size with statistical-power. This is statistical design guidance, not a laboratory protocol.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
