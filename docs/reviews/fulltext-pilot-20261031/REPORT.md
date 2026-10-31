# Six-domain full-text extraction pilot — 2026-10-31

Status: six new manual Draft extractions completed locally; persistence verification is recorded below. This is source reading and structured data preparation, not an LLM API run, independent scientific replication, completed entity resolution or Neo4j construction.

## Scope

The same six scholarly works were already in the initial sample with abstract-level Drafts. This batch adds **separate version-pinned extractions**, preserving all earlier records, rather than presenting them as six newly discovered papers. Each uses fixed arXiv **v1**, not a claim that v1 is the latest revision.

| Domain | Paper | Numeric evidence preserved |
|---|---|---|
| Agent memory | A-Mem, 2502.12110v1 | LoCoMo Multi Hop F1, GPT-4o-mini: A-Mem45.85 vs MemGPT25.52. |
| Context | ACE, 2510.04618v1 | AppWorld test-normal TGC, DeepSeek-V3.1: offline ACE with labels76.2 vs ReAct63.7. |
| Tool use | ToolRL, 2504.13958v1 | BFCL V3 overall, Qwen2.5-7B-Instruct: GRPO Cold Start58.38 vs raw41.97. |
| RL post-training | DAPO, 2503.14476v1 | AIME2024 **avg@32**, Qwen2.5-32B base: complete DAPO50 vs naive GRPO30. |
| Recursive self-improvement | DGM, 2505.22954v1 | Full Polyglot30.7 vs14.2; separate50-task subset38.0 vs14.0. |
| Skill evolution | SkillWeaver, 2504.07079v1 | WebArena reported AVG., GPT-4o with skills29.8 vs baseline22.6. |

All scores are percentages reported by the papers in the cited conditions. Do not pool them as one comparable accuracy metric. No statistical significance or new reproduction is inferred.

## Records and provenance

- 6 new extractions, all `draft_requires_review`.
- 11 paper-version-scoped contribution descriptions,14 measurements,34 evidence anchors.
- Proposed methods, used components, concrete artifacts, problems, benchmarks, metrics, findings and typed candidate relations retained as structured JSON.
- Inspection scope is selected primary method/setup/result/limitation sections and tables, not exhaustive page-by-page review.
- Six original v1 HTML captures returned HTTP200. A separate arXiv batch metadata request timed out; no version publication timestamps were fabricated from that request. Existing publication metadata remains qualified as inherited.
- Original20 Draft extractions, all original sources, versions, prior relevance reviews and reconciliation audit rows remain byte-for-byte unchanged at the row level. Six new source-confirmed version rows and six HTML capture-provenance source rows were added.
- New relevance annotations confirm these six papers' scope from the selected primary sections. This does not promote their scientific claims or all312 initially included candidates to verified status.

## Validation

The private validation checks all34 HTML anchor targets, typed relation endpoints and all14 score literals. It also checks exact table rows/columns for the five tabular sources, and separate subset/full-result paragraphs for DGM. Database integrity and foreign keys pass. Re-importing the same six JSON records leaves the extraction count at26, demonstrating count-level idempotence.

The final database has365 paper identities,389 version/snapshot rows,397 source rows,26 Draft extractions,371 relevance-review rows and the original reconciliation audit. The six new drafts coexist with the original20.

## Ontology outcome

A candidate refinement is documented at `kg-builder/docs/ontology/ONTOLOGY_V0_2_EXTRACTION_PILOT.md`. Nine node kinds remain sufficient for these examples; no additional Finding/Result/Evidence kind was needed. The pilot exposed requirements for configuration-scoped measurements, claim attribution, descriptive artifact labels, source conflicts, explicit verification criteria and concrete-only revision lineage.

The candidate schema is not frozen, and the existing JSON importer is not a complete v0.2 schema validator. No production code changed in this batch. No graph writer, embedding index, automatic extraction API or schedule was executed.

## Key source caveats

SkillWeaver v1 prose, conclusion and table do not state a consistent average relative improvement; raw scores and the discrepancy are retained. DAPO avg@32 is not pass@32. DGM's subset/full results, frozen weights and fixed outer exploration mechanism remain explicit. SkillWeaver's exception-free skill check has a documented semantic failure example.

## Persistence verification and next step

The existing authoritative Drive database was updated in place after a pre-pilot backup and a separate post-pilot snapshot. Downloaded bytes match SHA256 `38e6c2f0afa41cc66a506946137f0e971dd06746968c3acfc2cf761276ee164d` (9,400,320 bytes); restored integrity/FK checks pass with26 extractions and371 relevance reviews. The private extraction JSON, minimized source-capture manifest and validation results are also saved in the project Drive folders. Primary source HTML is referenced by immutable version URLs and hashes; no raw full text or database is committed publicly.

Production KG Builder code remains the independently reviewed ingestion implementation. This batch adds documentation only. The next step is a machine-readable schema and extraction validation/migration contract, followed by a reviewed mapping from these JSON records to graph entities/relations. Global entity normalization, graph writes and retrieval benchmarking remain pending.

## Repository delivery

KG Builder documentation commit `ddaa6d546d6287ae3c9379288b4be7b0d707aa5e` adds the ontology pilot document only; its production code remains the reviewed `bc894774d830d98740cdd41ec58174d63c70d800` implementation. The main repository advances the submodule pointer and records this report. No private extraction JSON, full-text captures, database bytes or credentials are tracked in Git.
