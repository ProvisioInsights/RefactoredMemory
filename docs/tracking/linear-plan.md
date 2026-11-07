# RefactoredMemory — prepared tracking backlog

**External tracking is paused at the owner’s request.** No Linear team, projects or issues were created. No manual team-creation action is currently needed. This repository plan is available independently of Linear; external setup resumes only on a new owner request.

**Proposed future team:** RefactoredMemory · **suggested key:** RFM · **workspace:** Provisio Insights

**Scope:** personal v1 on Mac + Linux, both offline writable with sync; required MCP; Markdown/Logseq and prior LivingAtlas import. Corporate tenancy and product encryption are later.

**44 planned items across 3 projects.** All C01–C24 and M01–M19 are mapped, with E01–E12, R01–R06 and P01–P06 retained in the later roadmap. All 28 v1 items depend on explicit owner proceed. Q6 is accepted and recorded; Q7–Q10 remain unanswered. No dates, estimates or assignees are invented.

This readable view is generated from `linear-plan.json`. Planning keys are internal references, not Linear IDs or acceptance-test IDs. Statuses describe the plan/evidenced work, not remote Linear objects. R01 and R03 are completed documentation/decision records only; no product implementation or executed tests are claimed.

## Accepted policy and pending owner choices

| Decision | Status | Meaning | Tracked by |
| --- | --- | --- | --- |
| Q6 | Accepted | Automatically accept model-inferred additions within configured client/agent grants, without per-item human review. Preserve source/evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history. Acceptance is neither human verification nor established truth and cannot create or widen authority. | R03, R06, G01, G05, M02, M03, I02, Q01 |
| Q7 | Awaiting owner answer | Should configured clients proactively capture useful knowledge or write only on explicit requests? Q6 does not select capture triggers or authorize a separate extraction/background service. | R06, R08, G05, M01, I02 |
| Q8 | Awaiting owner answer | How should an explicit owner correction be preferred when competing claims remain, versus returning a dispute without a preferred claim? Preserve alternatives, provenance and correction history under either choice. | R06, R08, G02, S03, Q01 |
| Q9 | Awaiting owner answer | Should the v1 owner interface use MCP/CLI only or include a simple browser UI? Rich graphical/cinematic exploration remains separate later work. | R06, R08, Q02, Q04, L06 |
| Q10 | Awaiting owner answer | Which three day-one user tasks should v1 prove end to end? Use the answer to make usefulness and acceptance scenarios concrete. | R06, R08, Q02, Q05 |

## RefactoredMemory — Research and documentation gate

Active authorized planning for personal v1. Q6 is accepted and recorded: inferred additions are accepted automatically within configured client/agent grants without per-item review, with provenance and uncertainty retained. Q7–Q10, detailed contracts, source/migration evidence and architecture acceptance remain open. No product implementation starts until R09 is explicitly satisfied.

Milestones: Evidence and owner decisions; Reconciled architecture and readiness; Explicit implementation authorization

### R00 — Set up RefactoredMemory Linear tracking and verify full scope coverage

Planned status: Deferred by owner; external setup paused.

Deferred at the owner’s request. No Linear team, projects or issues exist from this work. Resume external setup only when requested. This tracking convenience is not a prerequisite for research, documentation or later authorized product implementation.

Acceptance criteria:

- After a new owner request to resume, verify the intended Provisio Insights workspace and create/reuse the exact RefactoredMemory team without duplicating existing work.
- Create/reconcile the three projects, workstream parents and actionable issues, with public-safe repository links and requirement/test mappings.
- Verify every C01–C24 and M01–M19 is tracked in its correct v1/later scope, all v1 implementation issues are directly blocked by R09, and no dependency cycle or fabricated completion exists.
- Record actual team/project/issue URLs and tracking conventions only after resumed setup and verification. R01 and R03 may be Done for their completed documentation/decision evidence; R00 remains deferred until actual external setup is requested and completed. No implementation or tests are implied.

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [DECISIONS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md)

### R01 — Publish and reconcile the personal-v1 documentation baseline

Planned status: Done.

Completed documentation-scope baseline from the preceding work. Do not reopen settled product scope unless new owner direction changes it.

Acceptance criteria:

- Accepted scope records one personal owner; Mac plus Linux both write offline and sync; MCP, Markdown/Logseq and prior LivingAtlas import are v1.
- Repository docs and companion Pages are reconciled; corporate tenancy, content encryption and transitive mesh remain later.
- Baseline published at commit 7303a93aeed3b15f24dc03b411d043404100b13f. The later accepted Q6 policy is recorded under R03; Q7–Q10 and the explicit proceed gate remain open. Baseline completion does not imply architecture or product acceptance.

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [ADRS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md) · [DECISIONS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md)

### R02 — Complete the source, current-state and research evidence ledger

Planned status: Backlog.

Acceptance criteria:

- Record document versions, repository commits and inspected files; distinguish documented, source-inspected, executed, measured and hypothetical claims.
- Reconcile predecessor and current-client memory authority assumptions without copying private code or data into public artifacts.
- Locate the supplied benchmark report/code/raw runs through authorized tools; preserve any unresolved archive-access limitation and do not select a backend from selective-read timing alone.
- Identify personal-v1 risks and useful primary research; do not require enterprise or advanced consolidation research to finish v1.

