---
name: image-editing
description: Use when modifying or compositing raster images.
metadata:
  sci:
    tags:
      - images
      - editing
      - compositing
      - raster
    category: productivity
version: 1.0.0
author: Boltzmann Labs
license: 'Project-authored instructions: see repository LICENSE.'
platforms:
  - linux
  - macos
  - windows
---

# Image editing Skill

Use this skill for requests to add, remove, overlay, annotate, crop, resize, or otherwise modify an existing image.

## When to Use

Use for requests matching the workflow below; do not extend the scientific scope without clarification.

## Prerequisites

Inspect current tools with `tool_search` where available and installed skills with `skills_list`. Service connections, authorization, datasets, and scientific software are not included merely by installing these instructions. Verify the prerequisites in the procedure; obtain approval before downloads, installation, or execution.

## How to Run

Use `read_file` for supplied documents and `search_files` for local discovery. Use configured scientific tools when suitable; any local execution uses `terminal` in an approved environment, never an ad hoc modification of the Agent Scientist runtime. Keep credentials and private samples out of reusable instructions.

## Quick Reference

Confirm the requested input, output, available tools, and prerequisites before following the workflow. These instructions are not proof of scientific validity or an installed service.

## Procedure

1. Identify the source image and preserve it unchanged. Create derived outputs beside it with a descriptive filename.
2. Inspect the source visually before editing. Use image analysis to choose a suitable placement, scale, crop, or region rather than guessing from filenames or dimensions alone.
3. Prefer a reproducible local script for edits. Write the script to a file, run it, and keep the script with the derived artifact when useful; avoid opaque inline one-liners for multi-step image composition.
4. For overlays, create a separate RGBA layer, composite it onto the source, and save to a new output path. Keep the original resolution unless the user requests resizing.
5. Verify the output in two ways: inspect file type/dimensions/size and load the edited image visually. Confirm the requested element is present, the source scene remains intact, and there are no obvious placement or clipping errors.
6. Report the absolute output path, format, and key verification result concisely. Mention when an element is a stylized approximation rather than an exact asset.

## Pitfalls

- Never overwrite the user's original image unless explicitly requested; reversible derived files make comparison and recovery possible.
- Use coordinate transforms consistently: if drawing in a scaled coordinate system, scale offsets around the anchor rather than scaling absolute image coordinates, because scaling the anchor itself can place all artwork outside the canvas.
- Always perform a visual verification after rendering; a successful image-file write does not prove that the overlay is visible or correctly positioned.
- Prefer openly licensed or user-provided assets for imported overlays. If no asset is available, create a clearly described stylized approximation instead of implying that a protected source asset was used.
- Keep generated scripts deterministic and name outputs by the edit, not by a transient session or error.

## Verification

Inspect actual outputs, provenance, counts, units, and limitations. Report missing dependencies or partial results honestly. A successful command or security review does not establish scientific correctness.

## References

- The compositing and coordinate-placement checks are included above; no separate reference file is bundled. Use `vision_analyze` to verify the resulting image where available.
