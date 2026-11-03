# Research Knowledge System

A Phase 2 research project that builds a scholarly knowledge graph and tests
whether an LLM agent can find papers, follow graph relationships, and answer
questions with traceable evidence. The corpus covers agent memory management,
context compression, and procedural skills, including related tool use.

## Repositories

| Submodule | Role | Pinned documentation |
| --- | --- | --- |
| [kg-builder](https://github.com/cao8011158/kg-builder) | Collects and reviews papers, builds the versioned graph, publishes it to Neo4j, and exports BM25 and HNSW indexes. | [README at `b25a8de`](https://github.com/cao8011158/kg-builder/blob/b25a8de7ebd5e9e11baaafb39eb3fc82ac71d1c9/README.md) |
| [research-agent](https://github.com/cao8011158/research-agent) | Runs Qwen through Strata in Colab, retrieves and reranks candidates, follows source records through read-only Neo4j MCP, and evaluates answers. | [README at `7b6b4f8`](https://github.com/cao8011158/research-agent/blob/7b6b4f8716c31c1dfe2d3b8dcbc2dbeefac5039e/README.md) |

## Phase 2 workflow

1. Collect titles, abstracts, and publication metadata from OpenAlex and arXiv.
   The full build screened **8,270 deduplicated candidates** and included
   **3,162 papers** with approved extraction items.
2. Build a frozen, versioned graph and publish it to Neo4j. The graph connects
   methods, benchmarks, research problems, and reported contributions to their
   paper evidence.
3. Use BM25 and HNSW to find candidates, rerank them with Qwen, and follow
   stable IDs through Cypher to verify sources and relationships. The agent
   separates graph relations, shared mentions, and inferences drawn from papers.

## Evaluation

All **24 known-source lookup checks** ranked the expected source first.
The Colab agent evaluation used seven prompts and three tool configurations.
**20 of 21 question–configuration pairs** produced an answer. The web-only run that exhausted its tool
budget received zero points.

| Configuration | Formal score (v1) |
| --- | ---: |
| KG only | 45/48 |
| KG plus web search | 46/48 |
| Web search only | 29/48 |

The formal total covers six questions. The privacy question used to calibrate
the run was scored separately. KG access helped most on tasks requiring
verification of project graph IDs and relationships. The
[Research Agent results](https://github.com/cao8011158/research-agent/blob/7b6b4f8716c31c1dfe2d3b8dcbc2dbeefac5039e/README.md#completed-results-v1)
describe the experimental code revision, per-question scores, and limitations.
The [v2 question set](https://github.com/cao8011158/research-agent/blob/7b6b4f8716c31c1dfe2d3b8dcbc2dbeefac5039e/experiments/kg-web-eval/questions-v2.json)
replaces the internal method-ID lookup with a question based on public evidence.
Its replacement question is pending in all three modes.

## Check out the pinned repositories

```bash
git clone --recurse-submodules https://github.com/cao8011158/research-knowledge-system.git
```

Use the two submodule READMEs for setup, development, and experiment details.

<details>
<summary>Earlier development records (October 2026)</summary>

## Current research scope — 2026-10-31

First public release2025-01-01onward. Active domains: **Agent Memory**, **Context Management & Compression**, and **Skill / Self-improving Skill**. Tool Use, RL Post-training and general Recursive Self-improvement are no longer independent discovery targets; retain cross-domain papers only when substantively focused on one of the three selected areas. [Current scope and boundaries](kg-builder/docs/CURRENT_RESEARCH_SCOPE.md).

Discovery config now has3domains/9queries, verified through the actual CLI config loader. The365-paper historical candidate pool and prior annotations are preserved; scoped re-screening before further LLM extraction remains to be done. Historical six-domain reports below are not the active scope.

## Latest retrieval preprocessing — 2026-10-31

[Current preprocessing and recovery report](docs/reviews/retrieval-preprocess-20261031/STAGE_REPORT.md). The retrieval-first approach reuses OpenAlex standard topics/keywords and source citation/recommendation metadata; original arXiv classes and historical Drafts remain separate. A disposable sidecar indexes all365existing papers, with304confirmed OpenAlex mappings,304source-topic-covered papers,303source-keyword-covered papers and296arXiv-class-covered papers. A bounded50-paper follow-up confirmedDAPO/ToolRL publication mappings;48remaining papers received explicitly assistant-predicted labels from the existingOpenAlex vocabulary. Including predictions,352papers have topic labels and351have keywords. Seven strong-ID ambiguities and6earlier classification gaps remain separate.

The authoritative master is unchanged (365papers/403versions/411sources/40Drafts). Sidecar retains11existing contributions across6papers;345summaries are text-ready and14needtext. Only18papers have nonempty reference lists, yielding317reference edges and just1corpus-internal reference link;3030related-work recommendations remain distinct. This is metadata preprocessing, not a completed semantic index or retrieval benchmark.33tests, independent real-data checks and actual Drive recovery/rebuild pass. Default live sources remain OpenAlex/arXiv; no Semantic Scholar or paid LLM call was made.

## Historical ingestion session — 2026-10-31

Read [the primary-source identity and problem-boundary review](docs/reviews/source-identity-20261031/STAGE_REPORT.md) for current implementation and validation, then the earlier reconciliation/pilot reports as historical context. The ingestion implementation was independently reviewed at `bc894774d830d98740cdd41ec58174d63c70d800`; see the newer pilot section below for the current submodule pin.

The private Drive database now retains365 candidate paper identities,383 version/metadata snapshots,391 source records and the original20 Draft extractions. Preliminary scope labels are312 include /38 pending /15 exclude; these are not full-text verification. Five same-title identity groups remain unresolved. Default live collection uses OpenAlex and arXiv; Semantic Scholar is opt-in. No LLM API extraction, scheduler, Neo4j or Agent evaluation was run. Database files, original abstracts and review datasets are not committed here.

## Six-domain source-reading pilot — 2026-10-31

[Full-text pilot report](docs/reviews/fulltext-pilot-20261031/REPORT.md) supersedes the earlier report for current database counts. Six version-pinned manual Draft extractions were added from selected source sections/tables: A-Mem, ACE, ToolRL, DAPO, DGM and SkillWeaver. The private database now has365 paper identities,389 version/snapshot rows,397 source records,26 Draft extractions and371 relevance-review rows. All previous records remain preserved. The KG Builder ontology pilot document refines candidate properties, identity boundaries and edge contracts; the schema is not frozen and no Neo4j graph has been built.

## Executable schema and atomic imports — 2026-10-31

The candidate JSON Schema 2020-12 profile now checks extraction structure, evidence references, typed relation endpoints, version scope and metric units. Unversioned records use an explicit legacy compatibility profile. Imports validate the batch before storage and commit or roll back the entire batch while preserving caller transactions. Unchanged reimports preserve stored IDs, payloads and timestamps. Reconciliation retains relevance reviews and provenance, rewrites only declared ID fields, and rejects unsupported tables/columns.

Two independent review rounds closed source-text remapping and empty-evidence issues. The final13 tests, real20legacy+6pilot validation,371review retention, failure/recovery paths, installed-wheel loading and indexed SQLite growth checks passed. All26 extractions remain Draft; the authoritative private database was not rewritten. Schema acceptance does not complete cross-paper entity resolution or graph construction.

## Manual entity identity review — 2026-10-31

[Entity-resolution review and acceptance](docs/reviews/entity-resolution-20261031/STAGE_REPORT.md) covers all74 Method/ResearchProblem/Artifact mentions in the existing26 Draft extractions.34 mentions resolve to27 scoped identities (7Methods,20Artifacts);40 remain explicitly pending (14legacyMethods,26Problemmentions).15Artifacts are paper-version-local configurations/libraries/example code. Method and same-named Artifact stay distinct; shared GRPO identifies a concept rather than identical training implementations. This does not resolve all365paper candidates.

SQLite stores immutable manual review batches separately from original extractions. Every binding and supporting source is pinned by exact payload hash; queries hide active identities if a source changes and use indexed lookups in one read snapshot. Imports are atomic and preserve caller transactions. Reconciliation preserves review evidence or fails explicitly if annotated IDs/bytes would change. Two review rounds closed a column-order copy defect;21 tests, real-data/restore/lookup checks and an installed-wheel check passed. Original26Drafts and371relevance reviews retain exact values; no graph or LLM API extraction was run.

## Primary-source adjudication and Problem boundaries — 2026-10-31

[Current review and recovery evidence](docs/reviews/source-identity-20261031/STAGE_REPORT.md) supersedes earlier counts. Fourteen fixed-v1 primary papers were checked at selected introduction/method/taxonomy sections. The14pending legacy Method labels are8single mappings,4compound labels with separate components, and2survey-taxonomy labels not assigned Method identities. The original26Problem mentions have explicit scoped definitions: equivalent ToolRL/DGM pairs share identity, other scopes remain distinct, and25reviewer-authored parent links organize30Problem concepts. These are candidate modeling decisions, not paper-claimed empirical relations or an ontology freeze.

Select current immutable batch `entity-resolution-20261031-v2` explicitly:105mentions,99single mappings,4compound outcomes,2nonmethod outcomes,0insufficient-evidence outcomes;74current entities. The previous v1batch remains historical. Total DB:365papers,403versions,411sources,40Draft extractions,371relevance reviews,2resolution batches/101stored entities/179stored mentions.14new Drafts cover identity/problem sections only, with empty experiment/result arrays; no reproduction or verified publication-date/checkpoint claim. Original26Drafts and old review rows are retained exactly.

Resolutionv0.2 adds typed outcomes/components and Problem parent IDs without SQLite DDL changes.29tests and two independent review rounds passed, including a fixed v1opaque-extension compatibility defect, atomicity/stale dependency handling, indexed growth checks, installed profiles, reconciliation and Drive raw-file restoration. Raw full-paper captures stay outside deliverables; metadata/hashes and structured paraphrases are private Drive artifacts. No graph writer, embeddings, LLMAPI extraction or scheduler ran.

</details>
