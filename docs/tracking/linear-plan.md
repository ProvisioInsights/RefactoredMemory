# RefactoredMemory backlog and coverage map

Linear setup remains **paused by the owner**. No team, projects or issues have been created. Planning keys are repository references, not remote Linear IDs.

51 items: 10 research/documentation, 35 personal-v1 and 6 later-roadmap items. Coverage: C01–C30 and M01–M25.

Repository docs govern scope; tracking records delivery and evidence. Personal-v1 implementation and the NAS extension are authorized. Actual deployment, private-data use and access changes retain their explicit boundaries.

## Current evidence

The personal graph, MCP/OAuth, imports, split TLS listeners, guarded writes and resumable automatic synchronization are implemented. Native Linux qualification passed 146 tests. The acceptance report records current container and hosted-OS evidence separately. Actual NAS/Mac networking, hosted provider clients and original archives remain unqualified.

See [acceptance results](../ACCEPTANCE-RESULTS.md), [NAS deployment](../NAS-DEPLOYMENT.md) and [maintenance access](../REMOTE-ADMIN.md).

Hosted Ubuntu and macOS each passed all 146 tests and the three demonstrations at `73ab9e8`; see [CI evidence](../results/nas-hosted-ci.json).

## Accepted decisions

- **Q6 (accepted)**: Automatically accept model-inferred additions within configured client/agent grants, without per-item human review. Preserve source/evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history. Acceptance is neither human verification nor established truth and cannot create or widen authority.
- **Q7 (accepted)**: Configured clients/agents proactively capture useful knowledge within their grants. This does not authorize arbitrary source access, widened grants, unapproved continuous monitoring or a separate extraction service.
- **Q8 (accepted)**: Prefer an explicit owner correction in answers while preserving conflicting claims, evidence, concurrent branches and history. An authorized, attributed resolution references heads considered; preference is neither destructive overwrite nor proof of truth.
- **Q9 (accepted)**: MCP plus CLI first; no browser UI in v1. Richer graphical exploration remains later.
- **Q10 (accepted)**: Prove all three day-one workflows: retrieve project decisions and why; find relationships and supporting evidence; explain changes since last month. Use observable synthetic end-to-end scenarios.

## RefactoredMemory — Research and documentation gate

Q6–Q10 are accepted: scoped automatic inferred additions, proactive capture, preferred explicit owner corrections with alternatives/history retained, MCP plus CLI without browser UI, and all three day-one workflows. Explicit Proceed was received 2026-11-07. Detailed contracts, source/migration evidence and readiness criteria remain open where unverified; authorization does not pass them.

### R00 — Set up RefactoredMemory Linear tracking and verify full scope coverage

Status: **Backlog**.

Deferred at the owner’s request. No Linear team, projects or issues exist from this work. Resume external setup only when requested. This tracking convenience is not a prerequisite for research, documentation or later authorized product implementation.

Acceptance criteria:

- After a new owner request to resume, verify the intended Provisio Insights workspace and create/reuse the exact RefactoredMemory team without duplicating existing work.
- Create/reconcile the three projects, workstream parents and actionable issues, with public-safe repository links and requirement/test mappings.
- Verify every C01–C25 and M01–M20 is tracked in its correct v1/later scope, all v1 implementation issues retain their satisfied R09 authorization dependency, and no dependency cycle or fabricated completion exists.
- Record actual team/project/issue URLs and tracking conventions only after resumed setup and verification. R01/R03 record documentation/policy evidence; R09 records received authorization only. R00 remains deferred until requested external setup is actually completed. No product or qualification completion is implied.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md).

### R01 — Publish and reconcile the personal-v1 documentation baseline

Status: **Done**.

Completed documentation-scope baseline from the preceding work. Do not reopen settled product scope unless new owner direction changes it.

Acceptance criteria:

- Accepted scope records one personal owner; Mac plus Linux both write offline and sync; MCP, Markdown/Logseq and prior LivingAtlas import are v1.
- Repository docs and companion Pages are reconciled; corporate tenancy, content encryption and transitive mesh remain later.
- Baseline published at commit 7303a93aeed3b15f24dc03b411d043404100b13f. Q6 is recorded under R03; Q7–Q10 answers and explicit Proceed were received 2026-11-07 and are recorded in DECISIONS/R09. Baseline completion does not imply architecture or product acceptance.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md).

### R02 — Complete the source, current-state and research evidence ledger

Status: **In Progress**.



Acceptance criteria:

- Record document versions, repository commits and inspected files; distinguish documented, source-inspected, executed, measured and hypothetical claims.
- Reconcile predecessor and current-client memory authority assumptions without copying private code or data into public artifacts.
- Locate the supplied benchmark report/code/raw runs through authorized tools; preserve any unresolved archive-access limitation and do not select a backend from selective-read timing alone.
- Identify personal-v1 risks and useful primary research; do not require enterprise or advanced consolidation research to finish v1.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RESEARCH.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/EXECUTION_PROMPT.md).

### R03 — Record accepted Q6: scoped automatic acceptance of inferred knowledge

Status: **Done**.

The owner accepted automatic inferred additions within configured client/agent grants, without per-item human review. This completed item records policy in planning docs only, with no product implementation or tests claimed. Q7–Q10 are now accepted separately; explicit implementation authorization is recorded under R09.

Acceptance criteria:

- Record Q6 as accepted: model-inferred additions are automatically accepted within configured client/agent grants without per-item human review; preserve the distinction from explicit owner instructions and any actual human verification.
- Propagate the accepted policy through PRD, ADRs, MCP/import contracts, prompt, validation plan and tracking records. Record Q7–Q10 separately without reopening Q6.
- Require evidence/source links, actor/model/derivation attribution, uncertainty, conflicting claims and correction history. Acceptance is not human verification or established truth; source text and accepted assertions cannot create or widen grants.

Requirements: C20, C23.

Acceptance cases: M18.

ADRs: A03, A15.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md).

### R04 — Inventory legacy sources and define the import/migration contract

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Selected A17 implementation and recorded synthetic Linux evidence are now available. Complete this research/contract/readiness item only against its actual criteria; access and qualification gaps remain explicit.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md"], "remainingGaps": ["Owner’s actual Mac/Praxis2 and original legacy-run evidence remain incomplete where applicable."]}

Acceptance criteria:

- Inventory authorized Markdown/Logseq layouts and every discovered previous LivingAtlas store/run generation, snapshot, export and manifest without changing originals.
- Record availability/access gaps and define per-generation mappings for identity, source versions, provenance, world/knowledge times, corrections and unsupported/unknown fidelity.
- Define complete source/record accounting, repeat/change/removal behavior, isolated destinations, backup and rollback; separate legacy decryption compatibility from new product encryption.
- Prepare synthetic compatibility fixtures and a concrete live-import approval plan; this issue does not authorize live personal-data ingestion or key use.

Requirements: C14, C17, C19.

Acceptance cases: M11.

ADRs: A03, A10.

Dependencies: R02.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md).

### R05 — Select persistence and peer synchronization technology against the full contract

Status: **In Progress**.

ADR A17 selects Python 3.12+ standard library, SQLite WAL/synchronous=FULL and explicit dependency-based direct synchronization. The implementation and Linux evidence exist; source comparison, durability limits and actual target/client qualification remain subject to the recorded evidence boundaries.

Progress (historical core baseline): {"summary": "Selected A17 implementation and recorded synthetic Linux evidence are now available. Complete this research/contract/readiness item only against its actual criteria; access and qualification gaps remain explicit.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md"], "remainingGaps": ["Owner’s actual Mac/Praxis2 and original legacy-run evidence remain incomplete where applicable."]}

Acceptance criteria:

- Compare credible candidates for personal temporal semantics, durable acknowledgment, bounded graph retrieval, two offline writers, concurrency, recovery, portability and operating burden.
- Pin sources/versions, workload and durability assumptions; distinguish actual measurements from provider claims and missing contract features.
- Record the selected stack, alternatives, migration cost and revisit triggers in ADR A17 and the related ADRs. Use the received R09 authorization for bounded synthetic engineering work; installation, real-data and external-deployment permissions remain separate.