Sources: [RESEARCH.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RESEARCH.md) · [EXECUTION_PROMPT.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/EXECUTION_PROMPT.md)

### R03 — Record accepted Q6: scoped automatic acceptance of inferred knowledge

Planned status: Done.

The owner has accepted automatic inferred additions within configured client/agent grants, without per-item human review. This issue records the policy in planning documents only. No product implementation, executed tests or permission to proceed is claimed. Q7–Q10 remain unanswered.

Acceptance criteria:

- Record Q6 as accepted: model-inferred additions are automatically accepted within configured client/agent grants without per-item human review; preserve the distinction from explicit owner instructions and any actual human verification.
- Propagate the accepted policy through PRD, ADRs, MCP/import contracts, prompt, validation plan and tracking records. Track Q7–Q10 separately without inferring their answers or reopening Q6.
- Require evidence/source links, actor/model/derivation attribution, uncertainty, conflicting claims and correction history. Acceptance is not human verification or established truth; source text and accepted assertions cannot create or widen grants.

Requirements: C20, C23 · Tests: M18 · ADRs: A03, A15 · Decisions: Q6

Sources: [DECISIONS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md) · [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md)

### R04 — Inventory legacy sources and define the import/migration contract

Planned status: Backlog.

Acceptance criteria:

- Inventory authorized Markdown/Logseq layouts and every discovered previous LivingAtlas store/run generation, snapshot, export and manifest without changing originals.
- Record availability/access gaps and define per-generation mappings for identity, source versions, provenance, world/knowledge times, corrections and unsupported/unknown fidelity.
- Define complete source/record accounting, repeat/change/removal behavior, isolated destinations, backup and rollback; separate legacy decryption compatibility from new product encryption.
- Prepare synthetic compatibility fixtures and a concrete live-import approval plan; this issue does not authorize live personal-data ingestion or key use.

Requirements: C14, C17, C19 · Tests: M11 · ADRs: A03, A10

Prerequisites: R02

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### R05 — Select persistence and peer synchronization technology against the full contract

Planned status: Backlog.

Acceptance criteria:

- Compare credible candidates for personal temporal semantics, durable acknowledgment, bounded graph retrieval, two offline writers, concurrency, recovery, portability and operating burden.
- Pin sources/versions, workload and durability assumptions; distinguish actual measurements from provider claims and missing contract features.
- Record selected stack, alternatives, migration cost and revisit triggers in ADRs. Propose only necessary bounded experiments; no new experimental/product code without separate approval before the proceed gate.

Requirements: C02, C04, C07, C11, C18 · ADRs: A04, A09

Prerequisites: R02

Sources: [ADRS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md) · [RESEARCH.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RESEARCH.md)

### R06 — Finalize versioned temporal, query, authority and sync contracts

Planned status: Backlog.

Apply accepted Q6. Q7 capture triggers, Q8 preferred-claim handling, Q9 owner interface and Q10 day-one tasks remain consequential open choices; do not resolve them by implication.

Acceptance criteria:

- Specify identities/types, evidence, world-time uncertainty, replica-scoped knowledge/frontiers, source disputes, correction actions and concurrent lineage resolution.
- Define atomic operation groups, dependency visibility, durable progress, personal peer/client authority, current permissions across history and delete/rejoin/restore semantics.
- Define common query coverage/fidelity/error responses and limits; preserve an export/migration path without building corporate tenancy or encryption infrastructure.
- Reconcile diagrams, PRD and ADRs with accepted Q6, technology and migration decisions. Obtain and record Q7–Q10 answers for capture triggers, owner-correction/claim preference, v1 interface and three day-one tasks; do not treat Q6 as answering those questions.

Requirements: C01, C02, C04, C05, C06, C07, C09, C11, C12, C13, C15, C16, C17, C19, C20, C21, C23 · ADRs: A02, A05, A06, A09, A10, A15 · Decisions: Q6, Q7, Q8, Q9, Q10

Prerequisites: R03, R04, R05

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md) · [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [ADRS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md)

### R07 — Verify latest-stable MCP and the actual client/SDK compatibility matrix

Planned status: Backlog.

Acceptance criteria:

- Check official latest published stable MCP; record verification date, protocol revision, SDK support and actual target client versions.
- Inspect relevant Praxis client behavior and select an accessible independent MCP client. Record transports, discovery/metadata, version compatibility and auth requirements.
- Create applicable conformance and real-client evidence plans for stdio/Streamable HTTP. Do not assume an older initialize lifecycle or count mocks as client integration.
- Name client/credential/access blockers precisely; no external deployment or permission change is implied.

Requirements: C24, C08, C09 · Tests: M19 · ADRs: A16

Sources: [MCP.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md) · [ADRS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md)

### R08 — Finish documentation reconciliation and the personal-v1 readiness review

Planned status: Backlog.

Acceptance criteria:

- PRD, ADRs, architecture, MCP, validation, research, decisions, execution prompt and companion Pages agree on scope and accepted decisions.
- Every required C/M item maps to an observable acceptance check and a delivery issue; deferred C22/M17, M08 and P01–P06 cannot block v1.
- Resolve Q7–Q10 and other implementation-blocking ambiguities, or record explicit owner acceptance of any remaining limitation; present document links and readiness summary. Accepted Q6 and its recording are not implementation authorization.
- Do not start product implementation or mark the separate owner-proceed issue complete automatically.

Decisions: Q7, Q8, Q9, Q10

Prerequisites: R01, R02, R03, R04, R05, R06, R07

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md) · [DECISIONS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md) · [EXECUTION_PROMPT.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/EXECUTION_PROMPT.md)

