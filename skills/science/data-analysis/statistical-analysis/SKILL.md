---
name: statistical-analysis
description: Select tests, check assumptions, and report effect sizes.
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
      - statsmodels
      - statistical-power
      - experimental-design
  upstream:
    url: https://github.com/K-Dense-AI/scientific-agent-skills
    revision: 49c6e97775eaa18ba791bebe23162a70ae601c18
---

# Statistical Analysis Skill

Select tests, check assumptions, and report effect sizes. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): `numpy==2.5.3`, `pandas==2.3.3`, `scipy==1.16.3`, `statsmodels==0.14.6`, `pingouin==0.6.1`, `matplotlib==3.11.2`, `seaborn==0.13.2`.
- Optional prerequisites: pymc and arviz for Bayesian examples
- Companion skills (check availability with `skills_list`): `statsmodels`, `statistical-power`, `experimental-design`
- Other skills named in upstream references are optional and may be absent. Use `skills_list` before loading one; a Python package is not a skill dependency.

## How to Run

Replace `<science-python>` in the examples with the verified interpreter path; it is a placeholder, not a shell command. Resolve `SCI_SKILL_DIR`, where used, to this installed skill directory. Check current tools first: prefer an authorized matching scientific tool, including Boltzmann when applicable. Use local execution only when appropriate or explicitly requested, and explain any fallback.

Use Sci `read_file` and `search_files` for inspection and `terminal` for execution. Read `references/upstream-workflow.md` and the relevant API reference before implementing an unfamiliar operation.

Run Python API examples with `<science-python>` through `terminal`. This skill has no argparse command-line helpers; import its documented functions where provided. Keep input data unchanged and write generated artifacts in the task workspace. Historical installation examples do not authorize package installation. Never modify the Agent Scientist runtime environment.

## Quick Reference

- `scripts/assumption_checks.py` — Python module; import its functions

## Procedure

1. Specify estimand, observational unit, pairing, independence, and planned comparisons before fitting a model.
2. Inspect distributions and diagnostics; choose methods for the design rather than switching mechanically on a normality-test p-value.
3. Report effect sizes and intervals with exact test results, multiplicity handling, assumptions, missing-data decisions, and limitations. Statistical significance does not establish causality or practical importance.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
