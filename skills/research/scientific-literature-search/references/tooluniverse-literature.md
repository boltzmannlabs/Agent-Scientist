# ToolUniverse Literature Search Reference

## Backend selection

| Need | Preferred capability | Why |
|---|---|---|
| Biomedical articles and abstracts | `EuropePMC_search_articles` | Biomedical coverage, fielded queries, dates, and hit counts |
| PubMed recent-paper lists | `PubMed_search_articles` | PMID-based discovery, publication-date sorting, date bounds, article types, and optional abstracts |
| Known PubMed-paper metadata | `PubMed_get_article` | Abstract and available publication-date, author, journal, and MeSH metadata; inspect date precision and omissions rather than assuming every field is present |
| Broad scholarly discovery | `SemanticScholar_search_papers` | Cross-disciplinary index, abstracts, TLDRs, venues, and identifiers |
| New preprints | `ArXiv_search_papers` | Publication dates, categories, abstracts, and open PDFs |
| Known-paper metadata | `SemanticScholar_get_paper` | DOI, PMID, arXiv, or Semantic Scholar identifiers |
| Related-work discovery | `SemanticScholar_get_recommendations` | Recommendations from a seed paper |
| Open full text | `EuropePMC_get_full_text` | Structured sections, figures, tables, and references |
| Citation network | Europe PMC or Semantic Scholar citation/reference tools | Follow impact and intellectual lineage |
| Term-focused PDF reading | `ArXiv_get_pdf_snippets` | Bounded text around specified terms |
| Clinical trial discovery | `ClinicalTrials_search_studies` | Search ClinicalTrials.gov by condition, intervention, status, phase, or free-text terms |
| Clinical trial details | `ClinicalTrials_get_study` | Retrieve official title, status, phase, intervention, summary, and registry eligibility |
| Trial eligibility batch | `get_clinical_trial_eligibility_criteria` | Retrieve inclusion/exclusion criteria for multiple NCT IDs |

For clinical-trial searches, prefer `ClinicalTrials_search_studies` with a condition such as beta-thalassemia and a free-text term such as CRISPR or gene editing. Then call `ClinicalTrials_get_study` for each selected NCT ID and `get_clinical_trial_eligibility_criteria` for structured eligibility. Search rows are discovery-level metadata; do not report intervention details or eligibility summaries from them alone.

## Reusable discovery queries

Start with a focused ToolUniverse capability query:

```text
Find tools for searching biomedical literature by keyword, publication date, abstract, and recentness.
```

If that returns no tools, broaden it:

```text
Find tools for PubMed, Europe PMC, Semantic Scholar, arXiv, or scientific paper search.
```

For CRISPR, search with method and application variants rather than only the acronym:

```text
CRISPR OR Cas9 OR Cas12 OR Cas13 OR base editing OR prime editing OR gene editing
```

Combine the core method with the biological target, system, and date filter supported by the backend. Keep separate queries for discovery, delivery, off-target effects, clinical studies, and therapeutic applications when a broad query produces noisy results.

## Direct PubMed MCP recipe

Use this branch when the user requests the connected PubMed MCP server rather than ToolUniverse. Resolve `QUERY`, `START`, and `END` from the requested topic and verified date window before invoking the example calls.

1. Discover the refreshed capabilities with `tool_search(queries=["pubmed search articles", "pubmed fetch articles"])`, then inspect the returned search and fetch names with `tool_describe`. Do not transfer ToolUniverse argument names into this adapter.
2. Invoke the discovered `mcp__pubmed__pubmed_search_articles` through `tool_call` with `query: QUERY`, `dateRange: {minDate: START, maxDate: END, dateType: "pdat"}`, `sort: "pub_date"`, `maxResults: 20`, and `summaryCount: 20`. Size the candidate page above the requested final count so relevance screening can discard false positives; both date bounds must be resolved before searching.
3. Prefer the returned `structuredContent` for PMID handoff and hit counts; the prose result mirrors the same records and is not a second source. Keep `totalCount` separate from the page size. For humanization searches, distinguish engineered antibodies, VHHs, and scFvs from humanized model organisms, receptors, and unrelated proteins; an antibody mention elsewhere in an abstract can satisfy a broad query without direct topic relevance.
4. Invoke the discovered `mcp__pubmed__pubmed_fetch_articles` once with `pmids` set to the selected identifier array; set `includeMesh: false` and `includeGrants: false` when the requested deliverable needs only bibliographic fields and abstracts. Verify response identities and complete coverage, including unavailable or deferred records, before selecting the final count.
5. Ground publication precision in `journalInfo.publicationDate`, not a potentially normalized summary date. Report an explicitly returned electronic date from `articleDates` as online publication, separately from the journal issue date. Preserve a missing day rather than converting a month-only record to its first day.
6. Register each fetched `pubmedUrl` with a task-specific `grounded-citations` ledger, verify unique PMIDs and the date window programmatically, and render the compact requested list. Reuse the complete metadata batch instead of refetching individual articles without a discrepancy.

## ToolUniverse recent PubMed recipe

1. Discover `PubMed_search_articles` and `PubMed_get_article` through ToolUniverse before invoking them.
2. Search with two to four core concepts plus synonyms; set `datetype` to `pdat`, provide explicit `mindate`/`maxdate`, request `include_abstract`, and sort by `pub_date`.
3. Check returned publication dates against the requested minimum and maximum, even if the API accepted both filters. Preserve year-only or month-only precision and distinguish electronic-first dates from issue dates where provided.
4. Select the requested number of directly relevant records, then call `PubMed_get_article` with a comma-separated PMID string when supported.
5. Summarize from the retrieved abstract, label reviews versus original studies, and use `et al.` when the returned author list is visibly truncated.

## Structure-to-literature identifier handoff

1. Discover and inspect `RCSBGraphQL_get_structure_summary`; execute it with the supplied `pdb_id`.
2. Match each returned row by `pdb_id`, then read its `citation_pubmed_id`; do not associate a batch response by array position, because returned order can differ from requested order. For a single entry, first verify that the row identifies the requested structure. Stop the PMID-dependent lookup if the field is absent; never supply a remembered citation identifier.
3. Discover and inspect `PubMed_get_article`, then pass the returned value as `pmid`.
4. Verify the literature response's PMID matches the transferred identifier. Report title, available publication metadata, and an abstract-based summary with source links. Mark missing volume, issue, pages, or exact date as missing rather than completing them from memory.
5. Show the audit chain as input PDB ID → returned citation field/value → literature-tool argument → returned PMID. Separate biological interpretation from the retrieved metadata; structure provenance alone does not establish binding affinity.

## Result handling

Preserve DOI, PMID, PMCID, arXiv, and Semantic Scholar IDs exactly as returned. Record both the number returned and the backend's total matching count. Label peer-reviewed articles, preprints, reviews, corrections, and retractions separately before synthesis.