Requirements: C02, C04, C07, C11, C18.

ADRs: A04, A09, A17.

Dependencies: R02.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RESEARCH.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md).

### R06 — Finalize versioned temporal, query, authority and sync contracts

Status: **In Progress**.

Accepted Q6–Q10 and selected ADR A17 are reflected in implementation contracts. Detailed conformance and source/client evidence gaps remain open; the received Proceed and partial Linux results do not complete this contract/readiness record.

Progress (historical core baseline): {"summary": "Selected A17 implementation and recorded synthetic Linux evidence are now available. Complete this research/contract/readiness item only against its actual criteria; access and qualification gaps remain explicit. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md"], "remainingGaps": ["Owner’s actual Mac/Praxis2 and original legacy-run evidence remain incomplete where applicable."]}

Acceptance criteria:

- Specify identities/types, evidence, world-time uncertainty, replica-scoped knowledge/frontiers, source disputes, correction actions and concurrent lineage resolution.
- Define atomic operation groups, dependency visibility, durable progress, personal peer/client authority, current permissions across history and delete/rejoin/restore semantics.
- Define common query coverage/fidelity/error responses and limits; preserve an export/migration path without building corporate tenancy or encryption infrastructure.
- Reconcile diagrams, PRD and ADRs with accepted Q6–Q10, technology and migration decisions. Specify proactive capture within grants, explicit owner-correction preference without loss of conflicts/history, MCP/CLI only in v1, and observable project-decision/why, relationship/evidence and last-month-change workflows.

Requirements: C01, C02, C04, C05, C06, C07, C09, C11, C12, C13, C15, C16, C17, C19, C20, C21, C23.

ADRs: A02, A05, A06, A09, A10, A15, A17.

Dependencies: R03, R04, R05.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 6](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md).

### R07 — Verify latest-stable MCP and the actual client/SDK compatibility matrix

Status: **In Progress**.

Praxis2 is the confirmed target. Verify the latest stable MCP contract in RefactoredMemory and record installed-client execution separately; no changes in Praxis or Praxis2 are authorized or required as prerequisites.

Progress (historical core baseline): {"summary": "Selected A17 implementation and recorded synthetic Linux evidence are now available. Complete this research/contract/readiness item only against its actual criteria; access and qualification gaps remain explicit.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md"], "remainingGaps": ["Owner’s actual Mac/Praxis2 and original legacy-run evidence remain incomplete where applicable."]}

Acceptance criteria:

- Check official latest published stable MCP; record verification date, protocol revision, SDK support and actual target client versions.
- Use the confirmed Praxis2 target and the existing independent MCP client to record transports, discovery/metadata, version compatibility and authentication requirements. Do not request target confirmation or modify either client repository.
- Create applicable conformance and real-client evidence plans for stdio/Streamable HTTP. Do not assume an older initialize lifecycle or count mocks as client integration.
- Name client/credential/access blockers precisely; no external deployment or permission change is implied.

Requirements: C24, C08, C09.

Acceptance cases: M19.

ADRs: A16.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md).

### R08 — Finish documentation reconciliation and the personal-v1 readiness review

Status: **In Progress**.

Repository contracts, run instructions and evidence reports are being reconciled against the implemented scope and accepted decisions. Keep remaining source/client/platform qualification criteria open; R09 authorization does not auto-pass readiness.

Progress (historical core baseline): {"summary": "Selected A17 implementation and recorded synthetic Linux evidence are now available. Complete this research/contract/readiness item only against its actual criteria; access and qualification gaps remain explicit. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["Owner’s actual Mac/Praxis2 and original legacy-run evidence remain incomplete where applicable."]}

Acceptance criteria:

- PRD, ADRs, architecture, MCP, validation, research, decisions, execution prompt and companion Pages agree on scope and accepted decisions.
- Every required C/M item maps to an observable acceptance check and a delivery issue; deferred C22/M17, M08 and P01–P06 cannot block v1.
- Record accepted Q7–Q10 and resolve genuinely new implementation-blocking ambiguities, or record explicit owner acceptance of remaining limitations; present document links and an honest readiness summary. Keep source/client evidence gaps visible.
- Verify remaining readiness criteria on their own evidence. Explicit Proceed was received 2026-11-07 and is recorded by R09; this authorization does not itself complete R06/R08 or any release qualification.

Dependencies: R01, R02, R03, R04, R05, R06, R07.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/EXECUTION_PROMPT.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 6](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 7](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 8](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 9](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### R09 — Record received owner Proceed for personal-v1 implementation

Status: **Done**.

Owner explicitly said Proceed on 2026-11-07 after answering Q7–Q10. This Done item records permission to implement the agreed personal-v1 scope, not completion of contracts, research/readiness evidence or product qualification. Do not request the same authorization again.

Acceptance criteria:

- Record the explicit owner instruction “Proceed” on 2026-11-07 authorizing implementation of the agreed personal-v1 scope after accepted Q7–Q10.
- Reconcile accepted decisions throughout the docs before core coding; retain R06/R08 detailed-contract/readiness and source/client evidence gaps until their actual criteria are met.
- Keep all v1 items linked to this satisfied authorization record. Its completion is not product completion, passed tests or release acceptance.
- Keep Linear paused and later-roadmap, real-data, installation, external-deployment/provisioning, credentials/permissions, agreements and private-data exposure boundaries separate.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/EXECUTION_PROMPT.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md).

## RefactoredMemory — Personal knowledge store v1

The personal graph, MCP/OAuth, imports, split TLS listeners, guarded writes and resumable automatic synchronization are implemented. Native Linux qualification passed 146 tests. The acceptance report records current container and hosted-OS evidence separately. Actual NAS/Mac networking, hosted provider clients and original archives remain unqualified. Corporate tenancy, product content encryption, third-peer mesh and a cloud storage peer remain later. No Praxis repository changes or Linear setup.

### G00 — Personal temporal graph, storage and authority

Status: **In Progress**.

Temporal graph, storage, grants and lifecycle code are implemented with synthetic Linux acceptance evidence. This workstream remains In Progress while the complete cross-runtime/client/import qualification matrix is unfinished; passing Linux tests does not certify the owner’s Mac, Praxis2 or original archives.

Progress (historical core baseline): {"summary": "Graph/SQLite service and CLI are implemented. Synthetic Linux evidence covers sourced assertions, temporal history, owner-correction preference, scoped grants, atomic retry, restart, rebuild and restore; full issue acceptance remains open. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["No actual Mac runtime/filesystem qualification or physical-power-loss certification.", "Individual acceptance criteria remain subject to the complete evidence matrix; this state is not release completion."]}

Acceptance criteria:

- Complete graph/schema, time/lineage, durable storage, consistent queries, personal access and lifecycle subissues.
- Provide source-linked, bounded and inspectable personal knowledge with correct history after restart; retain one owner, not corporate tenancy.

Requirements: C01, C02, C05, C06, C07, C08, C09, C10, C11, C13, C16, C17, C19, C20, C21, C23.

Acceptance cases: M01, M02, M06, M07, M10, M12, M13, M14, M15, M16, M18.

ADRs: A17.

Dependencies: R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### G01 — Implement typed entities, sourced assertions, observations and evidence

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Graph/SQLite service and CLI are implemented. Synthetic Linux evidence covers sourced assertions, temporal history, owner-correction preference, scoped grants, atomic retry, restart, rebuild and restore; full issue acceptance remains open. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["No actual Mac runtime/filesystem qualification or physical-power-loss certification.", "Individual acceptance criteria remain subject to the complete evidence matrix; this state is not release completion."]}

Acceptance criteria:

