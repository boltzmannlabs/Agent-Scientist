---
title: "Image Retrieval And Compositing — Use when editing or compositing images from a source URL"
sidebar_label: "Image Retrieval And Compositing"
description: "Use when editing or compositing images from a source URL"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Image Retrieval And Compositing

Use when editing or compositing images from a source URL.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/productivity/image-retrieval-and-compositing` |
| Version | `1.0.0` |
| Author | Boltzmann Labs |
| License | Project-authored instructions: see repository LICENSE. |
| Platforms | linux, macos, windows |
| Tags | `images`, `download`, `compositing`, `pillow`, `visual-verification` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Image Retrieval and Compositing Skill

Use this skill when the user asks to download an image, add an image or character to an existing image, or edit a locally available raster image.

## When to Use

Use for requests matching the workflow below; do not extend the scientific scope without clarification.

## Prerequisites

Inspect current tools with `tool_search` where available and installed skills with `skills_list`. Service connections, authorization, datasets, and scientific software are not included merely by installing these instructions. Verify the prerequisites in the procedure; obtain approval before downloads, installation, or execution.

## How to Run

Use `read_file` for supplied documents and `search_files` for local discovery. Use configured scientific tools when suitable; any local execution uses `terminal` in an approved environment, never an ad hoc modification of the Agent Scientist runtime. Keep credentials and private samples out of reusable instructions.

## Quick Reference

Confirm the requested input, output, available tools, and prerequisites before following the workflow. These instructions are not proof of scientific validity or an installed service.

## Procedure

### Standing rules

- Prefer the exact image asset from the user-provided URL over drawing a substitute when the request names a recognizable subject and the source exposes a downloadable asset.
- Do not claim an image is free, public-domain, or licensed for reuse unless the source explicitly establishes that; preserve the source URL for attribution when relevant.
- Preserve the original image. Write edited results to a separate output path.
- Verify the downloaded asset's file type, dimensions, and transparency before compositing.
- Verify the final image visually before reporting completion; a successful file write alone is not enough.
- Report the absolute output path and identify the tools actually used, matching the user's standing preference.

1. Inspect the source page before choosing a substitute.
   - Fetch the user-provided URL with `curl -L --fail -A 'Mozilla/5.0'`.
   - Search the saved HTML for `og:image`, `data-share-image`, `data-embed-img`, JSON-LD `contentUrl`, or a direct `.png`/`.jpg`/`.jpeg` URL.
   - Prefer the full-resolution download URL over a thumbnail URL.
2. Download the asset.
   - Use `curl -L --fail -A 'Mozilla/5.0' '<asset-url>' -o '<scratch>/<asset-name>'`.
   - Run `file` and, when available, `identify` to confirm the artifact is an image and capture dimensions/color mode.
   - If the asset is a transparent PNG, retain its alpha channel.
3. Inspect both images before editing.
   - Use visual analysis to choose a non-destructive placement area and estimate scale.
   - Keep the requested subject visible without obscuring the main scene unless the user asks for occlusion.
4. Composite with Pillow or another verified local image library.
   - Load the background as RGBA and the asset as RGBA.
   - Resize with a high-quality resampler.
   - Add a soft shadow only when it improves grounding and does not alter the source asset.
   - Alpha-composite onto a new output file; do not overwrite the source.
5. Verify the output.
   - Run `file` and size/dimension checks.
   - Use visual analysis to confirm the requested asset is actually present, the background remains intact, and the placement is usable.
   - If verification fails, fix the transform or placement and rerun; do not report success from the first write alone.
6. Report only the result needed by the user: output path, concise verification, and tools used. Mention source attribution or licensing uncertainty when it matters.

## Pitfalls

- Check the supplied page for its actual asset URL before drawing a replacement; many image pages expose a direct download link in metadata even when page extraction is imperfect.
- Do not stop after a browser failure; use the page URL with `curl` and parse the saved HTML when browser automation is unavailable.
- Do not use a thumbnail when a full-resolution download path is present; thumbnails can be too small for clean compositing.
- Keep coordinate transforms explicit when scaling overlays: scale the offset terms separately from the image-relative coordinates, or the overlay may render off-canvas.
- Visually verify after compositing; an incorrect transform can produce a valid image file with no visible overlay.

## Verification

Inspect actual outputs, provenance, counts, units, and limitations. Report missing dependencies or partial results honestly. A successful command or security review does not establish scientific correctness.
