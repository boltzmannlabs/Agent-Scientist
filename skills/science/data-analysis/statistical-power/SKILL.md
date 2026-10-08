---
name: statistical-power
description: Estimate sample size, power, and detectable effects.
version: 1.1+sci.1
author: K-Dense Inc.; Sci adaptation for Agent Scientist
license: MIT license
platforms:
  - linux
metadata:
  version: '1.1'
  skill-author: K-Dense Inc.
  sci:
    category: science/data-analysis
    tags:
      - science
      - data-analysis
    related_skills:
      - experimental-design
      - statistical-analysis
  upstream:
    url: https://github.com/K-Dense-AI/scientific-agent-skills
    revision: 49c6e97775eaa18ba791bebe23162a70ae601c18
---

# Statistical Power Skill

Estimate sample size, power, and detectable effects. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): `statsmodels==0.14.6`, `scipy==1.16.3`, `pingouin==0.6.1`, `numpy==2.5.3`, `pandas==2.3.3`, `matplotlib==3.11.2`.
- Optional prerequisites: lifelines for optional survival simulations
- Companion skills (check availability with `skills_list`): `experimental-design`, `statistical-analysis`
- Other skills named in upstream references are optional and may be absent. Use `skills_list` before loading one; a Python package is not a skill dependency.

## How to Run

Replace `<science-python>` in the examples with the verified interpreter path; it is a placeholder, not a shell command. Resolve `SCI_SKILL_DIR`, where used, to this installed skill directory. Check current tools first: prefer an authorized matching scientific tool, including Boltzmann when applicable. Use local execution only when appropriate or explicitly requested, and explain any fallback.

Use Sci `read_file` and `search_files` for inspection and `terminal` for execution. Read `references/upstream-workflow.md` and the relevant API reference before implementing an unfamiliar operation.

Run Python API examples with `<science-python>` through `terminal`. This skill has no argparse command-line helpers; import its documented functions where provided. Keep input data unchanged and write generated artifacts in the task workspace. Historical installation examples do not authorize package installation. Never modify the Agent Scientist runtime environment.

## Quick Reference

- `scripts/power.py` — Python module; import its functions
- `scripts/simulate_power.py` — Python module; import its functions

## Procedure

1. Specify design, effect definition, alpha, target power, allocation, variance, dependence, and attrition assumptions.
2. Use an appropriate analytic solver or seeded simulation; report sensitivity across plausible effect sizes and uncertainty in Monte Carlo estimates.
3. State whether sample size is per arm, total, cluster, or biological replicate; avoid interpreting observed post hoc power as new evidence.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
