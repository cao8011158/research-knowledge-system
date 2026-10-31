# Extraction schema and atomic import — 2026-10-31

Current status: independent review passed in round2; kg-builder main fast-forwarded to `f87c460924aaca04e9500c79ed82c0991fedf8e6`. Parent integration and evidence publication follow below.

Stages: baseline → developer candidate → review1 (two P2 findings) → developer fixes → review2/pass → publication and handoff.

## Scope and baseline

User authorized executable schema validation, atomic extraction imports and reconciliation retention, with acceptance on 20 legacy and 6 pilot Draft records. No LLM API calls, scheduler or graph materialization.

Main baseline: `3c289c84acc4836ab337846c682aced05c2c829f`; kg-builder baseline: `ddaa6d546d6287ae3c9379288b4be7b0d707aa5e`. Branch: `release/fulltext-pilot-20261031`; publication targets must be rechecked before updates. Developer: existing ingestion_fix agent; independent reviewer: root.

Baseline: `PYTHONPATH=src python -m unittest discover -s tests -v`, kg-builder, exit 0, 6 tests. Default Python currently lacks jsonschema; dependency setup is under investigation.

Acceptance: versioned strict schema and explicit legacy profile; invalid batches leave no partial writes; caller transactions remain controlled by caller; repeated imports preserve IDs and unchanged data; evidence and typed endpoints resolve; relevance reviews and provenance survive reconciliation; unknown tables fail explicitly. Real source payloads remain private. Tests include negative contracts, packaged schemas, real 26-record acceptance, recovery and indexed ID query cost under unrelated growth.

Formal review rounds completed: 0.

## Pre-implementation evidence

Fresh Drive readback matches SHA256 `38e6c2f0afa41cc66a506946137f0e971dd06746968c3acfc2cf761276ee164d`, integrity OK. Baseline counts: 365 papers,389 versions,397 source records,26 extraction rows,371 relevance reviews. Full table row digests and original 26 payloads retained privately.

Known authorized requirement reproduced against baseline source in an isolated copy: a two-record CLI import changes the first existing record, then rejects the second unknown version (exit1). The first change remains committed. This diagnosis precedes formal review and does not count as a review round.

Dependency setup: isolated `/tmp/kg-builder-test-venv`, jsonschema4.26.0 available; default runtime remains unchanged. Git remote main heads still match the two recorded baselines.

## Stage 1 — developer delivery (local, not yet pushed)

Candidate local commit `8fdf4b387a992e624f0c2fa8bcd36d285993f666`, tree `66b9153f8c530cc80cc2431ac69e662e44a74e23`, base `ddaa6d546d6287ae3c9379288b4be7b0d707aa5e`. Developer: ingestion_fix; independent reviewer: root.

Implementation: packaged Draft2020-12 legacy and pilot schemas, per-kind known-field and semantic reference checks; batch savepoint import with stable existing IDs and unchanged payload/timestamp retention; CLI prevalidation; review retention, structured-reference remapping and explicit unsupported table/column rejection during reconciliation. Candidate ontology documentation and operations instructions updated.

Developer evidence: targeted seven tests passed; fast13 tests passed; diff whitespace check passed (exit0). Logs copied into this report directory. Wheel contents include both JSON schemas. Developer also reports actual26 profile validation and copied-data stable reimport plus371review retention. Those real-data results are not yet independent acceptance.

No LLM API, scheduler or graph execution. Supplementary unknown JSON properties retained; known properties checked. Schema remains candidate, and legacy rows are neither rewritten nor promoted. Next: publish exact tree to candidate branch, verify remote SHA, perform independent review round1 and real-data failure/scale checks.

## Stage 2 — remote candidate and independent review round 1/3

Reviewed remote commit `c09b091a114d505ee3cfabe8654334d7af7207a4`; fetched branch `work/extraction-schema-20261031`, tree exactly `66b9153f8c530cc80cc2431ac69e662e44a74e23`, identical to developer local commit. The full baseline-to-head implementation, schemas, tests and changed documentation were inspected. Verdict: **changes required**, two confirmed P2 issues in current authorized batch. Main remains at baseline.

Independent checks: fast13 tests passed (exit0); actual26-record acceptance passed, including CLI invalid second item, injected SQL second-write failure, stable stored IDs/payload strings/timestamps, outer transaction ownership, all original active rows,371review retention, provenance membership and repeat reconciliation. Original private input bytes unchanged; output integrity OK and no foreign-key violations. Locality: first/repeat calls both at0 and1000 unrelated records (16,384,000 abstract bytes) execute44 SQLite VM instructions,4 statements,2 indexed SELECTs returning2 rows,33 reply bytes. EXPLAIN QUERY PLAN shows indexed version ID and natural extraction-key searches, no table scans. Full reconciliation necessarily reads all input rows.

### RKG-S01 — source text altered during ID remapping (P2, blocking)

Location: `scripts/reconcile_sqlite.py:remap_payload`. New recursive remapping rewrites every matching string, regardless of field semantics. Public synthetic reconcile of two same-DOI inputs correctly maps paper/version IDs but also changes summary equal to an old ID, method description beginning with an old version key, and an arbitrary extension quote. Expected: only structured ID paths change; all source text remains exact. Root cause is context-free recursion over strings. Fix: rewrite only schema-declared identifier paths (top-level ownership, declared entity keys/relation and evaluation references); preserve free text/extensions. Test public reconcile and retain existing nested reference remapping.

### RKG-S02 — empty assertion evidence accepted (P2, blocking)

Location: pilot JSON Schema evidence_refs arrays. A valid contribution with `evidence_refs=[]` passes validation, contradicting the source-attribution contract. Fix: require at least one reference for declared pilot assertions/relations and an evidence locator for the full-text pilot profile. Keep legacy compatibility unchanged. Validate six real pilot records and negative empty-evidence cases.

