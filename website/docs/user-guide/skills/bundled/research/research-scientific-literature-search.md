---
title: "Scientific Literature Search — Use when searching scientific literature"
sidebar_label: "Scientific Literature Search"
description: "Use when searching scientific literature"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Scientific Literature Search

Use when searching scientific literature.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/research/scientific-literature-search` |
| Version | `1.0.0` |
| Author | Sci Agent |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `Research`, `Literature`, `Biomedical`, `Papers`, `CRISPR`, `PubMed`, `Europe PMC`, `Semantic Scholar`, `ArXiv`, `ToolUniverse` |
| Related skills | [`arxiv`](../../bundled/research/research-arxiv.md), [`grounded-citations`](../../bundled/research/research-grounded-citations.md), [`pdf`](../../bundled/productivity/productivity-pdf.md) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Scientific Literature Search Skill

Use this skill for literature discovery, recent-paper scans, evidence gathering, and related-work exploration across biomedical databases, scholarly indexes, and preprint repositories.

## When to Use

Use for requests matching the workflow below; do not extend the scientific scope without clarification.

## Prerequisites

Inspect current tools with `tool_search` where available and installed skills with `skills_list`. Service connections, authorization, datasets, and scientific software are not included merely by installing these instructions. Verify the prerequisites in the procedure; obtain approval before downloads, installation, or execution.

## How to Run

Use `read_file` for supplied documents and `search_files` for local discovery. Use configured scientific tools when suitable; any local execution uses `terminal` in an approved environment, never an ad hoc modification of the Agent Scientist runtime. Keep credentials and private samples out of reusable instructions.

## Quick Reference

Confirm the requested input, output, available tools, and prerequisites before following the workflow. These instructions are not proof of scientific validity or an installed service.

## Procedure

1. Define the search target before choosing a backend: topic or mechanism, organism or disease, study type, date window, and whether the user needs abstracts, full text, citations, recommendations, or only a tool list.

2. Resolve the requested backend and inspect its live operation schemas before execution; direct PubMed MCP and ToolUniverse expose different names and argument shapes. For direct PubMed MCP, use `tool_search` for PubMed search and article-fetch capabilities, then `tool_describe` on the returned names before calling them through `tool_call`; follow the direct-MCP recipe in `references/tooluniverse-literature.md`. If the user asks to use ToolUniverse, call `mcp__tooluniverse__find_tools` with a focused capability query. If semantic discovery misses an explicitly named tool, retry that exact name with `search_method="keyword"`; do not combine several exact tool names in one query. Inspect the execution-wrapper schema before using it. For backend-restricted integration tests, keep retrievals and calculations on the requested backend, never replace missing output with remembered facts, and stop dependent operations when required inputs are absent. Count scientific operations separately from discovery/schema calls when testing a single-tool constraint.

3. Honor a named backend throughout discovery and record enrichment; a small fixed-count PubMed list does not require an unrelated index. For broad or coverage-sensitive searches without a backend restriction, select a primary biomedical index and a complementary scholarly index. Prefer Europe PMC/PubMed-style search for biomedical records, Semantic Scholar for cross-disciplinary discovery and related papers, and arXiv for preprints. Use domain-specific full-text or citation tools only after identifying seed papers.

4. Search with explicit recency controls where the backend supports them. For broad concepts, run several narrow queries rather than one overloaded query; include synonyms, method names, and spelling variants. Record the backend's total-hit count separately from the number returned on the current page.

5. Inspect returned metadata before synthesizing: title, authors, publication date, venue, identifiers, abstract, open-access status, and whether the record is a preprint, correction, retraction, or duplicate. Preserve identifiers exactly as returned. Deduplicate by DOI or PMID before final selection, retaining every discovery source for merged records. Screen abstracts for original experiments and direct topic relevance; a NOT-review filter can still admit historical overviews, and a topic search can return papers that only mention the target in passing. Do not classify a Journal Article as original research from that label alone.

6. Enrich promising records with the appropriate follow-up tool: full paper metadata, open-access full text, references, citations, recommendations, or PDF snippets around a specific term. For PubMed deliverables, batch the selected PMIDs through the inspected backend's metadata operation: direct MCP `pubmed_fetch_articles` accepts a `pmids` array, whereas ToolUniverse `PubMed_get_article` may accept a comma-separated string. Join results by PMID, check that every requested record was resolved, and retrieve any deferred records before claiming the requested count. Reuse an already complete batch rather than repeating individual fetches without a missing field or discrepancy. Treat search snippets as discovery evidence only. For an abstract-based evidence table, derive the research-approach and main-finding fields strictly from each fetched abstract, mark an absent abstract as `unavailable`, and reproduce full abstract text only when the user explicitly requests it.

7. For clinical-trial requests, discover ClinicalTrials.gov tools before invoking them. Search with the disease/condition plus a free-text intervention concept such as CRISPR, gene editing, Cas9, Cas12, or the therapy name; then retrieve each selected record with the study-detail tool and retrieve eligibility criteria with the batch eligibility tool when available. Select trials by direct intervention relevance, not merely by mentioning the disease or gene editing in background text.

8. Validate each retrieved publication date against both requested endpoints, not only the current date. Resolve an open-ended "since YEAR" request as January 1 of that year through the verified applicable current date, unless the user supplies another boundary. Some index APIs return records outside the requested window despite accepting date filters. Inspect the full record's publication-date components before assigning day-level precision: a search summary's first-of-month or first-of-year date can stand for a partial date. Preserve month-only and year-only precision. Distinguish electronic-first and issue dates when available and state the date basis used. When author output is truncated, mark the list with `et al.` instead of implying it is complete. For Vancouver-style references, format only bibliographic fields returned by the record; never reconstruct journal abbreviations, volume, issue, pagination, or article numbers from a DOI or model knowledge, and label required missing fields `unavailable`. For trial reports, state the registry-status snapshot date and preserve `UNKNOWN`, `NOT YET RECRUITING`, or `NA` exactly when returned rather than silently interpreting them.

9. For a grounded report or answer, register fetched sources as they arrive with the `grounded-citations` workflow, cite claims at sentence level, and verify the final citations before delivery. For a simple tool inventory, report tool names, what each is for, and the recommended starting combination without pretending that a literature search was performed.

10. Report coverage honestly: show exact queries and filters, usable records returned, and database-reported total hits separately for each search. Inspect nested error objects even when the outer status says success; an error placeholder is not an article and an unavailable total is not zero. Mark failed complementary-index coverage as incomplete and never claim cross-index deduplication when that index supplied no records. In integration-test reports, separate retrieved facts, calculated values, and interpretation; list actual scientific tools, exact identifier/sequence handoffs, source links, errors, and missing fields. Distinguish links returned by tools from links constructed from retrieved identifiers. Preserve partial date precision rather than inventing a month or day.

11. For multi-stage computational-biology requests, decompose the request into atomic operations before acting: target/sequence retrieval, candidate generation, numbering, structure prediction, docking, affinity, stability, developability, and validation. Discover alternatives by capability descriptions rather than requiring particular tool names. If semantic discovery is inconclusive, inspect `mcp__tooluniverse__grep_tools` and search its description field with focused text or regex patterns; inspect candidate schemas before execution. Distinguish executable services from package-information tools and existing-record retrieval, since describing software or finding a deposited simulation does not run the requested computation. Map every operation to a discovered tool, execute the supported stages, and label unsupported stages as unperformed; never repurpose a single-protein predictor or small-molecule docking tool as evidence for an antibody–antigen complex result. For each step in an integration workflow, report the actual tool/operation, exact arguments or a defined sequence reference, returned result and source, transformation, explicit output-field → next-input-field mapping, and status (SUCCESS, EMPTY, ERROR, UNSUPPORTED, or SKIPPED). Give a brief result after each stage and finish with comparison tables and a handoff audit, not just a tool inventory. Stop only the branch whose required input failed; continue independent branches with valid inputs. Join batch responses by returned identifiers rather than request order, because services can reorder records. Preserve source disagreements and distinguish source-reported sequence-identity tiers from newly computed identity. Batch necessary clarifications about execution permissions, target objective, and resource budget into one request before state-changing work. For paired-antibody sequence-to-structure evidence workflows, follow `references/antibody-evidence-handoffs.md`.

12. When the user asks for execution rather than a tool list, perform the available discovery and enrichment calls first, then produce the requested artifact only if every required stage has a validated tool path. If a stage is missing, return the executed partial results and the exact missing capability instead of inventing sequences, scores, structures, confidence values, or validation outcomes.

### ToolUniverse discovery notes

A successful discovery pass commonly yields tools for `SemanticScholar_search_papers`, `SemanticScholar_get_paper`, `SemanticScholar_get_recommendations`, `EuropePMC_search_articles`, `EuropePMC_get_full_text`, citation/reference traversal, and `ArXiv_search_papers`. Treat these names as discovered capabilities, not as guaranteed availability for a later invocation; refresh discovery if the runtime says a discovered name is unavailable.

For a concise tool inventory, group results into: discovery/search, record enrichment, full-text retrieval, and citation-network traversal. Recommend the smallest combination that satisfies the request.

See `references/tooluniverse-literature.md` for the backend-selection table and reusable query patterns.

## Pitfalls

- Broaden a failed capability search before declaring the catalog empty, because overly specific wording or category filters can hide otherwise relevant tools.
- Do not equate the page size with the corpus size; APIs often return a slice and expose the real hit count separately.
- Keep preprints and peer-reviewed articles labeled separately, because “recent” does not imply equivalent publication status.
- Preserve DOI, PMID, PMCID, arXiv, and Semantic Scholar identifiers exactly, because normalizing a token can break follow-up retrieval.
- Use a second index for important searches, because no single scholarly database has complete biomedical and preprint coverage.
- Do not cite a search-result description for claims that require an abstract or article body; retrieve the underlying record first.
- Use the inspected backend's publication-date controls instead of transferring argument names between PubMed adapters — direct MCP uses `dateRange`, while a ToolUniverse operation may use `mindate`/`maxdate`/`datetype`.
- For a ClinicalTrials.gov list, retrieve the full study record and eligibility criteria after discovery; search-result rows often omit the intervention description and detailed inclusion/exclusion rules needed for a useful answer.
- Preserve registry statuses exactly, including `UNKNOWN`, and label phase `NA` as not applicable or not reported rather than converting it to a conventional phase.
- For a short paper list, put the requested title, PMID, publication date, and retrieved link together for each record; identify the scientific tools actually used, and keep discovery plumbing secondary to the requested results.

## Verification

Inspect actual outputs, provenance, counts, units, and limitations. Report missing dependencies or partial results honestly. A successful command or security review does not establish scientific correctness.