- Implement stable IDs, schema versions, typed values/predicates/endpoints and bounded unresolved observations; unknown actions/predicates cannot silently affirm facts.
- Preserve supporting/contradicting/context evidence and source versions; distinguish source, actor, model/version, derivation, uncertainty and actual human review without manufacturing corroboration. Automatically admitted inferred assertions are not labelled human-verified or established truth.
- Exercise synthetic scalar/relationship/observation capture and evidence lookup with the same contract used by MCP and import.

Requirements: C01, C20.

Acceptance cases: M01, M13, M15.

ADRs: A02, A03.

Dependencies: R09, R06.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### G02 — Implement bitemporal history, semantic actions and visible conflicts

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Graph/SQLite service and CLI are implemented. Synthetic Linux evidence covers sourced assertions, temporal history, owner-correction preference, scoped grants, atomic retry, restart, rebuild and restore; full issue acceptance remains open. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["No actual Mac runtime/filesystem qualification or physical-power-loss certification.", "Individual acceptance criteria remain subject to the complete evidence matrix; this state is not release completion."]}

Acceptance criteria:

- World time and peer-scoped knowledge positions/frontiers are independent; preserve origin, receipt and application metadata, unknown/approximate dates and half-open intervals.
- Correct/retract/invalidate/reinstate append sourced lineage and reasons; retain past beliefs and concurrent heads without wall-clock winners. Prefer explicit owner corrections in answers under accepted Q8 while preserving competing claims, evidence, concurrent branches and history. An authorized, attributed resolution references the heads considered; automatic acceptance does not impose a human-review gate or silently resolve competing claims.
- Distinguish conflicting independent sources from revision branches and copied evidence; verify late receipt never backdates local knowledge.

Requirements: C05, C17, C19, C20.

Acceptance cases: M04, M13, M14, M15, M16.

ADRs: A02, A09.

Dependencies: R09, G01.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### G03 — Implement durable atomic operation storage and restart recovery

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Graph/SQLite service and CLI are implemented. Synthetic Linux evidence covers sourced assertions, temporal history, owner-correction preference, scoped grants, atomic retry, restart, rebuild and restore; full issue acceptance remains open. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["No actual Mac runtime/filesystem qualification or physical-power-loss certification.", "Individual acceptance criteria remain subject to the complete evidence matrix; this state is not release completion."]}

Acceptance criteria:

- Commit semantic groups and synchronization eligibility durably before acknowledgment; never expose a partial group.
- Implement stable operation IDs, versioned representation, replay/checkpoints and safe retries appropriate to the selected engine.
- Fail around local commits/checkpoints and restart without losing acknowledged work or inventing progress; record durability limits.

Requirements: C02, C04, C11.

Acceptance cases: M01, M06, M10, M16.

ADRs: A04, A09, A17.

Dependencies: R09, G01, R05.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### G04 — Implement consistent temporal queries, traversal, search and index rebuild

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Graph/SQLite service and CLI are implemented. Synthetic Linux evidence covers sourced assertions, temporal history, owner-correction preference, scoped grants, atomic retry, restart, rebuild and restore; full issue acceptance remains open. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["No actual Mac runtime/filesystem qualification or physical-power-loss certification.", "Individual acceptance criteria remain subject to the complete evidence matrix; this state is not release completion."]}

Acceptance criteria:

- Implement lookup, bounded neighbors/paths, timeline/history, evidence and text search with identical temporal/lineage semantics.
- Return replica/frontier, precision, conflicts, missing dependencies, history floor and coverage; partial absence cannot masquerade as global falsehood.
- Rebuild derived indexes from retained history and verify fixed-frontier answers/provenance before and after rebuild/compaction.

Requirements: C07, C15, C16, C21.

Acceptance cases: M01, M12, M13, M14, M16.

ADRs: A17.

Dependencies: R09, G02, G03.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### G05 — Enforce personal client grants, current authority and safe boundaries

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Graph/SQLite service and CLI are implemented. Synthetic Linux evidence covers sourced assertions, temporal history, owner-correction preference, scoped grants, atomic retry, restart, rebuild and restore; full issue acceptance remains open. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["No actual Mac runtime/filesystem qualification or physical-power-loss certification.", "Individual acceptance criteria remain subject to the complete evidence matrix; this state is not release completion."]}

Acceptance criteria:

- Authenticate personal clients and scope read/write/admin authority. Automatically accept inferred additions within configured client/agent grants without per-item review; deny out-of-grant operations and source-text attempts to widen authority. Allow proactive capture within configured grants under accepted Q7; do not widen source access or authority.
- Current grants govern historical queries and output destinations; local revocation prevents old known-at access from re-enabling authority.
- Bound input/query sizes, protect credentials and local paths, redact logs and label actual plaintext/processing profile honestly; HTTPS/TLS protects remote transport.
- Retain source/evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history for automatic acceptance; do not label acceptance as human verification or established truth.

Requirements: C08, C09, C10, C12, C16, C23.

Acceptance cases: M02, M09, M12, M18.

ADRs: A05, A06, A15.

Dependencies: R09, R03, G01.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### G06 — Implement personal delete, export, backup and restore lifecycle

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Graph/SQLite service and CLI are implemented. Synthetic Linux evidence covers sourced assertions, temporal history, owner-correction preference, scoped grants, atomic retry, restart, rebuild and restore; full issue acceptance remains open. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["No actual Mac runtime/filesystem qualification or physical-power-loss certification.", "Individual acceptance criteria remain subject to the complete evidence matrix; this state is not release completion."]}

Acceptance criteria:

- Keep administrative tombstones/restore separate from semantic retraction/invalidation; retain delete/edit conflicts.
- Export/restore consistent evidence, history, heads/conflicts, tombstones and progress with versioned mappings and controlled rejoin/fresh identity.
- Reject corrupt/missing artifacts and reconcile current personal grants/deletions before serving restored data; prevent stale-peer resurrection.
- Encoding round-trip proves portability, not encryption or enterprise erasure.

Requirements: C06, C11, C13, C21, C23.

Acceptance cases: M07, M10, M14, M16, M18.

Dependencies: R09, G02, G03, G05.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### S00 — Two personal offline-writable peers and direct synchronization

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Direct authenticated synchronization is implemented. Recorded Linux tests exercise separate stores/processes, offline corrections, dependency gaps, retries/replay, restart and stale/revoked peers. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["Actual owner Mac/Linux cross-machine qualification remains unavailable.", "Production certificates/endpoints and external deployment were not qualified or authorized."]}

Acceptance criteria:

- Complete authenticated peer identity/admission, dependency-aware exchange, conflict/frontier behavior and actual Mac/Linux qualification.
- Both peers remain locally readable/writable offline; synchronize semantic histories and fixed-frontier answers without rewriting earlier local-known history.

Requirements: C03, C04, C05, C06, C09, C12, C15, C17, C18.

Acceptance cases: M03, M04, M05, M06, M07, M09, M15, M16.

ADRs: A17.

Dependencies: R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### S01 — Implement personal peer admission, identity and protected transport

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Direct authenticated synchronization is implemented. Recorded Linux tests exercise separate stores/processes, offline corrections, dependency gaps, retries/replay, restart and stale/revoked peers. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["Actual owner Mac/Linux cross-machine qualification remains unavailable.", "Production certificates/endpoints and external deployment were not qualified or authorized."]}

Acceptance criteria:

- Admit only the owner’s intended personal peers with protected credentials and authenticated cross-host transport; graph writes cannot enroll peers.
- Validate origin/scope, peer identity and restart epochs; reject revoked/incorrect origins, conflicting replay and cloned identity cases.
- Document stale/offline policy limits and avoid content-encryption/operator-blind claims.

Requirements: C04, C09, C10, C12.

Acceptance cases: M02, M09.

ADRs: A06, A09, A17.

Dependencies: R09, G03, G05.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### S02 — Implement bounded graph-operation exchange and durable causal progress

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Direct authenticated synchronization is implemented. Recorded Linux tests exercise separate stores/processes, offline corrections, dependency gaps, retries/replay, restart and stale/revoked peers. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["Actual owner Mac/Linux cross-machine qualification remains unavailable.", "Production certificates/endpoints and external deployment were not qualified or authorized."]}

