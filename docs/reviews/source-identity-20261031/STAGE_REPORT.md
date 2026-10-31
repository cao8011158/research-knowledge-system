# Primary-source identity and problem-boundary review — 2026-10-31

Current status: independent review passed in round2; code merged and backed-up Drive database restored successfully. Final parent integration follows below.

本批结果：14个旧方法标签中8个明确映射、4个拆分、2个分类标签不作Method；26个研究问题已逐项定界，25条上下位联系均标明是建模判断。旧记录保留，未执行建图。

## Scope and baseline

User 好的请继续 accepts verifying14old Method labels and26ResearchProblem mentions, defining aliases/type separation/proper subproblem links only where evidence supports them. Code push, main gitlink update and private Drive persistence retain earlier authorization. No LLM API extraction, graph construction, embeddings or scheduler execution.

Parent baseline5e18fcee15083996fb9788d16ac730403ebe3985; childdfb170532d53afc60e1e3f06197fc640f0f6e4a7. Current private DB SHA256f2f9ac10981a30be8442e96557352ff03346cbc868fba0aeefeb4aa389e9d6c8,9,625,600bytes,365papers/389versions/397sources/26Drafts/371relevance reviews/1identity batch/27entities/74mentions. All existing rows/batch must be preserved exactly.

Developer ingestion_fix; root independent reviewer and manual source interpretation. Bounded code change: candidate resolution manifestv0.2 alongside v0.1, typed terminal review outcomes for compound/nonmethod labels without coercing them into one identity; optional reviewer-authored ResearchProblem parent IDs; indexed source/parent/component closure checks, atomic immutable import, consistent read snapshot, existing-table reconciliation retention. No new graph node kind or database-table migration is assumed.

Acceptance: primary sources pinned to actually inspected version and capture scope; no treating abstract reading as full-paper reproduction; original Drafts unchanged, new source-grounded review Drafts explicitly tagged; manifest decisions cite exact stored source payload hashes; proper question definitions and acyclic parent links; composite labels map components separately and survey taxonomies excluded as algorithms; both manifestversions and all prior rows survive backup/restore/reconcile or fail closed. Tests cover negative outcomes/references/cycles, stale closure, nested transactions, packaging and actualindexed lookup costs under unrelated growth.

## Stage 1 — developer delivery, local/unpushed

Local commit d63dd8117d21196c156fbe47a17289bafa08fdb9, tree81f0635597b6017cba296ffd0d6e69d6b15fbb49, based on dfb170532d53afc60e1e3f06197fc640f0f6e4a7. Additive resolution manifestv0.2 and API/docs/tests only; existing three-table DDL and v0.1 profile retained.

New outcomes distinguish single identity mapping, compound label, non-method taxonomy label and insufficient evidence. Problem parent links require explicit reviewer_taxonomy basis and valid acyclic same-kind references. Indexed entity/mention getters validate exact support/parent/component closure in one read snapshot with per-request deduplication; v0.1 output preserved.

Developer targeted7v2+8v1 and fast28 passed, including1050-deep iterative hierarchy, diamond stale parent, stale component, atomicity,500unrelated rows and negative read tests; whitespace check passes. New profile appears in wheel. Logs retained. No private v2 manifest was yet available to developer, so real-data acceptance remains root work.

Root source work:14fixed-v1 HTML captures fetched, titles matched and selected introduction/method/taxonomy sections read.14new identity/problem-only Draft payloads (13Method,14Problem,4Artifact mentions) pass existing extraction schema. Full source captures stay local research intermediates; only metadata/hashes and paraphrased structured records will be persisted. Expected metadata enrichment adds14known versions/source records and updates their owning papers' known-version pointers/timestamps; existing extraction, review and immutable resolution rows must remain exact. Next publish identical candidate tree, then independent full-diff/real-data review.

## Stage 2 — independent review round 1 of 3

Remote candidate ef73f9b4a3b7506b68aad27fbbe6739a5eccd6d7 fetched and checked out; tree81f0635597b6017cba296ffd0d6e69d6b15fbb49 matches developer local. Full baseline-to-head implementation/schema/docs/tests inspected. Verdict **changes required**: one confirmed current-scopeP2, SI-01. Main/live DB unchanged.

Independent full28tests pass (1.120s,exit0). Real private review data also passes: original26Drafts and371relevance reviews remain exact;14new selected-section identity Drafts give40total,14known v1versions and source records added (403versions/411sources). Only owning-paper known-version pointers and update timestamps change, not historical source rows or old annotations. Originalv1batch query/rows remain unchanged on its actual data.

New v2manifest:74entities (20Method,24Artifact,30ResearchProblem),105mentions including99single mappings,4completed compound-label adjudications and2nonmethod taxonomy labels;0insufficient-evidence outcomes. The original14pendingMethod labels are8mapped/4compound/2nonmethod. Original26Problemmentions are reviewed, with equivalent ToolRL/DGM pairs sharing identities and other question distinctions retained.25parent links carry explicit reviewer_taxonomy basis. The proposed hierarchy is modeling, not an empirical assertion. Atomicity/cycles/kind/component/parent-support staleness, restore and repeated reconciliation checks pass; all active references current.

