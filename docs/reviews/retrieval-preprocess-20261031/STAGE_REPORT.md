# Retrieval preprocessing — 2026-10-31

Status: collecting standardized metadata; implementation in progress.

Scope: preprocess existing 365-paper corpus as a separate reproducible retrieval index. Master SQLite, 40 Drafts, original classifications and entity-resolution history remain unchanged. Reuse OpenAlex topics/keywords/references/related-work recommendations and existing contributions. No Semantic Scholar API, paid LLM, embeddings or graph writes. Source failure is not a negative lookup. Missing metadata and missing contributions are separately reported.

Baseline parent070be6edaa6c42a12378f99f43c71a498bd3e81b; childd99883bdba496373d1a61365a47e63dff0e5bf41. Input Drive file1hO1VlJN_NOL1mDTyTTxDnopf331-62Q7 unchanged at10,076,160bytes /2026-10-31T07:10:37.248Z; local restored SHA25632dc56e3cfc6e7ce531535c7d523303e3f7b96105f4ffb64e093c5ee21dc1aa5. Sidecar avoids changing the established reconciliation contracts.

Developer retrieval_preprocess(gpt-6-sol/medium); root collection and independent review. Branchfeat/retrieval-preprocessing-20261031. Acceptance:365paper coverage; strong-ID matches or explicit unresolved candidates; provenance/score/namespaces preserved; absent/error/empty differentiated; master untouched; atomic separate index build; indexed paper lookup; no manufactured source IDs; installed and fast tests; Drive upload/download hash restoration.

## Collection checkpoint

OpenAlex single-record probe200; unauthenticated batch429. Authorized key used privately; first2requests401 from a local transcription error then corrected. Subsequent ID/DOI/location batches200,309unique works collected before title-candidate fallback. Neither key nor authenticated URLs included in logs/exports. Title search discovers candidates only; identity acceptance remains strong-ID based. ArXiv original class fetch follows. No source failure treated as absence.

## Stage 1 — developer delivery, local

Local7d4f1afb3a448637f83f8e5badfaa644c44adf18, branchfeat/retrieval-preprocessing-20261031, not yet pushed. Three files/485insertions: sidecar builder+indexed point getter, contract docs,4focused tests. Sidecar stores original paper/version/source IDs, standardized OA labels and scores/parent hierarchy, distinct reference/recommendation edges, existing contribution objects and separate missing-work queues. Atomic output replacement; master read-only; expected sourcehash verification and consistent source read transaction.

Developer4targeted tests pass, master-only365paper build succeeds with403versions/411sources/11contributions across6papers/40historical Drafts. Initial system-Python full suite blocked:4legacy modules lackjsonschema; this is an environment failure, not a passed suite. Rerun in existing dependency-installed test venv pending before publication. Actual enrichment still collecting; no claim of full data acceptance. Root independently examining implementation/collector.

### Developer verification completion

Follow-up6fed63f03d329afeafcfd1a21ad45c6f1893ee31 adds reverse label/edge indexes for shared-label and incoming-edge expansion. Tree8aebd6a97b993ca5a0f27927cd1e0cbfd79b88fa. Dependency-installed /tmp/kg-builder-test-venv/bin/python full unittest33passed/1.310s/exit0; developer log preserved. Previous system dependency failure remains historical evidence; no production defect inferred. Ready for matching remote publication and independent review.

## Stage 2 — fixed-remote independent review round1/3

Remote candidatef77d3be5a5e764ab26089a683708de6c26aa1cf6 fetched; tree9c37f4dc004664fec49440c8e8f7b08d62cb0873 equals local final developer2b27a0b9b703df81021ea7c14da337c066517239. This final developer extension retains original S2 category fields when available. Full baseline-to-head303line module, docs and132line tests reviewed. Verdict PASS; no confirmed blocking finding. Root independent full regression33passed/1.097s/exit0. Dependency-installed environment resolves initial system-Python import block. Wheel built successfully and includes new module.