Acceptance criteria:

- Exchange missing operations plus required entities/evidence/predecessors with bounded batches, idempotency and durable receipt/application cursors.
- Do not make dependencies visible prematurely or skip gaps; detect reuse of an operation ID for different content.
- Handle duplicate/reordered/interrupted delivery, lost responses and checkpoint restarts without partial graph state or acknowledged-data loss.

Requirements: C03, C04, C15.

Acceptance cases: M03, M05, M06.

ADRs: A09, A17.

Dependencies: R09, S01, G02, G03.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 6](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### S03 — Converge offline corrections and expose peer knowledge, conflicts and sync state

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Direct authenticated synchronization is implemented. Recorded Linux tests exercise separate stores/processes, offline corrections, dependency gaps, retries/replay, restart and stale/revoked peers. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["Actual owner Mac/Linux cross-machine qualification remains unavailable.", "Production certificates/endpoints and external deployment were not qualified or authorized."]}

Acceptance criteria:

- Preserve concurrent offline lineage changes including retract versus invalidate and append an authorized resolution naming considered heads with actor/evidence attribution. Prefer explicit owner corrections while retaining conflicting claims/evidence/history under Q8; an automatic acceptance is not a human review event.
- Compare semantic answers at common frontiers; retain differing earlier local-known histories and distinguish source disputes from revision branches.
- Expose sync progress, dependency gaps, peer errors, unresolved branches, frontier and coverage to clients/inspection.

Requirements: C05, C15, C17, C20.

Acceptance cases: M04, M05, M12, M15.

Dependencies: R09, S02, G02, G04.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 6](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### S04 — Qualify the Mac/Linux disconnect, reconnect, crash and stale-rejoin journey

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Direct authenticated synchronization is implemented. Recorded Linux tests exercise separate stores/processes, offline corrections, dependency gaps, retries/replay, restart and stale/revoked peers. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["Actual owner Mac/Linux cross-machine qualification remains unavailable.", "Production certificates/endpoints and external deployment were not qualified or authorized."]}

Acceptance criteria:

- Run two actual selected runtimes on synthetic data; write on both while disconnected, correct concurrently, reconnect and verify semantic convergence.
- Exercise delivery disruption, process restart, delete/edit conflict and stale-peer rejoin using the declared transport/durability configuration.
- Record reproducible commands, versions, evidence and unavailable runtime/access gaps. Two-peer success does not qualify third-hop mesh.

Requirements: C03, C04, C05, C06, C13, C18.

Acceptance cases: M03, M04, M05, M06, M07, M09, M10, M15, M16, M18.

Dependencies: R09, S03, G06.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### M00 — Required MCP server and real-client interoperability

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Current-standard MCP stdio/HTTP and explicit legacy stdio compatibility are implemented. The installed independent Python MCP SDK 1.29.0 passed real Store/Service workflows over the 2025-11-25 compatibility path; modern 2026-07-28 checks are protocol/schema evidence. Praxis2 is the confirmed target, with actual installed integration still unexecuted. Both independent SDK tests passed locally; hosted macOS skips them. Do not change either Praxis repository.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["Actual installed Praxis2 integration remains unexecuted. Verify against the installed client when accessible; no change to either Praxis repository is authorized or a prerequisite for RefactoredMemory MCP support.", "Independent SDK evidence does not certify that SDK for the modern protocol or every LLM host."]}

Acceptance criteria:

- Expose the same personal graph/authority contract through true latest-published-stable MCP support and the agreed transports. Keep implementation changes in RefactoredMemory; client repository changes are outside this task and are not prerequisites.
- Qualify actual Praxis2 and at least one independent MCP client; protocol mocks cannot substitute for client evidence.

Requirements: C08, C09, C16, C23, C24.

Acceptance cases: M02, M12, M18, M19.

ADRs: A16, A17.

Dependencies: R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### M01 — Implement the current-standard MCP server and bounded graph tool surface

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Current-standard MCP stdio/HTTP and explicit legacy stdio compatibility are implemented. The installed independent Python MCP SDK 1.29.0 passed real Store/Service workflows over the 2025-11-25 compatibility path; modern 2026-07-28 checks are protocol/schema evidence. Praxis2 is the confirmed target, with actual installed integration still unexecuted. Both independent SDK tests passed locally; hosted macOS skips them. Do not change either Praxis repository.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["Actual installed Praxis2 integration remains unexecuted. Verify against the installed client when accessible; no change to either Praxis repository is authorized or a prerequisite for RefactoredMemory MCP support.", "Independent SDK evidence does not certify that SDK for the modern protocol or every LLM host."]}

Acceptance criteria:

- Implement the latest published stable MCP discovery, metadata/capabilities, schemas and stdio/Streamable HTTP behavior against official conformance requirements. Verify the standard-library implementation directly; optional SDK evidence cannot substitute for newest-spec support.
- Expose bounded capture, query, search/traversal, history/evidence and correction tools with consistent graph/provenance/coverage results. Accept inferred additions automatically within configured grants under Q6; support proactive capture within configured grants under accepted Q7 without widening authority or source access.
- Implement only deliberate tested compatibility for actual client needs; keep consumer, peer and owner-administration authority separate.

Requirements: C07, C08, C15, C16, C24.

Acceptance cases: M01, M12, M19.

ADRs: A16, A17.

Dependencies: R09, R07, G04, G05.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### M02 — Qualify MCP authorization, protocol errors, retries and interruption

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Current-standard MCP stdio/HTTP and explicit legacy stdio compatibility are implemented. The installed independent Python MCP SDK 1.29.0 passed real Store/Service workflows over the 2025-11-25 compatibility path; modern 2026-07-28 checks are protocol/schema evidence. Praxis2 is the confirmed target, with actual installed integration still unexecuted. Both independent SDK tests passed locally; hosted macOS skips them. Do not change either Praxis repository.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["Actual installed Praxis2 integration remains unexecuted. Verify against the installed client when accessible; no change to either Praxis repository is authorized or a prerequisite for RefactoredMemory MCP support.", "Independent SDK evidence does not certify that SDK for the modern protocol or every LLM host."]}

Acceptance criteria:

- Exercise unauthorized/overscoped requests, invalid schemas, unsupported versions, selected auth/transport requirements and bounded outputs.
- Automatically accept in-grant inferred additions without per-item human review, preserving source/evidence, actor/model/derivation, uncertainty, conflicts and correction history. Reject out-of-grant writes and grant-elevation attempts; retries and interruption/cancellation cannot invent completed writes or human verification.
- Compare MCP time/provenance/coverage answers to direct graph API results and verify sensitive content/credentials do not leak into ordinary logs.

Requirements: C08, C09, C10, C16, C23, C24.

Acceptance cases: M02, M12, M18, M19.

Dependencies: R09, M01, G05.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### M03 — Demonstrate real Praxis2 and independent-client memory workflows

Status: **In Progress**.

Praxis2 is the confirmed integration target. Record actual installed-client use when it can be executed, without changing either Praxis repository. Independent SDK results remain valid evidence for their tested protocol path, not a substitute for installed Praxis2 evidence.

