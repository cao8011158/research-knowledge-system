# Cross-paper entity resolution — 2026-10-31

Current status: complete. Review passed in round2; child main `dfb170532d53afc60e1e3f06197fc640f0f6e4a7`, parent integration `8524c60fe3c949dc8fe017ddb96d6957bd550b2b`. Private DB/decisions are saved and restored successfully. This final handoff-only update follows the integration commit.

Stages: baseline → developer candidate → review1/ER-01 → bounded fix → review2/pass → Drive backup/publication/restore → parent integration.

## Scope and baseline

User “好的 继续” accepts cross-paper Method/ResearchProblem/Artifact disambiguation and durable review results before graph construction. Previous authorization covers code push, parent gitlink update and private Drive data persistence. No LLM API, graph, embeddings or scheduler execution.

Parent baseline `a22851cf3e6d4e198f7e5234afaf1fb3be53de95`; kg-builder `f87c460924aaca04e9500c79ed82c0991fedf8e6`. Current branch parent release/extraction-schema-20261031-final, child review/extraction-schema-20261031-r2; eventual targets main must be rechecked. Developer ingestion_fix; independent reviewer root.

Input candidate database365papers/389versions/397source records/26Draft extractions/371relevance reviews, SHA25638e6c2f0afa41cc66a506946137f0e971dd06746968c3acfc2cf761276ee164d. Metadata remains unchanged since last read; fresh bytes will be checked.

Acceptance: identity decisions separate from original extraction payloads; scope/version boundaries and kinds enforced; immutable, atomic, hash-anchored review admission and explicit stale lookup; indexed extraction-specific lookup; supported reconciliation retention or explicit failure before losing resolution provenance; actual74Method/Problem/Artifact mentions reviewed with conservative pending states; validated DB backed up and Drive roundtrip checked. Exact names are candidates, not automatic merge instructions.

Test plan: focused invalid/stale/rollback/immutable cases, fast regression, real-data application and repeated import/reconcile, installed schema loading, indexed lookup plans/VM counts under unrelated growth. Original26extraction rows and371reviews must retain exact values.

## Stage 1 — developer delivery (local, not pushed)

Local commit `2e52a204f80bb2263654bd5f9b8e85439f20561f`, tree `eff3b33ce91503493f5f866fd3837a7ddfc06107`, base `f87c460924aaca04e9500c79ed82c0991fedf8e6`. Developer ingestion_fix; independent reviewer root.

Implemented packaged resolution-manifest schema, immutable source-hash-bound batches/entities/mentions, atomic CLI/import with caller transaction ownership, version/kind/artifact subtype/evidence admission checks, indexed explicit lookup with support-closure stale detection and one consistent read snapshot. Empty review lookup reads no extraction payload. Reconciliation preserves all three tables/audit or fails explicitly on annotated-source remapping/conflicting immutable batches.

Developer postcommit targeted7 and fast20 tests pass (exit0), including deterministic WAL concurrent-write counterexample, negative lookup locality, stale support and atomic failure checks; whitespace check passes. Read-only real manifest schema/source bindings pass for27entities/74mentions; these are developer checks until independent acceptance. New JSON schema is included in wheel contents. Logs retained in this directory.

Manual first-pass review:74mentions across the existing26Drafts,34resolved into27identities (7Methods,20Artifacts),40pending (14legacyMethods,26ResearchProblems). Fifteen artifacts remain version-local. Six source captures match their previously stored HTML SHA256 and selected method/setup/results/example sections were re-read. GRPO is a shared concept across ToolRL/DAPO, not an assertion of equal implementations. Method and same-named system remain distinct; example function update_product_quantity is version-local. No private payloads are committed.

Next: publish identical candidate tree, verify remote SHA, independently assess full diff and run real retention/failure/scale acceptance. No LLM API, graph or Draft promotion.

## Stage 2 — remote candidate / independent review round 1 of 3

Reviewed remote `884f41f8c5e3ffba97567d894c78199c213cb9aa`, fetched from work/entity-resolution-20261031; tree `eff3b33ce91503493f5f866fd3837a7ddfc06107` matches developer commit. Full baseline-to-head diff and contracts inspected. Verdict: **changes required**, one current-scope P2 blocker, ER-01. No authoritative DB replacement or main merge.

Independent checks: fast20 passed (0.573s,exit0); actual manifest imports27entities/74mentions,34resolved/40pending; all original26Drafts and371relevance reviews remain exact, immutable repeat is unchanged. Hash/evidence/kind/subtype/local-global/conflict/SQL-fault/outer-transaction tests pass. Source-support mutation makes the dependent cross-paper GRPO decision stale while unrelated DAPO remains active; restoring exact bytes restores currentness. Same-identity reconcile and repeat preserve all active rows and historical audit. Original source SHA256 unchanged.