Real-data public CLI indexed all365papers/403versions/411source pointers. Exact all365enrichment-row crosscheck, original IDs/versions and11contribution objects unchanged, masterSHA unchanged, SQLite integrity/FK pass.302papers matched toOA;302withtopics/301withkeywords,296with originalarxivclasses.7ambiguous strong-ID mappings and50unconfirmed title candidate lists defer;6bounded lookups return noresults. First2auth errors recovered successfully; current pending cases are identity ambiguity, not observed active429.

Index labels4706(including772heuristic candidate rows,906standard topic rows+302primary copies,1917keywords,513arxivclass rows+296primary copies);3327edges(317references across18papers,3010recommendations across301papers). Only1reference edge connects two local candidates; citation completeness is sparse and graph retrieval quality is untested. Recommendation edges are not citations, and external IDs do not expand corpus recursively.

Outstanding tasks:345contribution summaries with text;14needtext;6classification gaps eligible for a later prediction;57classification cases defer pending identity confirmation. Existing11contributions/6papers remain Draft. No newLLMsummary, fabricatedOAIDs, embeddings, graph or final retrieval benchmark executed.

Locality from publicget_paper:8indexedSELECTs/1219SQLiteVM/19,380replybytes, cold and repeated; adding1000unrelated4KBpapers+labels leaves VM/SELECT/output identical. Missingtarget1SELECT/206VM/4replybytes. ActualEXPLAIN plans index bypaperID; only selected children sort. Full-build scans are necessary one-passcorpus preparation. Raw evidence and acceptance driver preserved.

## Stage 3 — publication and actual recovery

GateREADY,1review round, no blockers; expected-SHA nonforced childmain update published reviewedf77d3be5a5e764ab26089a683708de6c26aa1cf6. Source master remains unchanged. Separate sidecar6,275,072bytes SHA2565b7d2c6f6c4c9e902a36958167cf3442a780fe9e7367cac4d32e95d9e853acb0.

Drive artifacts:
- [Retrieval index](https://drive.google.com/file/d/11Sds7d838toBqjuj4UWxJKbB2FI8EnDg/view?usp=drivesdk)
- [Before-step master backup](https://drive.google.com/file/d/1v0Yzc1PqOuxiV0Q8CRJ9dpR6uToESgNf/view?usp=drivesdk)
- [Enrichment snapshot](https://drive.google.com/file/d/1Tq1VVh2Q3H7JmYIWxNxNQ9KyGz4pCnfZ/view?usp=drivesdk)
- [Remaining task queue](https://drive.google.com/file/d/1QRYKfswfnBkVax7v1abOndxALKx0cGml/view?usp=drivesdk)
- [Collection audit](https://drive.google.com/file/d/1fBFYPB3TNMPfIGP7Zv-rs5YeZ6383I0H/view?usp=drivesdk)
- [Independent validation](https://drive.google.com/file/d/11_Cmwgc6ROg9yZ6gGZe5plAh0scY7wpW/view?usp=drivesdk)

All6files downloaded again; exactSHA256 matches, restoredSQLite integrityOK/FK0. Rebuilt sidecar from downloaded original backup+enrichment; all8data tables exactly equal downloaded index (build timestamp/input filename metadata intentionally differ). Original master backup hash32dc56e3cfc6e7ce531535c7d523303e3f7b96105f4ffb64e093c5ee21dc1aa5. Source/enrichment/tasks/audit/validation hashes inlogs/roundtrip.json. Wheelzipimport outside checkout verified; package source no credentials/private datasets. Temporary authorized key file removed after collection.

Current work complete: standardized preprocessing pass and gap accounting. Contribution generation remains345text-ready +14needtext;6classification predictions are not performed;57identity cases defer. No claim of full semantic processing or measured graph-retrieval quality. Parent report/pin integration follows.