Progress (historical core baseline): {"summary": "Current-standard MCP stdio/HTTP and explicit legacy stdio compatibility are implemented. The installed independent Python MCP SDK 1.29.0 passed real Store/Service workflows over the 2025-11-25 compatibility path; modern 2026-07-28 checks are protocol/schema evidence. Praxis2 is the confirmed target, with actual installed integration still unexecuted. Both independent SDK tests passed locally; hosted macOS skips them. Do not change either Praxis repository.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["Actual installed Praxis2 integration remains unexecuted. Verify against the installed client when accessible; no change to either Praxis repository is authorized or a prerequisite for RefactoredMemory MCP support.", "Independent SDK evidence does not certify that SDK for the modern protocol or every LLM host."]}

Acceptance criteria:

- Record actual client/SDK/protocol versions and connection configuration without secrets.
- From Praxis2 and an independent client, discover capabilities, submit an automatically accepted sourced inference within a configured grant without per-item review, query temporal evidence, inspect/correct it and verify denied unauthorized use. Acceptance retains provenance/uncertainty and is not human verification.
- Provide repeatable RefactoredMemory connection/run instructions and distinguish unexecuted installed Praxis2 integration from passing independent SDK/protocol checks. Neither Praxis repository is to be modified.
- Exercise all three C25/M20 day-one workflows through supported MCP clients and retain source/time/history/coverage fidelity; the installed independent SDK result does not substitute for actual Praxis2 application qualification.

Requirements: C08, C24, C25.

Acceptance cases: M19, M20.

Dependencies: R09, M02.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### I00 — Markdown/Logseq import and migration from previous LivingAtlas runs

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Markdown/Logseq and inspected legacy-format adapters, manifests, source bounds, repeat/change accounting and backup/rollback are implemented and exercised with synthetic SQLite fixtures.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["No original run inventory, personal archive or original keys were available.", "Encrypted adapters, old journal replay/hash qualification, identity alias handling and other documented fidelity gaps remain incomplete."]}

Acceptance criteria:

- Implement the common importer, Markdown/Logseq conversion and adapters for inventoried prior run/store generations.
- Preserve originals, source/time/identity/correction fidelity and per-record accounting; demonstrate repeat-safe synthetic migration and rollback.
- Legacy encrypted-source compatibility and a live-data approval plan remain separate from building new product encryption or performing a live import.

Requirements: C11, C13, C14, C17, C19, C20.

Acceptance cases: M10, M11, M13, M14, M16.

ADRs: A03, A10.

Dependencies: R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### I01 — Implement import manifests, source boundaries and complete record accounting

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Markdown/Logseq and inspected legacy-format adapters, manifests, source bounds, repeat/change accounting and backup/rollback are implemented and exercised with synthetic SQLite fixtures.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["No original run inventory, personal archive or original keys were available.", "Encrypted adapters, old journal replay/hash qualification, identity alias handling and other documented fidelity gaps remain incomplete."]}

Acceptance criteria:

- Route authorized imported changes through the common graph contract; preserve source identities/versions and distinguish original times from new-peer import knowledge. Model-derived additions may be accepted automatically within configured grants under Q6, without inventing source fidelity, human verification or permission to read additional sources.
- Bound approved roots/formats/sizes, prevent arbitrary file access and make unchanged, imported, unsupported, quarantined and failed outcomes inspectable.
- Persist ID mappings and import progress for safe retry; do not silently drop records, fabricate fidelity or overwrite originals.

Requirements: C14, C16, C17, C20.

Acceptance cases: M02, M11, M13, M15.

Dependencies: R09, R04, G02, G03, G05.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### I02 — Implement Markdown and Logseq capture with repeat/change semantics

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Markdown/Logseq and inspected legacy-format adapters, manifests, source bounds, repeat/change accounting and backup/rollback are implemented and exercised with synthetic SQLite fixtures.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["No original run inventory, personal archive or original keys were available.", "Encrypted adapters, old journal replay/hash qualification, identity alias handling and other documented fidelity gaps remain incomplete."]}

Acceptance criteria:

- Convert the inventoried supported Markdown/Logseq layouts with source references, supported structured facts and bounded unresolved observations.
- Automatically accept inferred additions within configured client/agent grants without per-item human review; retain evidence, actor/model/derivation, uncertainty, conflicts and correction history rather than presenting inference as source-stated or human-verified. Support proactive capture within configured grants under accepted Q7; importing real sources or adding a separate extraction service remains separately scoped.
- Test unchanged reimport, changed content/source versions, duplicate references, removals, malformed/unsupported inputs and source-level accounting with synthetic files.

Requirements: C01, C14, C19, C20.

Acceptance cases: M01, M11, M14, M15.

Dependencies: R09, I01, R03.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### I03 — Implement adapters for inventoried historical LivingAtlas generations

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Markdown/Logseq and inspected legacy-format adapters, manifests, source bounds, repeat/change accounting and backup/rollback are implemented and exercised with synthetic SQLite fixtures.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["No original run inventory, personal archive or original keys were available.", "Encrypted adapters, old journal replay/hash qualification, identity alias handling and other documented fidelity gaps remain incomplete."]}

Acceptance criteria:

- Provide and label adapter coverage for each available prior run/store/export generation from the inventory; missing/unsupported generations remain explicit gaps.
- Preserve IDs or mappings, original world/recorded-time meanings, evidence, correction branches and unknown fidelity while recording new import receipt knowledge separately.
- Use synthetic compatibility fixtures to verify meaningful temporal/provenance query equivalence, full record accounting and repeat/change safety; counts alone are insufficient.

Requirements: C11, C14, C17, C19, C20.

Acceptance cases: M11, M13, M14, M15, M16.

Dependencies: R09, I01, R04.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### I04 — Qualify encrypted legacy-input compatibility when inventory requires it

Status: **Backlog**.

Conditional compatibility work determined by inventoried legacy sources; it is not a mandate to build a new encryption system.

Progress (historical core baseline): {"summary": "Encrypted legacy inputs are identified and reported unavailable. No decryption compatibility implementation or original-key qualification is claimed; the conditional task remains Backlog.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["No original run inventory, personal archive or original keys were available.", "Encrypted adapters, old journal replay/hash qualification, identity alias handling and other documented fidelity gaps remain incomplete."]}

Acceptance criteria:

- Identify actual legacy encodings and original-key requirements from the source inventory; record not-applicable only with evidence if no encrypted input needs support.
- Qualify relevant decryption adapters using synthetic keys/fixtures, preserving source data and reporting unavailable original access precisely.
- Use original real keys only after separate authorization through approved secret handling; never request/store keys in chat, code or logs. Do not add new product encryption/custody infrastructure.

Requirements: C10, C14, C16.

Acceptance cases: M02, M11.

Dependencies: R09, R04, I03.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### I05 — Rehearse migration, verify rollback and prepare the live-import approval plan

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Markdown/Logseq and inspected legacy-format adapters, manifests, source bounds, repeat/change accounting and backup/rollback are implemented and exercised with synthetic SQLite fixtures.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["No original run inventory, personal archive or original keys were available.", "Encrypted adapters, old journal replay/hash qualification, identity alias handling and other documented fidelity gaps remain incomplete."]}

Acceptance criteria:

- Run isolated synthetic Markdown/Logseq and historical-generation migrations, preserving original archives and complete manifests/ID mappings.
- Verify meaningful temporal/source/lineage equivalence, repeated import, backup and rollback, including unsupported/fidelity/accounting reports.
- Prepare a concrete proposed real source set, destination, approvals/key needs, verification and rollback plan. Do not ingest live personal data or change original stores without separate explicit authorization.

Requirements: C13, C14, C17, C19.

Acceptance cases: M10, M11, M13, M14, M16.

Dependencies: R09, I02, I03, I04, G06.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### Q00 — Personal-v1 qualification, packaging and release evidence

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Local Linux verification passed all 86 synthetic tests, including both optional independent SDK tests. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2. Recorded acceptance, MCP, import, sync, benchmark and CLI evidence remains partial qualification.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["Owner’s actual Mac, installed Praxis2 and full original-archive qualification remain blocked on runtime/access/source evidence.", "No complete personal-v1 release acceptance, real-data migration or external deployment is claimed."]}

Acceptance criteria:

- Complete synthetic semantic/failure qualification, inspectability, comparable performance evidence, runtime packaging and the final acceptance matrix.
- Provide reproducible run/MCP/import/sync/restore instructions with limitations; distinguish measured Linux results from remaining actual Mac, Praxis2 and full-archive qualification.

Requirements: C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16, C17, C18, C19, C20, C21, C23, C24, C25.