Locality measured on actual v2data: leaf entity65VM/4indexedSELECTs/12692internal text bytes/996reply bytes; compound query158VM/9SELECTs/19636internal bytes/4902reply bytes. Missingentity19VM/1SELECT/0payload bytes, missingmentions20VM/1SELECT/0payload bytes.1000unrelated rows in each resolution table with49,152,000large text bytes leave reads/output unchanged. Plans use entity/mention composite indexes and extractionPK; no whole-manifest or table scan.

### SI-01 — v2 fields interpreted inside v1 opaque extension data (P2, blocking)

Location entity_resolution.py getters/_current_entity. V1 allows supplementary JSON properties. The new readers choose semantics from presence of review_outcome/parent_problem_ids instead of the batch's declared schema_version. A valid v1manifest with review_outcome={legacy_note:...} imports but get_resolution_mentions raisesKeyError for missingcomponent_entity_ids. A valid v1entity carrying parent_problem_ids as legacy supplementary metadata is falsely marked stale. This contradicts preserved v1semantics even though our actual previous batch lacks these extension fields. Reproducer v1_compatibility_check.py reports bothpreservation checksfalse; no real data modified.

Fix: dispatch outcome/hierarchy semantics using the immutable batch's declared version, read via indexed small schema_version metadata (never load/parse complete batchpayload). Preserve v1opaque fields and returnshape, enable newsemantics onlyv2, retain indexed missing-target earlyreturns and one consistent read snapshot. Test both legacy extension-name collisions on original public mention API and explicit entity getter, plus v2parent/component functionality.

Ownership currentbatch/step, no external dependency or scope upgrade. Route bounded developer fix then formalround2; previous round retained. No need for user permission escalation.

## Stage 3 — bounded SI-01 fix, local/unpushed

Local b0ffa08c52f41faa19cbb576de0e02a247c18a28, treed1063f8e9c21c7d52327e7db009a5cfd9f47b214, parent ef73f9b4a3b7506b68aad27fbbe6739a5eccd6d7. Getters now dispatch from indexed batch schema_version metadata inside the same read snapshot. V1new-name supplementary fields remain opaque and old query shape remains unchanged; v2 typed semantics apply only to v2. Missing-mention/entity early paths still avoid source/large manifest reads.

Postcommit developer targeted8 and full29 tests passed (exit0), original public compatibility reproducer bothtrue; whitespace check passed. Files limited to helper implementation, regression tests and clarifying v2documentation. No private data or DDL changes. Next identical remote tree publication and independent review2.

## Stage 4 — independent review round 2 of 3 / acceptance

Reviewed remote d99883bdba496373d1a61365a47e63dff0e5bf41; fetched tree d1063f8e9c21c7d52327e7db009a5cfd9f47b214 equals developer local b0ffa08. Full original diff and bounded fix assessed. **Verdict PASS. SI-01resolved; no open blocker.**

| Independent check | Result |
|---|---|
| Fast regression |29passed,0.991s,exit0; all prior v1/schema/ingestion and v2hierarchy/component cases |
| Original counterexample |Bothv1opaque extension checks true; v2meaning dispatched only by stored version; unknown schema fails explicitly |
| Real review data |105mentions:99mapped,4compound,2nonmethod,0insufficient;74current entities including30Problem concepts/25reviewer parent links |
| History/source scope |Original26Draft rows,371relevance reviews and originalv1batch rows/query exact;14selected-section Drafts,14source records and14known v1versions added; owningpaper current-known pointers/timestamps intentionally enriched |
| Failure and recovery |cycle/self/missing/cross-kind parents, invalid compound/hash and injectedSQL failure rejected atomically; caller transaction retained; parent/component hash changes hide active dependent results; repeated reconcile preserves active/history rows |
| Actual indexed entity leaf |78SQLiteVM instructions,5indexedSELECTs,12725internal text bytes,996reply bytes |
| Actual compound query |171VM,10indexedSELECTs,19669internal text bytes,4902reply bytes |
| Missing targets |entity19VM/mention20VM,1indexedSELECT,0source/manifest payload bytes;54/2reply bytes |
| Unrelated growth |1000extra rows per resolution table,49,152,000large text bytes; plans/reads/output unchanged, no scans/full manifest parsing |
| Installed wheel |fresh outside-source environment loads all4packaged JSONprofiles and validates/imports actualv2manifest; parent and compound getters current,FK0 |
| Primary capture audit |14fixed-v1titles normalized match, capturedHTMLSHA256 verified, introduction and method/taxonomy anchor checks pass |

Original14labels:8procedural identities mapped;4compound labels (Zep/Graphiti; DeepSeek-R1/training; Mem0/Mem0g; CAT/SWE-Compressor) retain2–3distinct components;2legacy survey-taxonomy labels are not assigned a Method identity. This does not erase survey contributions. Problem equivalence is restricted to matched objective/task/constraints; ToolRL/DGM paired descriptions share identities, other overlapping scopes remain distinct. A-Mem index/link/update and ACE collapse-avoidance examples are proper reviewer-proposed narrower questions. Broad roots are organizing questions, not author-claimed results.

