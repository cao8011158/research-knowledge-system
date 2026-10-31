# research-knowledge-system
A research knowledge system for evaluating knowledge graph-based information retrieval with LLM agents.

## Latest work session — 2026-10-31

Read [the current reconciliation handoff and review report](docs/reviews/ingestion-reconciliation-20261031/STAGE_REPORT.md) before the historical KG Builder bootstrap handoff. The ingestion implementation was independently reviewed at `bc894774d830d98740cdd41ec58174d63c70d800`; see the newer pilot section below for the current submodule pin.

The private Drive database now retains365 candidate paper identities,383 version/metadata snapshots,391 source records and the original20 Draft extractions. Preliminary scope labels are312 include /38 pending /15 exclude; these are not full-text verification. Five same-title identity groups remain unresolved. Default live collection uses OpenAlex and arXiv; Semantic Scholar is opt-in. No LLM API extraction, scheduler, Neo4j or Agent evaluation was run. Database files, original abstracts and review datasets are not committed here.

## Six-domain source-reading pilot — 2026-10-31

[Full-text pilot report](docs/reviews/fulltext-pilot-20261031/REPORT.md) supersedes the earlier report for current database counts. Six version-pinned manual Draft extractions were added from selected source sections/tables: A-Mem, ACE, ToolRL, DAPO, DGM and SkillWeaver. The private database now has365 paper identities,389 version/snapshot rows,397 source records,26 Draft extractions and371 relevance-review rows. All previous records remain preserved. The KG Builder ontology pilot document refines candidate properties, identity boundaries and edge contracts; the schema is not frozen and no Neo4j graph has been built.

Current KG Builder submodule pin: `ddaa6d546d6287ae3c9379288b4be7b0d707aa5e` (ontology documentation only; production code unchanged).