Acceptance cases: M01, M02, M03, M04, M05, M06, M07, M09, M10, M11, M12, M13, M14, M15, M16, M18, M19, M20.

Dependencies: R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 6](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 7](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### Q01 — Run integrated temporal, durability and failure-injection qualification

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Local Linux verification passed all 86 synthetic tests, including both optional independent SDK tests. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2. Recorded acceptance, MCP, import, sync, benchmark and CLI evidence remains partial qualification.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["Owner’s actual Mac, installed Praxis2 and full original-archive qualification remain blocked on runtime/access/source evidence.", "No complete personal-v1 release acceptance, real-data migration or external deployment is claimed."]}

Acceptance criteria:

- Exercise the Rae/Northstar two-time fixture, correction/retract/invalidate/reinstate, uncertainty, source disputes and fixed-frontier cross-view equivalence. Include an automatically accepted but wrong in-grant inference, denied out-of-grant writes and a later owner correction; acceptance must not be marked human verification. Verify the Q8 preference for an explicit owner correction while conflicting claims, evidence and correction history remain inspectable.
- Inject local/sync commit/checkpoint failures, disorder/gaps/duplicate-ID conflicts, restore corruption and stale rejoin; verify acknowledged data, atomic visibility, source lineage and current authority.
- Publish reproducible synthetic fixtures/commands and failures, distinguishing process-kill coverage from physical-power-loss proof.
- Exercise C25/M20 synthetic project-decision/why, relationship/evidence and last-month-change journeys with source-linked results, owner-correction preference, time/history and incomplete-coverage labels.

Requirements: C01, C02, C04, C05, C06, C11, C13, C17, C19, C20, C21, C23, C25.

Acceptance cases: M01, M04, M05, M06, M07, M10, M13, M14, M15, M16, M18, M20.

Dependencies: R09, G06, S03.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 6](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 7](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### Q02 — Verify usable inspection, bounds, coverage and safe operational reporting

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Local Linux verification passed all 86 synthetic tests, including both optional independent SDK tests. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2. Recorded acceptance, MCP, import, sync, benchmark and CLI evidence remains partial qualification.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["Owner’s actual Mac, installed Praxis2 and full original-archive qualification remain blocked on runtime/access/source evidence.", "No complete personal-v1 release acceptance, real-data migration or external deployment is claimed."]}

Acceptance criteria:

- Owner/client can inspect source, actor/model/derivation, actual human review, time/history, conflicts, peer progress and effective personal grants through MCP plus CLI under accepted Q9. Automatic acceptance is visibly distinct from human verification and truth.
- Exercise empty/error/offline and partial-history responses, high-degree/bounded traversal, request/payload limits and redacted logs.
- No browser UI is required in v1. Verify all three Q10 tasks through MCP/CLI: project decisions and why; relationships and evidence; and changes since last month, with honest temporal coverage and the actual storage/processing profile.

Requirements: C08, C10, C15, C16, C21, C23, C25.

Acceptance cases: M02, M12, M16, M18, M19, M20.

Dependencies: R09, G04, G05, S03, M01.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 6](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 7](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 8](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### Q03 — Benchmark representative personal reads, writes, sync and recovery

Status: **In Progress**.



Progress (historical core baseline): {"summary": "A correctness-checked 1,100-entity/assertion Linux benchmark records repeated reads/writes and single transfer/rebuild/backup/restore/reopen measurements with raw output and source digest. This is measured personal-workload evidence, not an engine comparison or capacity claim.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md"], "remainingGaps": ["Owner’s actual Mac, installed Praxis2 and full original-archive qualification remain blocked on runtime/access/source evidence.", "No complete personal-v1 release acceptance, real-data migration or external deployment is claimed.", "Actual Mac performance, larger stores and repeated cross-network convergence/recovery distributions are not established."]}

Acceptance criteria:

- Pin engine/runtime versions, commits, host/OS/filesystem, fixtures, indexes, cache state, batch sizes and durability settings; verify correctness before ranking performance.
- Measure declared current/historical retrieval, traversal, acknowledged writes, cold open/index rebuild, memory/storage, transfer/convergence and recovery work using repeated independent runs.
- Keep supplied selective-read results and independent experiments separate; unsupported paths/failures and no physical-durability/enterprise-scale proof are explicit.

Requirements: C02, C07, C10, C15, C18.

Acceptance cases: M03, M06, M12, M16.

ADRs: A17.

Dependencies: R09, G04, S04, Q01.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RESEARCH.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 6](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 7](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md).

### Q04 — Package Mac/Linux peers and publish reproducible operating instructions

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Local Linux verification passed all 86 synthetic tests, including both optional independent SDK tests. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2. Recorded acceptance, MCP, import, sync, benchmark and CLI evidence remains partial qualification.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["Owner’s actual Mac, installed Praxis2 and full original-archive qualification remain blocked on runtime/access/source evidence.", "No complete personal-v1 release acceptance, real-data migration or external deployment is claimed."]}

Acceptance criteria:

- Provide reproducible installation/run/configuration instructions for the agreed runtimes, with dependencies and any approval requirements explicit.
- Document MCP connections, MCP plus CLI, with no browser UI in v1 under Q9, personal peer admission, offline/reconnect flows, import dry-run/rehearsal, backup/restore, troubleshooting and rollback.
- Keep examples synthetic, credentials external and real-data/deployment approvals separate; do not provision external infrastructure automatically.

Requirements: C08, C10, C11, C13, C14, C18, C24.

Acceptance cases: M03, M10, M11, M12, M19.

ADRs: A17.

Dependencies: R09, S04, M03, I05.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 6](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 7](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 8](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### Q05 — Close the personal-v1 acceptance matrix with evidence and limitations

Status: **In Progress**.



Progress (historical core baseline): {"summary": "Local Linux verification passed all 86 synthetic tests, including both optional independent SDK tests. The 83-test suite passed hosted macOS and Ubuntu CI at commit ebb73d2. Hosted macOS skipped two optional SDK tests; both SDK tests passed in the local Linux run. This cross-platform CI does not qualify the owner’s actual Mac/Linux pair or installed Praxis2. Recorded acceptance, MCP, import, sync, benchmark and CLI evidence remains partial qualification.", "evidenceLinks": ["https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md", "https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml"], "remainingGaps": ["Owner’s actual Mac, installed Praxis2 and full original-archive qualification remain blocked on runtime/access/source evidence.", "No complete personal-v1 release acceptance, real-data migration or external deployment is claimed."]}

Acceptance criteria:

- Link each in-scope C/M requirement to actual passing evidence or a named unresolved gap; deferred M08/M17/P01–P06 remain deferred, not passed.
- Verify real Praxis2/independent-client workflows, actual Mac/Linux offline sync, importer compatibility and rollback, scoped automatic inferred-addition acceptance without per-item review, personal authority and representative performance. Prove all three Q10 tasks (project decisions/why, relationships/evidence, changes since last month) and accepted proactive capture, owner-correction preference with retained conflicts/history, and MCP/CLI-only v1 with evidence.
- Reconcile final PRD/ADRs/run instructions and report what was built, passed, remains, and how to use it. Do not declare release acceptance with missing required evidence or infer permission for a live cutover.

Requirements: C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16, C17, C18, C19, C20, C21, C23, C24, C25.

Acceptance cases: M01, M02, M03, M04, M05, M06, M07, M09, M10, M11, M12, M13, M14, M15, M16, M18, M19, M20.

Dependencies: R09, Q01, Q02, Q03, Q04, M03, I05, S04.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 3](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ACCEPTANCE-RESULTS.md), [source 4](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP-CONFORMANCE.md), [source 5](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/IMPORT-FORMATS.md), [source 6](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/SYNC-PROTOCOL.md), [source 7](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RUNBOOK.md), [source 8](https://github.com/ProvisioInsights/RefactoredMemory/blob/ebb73d2/.github/workflows/verify.yml).

### N00 — NAS-first deployable personal peer

Status: **In Progress**.

NAS-first implementation and local verification are authorized and tracked here. Consult the linked acceptance report for executed evidence; actual NAS, Mac and hosted-client qualification remains separate.

Progress: Implemented locally; see acceptance evidence and the unexecuted target-device requirements.

Acceptance criteria:

- Reconcile docs before production changes; preserve existing graph and independent writable Mac peer.
- Deliver isolated NAS profile, maintained-AS OAuth, automatic sync and local evidence. Actual NAS deployment remains pending access.

Requirements: C26, C27, C28, C29, C30.

Acceptance cases: M21, M22, M23, M24, M25.

ADRs: A18, A19, A20, A21.

Dependencies: R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/NAS-CONTRACT.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/ACCEPTANCE-RESULTS.md).

