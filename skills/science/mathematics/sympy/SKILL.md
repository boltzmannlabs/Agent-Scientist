---
name: sympy
description: Solve and verify exact symbolic mathematics in Python.
version: 1.3+sci.1
author: K-Dense Inc.; Sci adaptation for Agent Scientist
license: https://github.com/sympy/sympy/blob/master/LICENSE
platforms:
  - linux
metadata:
  version: '1.3'
  skill-author: K-Dense Inc.
  sci:
    category: science/mathematics
    tags:
      - science
      - mathematics
    related_skills:
      - uncertainty-and-units
      - matplotlib
  upstream:
    url: https://github.com/K-Dense-AI/scientific-agent-skills
    revision: 49c6e97775eaa18ba791bebe23162a70ae601c18
---

# Sympy Skill

Solve and verify exact symbolic mathematics in Python. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): `sympy==1.14.0`, `numpy==2.5.3`, `scipy==1.16.3`.
- Optional prerequisites: C or Fortran compiler for compiled code generation
- Companion skills (check availability with `skills_list`): `uncertainty-and-units`, `matplotlib`
- Other skills named in upstream references are optional and may be absent. Use `skills_list` before loading one; a Python package is not a skill dependency.

## How to Run

Replace `<science-python>` in the examples with the verified interpreter path; it is a placeholder, not a shell command. Resolve `SCI_SKILL_DIR`, where used, to this installed skill directory. Check current tools first: prefer an authorized matching scientific tool, including Boltzmann when applicable. Use local execution only when appropriate or explicitly requested, and explain any fallback.

Use Sci `read_file` and `search_files` for inspection and `terminal` for execution. Read `references/upstream-workflow.md` and the relevant API reference before implementing an unfamiliar operation.

Run Python API examples with `<science-python>` through `terminal`. This skill has no bundled command-line helpers. Keep input data unchanged and write generated artifacts in the task workspace. Historical installation examples do not authorize package installation. Never modify the Agent Scientist runtime environment.

## Quick Reference

Use the Python API examples in the detailed workflow.

## Procedure

1. Declare symbols and their domains and assumptions explicitly; use exact rational values where exactness matters.
2. Choose the solver appropriate to the equation, system, or domain; distinguish symbolic solutions from numerical approximations.
3. Substitute results back into the original problem and check domains and singularities before converting with lambdify or exporting formulas.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