Source-derived partial extraction explicitly omits numerical experiments/complete paper coverage. Publication dates, exact model/checkpoint/software releases and scientific truth are not certified;40records remain Draft. Registry v1remains immutable historical data, so callers must explicitly select current batch entity-resolution-20261031-v2. No graph writer, embedding, scheduler or LLMAPI executed.

Prepared standalone backup:10,076,160bytes, SHA25632dc56e3cfc6e7ce531535c7d523303e3f7b96105f4ffb64e093c5ee21dc1aa5, integrityOK/FK0. Totals365papers/403versions/411sources/40Drafts/371relevance reviews;2immutable resolution batches,101stored entities/179stored mentions (including historical v1). Next gate/ref checks and backed-up Drive publication/roundtrip.

## Stage 5 — publication, backed-up persistence and recovery

Prepublication refs: child main dfb170532d53afc60e1e3f06197fc640f0f6e4a7, candidate d99883bdba496373d1a61365a47e63dff0e5bf41; parent main5e18fcee15083996fb9788d16ac730403ebe3985. GateREADY/2rounds/SI-01resolved. Authorized nonforced expected-SHA update published child main at the reviewed commit. Source Drive metadata rechecked unchanged at9,625,600bytes before replacement; backup copied first, original file ID/organization preserved.

| Artifact | Verified Drive location |
|---|---|
| Current DB |[research_knowledge.sqlite3](https://drive.google.com/file/d/1hO1VlJN_NOL1mDTyTTxDnopf331-62Q7/view?usp=drivesdk),10,076,160bytes |
| Before-step backup |[pre_source_identity](https://drive.google.com/file/d/1qq6Ze4XfDOpZHTFsyni8AqWuPf1MCuO1/view?usp=drivesdk),oldSHA256f2f9ac10981a30be8442e96557352ff03346cbc868fba0aeefeb4aa389e9d6c8 |
| Reviewed snapshot |[source_identity snapshot](https://drive.google.com/file/d/1d6kAH1DixtrghTZhU9hykXMYQdXY4RWB/view?usp=drivesdk),same bytes as currentDB |
| Current review |[entity_resolution_v2_20261031.json](https://drive.google.com/file/d/1xUWNslrP4BVONr6zKQ8nwXshTIRkjlIt/view?usp=drivesdk),156,456bytes |
| New partial Drafts |[source_identity_drafts_20261031.json](https://drive.google.com/file/d/10N_5bCWi4DHckLunSplnD9Eeqe2Eb6kp/view?usp=drivesdk),45,077bytes |
| Source provenance metadata |[source_identity_captures_20261031.json](https://drive.google.com/file/d/1Uu_AT5HYGf_Eow7cawuhyYQfOZj3-aQa/view?usp=drivesdk),7,665bytes; URLs/hashes/anchors, no raw articles |
| Validation |[source_identity_validation_20261031.json](https://drive.google.com/file/d/1vAMPWiGegsIQZjnPlvGCorhhqEvRlMu5/view?usp=drivesdk),1,753bytes |
| Restore proof |[source_identity_roundtrip_20261031.json](https://drive.google.com/file/d/1nT4_AkA4vpSaPKnuxgHEeDFN5tCUtvyT/view?usp=drivesdk),downloaded-file hashes and restored query results |

All seven files were fetched again and hash-compared with their local inputs. Current DB/snapshot SHA25632dc56e3cfc6e7ce531535c7d523303e3f7b96105f4ffb64e093c5ee21dc1aa5; manifest6b9ce7cbd4ccda57c6b106194776c01e07ec3e0791d21c32317fc9402455230a; Draftsc44672b3e81988051478a50e8b8235e26f2773f0d2911adc4034747e557398f8; capturemeta5783c8a9edd38954ae1b7fcaa9f0d69acce9dd966609dd9ad9b92916a5f39dea; validatione2d18e3dad8ae52d773a846bc707c9a6e4750c2f1d9082fd4e70ea14f03da9bc. Restored integrityOK/FK0; currentv2 105mentions99mapped/4compound/2nonmethod, no stale; historicalv1 74mentions also current. Restore proof is saved separately after these checks and metadata-read back.

The current batch is entity-resolution-20261031-v2. Six SQLpending single-ID rows are intentional completed compound/nonmethod adjudications, not six unverified cases; review_outcome supplies the distinction. All old26Drafts and371relevance reviews retained. No Draft promotions, result reproduction, frozen ontology, embeddings, graph writer or LLMAPI extraction.

Parent integration will pin the reviewed code and persist cumulative reports/negative cases/recovery evidence; private DBs, source Drafts and manifests remain outside Git. Further work can validate additional varied ontology cases and define graph materialization policy for scoped identities and reviewer-authored relations; it must not pretend all365paper candidates have been extracted.