### N01 — OAuth resource authorization and client protocol compatibility

Status: **In Progress**.

NAS-first implementation and local verification are authorized and tracked here. Consult the linked acceptance report for executed evidence; actual NAS, Mac and hosted-client qualification remains separate.

Progress: OAuth validation and independent MCP HTTP workflows passed, including real Keycloak issuance. Actual hosted clients remain under N06.

Acceptance criteria:

- Validate pinned issuer/audience/RS256/JWKS and access-token lifetime; map exact subject/client to current local agent grants.
- Test independent app/API profiles, public discovery/challenges, current revocation and explicit legacy HTTP compatibility; never grant owner or peer authority.

Requirements: C27, C30.

Acceptance cases: M22, M25.

ADRs: A19.

Dependencies: N00, R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/NAS-CONTRACT.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/ACCEPTANCE-RESULTS.md).

### N02 — Harden NAS containers and separate network listeners

Status: **Done**.

NAS-first implementation and local verification are authorized and tracked here. Consult the linked acceptance report for executed evidence; actual NAS, Mac and hosted-client qualification remains separate.

Progress: Local hardened-container and real Keycloak/Postgres qualification passed. Actual NAS, Mac and hosted clients remain under N06.

Acceptance criteria:

- Build non-root read-only image with dedicated data volume and separate public MCP/private sync TLS listeners.
- Supply isolated-network and optional tunnel profiles; prove synthetic allowed/denied paths and keep NAS VLAN/IPv6 verification separate.

Requirements: C26.

Acceptance cases: M21.

ADRs: A18.

Dependencies: N00, R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/NAS-CONTRACT.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/ACCEPTANCE-RESULTS.md).

### N03 — Automatic sync with durable backoff and capacity refusal

Status: **Done**.

NAS-first implementation and local verification are authorized and tracked here. Consult the linked acceptance report for executed evidence; actual NAS, Mac and hosted-client qualification remains separate.

Progress: Automatic sync and capacity refusal passed local synthetic tests.

Acceptance criteria:

- Bound each sync cycle, persist retry deadlines, honor Retry-After and avoid multiple local runners.
- Pause on capacity/permanent errors without false acknowledgement; verify cancellation, resume and no duplicate semantic writes.

Requirements: C28.

Acceptance cases: M23.

ADRs: A20.

Dependencies: N00, R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/NAS-CONTRACT.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/ACCEPTANCE-RESULTS.md).

### N04 — Private maintenance access and operator runbook

Status: **In Progress**.

NAS-first implementation and local verification are authorized and tracked here. Consult the linked acceptance report for executed evidence; actual NAS, Mac and hosted-client qualification remains separate.

Progress: Private VPN/SSH runbook delivered; actual connection awaits access.

Acceptance criteria:

- Use private VPN and host-key-verified dedicated SSH identity for the workload VM.
- Exclude DSM admin, Docker group and unrestricted sudo; describe explicit revocation and fixed privileged helper boundaries.

Requirements: C29.

Acceptance cases: M24.

ADRs: A21.

Dependencies: N00, R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/NAS-CONTRACT.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/ACCEPTANCE-RESULTS.md).

### N05 — Local NAS-profile integration qualification

Status: **Done**.

NAS-first implementation and local verification are authorized and tracked here. Consult the linked acceptance report for executed evidence; actual NAS, Mac and hosted-client qualification remains separate.

Progress: Local hardened-container and real Keycloak/Postgres qualification passed. Actual NAS, Mac and hosted clients remain under N06.

Acceptance criteria:

- Run synthetic JWT/maintained-AS, network separation, container, sync/recovery and capacity tests in available Linux/Docker.
- Record actual images, commands, results and optional-dependency coverage; distinguish macOS CI from the owner Mac.

Requirements: C26, C27, C28, C29, C30.

Acceptance cases: M21, M22, M23, M24, M25.

ADRs: A18, A19, A20, A21.

Dependencies: N00, R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/NAS-CONTRACT.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/ACCEPTANCE-RESULTS.md).

### N06 — Qualify actual NAS, Mac and hosted client connections

Status: **Backlog**.

NAS-first implementation and local verification are authorized and tracked here. Consult the linked acceptance report for executed evidence; actual NAS, Mac and hosted-client qualification remains separate.

Progress: Waiting for owner-provided NAS access and separate actual-client qualification.

Acceptance criteria:

- When the owner supplies access, inspect real DSM/packages/RAM, VLAN/IPv6/host rules and local storage; test intended blocked destinations.
- Verify actual Mac/NAS sync and hosted app/API connections using approved synthetic fixtures; live personal data and publication remain separately authorized.

Requirements: C26, C27, C28, C29, C30.

Acceptance cases: M21, M22, M23, M24, M25.

ADRs: A18, A19, A20, A21.

Dependencies: N00, R09.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/NAS-CONTRACT.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/codex/personal-memory-v1/docs/ACCEPTANCE-RESULTS.md).

## RefactoredMemory — Later roadmap

Future options retained for visibility. These issues do not block personal v1 and are not authorized for implementation by the current scope or the received personal-v1 implementation authorization. No invented dates or estimates.

### L01 — Later: multi-tenant and corporate ownership lifecycle

Status: **Backlog**.



Acceptance criteria:

- Keep single-owner v1 unchanged; revisit multiple personal/corporate domains only under separately agreed later scope.
- Preserve confirmed future ownership principle; design membership, offboarding, transfers, mixed-source policy and isolation with explicit choices.
- Qualify C22/M17 and relevant E02/E09 only when this phase is authorized; this issue never blocks v1.

Requirements: C22.

Acceptance cases: M17.

ADRs: A11, A12, A14.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md).

### L02 — Later: product encryption, custody, recovery and protected processing

Status: **Backlog**.



Acceptance criteria:

- Design content encryption, key custody/recovery, metadata/executor trust and applicable profiles under separate later authorization.
- Qualify P01–P06 and honest revocation/erasure/backup limits before making protected/operator-blind claims.
- Do not confuse required v1 TLS/basic authority or legacy decryption import compatibility with completion of this phase.

ADRs: A05, A11, A13, A14.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md).

### L03 — Later: additional personal peers and transitive relay mesh

Status: **Backlog**.



Acceptance criteria:

- Agree need/topology and admission/subscription boundaries beyond the required two peers.
- Qualify third-hop store-forward exchange, echo prevention, origin integrity and convergence without simultaneous connectivity under M08.
- Two-peer v1 success is not treated as proof; this issue does not gate personal v1.

Acceptance cases: M08.

ADRs: A09, A11.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md).

### L04 — Later: evidence-driven advanced retrieval and memory consolidation

Status: **Backlog**.



Acceptance criteria:

- Evaluate optional vectors/associative retrieval, linked summaries, consolidation, maintained decisions and procedural memory only against useful measured tasks.
- Preserve graph/source authority, derivation/review, scoped jobs, budgets, retry semantics and original evidence; use R01–R06 as appropriate.
- Adopt advanced modules only with measured quality/cost/operating benefit. Accepting authorized client-generated inferences is already v1 under Q6; separate extraction engines and consolidation remain later unless explicitly added. Proactive capture by configured clients/agents within grants is v1 under Q7. It does not authorize arbitrary source monitoring or a separate extraction/background service.

