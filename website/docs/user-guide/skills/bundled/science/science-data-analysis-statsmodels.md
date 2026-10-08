---
title: "Statsmodels — Fit statistical models and check inference diagnostics"
sidebar_label: "Statsmodels"
description: "Fit statistical models and check inference diagnostics"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Statsmodels

Fit statistical models and check inference diagnostics.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/science/data-analysis/statsmodels` |
| Version | `1.3+sci.1` |
| Author | K-Dense Inc.; Sci adaptation for Agent Scientist |
| License | BSD-3-Clause license |
| Platforms | linux |
| Tags | `science`, `data-analysis` |
| Related skills | [`statistical-analysis`](../../bundled/science/science-data-analysis-statistical-analysis.md), [`experimental-design`](../../bundled/science/science-data-analysis-experimental-design.md) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Statsmodels Skill

Fit statistical models and check inference diagnostics. This package adapts K-Dense's workflow and helpers to the Agent Scientist runtime.

## When to Use

Use when the request needs the capability above. Apply the relevant steps to the user's scope; do not turn a small analysis into an unrelated end-to-end project.

## Prerequisites

- An approved isolated Linux scientific Python environment (Python 3.12 was used for the original validation). Resolve and verify its interpreter on this machine; no environment or dependency is installed by this skill.
- Reference dependency versions (check availability and compatibility before execution): `statsmodels==0.14.6`, `numpy==2.5.3`, `pandas==2.3.3`, `scipy==1.16.3`.
- Optional prerequisites: scikit-learn for optional prediction metrics
- Companion skills (check availability with `skills_list`): `statistical-analysis`, `experimental-design`
- Other skills named in upstream references are optional and may be absent. Use `skills_list` before loading one; a Python package is not a skill dependency.

## How to Run

Replace `<science-python>` in the examples with the verified interpreter path; it is a placeholder, not a shell command. Resolve `SCI_SKILL_DIR`, where used, to this installed skill directory. Check current tools first: prefer an authorized matching scientific tool, including Boltzmann when applicable. Use local execution only when appropriate or explicitly requested, and explain any fallback.

Use Sci `read_file` and `search_files` for inspection and `terminal` for execution. Read `references/upstream-workflow.md` and the relevant API reference before implementing an unfamiliar operation.

Run Python API examples with `<science-python>` through `terminal`. This skill has no bundled command-line helpers. Keep input data unchanged and write generated artifacts in the task workspace. Historical installation examples do not authorize package installation. Never modify the Agent Scientist runtime environment.

## Quick Reference

Use the Python API examples in the detailed workflow.

## Procedure

1. Choose model family, link, design matrix, reference levels, dependence structure, and missing-data treatment explicitly.
2. Fit and inspect convergence, rank, residuals, influential observations, and model assumptions; handle intercepts and categorical encodings deliberately.
3. Report estimands and intervals with the covariance method and limitations; a fitted model does not automatically support causal inference.

## Pitfalls

- Preserve input identifiers, units, provenance, sample hierarchy, and the distinction between retrieved facts, computed outputs, and interpretation.
- Do not assume optional services, datasets, credentials, GUI backends, or companion skills are configured. Explain a missing prerequisite before the dependent step.
- Examples in references include historical package versions. Verify the actual environment and record its dependency versions; changing packages requires approval and revalidation.

## Verification

Check exit status and scientific payload, not just whether a command ran. Verify shapes, units, record counts and identities, numerical tolerances, and output artifacts as applicable. Report methods, versions, assumptions, and unresolved limitations. Successful local tests do not establish live-service availability or scientific validity for a new dataset.

Detailed workflow: `references/upstream-workflow.md`. Upstream notices and revision are in `LICENSE.upstream.md` and `provenance.json`.