### R09 — Gate: record the owner’s explicit “proceed” before product implementation

Planned status: Backlog.

Manual authorization gate. Do not auto-close from dependency completion or inferred consent.

Acceptance criteria:

- Documentation readiness review is complete and presented to the owner.
- Record a specific owner message explicitly authorizing implementation of the agreed personal-v1 scope.
- Close this gate only on that explicit instruction. Answers to research questions, accepted ADRs or the Linear setup request do not satisfy it.
- Keep all personal-v1 implementation issues blocked by this gate until authorization; later roadmap and real-data/deployment approvals remain separate.

Prerequisites: R08

Sources: [EXECUTION_PROMPT.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/EXECUTION_PROMPT.md) · [DECISIONS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md)

## RefactoredMemory — Personal knowledge store v1

Implementation and qualification backlog. Every issue requires the explicit owner proceed gate. Corporate tenancy, product content encryption and transitive mesh are excluded. Synthetic data only; live imports, keys, installs and external deployments retain their separate approval requirements.

Milestones: Temporal core and personal authority; MCP and import compatibility; Mac/Linux offline synchronization; Qualification and usable delivery

### G00 — Personal temporal graph, storage and authority

Planned status: Backlog.

Acceptance criteria:

- Complete graph/schema, time/lineage, durable storage, consistent queries, personal access and lifecycle subissues.
- Provide source-linked, bounded and inspectable personal knowledge with correct history after restart; retain one owner, not corporate tenancy.

Requirements: C01, C02, C05, C06, C07, C08, C09, C10, C11, C13, C16, C17, C19, C20, C21, C23 · Tests: M01, M02, M06, M07, M10, M12, M13, M14, M15, M16, M18

Prerequisites: R09

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md)

### G01 — Implement typed entities, sourced assertions, observations and evidence

Planned status: Backlog.

Acceptance criteria:

- Implement stable IDs, schema versions, typed values/predicates/endpoints and bounded unresolved observations; unknown actions/predicates cannot silently affirm facts.
- Preserve supporting/contradicting/context evidence and source versions; distinguish source, actor, model/version, derivation, uncertainty and actual human review without manufacturing corroboration. Automatically admitted inferred assertions are not labelled human-verified or established truth.
- Exercise synthetic scalar/relationship/observation capture and evidence lookup with the same contract used by MCP and import.

Requirements: C01, C20 · Tests: M01, M13, M15 · ADRs: A02, A03 · Decisions: Q6

Prerequisites: R09, R06

Workstream parent: G00

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md)

### G02 — Implement bitemporal history, semantic actions and visible conflicts

Planned status: Backlog.

Acceptance criteria:

- World time and peer-scoped knowledge positions/frontiers are independent; preserve origin, receipt and application metadata, unknown/approximate dates and half-open intervals.
- Correct/retract/invalidate/reinstate append sourced lineage and reasons; retain past beliefs and concurrent heads without wall-clock winners. Apply the Q8 owner-correction/preferred-claim policy once answered, preserving competing claims and history. An authorized, attributed resolution references the heads considered; automatic acceptance does not impose a human-review gate or silently resolve competing claims.
- Distinguish conflicting independent sources from revision branches and copied evidence; verify late receipt never backdates local knowledge.

Requirements: C05, C17, C19, C20 · Tests: M04, M13, M14, M15, M16 · ADRs: A02, A09 · Decisions: Q8

Prerequisites: R09, G01

Workstream parent: G00

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md)

### G03 — Implement durable atomic operation storage and restart recovery

Planned status: Backlog.

Acceptance criteria:

- Commit semantic groups and synchronization eligibility durably before acknowledgment; never expose a partial group.
- Implement stable operation IDs, versioned representation, replay/checkpoints and safe retries appropriate to the selected engine.
- Fail around local commits/checkpoints and restart without losing acknowledged work or inventing progress; record durability limits.

Requirements: C02, C04, C11 · Tests: M01, M06, M10, M16 · ADRs: A04, A09

Prerequisites: R09, G01, R05

Workstream parent: G00

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### G04 — Implement consistent temporal queries, traversal, search and index rebuild

Planned status: Backlog.

Acceptance criteria:

- Implement lookup, bounded neighbors/paths, timeline/history, evidence and text search with identical temporal/lineage semantics.
- Return replica/frontier, precision, conflicts, missing dependencies, history floor and coverage; partial absence cannot masquerade as global falsehood.
- Rebuild derived indexes from retained history and verify fixed-frontier answers/provenance before and after rebuild/compaction.

Requirements: C07, C15, C16, C21 · Tests: M01, M12, M13, M14, M16

Prerequisites: R09, G02, G03

Workstream parent: G00

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md) · [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md)

### G05 — Enforce personal client grants, current authority and safe boundaries

Planned status: Backlog.

Acceptance criteria:

- Authenticate personal clients and scope read/write/admin authority. Automatically accept inferred additions within configured client/agent grants without per-item review; deny out-of-grant operations and source-text attempts to widen authority. Q7 still determines capture triggers.
- Current grants govern historical queries and output destinations; local revocation prevents old known-at access from re-enabling authority.
- Bound input/query sizes, protect credentials and local paths, redact logs and label actual plaintext/processing profile honestly; HTTPS/TLS protects remote transport.
- Retain source/evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history for automatic acceptance; do not label acceptance as human verification or established truth.

Requirements: C08, C09, C10, C12, C16, C23 · Tests: M02, M09, M12, M18 · ADRs: A05, A06, A15 · Decisions: Q6, Q7

Prerequisites: R09, R03, G01

Workstream parent: G00

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md) · [MCP.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md)

### G06 — Implement personal delete, export, backup and restore lifecycle

Planned status: Backlog.

Acceptance criteria:

- Keep administrative tombstones/restore separate from semantic retraction/invalidation; retain delete/edit conflicts.
- Export/restore consistent evidence, history, heads/conflicts, tombstones and progress with versioned mappings and controlled rejoin/fresh identity.
- Reject corrupt/missing artifacts and reconcile current personal grants/deletions before serving restored data; prevent stale-peer resurrection.
- Encoding round-trip proves portability, not encryption or enterprise erasure.

Requirements: C06, C11, C13, C21, C23 · Tests: M07, M10, M14, M16, M18

Prerequisites: R09, G02, G03, G05

Workstream parent: G00

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### S00 — Two personal offline-writable peers and direct synchronization

Planned status: Backlog.

Acceptance criteria:

- Complete authenticated peer identity/admission, dependency-aware exchange, conflict/frontier behavior and actual Mac/Linux qualification.
- Both peers remain locally readable/writable offline; synchronize semantic histories and fixed-frontier answers without rewriting earlier local-known history.

Requirements: C03, C04, C05, C06, C09, C12, C15, C17, C18 · Tests: M03, M04, M05, M06, M07, M09, M15, M16

Prerequisites: R09

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md)

### S01 — Implement personal peer admission, identity and protected transport

Planned status: Backlog.

Acceptance criteria:

- Admit only the owner’s intended personal peers with protected credentials and authenticated cross-host transport; graph writes cannot enroll peers.
- Validate origin/scope, peer identity and restart epochs; reject revoked/incorrect origins, conflicting replay and cloned identity cases.
- Document stale/offline policy limits and avoid content-encryption/operator-blind claims.

Requirements: C04, C09, C10, C12 · Tests: M02, M09 · ADRs: A06, A09

Prerequisites: R09, G03, G05

Workstream parent: S00

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md)

### S02 — Implement bounded graph-operation exchange and durable causal progress

Planned status: Backlog.

Acceptance criteria:

- Exchange missing operations plus required entities/evidence/predecessors with bounded batches, idempotency and durable receipt/application cursors.
- Do not make dependencies visible prematurely or skip gaps; detect reuse of an operation ID for different content.
- Handle duplicate/reordered/interrupted delivery, lost responses and checkpoint restarts without partial graph state or acknowledged-data loss.

Requirements: C03, C04, C15 · Tests: M03, M05, M06 · ADRs: A09

Prerequisites: R09, S01, G02, G03

Workstream parent: S00

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### S03 — Converge offline corrections and expose peer knowledge, conflicts and sync state

Planned status: Backlog.

Acceptance criteria:

- Preserve concurrent offline lineage changes including retract versus invalidate and append an authorized resolution naming considered heads with actor/evidence attribution. Apply Q8 preferred-claim behavior once answered; an automatic acceptance is not a human review event.
- Compare semantic answers at common frontiers; retain differing earlier local-known histories and distinguish source disputes from revision branches.
- Expose sync progress, dependency gaps, peer errors, unresolved branches, frontier and coverage to clients/inspection.

Requirements: C05, C15, C17, C20 · Tests: M04, M05, M12, M15 · Decisions: Q6, Q8

Prerequisites: R09, S02, G02, G04

Workstream parent: S00

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md)

### S04 — Qualify the Mac/Linux disconnect, reconnect, crash and stale-rejoin journey

Planned status: Backlog.

Acceptance criteria:

- Run two actual selected runtimes on synthetic data; write on both while disconnected, correct concurrently, reconnect and verify semantic convergence.
- Exercise delivery disruption, process restart, delete/edit conflict and stale-peer rejoin using the declared transport/durability configuration.
- Record reproducible commands, versions, evidence and unavailable runtime/access gaps. Two-peer success does not qualify third-hop mesh.

Requirements: C03, C04, C05, C06, C13, C18 · Tests: M03, M04, M05, M06, M07, M09, M10, M15, M16, M18

Prerequisites: R09, S03, G06

Workstream parent: S00