Lookup evidence: actual DAPO extraction returns6mentions with8indexed SELECTs and9137reply bytes. Internal fetched text is28112bytes (19743source,8369mention/entity). SQLite VM instructions181first /175repeat; after1000unrelated batches,entities andmentions (49,152,000large-payload bytes)175VM and identical reads/output. Absent batch:20VM,1indexed SELECT,0rows/0text bytes,2reply bytes, no source payload read. EXPLAIN QUERY PLAN shows composite mention/entity indexes and extraction PK, no scans. Full migrations intentionally inspect all inputs.

### ER-01 — supported table column order corrupts copied review rows (P2, blocking)

Location scripts/reconcile_sqlite.py, new resolution-table copy loops. Input schema admission compares column-name sets, correctly accepting alternate physical column order. Copying uses tuple(row.values()) and INSERT VALUES without named columns, assuming standard positional order. A valid input with unchanged named values/constraints/FK0 but reordered columns is accepted; all three output resolution tables have misassigned values, and get_resolution_mentions fails to decode the copied payload. A narrower batch-only repro swaps schema_version and reviewer silently. Synthetic copies only; the real source remains unchanged.

Root cause: confusing input physical order with target logical column mapping. Fix new three-table retention by choosing explicit canonical column names for values, comparison SELECT and INSERT; keep immutable conflict detection, exact raw payloads and fail-closed annotated-ID policy. Add reordered-column public reconcile and lookup regression for all three tables. Preserve original default-order, same-identity, repeated-merge and remap-rejection behavior. Root reproducer column_order_check.py records valid source preservation=false for all3 and lookup=false.

Ownership: introduced in this batch, within entity-resolution retention step, no external dependency/core upgrade. Route: bounded developer fix, retain review1 evidence and then independent round2; no permission escalation needed under current authorization. Wider claims remain limited to current26extractions and manual identity evidence, not365-paper full resolution or graph construction.

## Stage 3 — bounded ER-01 developer fix (local, not pushed)

Local `088a942f50f49b7b89094c2485ff1de0a387d94b`, tree `df3e9f179e84d1920b4cf8fbee1e0ee47dfd58ae`, parent remote `884f41f8c5e3ffba97567d894c78199c213cb9aa`. Only new resolution-table copying and its regressions changed. Values and comparisons use explicit canonical column names, INSERTs name their columns, and immutable conflicts still fail. Existing historical pipeline copying was not expanded into scope.

Postcommit developer targeted8 and full21 tests passed; all-three reordered-column public reproducer now preserves values and active lookup; repeated merge and whitespace checks passed, exit0. Logs fix1-targeted.log and fix1-fast.log retain exact local SHA. Real private input untouched. These are developer results; next publish identical tree and independently review round2.

## Stage 4 — independent review round 2 of 3 / acceptance

Reviewed remote `dfb170532d53afc60e1e3f06197fc640f0f6e4a7`, fetched/checked out with tree `df3e9f179e84d1920b4cf8fbee1e0ee47dfd58ae`, identical to developer local088a942. Full earlier diff and bounded fix assessed. **Verdict: pass; ER-01 resolved; no open blocking finding.**

| Independent validation | Result |
|---|---|
| Fast suite |21passed,1.152s,exit0; includes WAL snapshot interleaving, typed/scope/stale guards and prior schema/ingestion regressions |
| Real manual manifest |27entities/74mentions,34resolved/40pending; all original26Drafts and371relevance reviews retain exact values |
| Source binding/failures | exact support/mention hashes, bad second binding, wrong evidence pointer, kind/subtype/global-local conflict, immutable/raw mismatch and injected SQL failure rejected without partial changes; caller owns transaction |
| Staleness | changing a shared GRPO support source hides dependent identity; unrelated DAPO stays active; exact restore reactivates; historical repeat does not hide stale state |
| Retention | same-identity/repeat preserves all original and resolution rows; supported reordered columns preserve all3tables and lookup, FK0 |
| Actual locality |6results,8indexed SELECTs,28112internal text bytes,9137reply bytes;181first/175repeat SQLite VM instructions;1000unrelated batches/entities/mentions with49,152,000payload bytes keep reads/output unchanged at175VM |
| Negative lookup |20VM,1indexed SELECT,0rows/0payload text bytes,2reply bytes before/after unrelated growth |
| Installed wheel |new packaged schema passes meta-schema validation; fresh outside-source venv imports actual74review bindings and successfully queries current decisions,FK0 |

Immutable review data uses manual evidence rather than name-only merging. All40pending remain explicit, including all26Problemmentions; coverage is the26existing extraction records, not all365paper candidates. Per-extraction hash checking reads the necessary source payload/support closure; migrations intentionally inspect full input snapshots. Candidate identities are not a frozen ontology, exact model/checkpoint verification, scientific reproduction, or graph materialization.