ADRs: A07, A08, A15.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RESEARCH.md).

### L05 — Later: shared SaaS, hybrid deployment and enterprise scale

Status: **Backlog**.



Acceptance criteria:

- Use observed workloads to justify partitioning, independently scaled workers, selective replication and broader operational profiles.
- Preserve temporal/provenance/coverage contracts and quantify cross-partition limits and actual security/performance assumptions.
- No enterprise-scale implementation or benchmarks gate personal v1; create a separate release scope and approval when needed.

ADRs: A11.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md), [source 2](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md).

### L06 — Later: richer personal inspection and graphical exploration

Status: **Backlog**.



Acceptance criteria:

- Identify later owner workflows beyond accepted MCP plus CLI v1. Browser UI is excluded from v1 under Q9 and may be evaluated here only under separately agreed future scope.
- Expose evidence/history/conflicts/authority accessibly without implying a visual graph is needed for v1 acceptance.
- Keep advanced visual/cinematic or automatic identity features separate from current source-linked inspection requirements.

Requirements: C08.

ADRs: A15.

Evidence and sources: [source 1](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md).

## Coverage

| Kind | ID | Tracked by |
| --- | --- | --- |
| requirements | C01 | R06, G00, G01, I02, Q00, Q01, Q05 |
| requirements | C02 | R05, R06, G00, G03, Q00, Q01, Q03, Q05 |
| requirements | C03 | S00, S02, S04, Q00, Q05 |
| requirements | C04 | R05, R06, G03, S00, S01, S02, S04, Q00, Q01, Q05 |
| requirements | C05 | R06, G00, G02, S00, S03, S04, Q00, Q01, Q05 |
| requirements | C06 | R06, G00, G06, S00, S04, Q00, Q01, Q05 |
| requirements | C07 | R05, R06, G00, G04, M01, Q00, Q03, Q05 |
| requirements | C08 | R07, G00, G05, M00, M01, M02, M03, Q00, Q02, Q04, Q05, L06 |
| requirements | C09 | R06, R07, G00, G05, S00, S01, M00, M02, Q00, Q05 |
| requirements | C10 | G00, G05, S01, M02, I04, Q00, Q02, Q03, Q04, Q05 |
| requirements | C11 | R05, R06, G00, G03, G06, I00, I03, Q00, Q01, Q04, Q05 |
| requirements | C12 | R06, G05, S00, S01, Q00, Q05 |
| requirements | C13 | R06, G00, G06, S04, I00, I05, Q00, Q01, Q04, Q05 |
| requirements | C14 | R04, I00, I01, I02, I03, I04, I05, Q00, Q04, Q05 |
| requirements | C15 | R06, G04, S00, S02, S03, M01, Q00, Q02, Q03, Q05 |
| requirements | C16 | R06, G00, G04, G05, M00, M01, M02, I01, I04, Q00, Q02, Q05 |
| requirements | C17 | R04, R06, G00, G02, S00, S03, I00, I01, I03, I05, Q00, Q01, Q05 |
| requirements | C18 | R05, S00, S04, Q00, Q03, Q04, Q05 |
| requirements | C19 | R04, R06, G00, G02, I00, I02, I03, I05, Q00, Q01, Q05 |
| requirements | C20 | R03, R06, G00, G01, G02, S03, I00, I01, I02, I03, Q00, Q01, Q05 |
| requirements | C21 | R06, G00, G04, G06, Q00, Q01, Q02, Q05 |
| requirements | C22 | L01 |
| requirements | C23 | R03, R06, G00, G05, G06, M00, M02, Q00, Q01, Q02, Q05 |
| requirements | C24 | R07, M00, M01, M02, M03, Q00, Q04, Q05 |
| requirements | C25 | M03, Q00, Q01, Q02, Q05 |
| requirements | C26 | N00, N02, N05, N06 |
| requirements | C27 | N00, N01, N05, N06 |
| requirements | C28 | N00, N03, N05, N06 |
| requirements | C29 | N00, N04, N05, N06 |
| requirements | C30 | N00, N01, N05, N06 |
| tests | M01 | G00, G01, G03, G04, M01, I02, Q00, Q01, Q05 |
| tests | M02 | G00, G05, S01, M00, M02, I01, I04, Q00, Q02, Q05 |
| tests | M03 | S00, S02, S04, Q00, Q03, Q04, Q05 |
| tests | M04 | G02, S00, S03, S04, Q00, Q01, Q05 |
| tests | M05 | S00, S02, S03, S04, Q00, Q01, Q05 |
| tests | M06 | G00, G03, S00, S02, S04, Q00, Q01, Q03, Q05 |
| tests | M07 | G00, G06, S00, S04, Q00, Q01, Q05 |
| tests | M08 | L03 |
| tests | M09 | G05, S00, S01, S04, Q00, Q05 |
| tests | M10 | G00, G03, G06, S04, I00, I05, Q00, Q01, Q04, Q05 |
| tests | M11 | R04, I00, I01, I02, I03, I04, I05, Q00, Q04, Q05 |
| tests | M12 | G00, G04, G05, S03, M00, M01, M02, Q00, Q02, Q03, Q04, Q05 |
| tests | M13 | G00, G01, G02, G04, I00, I01, I03, I05, Q00, Q01, Q05 |
| tests | M14 | G00, G02, G04, G06, I00, I02, I03, I05, Q00, Q01, Q05 |
| tests | M15 | G00, G01, G02, S00, S03, S04, I01, I02, I03, Q00, Q01, Q05 |
| tests | M16 | G00, G02, G03, G04, G06, S00, S04, I00, I03, I05, Q00, Q01, Q02, Q03, Q05 |
| tests | M17 | L01 |
| tests | M18 | R03, G00, G05, G06, S04, M00, M02, Q00, Q01, Q02, Q05 |
| tests | M19 | R07, M00, M01, M02, M03, Q00, Q02, Q04, Q05 |
| tests | M20 | M03, Q00, Q01, Q02, Q05 |
| tests | M21 | N00, N02, N05, N06 |
| tests | M22 | N00, N01, N05, N06 |
| tests | M23 | N00, N03, N05, N06 |
| tests | M24 | N00, N04, N05, N06 |
| tests | M25 | N00, N01, N05, N06 |
| laterEvolution | E01 | L05 |
| laterEvolution | E02 | L01, L05 |
| laterEvolution | E03 | L03 |
| laterEvolution | E04 | L05 |
| laterEvolution | E05 | L05 |
| laterEvolution | E06 | L04 |
| laterEvolution | E07 | L02 |
| laterEvolution | E08 | L02 |
| laterEvolution | E09 | L01 |
| laterEvolution | E10 | L02 |
| laterEvolution | E11 | L02, L05 |
| laterEvolution | E12 | L04, L06 |
| adrs | A01 |  |
| adrs | A02 | R06, G01, G02 |
| adrs | A03 | R03, R04, G01, I00 |
| adrs | A04 | R05, G03 |
| adrs | A05 | R06, G05, L02 |
| adrs | A06 | R06, G05, S01 |
| adrs | A07 | L04 |
| adrs | A08 | L04 |
| adrs | A09 | R05, R06, G02, G03, S01, S02, L03 |
| adrs | A10 | R04, R06, I00 |
| adrs | A11 | L01, L02, L03, L05 |
| adrs | A12 | L01 |
| adrs | A13 | L02 |
| adrs | A14 | L01, L02 |
| adrs | A15 | R03, R06, G05, L04, L06 |
| adrs | A16 | R07, M00, M01 |
| adrs | A17 | R05, R06, G00, G03, G04, S00, S01, S02, M00, M01, Q03, Q04 |
| adrs | A18 | N00, N02, N05, N06 |
| adrs | A19 | N00, N01, N05, N06 |
| adrs | A20 | N00, N03, N05, N06 |
| adrs | A21 | N00, N04, N05, N06 |