Sources: [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### M00 — Required MCP server and real-client interoperability

Planned status: Backlog.

Acceptance criteria:

- Expose the same personal graph/authority contract through the latest verified stable MCP revision and agreed transports.
- Qualify actual Praxis and at least one independent MCP client; protocol mocks cannot substitute for client evidence.

Requirements: C08, C09, C16, C23, C24 · Tests: M02, M12, M18, M19 · ADRs: A16

Prerequisites: R09

Sources: [MCP.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md)

### M01 — Implement the current-standard MCP server and bounded graph tool surface

Planned status: Backlog.

Acceptance criteria:

- Implement selected revision discovery, metadata/capabilities, schemas and supported stdio/Streamable HTTP behavior using verified SDK support.
- Expose bounded capture, query, search/traversal, history/evidence and correction tools with consistent graph/provenance/coverage results. Accept inferred additions automatically within configured grants under Q6; apply the Q7 capture-trigger policy once answered.
- Implement only deliberate tested compatibility for actual client needs; keep consumer, peer and owner-administration authority separate.

Requirements: C07, C08, C15, C16, C24 · Tests: M01, M12, M19 · ADRs: A16 · Decisions: Q6, Q7

Prerequisites: R09, R07, G04, G05

Workstream parent: M00

Sources: [MCP.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md)

### M02 — Qualify MCP authorization, protocol errors, retries and interruption

Planned status: Backlog.

Acceptance criteria:

- Exercise unauthorized/overscoped requests, invalid schemas, unsupported versions, selected auth/transport requirements and bounded outputs.
- Automatically accept in-grant inferred additions without per-item human review, preserving source/evidence, actor/model/derivation, uncertainty, conflicts and correction history. Reject out-of-grant writes and grant-elevation attempts; retries and interruption/cancellation cannot invent completed writes or human verification.
- Compare MCP time/provenance/coverage answers to direct graph API results and verify sensitive content/credentials do not leak into ordinary logs.

Requirements: C08, C09, C10, C16, C23, C24 · Tests: M02, M12, M18, M19 · Decisions: Q6

Prerequisites: R09, M01, G05

Workstream parent: M00

Sources: [MCP.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### M03 — Demonstrate real Praxis and independent-client memory workflows

Planned status: Backlog.

Acceptance criteria:

- Record actual client/SDK/protocol versions and connection configuration without secrets.
- From Praxis and an independent client, discover capabilities, submit an automatically accepted sourced inference within a configured grant without per-item review, query temporal evidence, inspect/correct it and verify denied unauthorized use. Acceptance retains provenance/uncertainty and is not human verification.
- Provide repeatable setup/run instructions and distinguish unavailable-client gaps from passed harness checks.

Requirements: C08, C24 · Tests: M19 · Decisions: Q6

Prerequisites: R09, M02

Workstream parent: M00

Sources: [MCP.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/MCP.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### I00 — Markdown/Logseq import and migration from previous LivingAtlas runs

Planned status: Backlog.

Acceptance criteria:

- Implement the common importer, Markdown/Logseq conversion and adapters for inventoried prior run/store generations.
- Preserve originals, source/time/identity/correction fidelity and per-record accounting; demonstrate repeat-safe synthetic migration and rollback.
- Legacy encrypted-source compatibility and a live-data approval plan remain separate from building new product encryption or performing a live import.

Requirements: C11, C13, C14, C17, C19, C20 · Tests: M10, M11, M13, M14, M16 · ADRs: A03, A10

Prerequisites: R09

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### I01 — Implement import manifests, source boundaries and complete record accounting

Planned status: Backlog.

Acceptance criteria:

- Route authorized imported changes through the common graph contract; preserve source identities/versions and distinguish original times from new-peer import knowledge. Model-derived additions may be accepted automatically within configured grants under Q6, without inventing source fidelity, human verification or permission to read additional sources.
- Bound approved roots/formats/sizes, prevent arbitrary file access and make unchanged, imported, unsupported, quarantined and failed outcomes inspectable.
- Persist ID mappings and import progress for safe retry; do not silently drop records, fabricate fidelity or overwrite originals.

Requirements: C14, C16, C17, C20 · Tests: M02, M11, M13, M15 · Decisions: Q6

Prerequisites: R09, R04, G02, G03, G05

Workstream parent: I00

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md)

### I02 — Implement Markdown and Logseq capture with repeat/change semantics

Planned status: Backlog.

Acceptance criteria:

- Convert the inventoried supported Markdown/Logseq layouts with source references, supported structured facts and bounded unresolved observations.
- Automatically accept inferred additions within configured client/agent grants without per-item human review; retain evidence, actor/model/derivation, uncertainty, conflicts and correction history rather than presenting inference as source-stated or human-verified. Follow the eventual Q7 capture-trigger decision without assuming proactive capture.
- Test unchanged reimport, changed content/source versions, duplicate references, removals, malformed/unsupported inputs and source-level accounting with synthetic files.

Requirements: C01, C14, C19, C20 · Tests: M01, M11, M14, M15 · Decisions: Q6, Q7

Prerequisites: R09, I01, R03

Workstream parent: I00

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### I03 — Implement adapters for inventoried historical LivingAtlas generations

Planned status: Backlog.

Acceptance criteria:

- Provide and label adapter coverage for each available prior run/store/export generation from the inventory; missing/unsupported generations remain explicit gaps.
- Preserve IDs or mappings, original world/recorded-time meanings, evidence, correction branches and unknown fidelity while recording new import receipt knowledge separately.
- Use synthetic compatibility fixtures to verify meaningful temporal/provenance query equivalence, full record accounting and repeat/change safety; counts alone are insufficient.

Requirements: C11, C14, C17, C19, C20 · Tests: M11, M13, M14, M15, M16

Prerequisites: R09, I01, R04

Workstream parent: I00

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### I04 — Qualify encrypted legacy-input compatibility when inventory requires it

Planned status: Backlog.

Conditional compatibility work determined by inventoried legacy sources; it is not a mandate to build a new encryption system.

Acceptance criteria:

- Identify actual legacy encodings and original-key requirements from the source inventory; record not-applicable only with evidence if no encrypted input needs support.
- Qualify relevant decryption adapters using synthetic keys/fixtures, preserving source data and reporting unavailable original access precisely.
- Use original real keys only after separate authorization through approved secret handling; never request/store keys in chat, code or logs. Do not add new product encryption/custody infrastructure.

Requirements: C10, C14, C16 · Tests: M02, M11

Prerequisites: R09, R04, I03

Workstream parent: I00

Sources: [ARCHITECTURE.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ARCHITECTURE.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### I05 — Rehearse migration, verify rollback and prepare the live-import approval plan

Planned status: Backlog.

Acceptance criteria:

- Run isolated synthetic Markdown/Logseq and historical-generation migrations, preserving original archives and complete manifests/ID mappings.
- Verify meaningful temporal/source/lineage equivalence, repeated import, backup and rollback, including unsupported/fidelity/accounting reports.
- Prepare a concrete proposed real source set, destination, approvals/key needs, verification and rollback plan. Do not ingest live personal data or change original stores without separate explicit authorization.

Requirements: C13, C14, C17, C19 · Tests: M10, M11, M13, M14, M16

Prerequisites: R09, I02, I03, I04, G06

Workstream parent: I00

Sources: [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### Q00 — Personal-v1 qualification, packaging and release evidence

Planned status: Backlog.

Acceptance criteria:

- Complete synthetic semantic/failure qualification, inspectability, comparable performance evidence, runtime packaging and the final acceptance matrix.
- Provide reproducible run/MCP/import/sync/restore instructions with limitations; no current implementation/qualification is presumed passed.

Requirements: C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16, C17, C18, C19, C20, C21, C23, C24 · Tests: M01, M02, M03, M04, M05, M06, M07, M09, M10, M11, M12, M13, M14, M15, M16, M18, M19

Prerequisites: R09

Sources: [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### Q01 — Run integrated temporal, durability and failure-injection qualification

Planned status: Backlog.

Acceptance criteria:

- Exercise the Rae/Northstar two-time fixture, correction/retract/invalidate/reinstate, uncertainty, source disputes and fixed-frontier cross-view equivalence. Include an automatically accepted but wrong in-grant inference, denied out-of-grant writes and a later owner correction; acceptance must not be marked human verification. Add Q8 preferred-claim assertions once answered.
- Inject local/sync commit/checkpoint failures, disorder/gaps/duplicate-ID conflicts, restore corruption and stale rejoin; verify acknowledged data, atomic visibility, source lineage and current authority.
- Publish reproducible synthetic fixtures/commands and failures, distinguishing process-kill coverage from physical-power-loss proof.

Requirements: C01, C02, C04, C05, C06, C11, C13, C17, C19, C20, C21, C23 · Tests: M01, M04, M05, M06, M07, M10, M13, M14, M15, M16, M18 · Decisions: Q6, Q8

Prerequisites: R09, G06, S03

Workstream parent: Q00

Sources: [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### Q02 — Verify usable inspection, bounds, coverage and safe operational reporting

Planned status: Backlog.

Acceptance criteria:

- Owner/client can inspect source, actor/model/derivation, actual human review, time/history, conflicts, peer progress and effective personal grants through the v1 interface selected under Q9. Automatic acceptance is visibly distinct from human verification and truth.
- Exercise empty/error/offline and partial-history responses, high-degree/bounded traversal, request/payload limits and redacted logs.
- Q9 remains open between MCP/CLI only and a simple browser UI; no rich/cinematic GUI is required. Use the three Q10 day-one tasks once supplied, with honest coverage and actual storage/processing profile.

Requirements: C08, C10, C15, C16, C21, C23 · Tests: M02, M12, M16, M18, M19 · Decisions: Q6, Q9, Q10

Prerequisites: R09, G04, G05, S03, M01

Workstream parent: Q00

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### Q03 — Benchmark representative personal reads, writes, sync and recovery

Planned status: Backlog.

Acceptance criteria:

- Pin engine/runtime versions, commits, host/OS/filesystem, fixtures, indexes, cache state, batch sizes and durability settings; verify correctness before ranking performance.
- Measure declared current/historical retrieval, traversal, acknowledged writes, cold open/index rebuild, memory/storage, transfer/convergence and recovery work using repeated independent runs.
- Keep supplied selective-read results and independent experiments separate; unsupported paths/failures and no physical-durability/enterprise-scale proof are explicit.

Requirements: C02, C07, C10, C15, C18 · Tests: M03, M06, M12, M16

Prerequisites: R09, G04, S04, Q01

Workstream parent: Q00

Sources: [RESEARCH.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RESEARCH.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### Q04 — Package Mac/Linux peers and publish reproducible operating instructions

Planned status: Backlog.

Acceptance criteria:

- Provide reproducible installation/run/configuration instructions for the agreed runtimes, with dependencies and any approval requirements explicit.
- Document MCP connections, the v1 owner interface selected under Q9, personal peer admission, offline/reconnect flows, import dry-run/rehearsal, backup/restore, troubleshooting and rollback.
- Keep examples synthetic, credentials external and real-data/deployment approvals separate; do not provision external infrastructure automatically.

Requirements: C08, C10, C11, C13, C14, C18, C24 · Tests: M03, M10, M11, M12, M19 · Decisions: Q9

Prerequisites: R09, S04, M03, I05

Workstream parent: Q00

Sources: [DECISIONS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md) · [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md)

### Q05 — Close the personal-v1 acceptance matrix with evidence and limitations

Planned status: Backlog.

Acceptance criteria:

- Link each in-scope C/M requirement to actual passing evidence or a named unresolved gap; deferred M08/M17/P01–P06 remain deferred, not passed.
- Verify real Praxis/independent-client workflows, actual Mac/Linux offline sync, importer compatibility and rollback, scoped automatic inferred-addition acceptance without per-item review, personal authority and representative performance. Prove the three Q10 day-one tasks and the resolved Q7–Q9 behavior with evidence.
- Reconcile final PRD/ADRs/run instructions and report what was built, passed, remains, and how to use it. Do not declare release acceptance with missing required evidence or infer permission for a live cutover.

Requirements: C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16, C17, C18, C19, C20, C21, C23, C24 · Tests: M01, M02, M03, M04, M05, M06, M07, M09, M10, M11, M12, M13, M14, M15, M16, M18, M19 · Decisions: Q6, Q7, Q8, Q9, Q10

Prerequisites: R09, Q01, Q02, Q03, Q04, M03, I05, S04

Workstream parent: Q00

Sources: [VALIDATION.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/VALIDATION.md) · [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md)

## RefactoredMemory — Later roadmap

Future options retained for visibility. These issues do not block personal v1 and are not authorized for implementation by the current scope or its eventual proceed gate. No invented dates or estimates.

### L01 — Later: multi-tenant and corporate ownership lifecycle

Planned status: Backlog.

Acceptance criteria:

- Keep single-owner v1 unchanged; revisit multiple personal/corporate domains only under separately agreed later scope.
- Preserve confirmed future ownership principle; design membership, offboarding, transfers, mixed-source policy and isolation with explicit choices.
- Qualify C22/M17 and relevant E02/E09 only when this phase is authorized; this issue never blocks v1.

Requirements: C22 · Tests: M17 · ADRs: A11, A12, A14 · Later evolution: E02, E09 · Later qualification: M17

Sources: [DECISIONS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md) · [ADRS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md)

### L02 — Later: product encryption, custody, recovery and protected processing

Planned status: Backlog.

Acceptance criteria:

- Design content encryption, key custody/recovery, metadata/executor trust and applicable profiles under separate later authorization.
- Qualify P01–P06 and honest revocation/erasure/backup limits before making protected/operator-blind claims.
- Do not confuse required v1 TLS/basic authority or legacy decryption import compatibility with completion of this phase.

ADRs: A05, A11, A13, A14 · Later evolution: E07, E08, E10, E11 · Later qualification: P01, P02, P03, P04, P05, P06

Sources: [ADRS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md) · [DECISIONS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md)

### L03 — Later: additional personal peers and transitive relay mesh

Planned status: Backlog.

Acceptance criteria:

- Agree need/topology and admission/subscription boundaries beyond the required two peers.
- Qualify third-hop store-forward exchange, echo prevention, origin integrity and convergence without simultaneous connectivity under M08.
- Two-peer v1 success is not treated as proof; this issue does not gate personal v1.

Tests: M08 · ADRs: A09, A11 · Later evolution: E03 · Later qualification: M08

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [ADRS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md)

### L04 — Later: evidence-driven advanced retrieval and memory consolidation

Planned status: Backlog.

Acceptance criteria:

- Evaluate optional vectors/associative retrieval, linked summaries, consolidation, maintained decisions and procedural memory only against useful measured tasks.
- Preserve graph/source authority, derivation/review, scoped jobs, budgets, retry semantics and original evidence; use R01–R06 as appropriate.
- Adopt advanced modules only with measured quality/cost/operating benefit. Accepting authorized client-generated inferences is already v1 under Q6; separate extraction engines and consolidation remain later unless explicitly added. Proactive capture versus explicit requests remains Q7, and Q6 alone does not authorize continuous monitoring.

ADRs: A07, A08, A15 · Later evolution: E06, E12 · Later qualification: R01, R02, R03, R04, R05, R06 · Decisions: Q6, Q7

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md) · [RESEARCH.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/RESEARCH.md)

### L05 — Later: shared SaaS, hybrid deployment and enterprise scale

Planned status: Backlog.

Acceptance criteria:

- Use observed workloads to justify partitioning, independently scaled workers, selective replication and broader operational profiles.
- Preserve temporal/provenance/coverage contracts and quantify cross-partition limits and actual security/performance assumptions.
- No enterprise-scale implementation or benchmarks gate personal v1; create a separate release scope and approval when needed.

ADRs: A11 · Later evolution: E01, E02, E04, E05, E11

Sources: [ADRS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/ADRS.md) · [DECISIONS.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/DECISIONS.md)

### L06 — Later: richer personal inspection and graphical exploration

Planned status: Backlog.

Acceptance criteria:

- Identify advanced owner workflows beyond the v1 interface selected under Q9. Whether v1 includes a simple browser UI remains an open Q9 choice; this later item must not decide it.
- Expose evidence/history/conflicts/authority accessibly without implying a visual graph is needed for v1 acceptance.
- Keep advanced visual/cinematic or automatic identity features separate from current source-linked inspection requirements.

Requirements: C08 · ADRs: A15 · Later evolution: E12 · Decisions: Q9

Sources: [PRD.md](https://github.com/ProvisioInsights/RefactoredMemory/blob/main/docs/PRD.md)

## Requirement coverage

| Requirement | Planned items |
| --- | --- |
| C01 | R06, G00, G01, I02, Q00, Q01, Q05 |
| C02 | R05, R06, G00, G03, Q00, Q01, Q03, Q05 |
| C03 | S00, S02, S04, Q00, Q05 |
| C04 | R05, R06, G03, S00, S01, S02, S04, Q00, Q01, Q05 |
| C05 | R06, G00, G02, S00, S03, S04, Q00, Q01, Q05 |
| C06 | R06, G00, G06, S00, S04, Q00, Q01, Q05 |
| C07 | R05, R06, G00, G04, M01, Q00, Q03, Q05 |
| C08 | R07, G00, G05, M00, M01, M02, M03, Q00, Q02, Q04, Q05, L06 |
| C09 | R06, R07, G00, G05, S00, S01, M00, M02, Q00, Q05 |
| C10 | G00, G05, S01, M02, I04, Q00, Q02, Q03, Q04, Q05 |
| C11 | R05, R06, G00, G03, G06, I00, I03, Q00, Q01, Q04, Q05 |
| C12 | R06, G05, S00, S01, Q00, Q05 |
| C13 | R06, G00, G06, S04, I00, I05, Q00, Q01, Q04, Q05 |
| C14 | R04, I00, I01, I02, I03, I04, I05, Q00, Q04, Q05 |
| C15 | R06, G04, S00, S02, S03, M01, Q00, Q02, Q03, Q05 |
| C16 | R06, G00, G04, G05, M00, M01, M02, I01, I04, Q00, Q02, Q05 |
| C17 | R04, R06, G00, G02, S00, S03, I00, I01, I03, I05, Q00, Q01, Q05 |
| C18 | R05, S00, S04, Q00, Q03, Q04, Q05 |
| C19 | R04, R06, G00, G02, I00, I02, I03, I05, Q00, Q01, Q05 |
| C20 | R03, R06, G00, G01, G02, S03, I00, I01, I02, I03, Q00, Q01, Q05 |
| C21 | R06, G00, G04, G06, Q00, Q01, Q02, Q05 |
| C22 | L01 |
| C23 | R03, R06, G00, G05, G06, M00, M02, Q00, Q01, Q02, Q05 |
| C24 | R07, M00, M01, M02, M03, Q00, Q04, Q05 |

## Acceptance case coverage

| Acceptance case | Planned items |
| --- | --- |
| M01 | G00, G01, G03, G04, M01, I02, Q00, Q01, Q05 |
| M02 | G00, G05, S01, M00, M02, I01, I04, Q00, Q02, Q05 |
| M03 | S00, S02, S04, Q00, Q03, Q04, Q05 |
| M04 | G02, S00, S03, S04, Q00, Q01, Q05 |
| M05 | S00, S02, S03, S04, Q00, Q01, Q05 |
| M06 | G00, G03, S00, S02, S04, Q00, Q01, Q03, Q05 |
| M07 | G00, G06, S00, S04, Q00, Q01, Q05 |
| M08 | L03 |
| M09 | G05, S00, S01, S04, Q00, Q05 |
| M10 | G00, G03, G06, S04, I00, I05, Q00, Q01, Q04, Q05 |
| M11 | R04, I00, I01, I02, I03, I04, I05, Q00, Q04, Q05 |
| M12 | G00, G04, G05, S03, M00, M01, M02, Q00, Q02, Q03, Q04, Q05 |
| M13 | G00, G01, G02, G04, I00, I01, I03, I05, Q00, Q01, Q05 |
| M14 | G00, G02, G04, G06, I00, I02, I03, I05, Q00, Q01, Q05 |
| M15 | G00, G01, G02, S00, S03, S04, I01, I02, I03, Q00, Q01, Q05 |
| M16 | G00, G02, G03, G04, G06, S00, S04, I00, I03, I05, Q00, Q01, Q02, Q03, Q05 |
| M17 | L01 |
| M18 | R03, G00, G05, G06, S04, M00, M02, Q00, Q01, Q02, Q05 |
| M19 | R07, M00, M01, M02, M03, Q00, Q02, Q04, Q05 |

## Later evolution coverage

| Later evolution | Planned items |
| --- | --- |
| E01 | L05 |
| E02 | L01, L05 |
| E03 | L03 |
| E04 | L05 |
| E05 | L05 |
| E06 | L04 |
| E07 | L02 |
| E08 | L02 |
| E09 | L01 |
| E10 | L02 |
| E11 | L02, L05 |
| E12 | L04, L06 |