Both issues originate in this batch and lie within its authorized schema/data-retention scope; no external dependency limitation or scope expansion. They are not observed corruption of the real private database, which remains untouched. Route: bounded developer fixes, then review round2 on a newly frozen remote commit. Remaining broader limits: candidate ontology, no entity resolution or graph writer; performance evidence is SQLite/synthetic growth rather than graph-scale verification.

## Stage 3 — bounded developer fixes (local, not yet pushed)

Local commit `a28c6e390de849f1164d4adc0ae555ae2c17f506`, tree `b9499954bf6ed0aa326214348c6ddf3eb73497f7`, parent remote candidate `c09b091a114d505ee3cfabe8654334d7af7207a4`. Four files changed,78 additions/28 deletions, including operations documentation.

RKG-S01 fix restricts remapping to declared ownership/entity/evaluation/relation ID paths; review payloads map only top paper_id, and free text/extensions are preserved. Review schema_version is not processed as extraction schema. Early validation failures now close the newly opened read-only input. RKG-S02 adds minItems1 to pilot assertion/relationship references and evidence locators; legacy remains unchanged.

Developer targeted7 and full13 tests passed; root's public counterexample now reports all preservation/evidence checks true in developer execution. Whitespace check passed. Logs retained separately as fix1-targeted.log and fix1-fast.log. These results await independent round2; no LLM API/scheduler/graph activity or main merge.

## Stage 4 — independent review round 2/3 and feature acceptance

Reviewed remote commit `f87c460924aaca04e9500c79ed82c0991fedf8e6`, fetched and checked out with tree `b9499954bf6ed0aa326214348c6ddf3eb73497f7`, identical to developer local `a28c6e390de849f1164d4adc0ae555ae2c17f506`. Baseline-to-head implementation and round1-to-round2 changes assessed. **Verdict: pass. RKG-S01 and RKG-S02 resolved. No open blocking findings.**

| Independent check | Result and boundary |
|---|---|
| Fast regression |13 tests passed,0.423s,exit0; collectors use mocks, no LLM/API extraction execution |
| Public source-text remap counterexample | ownership IDs map; summary, description and arbitrary nested extensions preserve exact values; empty contribution evidence rejected |
| Actual stored payloads |20 legacy +6 pilot validated; all remain Draft; existing IDs,payload JSON strings,timestamps stable on repeated import |
| Atomicity and caller ownership | malformed/unknown-schema input creates no DB; invalid second version and injected second SQL failure leave no partial rows; caller success/failure remains rollbackable |
| Real reconciliation and repeat |365 papers,389 versions,397 source records,26 extractions,371reviews; every original active row unchanged, all prior audit/redirect rows retained; repeat output+original preserves active rows; integrity OK,FK0 |
| Retention guards | unsupported table and added column rejected before output/report creation |
| Locality | unchanged44VM instructions,4statements,2 indexed SELECTs/2rows,33reply bytes at0 and1000 unrelated versions containing16,384,000 abstract bytes,first/repeat calls; query plans use version PK and natural extraction unique key |
| Installed package | wheel built via declared isolated build requirements, installed into a fresh venv outside source tree; both packaged schemas pass standards meta-schema checks and installed validator accepts actual26records; jsonschema4.26.0 |

Initial package build with `--no-build-isolation` failed because the test venv lacked setuptools. This is retained as an environment failure log, not a product defect. Retrying with the declared standard build isolation succeeded; clean install and probe exited0. No production change was needed. Wheel SHA256 `fbe0811813299f6a89e562f752c03499dc860ed85f1727fe50c6b6d07a16d160`.

Private source DB SHA256 remains `38e6c2f0afa41cc66a506946137f0e971dd06746968c3acfc2cf761276ee164d`. Acceptance was run on private copies; this batch does not rewrite the authoritative database or promote Drafts. Full reconciliation is intentionally O(N); per-record import reads only the referenced version/extraction via indexes. No graph-scale or cross-paper entity-resolution claim is made. Next: recheck target refs and gate, fast-forward approved code, update parent submodule/report, save validation result to Drive.

## Stage 5 — publication and handoff

Before publication, remote kg-builder main was still `ddaa6d546d6287ae3c9379288b4be7b0d707aa5e`; candidate was exactly `f87c460924aaca04e9500c79ed82c0991fedf8e6`, and parent main still `3c289c84acc4836ab337846c682aced05c2c829f`. Evidence gate returned READY with2completed review rounds and no blocking findings. Existing user authorization covers code push/main submodule update. Nonforced expected-SHA fast-forward of kg-builder main to the reviewed candidate succeeded.

The private validation result is saved at [schema_validation_20261031.json](https://drive.google.com/file/d/1pYnfiikonbQW3RNDPUbTICRzsvStkfsi/view?usp=drivesdk). Connector metadata readback and authenticated download verified1578bytes, SHA256 `505266dc596b50a5fe2e704e8040af95206ad08103dcb4cf81f89c453c4184f7`, identical to uploaded bytes. The source database metadata is still9400320bytes, modified2026-10-31T04:21:57.754Z. No authoritative DB replacement was needed for this validation-only batch.

Parent integration consists of the reviewed gitlink, README handoff and this cumulative report with synthetic reproducible checks and full logs. Code and reports contain no private source payloads, SQLite files or credentials. Review findings/earlier failure logs are retained.

Next authorized planning boundary: review cross-paper Method/ResearchProblem/Artifact aliases and add varied source-grounded examples before freezing the ontology or materializing a graph. This batch implements admission/retention correctness only; source-checking a reported result is not reproducing an experiment. No LLM API, scheduler, embedding or Neo4j execution occurred.
