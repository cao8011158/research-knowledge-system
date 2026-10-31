# research-knowledge-system
A research knowledge system for evaluating knowledge graph-based information retrieval with LLM agents.

## Latest work session — 2026-10-31

Read [the entity-resolution handoff and review](docs/reviews/entity-resolution-20261031/STAGE_REPORT.md) for current implementation and validation, then the earlier reconciliation/pilot reports as historical context. The ingestion implementation was independently reviewed at `bc894774d830d98740cdd41ec58174d63c70d800`; see the newer pilot section below for the current submodule pin.

The private Drive database now retains365 candidate paper identities,383 version/metadata snapshots,391 source records and the original20 Draft extractions. Preliminary scope labels are312 include /38 pending /15 exclude; these are not full-text verification. Five same-title identity groups remain unresolved. Default live collection uses OpenAlex and arXiv; Semantic Scholar is opt-in. No LLM API extraction, scheduler, Neo4j or Agent evaluation was run. Database files, original abstracts and review datasets are not committed here.

## Six-domain source-reading pilot — 2026-10-31

[Full-text pilot report](docs/reviews/fulltext-pilot-20261031/REPORT.md) supersedes the earlier report for current database counts. Six version-pinned manual Draft extractions were added from selected source sections/tables: A-Mem, ACE, ToolRL, DAPO, DGM and SkillWeaver. The private database now has365 paper identities,389 version/snapshot rows,397 source records,26 Draft extractions and371 relevance-review rows. All previous records remain preserved. The KG Builder ontology pilot document refines candidate properties, identity boundaries and edge contracts; the schema is not frozen and no Neo4j graph has been built.

Current KG Builder submodule pin: `dfb170532d53afc60e1e3f06197fc640f0f6e4a7`.

## Executable schema and atomic imports — 2026-10-31

The candidate JSON Schema 2020-12 profile now checks extraction structure, evidence references, typed relation endpoints, version scope and metric units. Unversioned records use an explicit legacy compatibility profile. Imports validate the batch before storage and commit or roll back the entire batch while preserving caller transactions. Unchanged reimports preserve stored IDs, payloads and timestamps. Reconciliation retains relevance reviews and provenance, rewrites only declared ID fields, and rejects unsupported tables/columns.

Two independent review rounds closed source-text remapping and empty-evidence issues. The final13 tests, real20legacy+6pilot validation,371review retention, failure/recovery paths, installed-wheel loading and indexed SQLite growth checks passed. All26 extractions remain Draft; the authoritative private database was not rewritten. Schema acceptance does not complete cross-paper entity resolution or graph construction.

## Manual entity identity review — 2026-10-31

[Entity-resolution review and acceptance](docs/reviews/entity-resolution-20261031/STAGE_REPORT.md) covers all74 Method/ResearchProblem/Artifact mentions in the existing26 Draft extractions.34 mentions resolve to27 scoped identities (7Methods,20Artifacts);40 remain explicitly pending (14legacyMethods,26Problemmentions).15Artifacts are paper-version-local configurations/libraries/example code. Method and same-named Artifact stay distinct; shared GRPO identifies a concept rather than identical training implementations. This does not resolve all365paper candidates.

SQLite stores immutable manual review batches separately from original extractions. Every binding and supporting source is pinned by exact payload hash; queries hide active identities if a source changes and use indexed lookups in one read snapshot. Imports are atomic and preserve caller transactions. Reconciliation preserves review evidence or fails explicitly if annotated IDs/bytes would change. Two review rounds closed a column-order copy defect;21 tests, real-data/restore/lookup checks and an installed-wheel check passed. Original26Drafts and371relevance reviews retain exact values; no graph or LLM API extraction was run.
