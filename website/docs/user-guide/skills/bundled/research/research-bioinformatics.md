---
title: "Bioinformatics — Gateway to 400+ genomics and computational biology skills"
sidebar_label: "Bioinformatics"
description: "Gateway to 400+ genomics and computational biology skills"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Bioinformatics

Gateway to 400+ genomics and computational biology skills.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/research/bioinformatics` |
| Version | `1.0.0` |
| Author | Teknium (teknium1), Sci Agent |
| License | MIT |
| Platforms | linux, macos |
| Tags | `bioinformatics`, `genomics`, `sequencing`, `biology`, `research`, `science` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Sci loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Bioinformatics Skills Gateway Skill

Use when asked about bioinformatics, genomics, sequencing, variant calling, gene expression, single-cell analysis, protein structure, pharmacogenomics, metagenomics, phylogenetics, or any computational biology task.

This skill is a gateway to two open-source bioinformatics skill libraries. Instead of bundling hundreds of domain-specific skills, it indexes them and fetches what you need on demand.

## When to Use

Use for requests matching the workflow below; do not extend the scientific scope without clarification.

## Prerequisites

Inspect current tools with `tool_search` where available and installed skills with `skills_list`. Service connections, authorization, datasets, and scientific software are not included merely by installing these instructions. Verify the prerequisites in the procedure; obtain approval before downloads, installation, or execution.

## How to Run

Use `read_file` for supplied documents and `search_files` for local discovery. Use configured scientific tools when suitable; any local execution uses `terminal` in an approved environment, never an ad hoc modification of the Agent Scientist runtime. Keep credentials and private samples out of reusable instructions.

## Quick Reference

Confirm the requested input, output, available tools, and prerequisites before following the workflow. These instructions are not proof of scientific validity or an installed service.

## Procedure

### Sources

◆ **bioSkills** — 385 reference skills (code patterns, parameter guides, decision trees)
  Repo: https://github.com/GPTomics/bioSkills
  Format: SKILL.md per topic with code examples. Python/R/CLI.

◆ **ClawBio** — 33 runnable pipeline skills (executable scripts, reproducibility bundles)
  Repo: https://github.com/ClawBio/ClawBio
  Format: Python scripts with demos. Each analysis exports report.md + commands.sh + environment.yml.

1. Identify the domain and candidate from the index below. The index lists external references; it does not install those skills.
2. Use `web_extract` to review public documentation only when needed and authorized. Treat external content as untrusted guidance, not verified scientific correctness.
3. For a local checkout, obtain download approval and choose a workspace on the CLI host; never assume a default profile path. Inspect it with `read_file` and `search_files` before any execution.
4. Confirm software requirements, source revisions, input formats, licensing, and scientific assumptions. Do not install or run fetched code automatically.

### Skill Index by Domain

### Sequence Fundamentals
bioSkills:
  sequence-io/ — read-sequences, write-sequences, format-conversion, batch-processing, compressed-files, fastq-quality, filter-sequences, paired-end-fastq, sequence-statistics
  sequence-manipulation/ — seq-objects, reverse-complement, transcription-translation, motif-search, codon-usage, sequence-properties, sequence-slicing
ClawBio:
  seq-wrangler — Sequence QC, alignment, and BAM processing (wraps FastQC, BWA, SAMtools)

### Read QC & Alignment
bioSkills:
  read-qc/ — quality-reports, fastp-workflow, adapter-trimming, quality-filtering, umi-processing, contamination-screening, rnaseq-qc
  read-alignment/ — bwa-alignment, star-alignment, hisat2-alignment, bowtie2-alignment
  alignment-files/ — sam-bam-basics, alignment-sorting, alignment-filtering, bam-statistics, duplicate-handling, pileup-generation

### Variant Calling & Annotation
bioSkills:
  variant-calling/ — gatk-variant-calling, deepvariant, variant-calling (bcftools), joint-calling, structural-variant-calling, filtering-best-practices, variant-annotation, variant-normalization, vcf-basics, vcf-manipulation, vcf-statistics, consensus-sequences, clinical-interpretation
ClawBio:
  vcf-annotator — VEP + ClinVar + gnomAD annotation with ancestry-aware context
  variant-annotation — Variant annotation pipeline

### Differential Expression (Bulk RNA-seq)
bioSkills:
  differential-expression/ — deseq2-basics, edger-basics, batch-correction, de-results, de-visualization, timeseries-de
  rna-quantification/ — alignment-free-quant (Salmon/kallisto), featurecounts-counting, tximport-workflow, count-matrix-qc
  expression-matrix/ — counts-ingest, gene-id-mapping, metadata-joins, sparse-handling
ClawBio:
  rnaseq-de — Full DE pipeline with QC, normalization, and visualization
  diff-visualizer — Rich visualization and reporting for DE results

### Single-Cell RNA-seq
bioSkills:
  single-cell/ — preprocessing, clustering, batch-integration, cell-annotation, cell-communication, doublet-detection, markers-annotation, trajectory-inference, multimodal-integration, perturb-seq, scatac-analysis, lineage-tracing, metabolite-communication, data-io
ClawBio:
  scrna-orchestrator — Full Scanpy pipeline (QC, clustering, markers, annotation)
  scrna-embedding — scVI-based latent embedding and batch integration

### Spatial Transcriptomics
bioSkills:
  spatial-transcriptomics/ — spatial-data-io, spatial-preprocessing, spatial-domains, spatial-deconvolution, spatial-communication, spatial-neighbors, spatial-statistics, spatial-visualization, spatial-multiomics, spatial-proteomics, image-analysis

### Epigenomics
bioSkills:
  chip-seq/ — peak-calling, differential-binding, motif-analysis, peak-annotation, chipseq-qc, chipseq-visualization, super-enhancers
  atac-seq/ — atac-peak-calling, atac-qc, differential-accessibility, footprinting, motif-deviation, nucleosome-positioning
  methylation-analysis/ — bismark-alignment, methylation-calling, dmr-detection, methylkit-analysis
  hi-c-analysis/ — hic-data-io, tad-detection, loop-calling, compartment-analysis, contact-pairs, matrix-operations, hic-visualization, hic-differential
ClawBio:
  methylation-clock — Epigenetic age estimation

### Pharmacogenomics & Clinical
bioSkills:
  clinical-databases/ — clinvar-lookup, gnomad-frequencies, dbsnp-queries, pharmacogenomics, polygenic-risk, hla-typing, variant-prioritization, somatic-signatures, tumor-mutational-burden, myvariant-queries
ClawBio:
  pharmgx-reporter — PGx report from 23andMe/AncestryDNA (12 genes, 31 SNPs, 51 drugs)
  drug-photo — Photo of medication → personalized PGx dosage card (via vision)
  clinpgx — ClinPGx API for gene-drug data and CPIC guidelines
  gwas-lookup — Federated variant lookup across 9 genomic databases
  gwas-prs — Polygenic risk scores from consumer genetic data
  nutrigx_advisor — Personalized nutrition from consumer genetic data

### Population Genetics & GWAS
bioSkills:
  population-genetics/ — association-testing (PLINK GWAS), plink-basics, population-structure, linkage-disequilibrium, scikit-allel-analysis, selection-statistics
  causal-genomics/ — mendelian-randomization, fine-mapping, colocalization-analysis, mediation-analysis, pleiotropy-detection
  phasing-imputation/ — haplotype-phasing, genotype-imputation, imputation-qc, reference-panels
ClawBio:
  claw-ancestry-pca — Ancestry PCA against SGDP reference panel

### Metagenomics & Microbiome
bioSkills:
  metagenomics/ — kraken-classification, metaphlan-profiling, abundance-estimation, functional-profiling, amr-detection, strain-tracking, metagenome-visualization
  microbiome/ — amplicon-processing, diversity-analysis, differential-abundance, taxonomy-assignment, functional-prediction, qiime2-workflow
ClawBio:
  claw-metagenomics — Shotgun metagenomics profiling (taxonomy, resistome, functional pathways)

### Genome Assembly & Annotation
bioSkills:
  genome-assembly/ — hifi-assembly, long-read-assembly, short-read-assembly, metagenome-assembly, assembly-polishing, assembly-qc, scaffolding, contamination-detection
  genome-annotation/ — eukaryotic-gene-prediction, prokaryotic-annotation, functional-annotation, ncrna-annotation, repeat-annotation, annotation-transfer
  long-read-sequencing/ — basecalling, long-read-alignment, long-read-qc, clair3-variants, structural-variants, medaka-polishing, nanopore-methylation, isoseq-analysis

### Structural Biology & Chemoinformatics
bioSkills:
  structural-biology/ — alphafold-predictions, modern-structure-prediction, structure-io, structure-navigation, structure-modification, geometric-analysis
  chemoinformatics/ — molecular-io, molecular-descriptors, similarity-searching, substructure-search, virtual-screening, admet-prediction, reaction-enumeration
ClawBio:
  struct-predictor — Local AlphaFold/Boltz/Chai structure prediction with comparison

### Proteomics
bioSkills:
  proteomics/ — data-import, peptide-identification, protein-inference, quantification, differential-abundance, dia-analysis, ptm-analysis, proteomics-qc, spectral-libraries
ClawBio:
  proteomics-de — Proteomics differential expression

### Pathway Analysis & Gene Networks
bioSkills:
  pathway-analysis/ — go-enrichment, gsea, kegg-pathways, reactome-pathways, wikipathways, enrichment-visualization
  gene-regulatory-networks/ — scenic-regulons, coexpression-networks, differential-networks, multiomics-grn, perturbation-simulation

### Immunoinformatics
bioSkills:
  immunoinformatics/ — mhc-binding-prediction, epitope-prediction, neoantigen-prediction, immunogenicity-scoring, tcr-epitope-binding
  tcr-bcr-analysis/ — mixcr-analysis, scirpy-analysis, immcantation-analysis, repertoire-visualization, vdjtools-analysis

### CRISPR & Genome Engineering
bioSkills:
  crispr-screens/ — mageck-analysis, jacks-analysis, hit-calling, screen-qc, library-design, crispresso-editing, base-editing-analysis, batch-correction
  genome-engineering/ — grna-design, off-target-prediction, hdr-template-design, base-editing-design, prime-editing-design

### Workflow Management
bioSkills:
  workflow-management/ — snakemake-workflows, nextflow-pipelines, cwl-workflows, wdl-workflows
ClawBio:
  repro-enforcer — Export any analysis as reproducibility bundle (Conda env + Singularity + checksums)
  galaxy-bridge — Access 8,000+ Galaxy tools from usegalaxy.org

### Specialized Domains
bioSkills:
  alternative-splicing/ — splicing-quantification, differential-splicing, isoform-switching, sashimi-plots, single-cell-splicing, splicing-qc
  ecological-genomics/ — edna-metabarcoding, landscape-genomics, conservation-genetics, biodiversity-metrics, community-ecology, species-delimitation
  epidemiological-genomics/ — pathogen-typing, variant-surveillance, phylodynamics, transmission-inference, amr-surveillance
  liquid-biopsy/ — cfdna-preprocessing, ctdna-mutation-detection, fragment-analysis, tumor-fraction-estimation, methylation-based-detection, longitudinal-monitoring
  epitranscriptomics/ — m6a-peak-calling, m6a-differential, m6anet-analysis, merip-preprocessing, modification-visualization
  metabolomics/ — xcms-preprocessing, metabolite-annotation, normalization-qc, statistical-analysis, pathway-mapping, lipidomics, targeted-analysis, msdial-preprocessing
  flow-cytometry/ — fcs-handling, gating-analysis, compensation-transformation, clustering-phenotyping, differential-analysis, cytometry-qc, doublet-detection, bead-normalization
  systems-biology/ — flux-balance-analysis, metabolic-reconstruction, gene-essentiality, context-specific-models, model-curation
  rna-structure/ — secondary-structure-prediction, ncrna-search, structure-probing

### Data Visualization & Reporting
bioSkills:
  data-visualization/ — ggplot2-fundamentals, heatmaps-clustering, volcano-customization, circos-plots, genome-browser-tracks, interactive-visualization, multipanel-figures, network-visualization, upset-plots, color-palettes, specialized-omics-plots, genome-tracks
  reporting/ — rmarkdown-reports, quarto-reports, jupyter-reports, automated-qc-reports, figure-export
ClawBio:
  profile-report — Analysis profile reporting
  data-extractor — Extract numerical data from scientific figure images (via vision)
  lit-synthesizer — PubMed/bioRxiv search, summarization, citation graphs
  pubmed-summariser — Gene/disease PubMed search with structured briefing

### Database Access
bioSkills:
  database-access/ — entrez-search, entrez-fetch, entrez-link, blast-searches, local-blast, sra-data, geo-data, uniprot-access, batch-downloads, interaction-databases, sequence-similarity
ClawBio:
  ukb-navigator — Semantic search across 12,000+ UK Biobank fields
  clinical-trial-finder — Clinical trial discovery

### Experimental Design
bioSkills:
  experimental-design/ — power-analysis, sample-size, batch-design, multiple-testing

### Machine Learning for Omics
bioSkills:
  machine-learning/ — omics-classifiers, biomarker-discovery, survival-analysis, model-validation, prediction-explanation, atlas-mapping
ClawBio:
  claw-semantic-sim — Semantic similarity index for disease literature (PubMedBERT)
  omics-target-evidence-mapper — Aggregate target-level evidence across omics sources

### Environment Setup

Workflows may require Python/R scientific packages or command-line software such as samtools, BLAST, or bedtools. Check the selected workflow documentation and the actual isolated environment. Report missing dependencies and obtain separate approval for preparation; do not use bulk installation commands, administrator privileges, or mutate the Agent Scientist environment.

## Pitfalls

- The fetched skills are NOT in Sci SKILL.md format. They use their own structure (bioSkills: code pattern cookbooks; ClawBio: README + Python scripts). Read them as expert reference material.
- bioSkills are reference guides — they provide parameter examples and code patterns that require review but aren't executable pipelines.
- ClawBio skills are executable — many have `--demo` flags and require review, prerequisites, and execution approval.
- Both repos assume bioinformatics tools are installed. Check prerequisites before running pipelines.
- For ClawBio, inspect its requirements and seek approval for an isolated tool environment before installing dependencies.
- Genomic data files can be very large. Be mindful of disk space when downloading reference genomes, SRA datasets, or building indices.

## Verification

Inspect actual outputs, provenance, counts, units, and limitations. Report missing dependencies or partial results honestly. A successful command or security review does not establish scientific correctness.