A consistent standalone SQLite backup was prepared with the reviewed code:9,625,600bytes, SHA256 `f2f9ac10981a30be8442e96557352ff03346cbc868fba0aeefeb4aa389e9d6c8`, integrityOK/FK0; every original source table row remains exact. New tables contain1batch,27entities,74mentions. Next: gate/ref checks, publish approved code and persist backed-up DB/manifest/validation to Drive with download verification.

## Stage 5 — code publication, data persistence and recovery

Remote heads rechecked before updates: kg-builder main `f87c460924aaca04e9500c79ed82c0991fedf8e6`, candidate `dfb170532d53afc60e1e3f06197fc640f0f6e4a7`; parent main `a22851cf3e6d4e198f7e5234afaf1fb3be53de95`. Evidence gate READY (2rounds,ER-01resolved). Existing user authorization covers publication and data persistence. Child main fast-forwarded with expected-SHA/nonforced update to the reviewed candidate.

Drive source metadata was checked immediately before replacement and still matched the original9,400,320bytes/2026-10-31T04:21:57.754Z. The prior DB was copied before any replacement. The authoritative file ID and folder organization are preserved; only the new additive resolution tables/data change.

| Private artifact | Drive result |
|---|---|
| Authoritative DB |[research_knowledge.sqlite3](https://drive.google.com/file/d/1hO1VlJN_NOL1mDTyTTxDnopf331-62Q7/view?usp=drivesdk),9,625,600bytes,modified2026-10-31T06:07:30.599Z |
| Before-review backup |[pre_entity_resolution](https://drive.google.com/file/d/13R-a6OBaUt0XeqDTQuNKW1agMwm_agBD/view?usp=drivesdk),originalSHA25638e6c2f0afa41cc66a506946137f0e971dd06746968c3acfc2cf761276ee164d |
| Reviewed DB snapshot |[entity_resolution snapshot](https://drive.google.com/file/d/1ZL1DvwdE6N4f_GhHQooSHm8oWsaIGVla/view?usp=drivesdk),same exact bytes as authoritative DB |
| Manual decisions |[entity_resolution_manifest_20261031.json](https://drive.google.com/file/d/12tD1vXn_25BSbSBAPba9qxaR-DFBTIu0/view?usp=drivesdk),84,521bytes |
| Validation |[entity_resolution_validation_20261031.json](https://drive.google.com/file/d/19M64dlQn8xNQ6G4RgZsS-scfnnRUHJJN/view?usp=drivesdk),1,426bytes |
| Restore proof |[entity_resolution_roundtrip_20261031.json](https://drive.google.com/file/d/1iRC2LgpP8MWGlzNA4Dav-Y-rVIXjST9a/view?usp=drivesdk),actual downloaded-byte hashes and restored lookup counts |

The authoritative DB, prior DB backup, reviewed snapshot, manual manifest and validation JSON were downloaded again and verified byte-for-byte SHA256 equality. Restore proof was generated from those checks, uploaded separately and metadata-read back. Current DB/snapshot hash `f2f9ac10981a30be8442e96557352ff03346cbc868fba0aeefeb4aa389e9d6c8`; manifest `c0a5f29fe74aac52acb46456c9839a1e4f4c201d7e430976cb0206aed46e3106`; validation `cf7fe26abedc1deed10234f48f8ede20fa780d7303e2b9d476ab3fef2db44f9a`. Restored DB integrityOK/FK0;365papers,389versions,397sources,26extractions,371relevance reviews,1resolution batch,27entities,74mentions. API lookup of all74returns34current identities and40pending,0stale.

The first restore-script invocation accidentally used the default interpreter without jsonschema and failed before any download/write. Retried with the established dependency environment; all restore checks passed. This environment-only failure and successful raw results are retained separately.

Parent integration pins the reviewed child and adds this cumulative report, reproducible synthetic/private-input check drivers, logs and README handoff. Private manifests, DBs and original paper payloads are excluded from Git. Next work should review the14pending legacy Method labels against primary sources and define shared ResearchProblem granularity; pending remains meaningful evidence, not permission to fabricate merges. No graph materialization, LLM API, embedding or scheduler ran.

### Final integration readback

Parent main fetched at `8524c60fe3c949dc8fe017ddb96d6957bd550b2b`; tree `a1329c2d08956ab95336b9e5f574b14e251df385` matches the prepared local tree. Gitlinks: kg-builder `dfb170532d53afc60e1e3f06197fc640f0f6e4a7`; research-agent `75a08ee785a02a8b6d0c17a10501f6fe076fbd57` unchanged. Working trees clean at readback. Final report-only publication does not change the reviewed implementation and does not require rerunning passed production tests. No open blocker or outstanding permission request.
