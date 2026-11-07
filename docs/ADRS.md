# RefactoredMemory Architecture Decisions

**Status:** Personal-v1 scope approved; implementation available, release qualification incomplete. **Revised:** 7 November 2026. The owner has confirmed that **RefactoredMemory v1 is his personal knowledge store**, with two offline-writable personal peers, synchronization, mandatory MCP integration, Markdown/Logseq import, migration of data from previous LivingAtlas runs, and automatic acceptance of inferred additions within configured client/agent grants. Per-item human review is not required for those authorized additions; acceptance does not mean human-verified truth. Multi-tenancy, corporate ownership, product content encryption and custody/recovery machinery are later phases. Temporal semantics, evidence, attribution, uncertainty and correction lineage remain core; Q7–Q10 confirm proactive capture within grants, explicit-owner correction preference with conflicts/history retained, MCP+CLI first without a v1 browser UI, and all three day-one tasks. The owner explicitly said **“Proceed”**; the authorized implementation now exists on `codex/personal-memory-v1`. A17 records the engineering stack; the evidence summary below distinguishes passing checks from remaining release qualification.

**Confirmed MCP target and repository boundary:** The owner uses **Praxis2**. RefactoredMemory must provide standards-conformant MCP 2026-07-28 stdio and Streamable HTTP connections, with the latest published stable revision rechecked for future upgrades. No changes to either the Praxis or Praxis2 repository—including client code, provider endpoints or approval paths—are authorized or required by this task. Installed Praxis2 end-to-end behavior remains unverified until a compatible client connection is available; any hardcoded-provider limitation is an external interoperability evidence gap, not work to change those repositories.

## Current implementation and evidence

The implementation is available on [codex/personal-memory-v1](https://github.com/ProvisioInsights/RefactoredMemory/tree/codex/personal-memory-v1/docs). It includes the temporal graph and CLI, two local offline-writable peers with direct synchronization, documented Markdown/Logseq and legacy-format import adapters, and verified synthetic restart/restore recovery. Linux synthetic checks have passed for the exercised scope, including the three day-one workflows. The already installed independent Python MCP SDK 1.29.0 passed against the real service over the separate 2025-11-25 stdio compatibility path. Modern 2026-07-28 protocol/schema checks are recorded separately; that legacy-client result does not prove a modern-client or actual Praxis2 integration. The official MCP specification permits custom authorization strategies. The current HTTP implementation uses owner-preconfigured opaque bearer grants; it does not implement the standard OAuth profile, protected-resource metadata discovery or OAuth-only host onboarding. OAuth is not an added v1 requirement for this selected profile; connecting clients must support the configured bearer strategy.

See [acceptance results](ACCEPTANCE-RESULTS.md), [MCP conformance and client matrix](MCP-CONFORMANCE.md), [supported import formats and fidelity limits](IMPORT-FORMATS.md), [sync and recovery protocol](SYNC-PROTOCOL.md), and [run instructions](RUNBOOK.md). Full v1 release acceptance remains incomplete: the owner's actual Mac, the installed Praxis2 application, and complete migration of original LivingAtlas archives remain unverified. All recorded data tests use synthetic fixtures; this evidence update does not authorize live-data ingestion, original-key use or external deployment.

The temporal graph stays central and the initial engineering stack is now selected under A17, with versioned contracts preserving a future replacement path. The [PRD](PRD.md) distinguishes personal-v1 requirements and acceptance from later enterprise/protection qualification. The owner has selected **two personal peers with offline writes and synchronization** for v1; the selected pair is the owner's Mac plus a Linux VM/container under the owner's control. Earlier C01–C23/M01–M18 references are an inventory, not a blanket gate: M17's multi-organization cases are later; M18 retains personal current-authority/history/restore checks. C24/M19 add mandatory MCP; C25/M20 add the three confirmed day-one tasks. E01–E12, R01–R06 and P01–P06 remain staged evolution, memory and protection work.

Versioned repository documentation is authoritative; the companion historical planning Page is reconciled with this file and remains accessible through authorized access. Use the existing repository and selected cloud environment. Atlas/LivingAtlas names in historical evidence identify the predecessor. The confirmed future principle remains that an organization retains its own data after departure and a person retains personal data; it does not make corporate ownership, recovery, offboarding, mixed-domain policy or encryption a v1 requirement. The [research and platform overview](RESEARCH.md) distinguishes current code, measured results and proposals. The owner has explicitly said **“Proceed.”** The scope reconciliation is complete and implementation has begun; do not request the same approval again. Assess current evidence and remaining source/client access and engineering qualification in the linked reports. Real-data ingestion, original-key use and external deployment are not authorized by this implementation approval, and Linear remains paused.

# Decision register

| Record | Decision | Release scope and status |
| --- | --- | --- |
| A01 | Personal temporal knowledge store and open implementation | Implemented personal core with passing Linux synthetic checks; full release qualification incomplete |
| A02 | Bitemporal assertions, evidence and per-peer knowledge lineage | V1 contract implemented; temporal/history evidence and limits recorded |
| A03 | MCP capture, Markdown/Logseq import and prior LivingAtlas migration | Required v1; scoped automatic inferred additions accepted; artifact inventory remains research |
| A04 | Compare eligible storage/projections under complete semantics | Python/SQLite selected under A17; full-contract qualification pending |
| A05 | Basic personal access controls now; content encryption later | Local grants/current-authority checks implemented; later content protection deferred |
| A06 | One personal owner, scoped clients and personal peer trust | V1; corporate domains deferred |
| A07 | Maintained decisions as a later graph module | Deferred; not a v1 gate |
| A08 | Research-guided retrieval, context and consolidation | Basic retrieval v1; advanced modules staged |
| A09 | Two personal offline-writable peers with causal sync | Direct HMAC-admitted journal sync implemented and tested with local Linux peers; actual Mac/Linux pair unverified |
| A10 | Personal graph operations, MCP and two-peer delivery | V1; third-peer/relay mesh later |
| A11 | Partitionable multi-tenant deployments and privacy profiles | Later-phase architecture; not a v1 prerequisite |
| A12 | Personal/organization ownership and employer lifecycle | Future principle confirmed; implementation deferred |
| A13 | Protected processing, key custody and recovery | Deferred protection architecture |
| A14 | Cross-domain information flow and advanced revocation/erasure | Later qualification; personal provenance/current authority retained in v1 |
| A15 | Inspectable knowledge and personal memory controls | V1 proactive capture, automatic acceptance, explicit-owner correction preference and MCP+CLI confirmed; advanced lifecycle later |
| A16 | Current-standard MCP integration | Modern protocol/schema checks and independent SDK legacy-stdio test pass; actual Praxis2 unverified |
| A17 | Python standard-library, SQLite WAL/FULL and explicit direct peer sync | Implemented; passing synthetic correctness/recovery and scoped MCP evidence recorded; full release qualification incomplete |

V1 is one person's useful knowledge store. It may contain knowledge about organizations and other people without implementing corporate ownership domains or multiple tenants. Retain stable IDs, provenance, clear local authority and versioned exports where useful; do not build enterprise abstractions solely to reserve a future feature. Later protection/deployment profiles need their own evidence and are not prerequisites for personal-v1 completion.

# A01 Temporal graph core and open implementation

**Status:** Personal-v1 core implemented with passing Linux synthetic evidence; full release qualification incomplete. **V1 scope:** Temporal graph, durable personal operation, two offline-writable peers, scoped clients, retrieval and MCP. **Depends on:** A02, A04, the personal portions of A05/A06, A09, A16 and A17. A11–A14 are later evolution, not v1 dependencies.

## Context and decision

RefactoredMemory v1 is the owner's personal temporal knowledge store. The owner is not bound to previous technology. Simplification reduces operating burden while preserving sourced entities, assertions, relationships and temporal history; it does not reduce the graph to generic records or freeze a database/language.

The initial deployment packages a useful personal graph, persistence, query projections, scoped API and mandatory MCP server on **two personally controlled peers**, each able to write offline and synchronize later. The owner has selected that topology; the selected pair is the owner's Mac plus a Linux VM/container under the owner's control. A17 selects a small Python 3.12+ standard-library process and SQLite WAL/FULL store per peer, with immutable atomic operations and explicit direct sync. Operational simplicity and a testable correctness path motivate the choice; it is not a claimed benchmark victory.

Entities provide identity; immutable assertions and relationships preserve sources, world/knowledge time and correction lineage. Working context, associative retrieval and consolidation use those semantics through versioned contracts. Configured clients/agents may submit inferred additions for automatic acceptance in v1. Q7 confirms proactive useful-knowledge capture within configured client/agent grants, without requiring an embedded model runtime or granting new source access.

Praxis2 and other clients own external execution. RefactoredMemory owns graph meaning, provenance and declared knowledge state; retrieving memory does not grant a client new execution or administrative authority.

## Alternatives and consequences

Reusing existing code can reduce cost but is not an architectural requirement. A clean implementation or native graph engine is acceptable when evidence justifies it. One primary store was considered as the simpler alternative; the owner selected two personally controlled offline-writable peers, so a single-writer-only implementation does not satisfy v1.

A broad service fleet increases operating burden before it creates personal value. Versioned contracts and export preserve deliberate future migrations. A11's multi-tenant partitioning, corporate domains and scalable worker fleet are later options and must not expand v1.

## Verification and revisit

Verify the PRD's applicable personal-v1 acceptance set, including temporal semantics, provenance, persistence/recovery, personal authority, real MCP workflows, Markdown/Logseq import, prior LivingAtlas migration and two-peer offline synchronization/convergence. M17 and corporate/protection portions of M18 are deferred; third-peer/relay mesh is later. A selective-read benchmark informs one workload, not future enterprise scale/encryption. M11 verifies import/migration against synthetic fixtures for the inventoried generations; actual personal-data ingestion and cutover require separate authorization. C25/M20 qualify project decisions/why, person relationships/evidence and changes since last month through MCP+CLI, including explicit-owner correction preference with alternatives/history retained.

# A02 Bitemporal graph and branch aware knowledge history

**Status:** Proposed temporal implementation for the confirmed two-personal-peer v1. **Scope:** Independent world/knowledge time, evidence, corrections, disputes, retained history and per-replica causal knowledge under A09. Detailed fields and protocol remain proposed.

## Context and decision

The [canonical knowledge model](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/docs/architecture/adr-0004-canonical-knowledge-records.md) separates stable entities from sourced facts, relationships and evidence. The [lineage decision](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/docs/architecture/adr-0005-assertion-lineage-and-evidence.md) retains semantic history independently of mutation journals. Preserve those principles in the personal store and its two-peer synchronization contract.

Each immutable assertion has an opaque identity, subject, registered predicate, typed value or target, namespace, evidence/provenance, world-time expression and semantic action. A bounded unresolved observation can lack structured meaning without inventing it. Entity identity is independent of labels and changing facts. Evidence links retain support, contradiction or context; copied upstream sources and replicas do not create independent corroboration. Unknown source independence stays unknown.

**World time** describes when a claim holds. Retain half-open state intervals, mixed precision, approximation and explicit unknown values. Under the existing contract an absent end means ongoing; an explicitly unknown end is different. Untimed or unknown-date material is not a certain match for a date filter. Recurrence solving and a universal ontology are deferred, but these basic time rules are core.

**Knowledge time** describes acquisition of a claim or correction in a particular view. For the selected two-personal-peer v1, preserve origin commit metadata, receipt metadata and per-replica causal-application positions separately. A query selects world time independently of a named replica knowledge position or causally closed frontier. A timestamp selector names the replica whose retained local history resolves it. Unsynchronized clocks do not provide a global knowledge order, and late receipt must not backdate what a peer knew.

Semantic actions append assertions with predecessor links: correct repairs an erroneous recording; retract withdraws a mistaken belief without inventing a world ending; invalidate preserves the interval when a relationship held and records its end; reinstate affirms previously retracted knowledge. Retraction is not an active edge after the relevant knowledge action, while invalidation can remain a historical edge for its valid interval. The [inspected assertion actions](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/packages/atlas-core/src/assertion.ts) are the compatibility reference.

Concurrent descendants of one lineage remain branches. Derive supersession and active heads from admitted actions at the selected frontier; do not replicate one mutable superseded-at value as a global winner. An authorized, attributed resolution references the heads considered, retains reasons/evidence and can leave uncertainty. Independently sourced competing assertions coexist separately from that technical branch conflict. Automatic acceptance of an inferred addition is not a human review event or proof of truth. Q8 confirms preference for an explicit authorized owner correction in the applicable temporal/knowledge view while preserving alternatives, evidence, uncertainty and lineage. Source text/model metadata cannot fabricate owner-correction authority; equally applicable conflicting owner corrections remain visible rather than silently resolved.

Keep logical assertion/operation identity separate from payload encoding and transport digests. Re-encoding or forwarding an assertion is neither new corroboration nor a new learning event at its origin. Receipt at another peer is a new local knowledge event there.

Knowledge history is not authorization history. Current personal-owner/client authority applies to old valid-at/known-at answers. Personal deletion and retention must be explicit rather than inventing a world event or silently returning current state for removed history. A14's cross-domain and cryptographic lifecycle is later qualification, not a v1 dependency.

## Alternatives and consequences

Overwriting facts or whole entities loses prior beliefs. Wall-clock last-write-wins discards causal branches. A global total order would add coordination and impair offline contribution. A branch-aware graph instead exposes the limits of each knowledge view.

The existing single-writer recorded-at/superseded-at API cannot silently become a multi-peer global clock. Import its original timestamps and fidelity unchanged, then introduce a versioned mesh contract. Exact public field names and the local knowledge-position implementation remain proposed engineering details.

## Verification and revisit

M13–M16's personal cases prove independent world/knowledge selection, semantic actions, delayed peer learning, competing source claims and preserved answers after sync/rebuild/restore. M04/M05 cover concurrent offline lineage, clock skew and dependencies. M11 qualifies required Markdown/Logseq import and migration from inventoried previous LivingAtlas generations. Actual personal-data ingestion/cutover remains separately authorized. No graph view may affirm an unknown semantic action by default.

# A03 MCP capture, Markdown/Logseq import and LivingAtlas migration

**Status:** MCP capture, Markdown/Logseq import and prior LivingAtlas migration are confirmed v1 requirements. Q6 confirms automatic acceptance of inferred additions within configured client/agent grants, without per-item review. **Discovery:** Inventory prior artifacts/store generations and source boundaries read-only. **Confirmed:** Q7 proactive capture within grants, Q8 preference for explicit owner corrections with alternatives/history retained, Q9 MCP+CLI first without a browser UI, and Q10 all three day-one tasks. Explicit owner instructions, source-stated assertions, automatically accepted inferences and any later human verification remain distinct.

## Context and decision

The personal graph accepts owner and authorized MCP-client submissions, imports Markdown/Logseq notes and migrates data from previous LivingAtlas runs. Research inventories relevant store/export/archive generations before choosing adapters; it must not assume all prior runs use the newest schema. Preserve source references, stable IDs or mappings, evidence, provenance, original world/knowledge-time meanings, correction lineage and fidelity. Configured client/agent grants allow inferred additions to be accepted automatically without per-item human review. Record the authenticated actor, model/version when applicable, derivation and uncertainty; missing provenance remains explicit. Acceptance does not certify truth or authorize new source access. Q7 confirms proactive useful-knowledge capture within configured grants; a separate extraction/model service is not implied.

Start with typed entity creation, bounded sourced assertions/relationships and evidence references. A submission records its authenticated actor, origin and source; it cannot supply authoritative server identity or global commit order. Unknown meaning remains an unresolved observation. Storing a claim does not establish its truth.

Connectors, parsers and models later submit through the same validated graph contract. They have no privileged storage access. Source text cannot execute code, enroll peers or change grants. Summarization and replication cannot turn a copied source into independent evidence. Person/entity matching is separate from security enrollment.

## Alternatives and consequences

Building every connector first delays the graph and expands source permissions and failure surfaces. Generic source-free record writes would postpone the graph semantics and make later correction expensive.

Markdown/Logseq import is repeat-safe for unchanged notes and files. Modified sources produce traceable versions and explicit graph changes/corrections where justified, without overwriting earlier evidence or duplicating corroboration. Keep unsupported or ambiguous source records visibly unresolved, skipped or quarantined with reasons. A sourced inferred addition may be accepted automatically within the configured grant, preserving derivation and uncertainty; it must not be mislabelled as source-stated or human-verified. Source text cannot authorize broader operations or access.

Legacy LivingAtlas migration is required v1. First inventory accessible prior-run artifacts and their storage/encoding generations read-only, preserving original archives. Account for every input record with imported, preserved-opaque, quarantined or explicitly unsupported status and reconciled counts. Retain stable IDs or inspectable ID mappings, source provenance, original temporal semantics, correction/history lineage and fidelity labels. Compare declared temporal/query equivalence, verify repeat-import safety and test backup/rollback; absence of a source artifact is an explicit discovery/access gap, not a reason to silently omit its generation.

Existing encrypted legacy inputs may require approved original keys and a compatible decryption adapter. This is migration compatibility, not adoption of product content encryption in v1. Do not expose plaintext or secrets in the public repository, logs or fixtures. Locating and analyzing formats does not authorize actual personal-data ingestion; development and migration tests use synthetic fixtures until separate approval.

## Verification and revisit

M01/M02 cover typed source-preserving submissions, invalid inputs and automatic acceptance of inferred additions within configured grants without per-item review; deny additions outside those grants. Preserve actor/model/derivation/evidence/uncertainty and distinguish acceptance from human verification. M11 qualifies Markdown/Logseq and inventoried LivingAtlas generations using synthetic fixtures for IDs/mappings, provenance, temporal/lineage fidelity, count reconciliation, unknown-fidelity labels, unchanged reimport idempotency, modified-file/correction handling, visible unsupported records and backup/rollback. Qualify any encrypted legacy adapter only with synthetic equivalents and approved key handling. M15 verifies evidence independence across reimports and peers. C25/M20 and the applicable M01/M12/M15 cases qualify the confirmed Q7–Q10 proactive capture, owner-correction preference, MCP+CLI and day-one outcomes; unrelated advanced connectors remain later.

# A04 Graph storage and projection evaluation

**Status:** Initial Python/SQLite stack selected under A17; broader correctness/performance qualification pending. **Scope:** C02, C04, C07, C13, C17, C19, C21; E01, E04, E05. **Related records:** A02, A09, A17; A11 remains later.

## Context and decision

Compare storage implementations under RefactoredMemory's logical graph and agreed personal-v1 contract. Existing Atlas is a baseline; indexed relational, native property-graph, Datalog, temporal-specialized and replication-oriented approaches can qualify. Two-peer offline sync and recovery fitness matter for v1; enterprise scale and protection profiles are evaluated later. The earlier open selection is now resolved for the initial implementation: Python standard library and SQLite WAL/FULL under A17. The rationale is operational simplicity and a testable correctness path, not the selective-read result; alternate engines remain revisit options.

For the selected initial SQLite implementation, entities/assertions/lineage/evidence can map to tables and indexes. A native graph or other store may use different physical structures. Canonical export, semantic actions, knowledge scope, coverage and consumer contracts remain explicit, and optional native capabilities must be advertised rather than changing normal answers silently.

Persist each graph group, its local knowledge/accounting metadata and replication eligibility durably before acknowledgement. Use an immutable operation journal and a SQLite transaction to make each admitted semantic group and its knowledge/application/replication accounting atomically visible; WAL with synchronous=FULL is the selected durability setting, still subject to failure/recovery tests. Prevent received operations with missing predecessors/entities/evidence from becoming graph-visible.

A later protected profile must place plaintext query/index work within its approved boundary. Encrypting files under a provider-readable server is not operator blindness, and the existing read benchmark does not qualify protected processing. This future qualification must not become a storage-selection gate for the agreed personal v1.

Adjacency, text/vector retrieval and current-head indexes are derived. Record their processed frontier and version. Retain promised semantic history independently of index rebuilds, sync pruning and operational audit retention.

## Evidence and alternatives

On the reported Apple M5 Max benchmark host, actual Atlas e36ebe8 and an indexed Node SQLite candidate ran three times at 11k and 110k assertions, without installs. At 110k, current read median/p95 was 0.6814/0.7859 ms for Atlas versus 0.0377/0.0605 ms for SQLite; historical was 0.6845/0.7977 versus 0.0320/0.0521 ms. All 1,200 full-assertion comparisons matched, including corrections, and all six reported reopen/count and retry checks passed.

The SQLite candidate omits coverage metadata and the full contract. No equivalent write, concurrency, replication, failure recovery or scale-out test was supplied. The separate SQLite FULL/WAL experiment uses a different environment/fixture, and overlay timing does not prove physical durability. The evaluation (historical planning Page; authorized access required) retains provenance, artifacts and separate limitations; neither run selects a backend.

[LadybugDB](https://github.com/LadybugDB/ladybug) documents an embedded property-graph approach, while [Cozo](https://docs.cozodb.org/en/latest/timetravel.html) documents Datalog/Validity queries. These are eligible capabilities, not tested Atlas behavior. [AeonG](https://ruc-deke.github.io/dbsys/publication/2024-aeong/) contributes current/history and anchor/delta storage ideas worth evaluating as history grows; its published results are not platform guarantees.

## Consequences and verification

A native engine may reduce traversal work; a relational engine may simplify local transactions; specialized history layout may reduce reconstruction/storage cost. Measure complete query cost, writes, memory, recovery and operations to qualify the selected A17 stack and determine whether a future change is justified. A shared service and edge peer may use different engines under versioned contracts.

M01/M13/M14 exercise temporal meaning; M05/M06/M10 exercise applicable network/dependency, local failure and restore boundaries; M16 compares history after rebuilding projections. Include complete coverage/access/horizon work in paired personal-store measurements. Do not duplicate existing benchmarks without a specific evidence gap.

Adoption requires semantic fit, measured usefulness, acceptable maintenance/operating cost and a versioned migration plan. Consumers do not depend on database files or physical tables.

# A05 Staged protection and operator boundaries

**Status:** Personal-v1 security boundary confirmed; mechanisms proposed. **V1:** Local access controls, owner/scoped-client authorization, safe credentials and transport protection where applicable. **Later:** Product content encryption, operator-blind storage/compute, enterprise custody, key recovery and cryptographic erasure. A12–A14 are future profiles, not v1 dependencies.

## Context and decision

The owner has explicitly deferred product content encryption to later phases. V1 is a personal store, with basic authentication/authorization and truthful statements about where plaintext exists. Do not turn deferral into a requirement for corporate-domain models, KMS, protected executors or recovery infrastructure. Do not claim encrypted-at-rest or operator-blind protection from a plaintext implementation.

Use synthetic-only data for development and tests. The initial personal profile can keep plaintext on owner-approved storage under its documented local access controls; actual personal-data use requires separate approval and an explicit acknowledgement of its storage/processing boundary. Encryption is not a blanket prerequisite for personal v1. Plaintext files, indexes, exports and backups are readable by their holders/operators. Historical [LivingAtlas storage paths](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/packages/atlas-mcp/src/store.ts#L535) remain evidence, not the selected implementation.

Retain basic local access controls, scoped client grants, safe credentials, input limits and appropriate listener restrictions. Use HTTPS/TLS and the applicable MCP authorization model for remote network access; local stdio and loopback have distinct boundaries. Authenticate both personal peers and admitted operations. Transport encryption remains applicable even though product content encryption is deferred.

Keep canonical identities, semantic provenance and versioned export stable enough for deliberate migrations. Supporting existing encrypted LivingAtlas inputs with approved original keys/decryption compatibility is part of the required migration where those artifacts exist; it does not require encrypting RefactoredMemory v1. Do not build a new key hierarchy or mock encryption subsystem solely to reserve a later feature. A future product-encryption project separately qualifies current data, journals/indexes, replicas, exports and backups.

A13 separates storage, custody, recovery and execution. Ordinary provider-controlled code able to invoke decryption is part of the plaintext trust boundary, even with customer-managed keys. The client/update, metadata, index/model/log/output and recovery paths need profile-specific qualification before an operator-blind claim.

## Alternatives and consequences

Requiring enterprise custody or content encryption before a personal store delays the confirmed v1 goal. Deferring basic access control or network transport protection is a separate risk and is not implied. A later encryption rollout cannot erase plaintext copies that already existed.

Content encryption and the stronger protection profiles in A13 are later work, not personal-v1 completion gates. This documentation update does not authorize ingestion of real data, new external processing or deployment; those actions retain their explicit approval boundaries.

## Verification and revisit

V1 verifies personal client authorization, listener/transport behavior, peer origins, input boundaries, log hygiene, backup/restore and offline rejoin. Do not require mock opaque encoding or key-recovery qualification for personal-v1 completion. A later content-encryption profile must inventory prior plaintext and qualify its actual guarantees.

# A06 Personal owner, scoped clients and peer trust

**Status:** Proposed personal authority contract. **V1:** One owner, configured clients/agents, two personally controlled peers and clear local access boundaries. **Later:** Multiple tenants, corporate owner domains, federation and stronger custody. **Related:** A05, A09, A16; A12–A14 are future profiles.

## Context and decision

API authorization and the ability to read a full local replica are different trust boundaries. A node holding plaintext files cannot be made blind through client-side result filtering.

V1 has one personal owner. Distinguish that owner from the actor/client, source and graph subject where it helps attribution and authorization. Facts about companies, employers or other people remain ordinary personal knowledge; they do not create corporate tenants, ownership domains or memberships. Do not require one personal plus two organization fixtures or implement multi-employer policy for v1.

Peer credentials and graph entities are separate. Ordinary records cannot create devices, change membership or broaden permissions. Owner-controlled administration changes admission. Consumer credentials have less authority than peer/admin credentials.

Current personal grants govern present and historical queries and derived outputs. Updated policy refuses revoked credentials; restoring an old snapshot must not silently re-enable an expired grant. The two offline personal peers need explicit stale-policy, rejoin and retained-plaintext limits; already disclosed plaintext cannot be recalled. Enterprise membership propagation, item-level cryptographic grants and multi-domain recovery remain later work.

V1 qualifies direct exchange between the two admitted personal peers. If a future third peer or relay forwards operations, authenticate origin as well as the connection and qualify that transitive path separately. Direct two-peer success is synchronization, not proof of a transitive mesh.

## Alternatives and consequences

A single fully trusted namespace keeps the first deployment small. Fine-grained selective replicas add policy and deletion complexity and can be added deliberately. A network location or a matching person name alone cannot establish admission.

This scope supports one owner's personal store with two offline-writable peers. Arbitrary untrusted federation, transitive relay/mesh and corporate tenancy are deferred.

## Verification and revisit

V1 tests owner/client grants, denied operations, historical-query authority, input/log boundaries and the actual MCP path, plus personal peer admission, replay, revocation, stale-policy and cloned-identity behavior. Multi-organization isolation and less-trusted federation require later profiles and tests.

# A07 Maintained decisions as a later graph module

**Status:** Proposed deferred. **Core acceptance:** Not a gate.

The future behavior remains retaining goals, alternatives, reasons, constraints and expected outcomes, then identifying when a changed condition affects a decision. A synthetic timing/cost scenario remains a suitable later acceptance case.

The core can represent a decision as entities and sourced assertions linked to reasons and constraints. A condition language, truth-maintenance engine, alternative search and notifications can follow once the agreed personal graph is useful; they do not depend on choosing synchronization for v1.

The later module must respect lineage branches and competing source claims. An uncertain prerequisite cannot silently satisfy a hard constraint. Reconsidering a decision does not authorize executing it.

Add this later module through a complete useful personal scenario. It does not grant clients new execution authority or change source permissions.

# A08 Research guided retrieval and consolidation

**Status:** Proposed staged experiments. **V1:** Useful source-linked retrieval, bounded context and automatic acceptance of inferred additions within configured client/agent grants. Q7 confirms proactive useful-knowledge capture within configured grants; Q8 confirms explicit-owner correction preference with alternatives/history retained. Q9 selects MCP+CLI, and Q10 selects all three day-one tasks. An embedded extraction runtime, background consolidation, vectors, linked summaries and distributed workers are separately scoped modules. Corporate/protected-processing requirements in A11–A14 remain later.

## Context and proposed mechanisms

A useful memory platform should retrieve related evidence, retain context and improve its organization over time. The temporal graph remains usable without a model; research modules can be developed alongside the core and promoted when they improve actual tasks.

[HippoRAG 2](https://proceedings.mlr.press/v267/gutierrez25a.html) motivates associative graph/passage retrieval. Test lexical/vector candidates, bounded graph expansion and reranking, preserving access, time, branch and source filters. Relevant evidence must remain inspectable; a high graph score is not a confidence or truth assessment.

[LightMem](https://proceedings.iclr.cc/paper_files/paper/2026/file/a05b72653ec5b473732129829ae04195-Paper-Conference.pdf) motivates fast capture, intermediate organization and slower offline consolidation. Keep the online path responsive while measuring total capture, maintenance and answer cost. Topic filtering/compression can omit crucial details, so summaries link to their evidence and cannot overwrite canonical claims.

[Zep/Graphiti](https://arxiv.org/html/2501.13956v1) supplies temporal episode/fact ideas, but its paper's newer-information invalidation policy is not RefactoredMemory's truth rule. Competing sources remain claims; models may propose correction or retraction actions through the normal graph contract.

[Apple's on-device graph design](https://arxiv.org/html/2305.09464v1#S5) supports testing incremental pause/resume construction and source-selective sync. [OpenAI's Dreaming](https://openai.com/index/chatgpt-memory-dreaming/) supports evaluating freshness-aware background synthesis. These mechanisms do not establish a shared vendor backend or Atlas's mesh/protection semantics.

[Anthropic's layered memory study](https://www.anthropic.com/research/components-of-agent-memory) motivates source logs, notes, linked representations and small task context. Its task-dependent wiki/search results justify comparative experiments rather than making a wiki mandatory. Retain source search and measure construction cost and representation growth.

[Google's Sleep framework](https://research.google/blog/the-sleep-framework-a-new-way-for-llms-to-retain-knowledge-in-continual-learning/) changes parameters, unlike external-memory synthesis. Proposed default: retain private facts in addressable external records and assess parameter learning separately for approved reusable skills. No private-fact training or weight-level erasure solution is adopted.

## Boundaries and tradeoffs

Working context is a bounded task selection with source links and a declared knowledge/projection position. Notes, summaries and embeddings are derived artifacts with input references and generator/schema versions. Preserve permitted sources and report unavailable ones. A stale index must not silently present an old belief as current; consolidation cannot multiply independent evidence. V1 enforces the owner's client/processing grants. Mixed-domain information flow and corporate destinations under A12–A14 are later qualification.

A consolidation run records job identity, authorized input scope/frontier, executor, versions, destination and budget. Pause/resume and retries preserve progress; idempotency prevents duplicate semantic application. Concurrent workers use guarded artifact updates or retain competing revisions. Before publication, recheck current authority and source supersession/deletion. Proposed graph changes use normal validation and semantic lineage; generated notes cannot become harness instructions or grants. The first experiment can run manually, without a distributed worker platform.

These mechanisms add model cost, extraction risk, index state and maintenance work. Biological inspiration does not establish brain equivalence, universal forgetting rules or correctness. Model artifacts cannot grant permissions, execute procedures or administer peers.

## Verification and promotion

Use the PRD's R01–R06 with tasks informed by [LongMemEval](https://arxiv.org/abs/2410.10813) and [LongMemEval-V2](https://arxiv.org/abs/2605.12493). Separate factual/time-update/abstention behavior from workflow experience. Compare search alone, graph-aware retrieval and linked summaries plus search under declared budgets. Include wrong inferences, late corrections, concurrent workers, revoked inputs and partial replicas. Measure source attribution, stale/conflicting answers, coverage, latency, storage and total capture/consolidation/answer cost.

No Atlas memory-quality experiment has been run by this design update. Promotion requires semantic fit and measured end-to-end gain without critical temporal/provenance regressions. A manually triggered synthetic project/timeline consolidation experiment remains a research candidate, with fixture, cost ceiling and promotion threshold to agree. Q10 has separately confirmed project decisions/why, person relationships/evidence and changes since last month. The owner's explicit “Proceed” authorized the agreed v1 implementation; optional consolidation experiments remain separately scoped and are not release evidence by themselves.

# A09 Scoped causal replication and semantic conflicts

**Status:** Two personally controlled offline-writable peers and synchronization confirmed for v1; explicit journal/dependency-based direct synchronization implemented under A17 and exercised with local Linux peers. The actual Mac/Linux pair remains unverified. **Pair:** The owner's Mac plus a personally controlled Linux VM/container. **Later:** Third-peer/relay mesh, selective multi-tenant replication and corporate federation. **Related:** A02, A04, A06; A11 is future scale, not a prerequisite.

## Context and decision

The owner selected two personally controlled peers that each accept graph operations while disconnected and exchange them later. V1 must preserve concurrent changes, reconnect safely and converge at a shared causal frontier. It does not require all-to-all topology, a global total clock or a third-peer relay.

Replicate immutable graph operations with origin identity/incarnation/sequence, causal dependencies, namespace/dataset scope and versioned progress. Carry required entities, evidence and assertion predecessors. Separate durable receipt from causal application and query-projection progress. Duplicate/lost delivery is idempotent; contradictory content under one operation ID is refused. A17 authenticates admitted origin operations with HMAC under the trusted personal-peer key model; local client grants remain outside the semantic journal so replay cannot restore authorization. HMAC is not content encryption or non-repudiation against holders of the same authentication key.

Independent source claims coexist; declared exclusivity can reveal a semantic dispute. Concurrent descendants of one assertion form lineage branches. A sourced resolution names the heads considered, may retain uncertainty and can reopen when an unseen branch arrives. Neither field merging nor recency adjudicates knowledge. Apply the confirmed Q8 explicit-owner correction preference only through authorized attribution and the selected temporal view, retaining conflicting claims and predecessor history.

Administrative tombstones remain separate from retraction/invalidation. A stale replica cannot silently resurrect availability, and restore/clone cannot reuse an active origin stream. Retirement/reseed and retained-history rules bound old-peer costs explicitly. Current policy and deletion/retention state must be reconciled on restore/rejoin; past knowledge selectors cannot restore former authority. Future blind relays validate only approved opaque envelopes, while authorized executors validate semantic plaintext.

## Scope and future scale

Begin with the owner's admitted personal dataset and declare its full replication boundary. Bound batches, dependency backlog and catch-up/reseed work. Future multi-tenant/selective subscriptions require entity/evidence/predecessor closure and policy-scoped checkpoints, with partial answers declaring coverage; do not add that machinery to v1 solely for the roadmap.

[INRIA's Merkle Search Tree research](https://radar.inria.fr/rapportsactivite/RA2019/wide/wide.pdf) motivates efficient state reconciliation when delta exchange becomes costly. Merkle/delta techniques remain candidates, not a replacement for origin authentication, dependency semantics or a qualified protocol.

[Coordination-avoidance research](https://vldb.org/2015/program/lib/FullProgram.html) motivates identifying which invariants survive merge. Immutable claims can be retained independently; admission, exclusive administrative policy and schema rollout require an explicit authority/coordination design. Ordinary graph writes cannot alter grants. No consensus fleet is required for the first one-owner profile.

## Implementations and verification

A17 selects explicit per-origin immutable operation exchange, dependency-aware application and HMAC-admitted direct peer origins for v1. PouchDB, RxDB and CRDT frameworks remain future alternatives rather than dependencies. Default winners, revision pruning and framework admission defaults cannot redefine RefactoredMemory semantics. A future replacement must preserve declared contracts and pass the same fixtures.

Direct exchange comes first; a store-forward relay or third peer is qualified separately. Cloudflare and other hosted runtimes are adapters to evaluate, not inherited requirements. The direct Atlas/SQLite read benchmark supplies no mesh qualification.

Qualify two-peer personal sync using applicable M03–M10 and M13–M16 cases for partitions, dependencies, identity, branches, tombstones, recovery and fixed-frontier answers; M08's third-hop path is deferred. Past local knowledge histories may differ. Multi-tenant/selective-replica qualification is later. No library is qualified merely by this document.

# A10 Minimum temporal graph operations and delivery

**Status:** Personal-v1 scope implemented to the extent recorded in the evidence reports; full release qualification incomplete. **Depends on:** A01–A06's applicable personal portions, A09, A16 and A17. A11–A14 are not v1 dependencies.

## Context and decision

The first release delivers the owner's useful personal temporal knowledge store through mandatory MCP, Markdown/Logseq import and migration from prior LivingAtlas runs, on two offline-writable personal peers. Demonstrate sourced capture/import, preserved legacy meanings, recall, temporal history, corrections, offline concurrent changes, reconnect and convergence without adding corporate tenancy or product encryption to v1. Q7–Q10 add proactive capture within grants, explicit-owner correction preference with retained alternatives, MCP+CLI-only inspection, and all three day-one tasks.

Provide entity create/read; sourced fact/relationship/observation submission; evidence lookup; correct/retract/invalidate/reinstate; lineage/branch inspection and authorized attributed resolution; valid-at plus scoped known-at queries; temporal neighbors and bounded traversal; timeline/history; text search; and a graph change feed. Authorized inferred additions are accepted automatically within configured grants, with their provenance and uncertainty. Human-verification events remain separately attributed. Exact public names follow contract review; version changed mesh knowledge-time semantics. Q8 prefers explicit authorized owner corrections in the applicable temporal view, without deleting competing claims, evidence or history.

The MCP server is a mandatory v1 client surface, using the same graph and authorization contract. A16 requires latest-stable stdio/Streamable HTTP server conformance and independent-client workflows. Record installed Praxis2 workflows when a compatible connection is available; neither Praxis repository is to be changed. Keep any peer admission/sync exchange separate from ordinary consumer authority; no general tool gateway or second scheduler is implied.

Provide an inspectable personal owner journey for entities, assertions, sources, temporal history, sync health and conflicts. Q9 confirms MCP and CLI first, with no browser inspection UI in v1. A cinematic graph UI, corporate workspace selector or model selector is not required. Responses identify the answering peer/frontier, temporal quality, disputes/branches and coverage, distinguish accepted inferences from human-verified claims, and show the actual personal client/processing boundary.

Prove local semantics, durable recovery, mandatory MCP, Markdown/Logseq import and prior LivingAtlas migration using synthetic fixtures. Qualify the owner's Mac and a personally controlled Linux VM/container as two offline-writable peers, including offline assertions/corrections, reconnect and temporal-query equivalence. Selecting this pair does not authorize external provisioning/deployment. Third-hop relay/mesh is later. Source artifact locations/store generations remain a discovery task; actual personal-data ingestion and legacy cutover still require separate authorization.

Record each build's runtime/profile, fixture, test results and limitations. Measure performance before scale claims. Content encryption and model-based memory functions are separate implementation steps.

## Alternatives and consequences

A usable owner journey through MCP and CLI is required under confirmed Q9; a browser UI is outside v1. An engineering spike alone is not evidence of a usable workflow. A dedicated graph-database console, full agent UI or broad connector suite is not implied.

The minimum graph operations and the PRD's scoped personal-v1 acceptance set make delivery reviewable without imposing a service fleet. M17's multi-organization cases and corporate/cryptographic checks are later. Typed neighbor/path queries can initially use ordinary indexed storage.

## Verification and revisit

Run applicable personal-v1 cases through actual storage, graph API and MCP clients, with an owner journey for evidence/history/corrections. Qualify the selected Mac and Linux VM/container as real offline-writable peer environments; a mocked second runtime is not sync acceptance. Provisioning/deployment remains subject to its existing approval boundary. Do not require all historical M01–M18 cases indiscriminately: third-hop mesh, corporate domains and cryptographic profiles are later. M20 exercises the confirmed project-decision/why, person-relationship/evidence and previous-month-change workflows through MCP+CLI. Implementation approval has been received; record actual results and access gaps without declaring unrun tests passed.

# A11 Partitionable deployment and privacy profiles

**Status:** Deferred evolution architecture. **V1 acceptance:** Not a gate. **Future scope:** Multi-tenant/shared deployments, corporate domains, independently scalable services and protection profiles. Only useful versioned contracts/export and current projection correctness are retained in v1; no tenant machinery is required now.

## Context and decision

The platform should work personally now and grow without treating its first technology as permanent. Preserve graph meaning and versioned boundaries while allowing different physical engines and deployment profiles. Ownership and protection profiles are separate from deployment location: local, on-premises, SaaS or hybrid. A blind SaaS relay can retain ciphertext while approved local/customer/protected remote environments materialize semantic views. An ordinary hosted plaintext executor is a different operator-trust profile.

Start with one local peer and its views. Grow to admitted peers or dataset subsets and an optional relay. Add partitioned shared persistence plus independently scalable query/materialization workers only when workload evidence justifies them. A shared service and a laptop may use different engines under explicit conformance/capability profiles.

For a later shared platform, evaluate partitioning by tenant/dataset and trust boundary, with scope carried through identity, operations, indexes, credentials and cursors. Do not implement multi-tenancy or cross-partition policy in personal v1 solely for this roadmap. Cross-partition references and queries require separate authority, budget and coverage qualification when introduced.

Record each projection's semantic/model/schema version and processed graph frontier. Support bounded read-your-write requirements locally, or return labelled lag/partial coverage. Later worker separation must preserve these meanings. [Differential dataflow](https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf) motivates incremental maintenance, but adopting a dataflow runtime requires measured benefit. Include source-owner restrictions and a processing/profile reference; protected plaintext views cannot be placed outside the approved execution boundary merely to improve speed. Current policy applies before traversal/ranking and to saved output. Privacy-aware cost, tenant fan-out, key release/cache behavior, revocation and erasure backlog need P06 measurements.

Separate the hot working set from retained semantic history. Evaluate checkpoints, compressed deltas and colder archive storage under E05; a missing historical interval is reported unavailable rather than answered from current state. Subscription closure, replica retirement and reseed rules belong to the protocol.

## Alternatives and consequences

A single global graph replicated everywhere is simple for two small peers but grows data, policy and history costs with the platform. A full distributed service fleet from the start increases operating burden before evidence. Namespace and projection seams provide a middle path; they reduce future change cost without proving effortless scale-out or zero-cost migration.

Engine-native graph features and research layouts remain eligible. Preserve a versioned canonical export and deliberate migrations rather than requiring every old API/schema to survive unchanged.

## Verification and revisit

Personal-v1 acceptance is the scoped PRD set and mandatory MCP integration; this ADR adds no release gate. Later multi-tenant gates cover isolation, dependency-closed partial replicas, policy scope, projection lag/recovery, bounded cross-partition queries and growing-history equivalence.

Scale-out needs new measurements of throughput, tail latency, memory, wire cost, failure recovery and operating cost. The 110k selective-read result does not establish any of these. Promote a research mechanism only after semantic fit, a bounded useful gain and end-to-end reliability/cost evidence.

# A12 Personal and organization ownership domains

**Status:** Future ownership principle confirmed; implementation deferred beyond personal v1. **V1 acceptance:** No corporate domains, employer lifecycle or M17 multi-organization fixtures required. **Future scope:** E02/E09 and P03, plus the corporate portions of C22/C23 and M18.

## Context and decision

For a later organizational product, personal data stays personal and each organization's data stays under its control across current/former employers. That future requires explicit controlling domains. V1 is the owner's personal knowledge store; a personal record about an employer or company does not instantiate a corporate ownership domain.

Model personal/organization domains independently of tenant/dataset, creator, source, subject, authenticated actor and membership. A person can belong to several organizations. Trusted account/workspace configuration can assign an approved owner; ambiguous source material is unassigned/quarantined. Employment assertions and source text cannot modify authority or transfer a record.

Default to separate personal and employer domains with independently administered policy/key references. Avoid automatic global person linking across domains. Cross-domain relationships, resolution, exports and persistent mixed-source results need explicit authority; changing jobs does not move work knowledge into a personal archive.

Confirmed product direction: when someone leaves an organization, the organization retains control of its own data and the person retains their personal data. Recorded owner direction confirms this ownership principle. This does not select membership/revocation rules, administrator/read roles or recovery authorities. An organization admin need not automatically be a reader; whoever can change read/key-release policy unilaterally is nevertheless an effective trusted authority. Ambiguous ownership and mixed-source/derived-data treatment remain unresolved; legal and contractual classification must be established separately from an LLM's inference.

## Lifecycle and consequences

The confirmed principle preserves organizational control of organization data and personal control of personal data after departure. Proposed offboarding rules must define expiry/revocation of employment-linked grants, any separately authorized continuing access, organizational recovery and treatment of copies. Other-employer domains remain separately controlled. Account deletion and deletion of organization-owned records require distinct policy; these mechanics remain open.

Ownership transfer is a deliberate administrative/export/import workflow with source lineage, destination authority and retention handling. It is not an ordinary graph update. A shared personal/work view does not by itself transfer either domain's ownership.

Separate domains add identity, policy and query-federation work. A single personal/work flag is simpler but fails for multiple employers and approved mixed results. Do not assume separate namespaces on an organization-administered device protect decrypted personal memory from that device's administrator.

## Verification

M17's personal-plus-organizations schema/isolation exercise and corporate portions of M18 are deferred. P03 later qualifies multi-employer lifecycle, organizational recovery and transfers. V1 verifies the separate personal owner/client boundary through A06. The future ownership principle remains confirmed; no implementation, ownership transfer, membership or permission change is claimed by this update.

# A13 Owner approved processing and key custody

**Status:** Deferred protection architecture; no cryptographic/execution solution selected. **V1 acceptance:** Not a gate. **Future scope:** Product content encryption, operator blindness, custody, key recovery, protected execution and P01/P02/P04/P06 qualification. Basic personal grants and transport authorization remain in A05/A06/A16.

## Context and decision

The target is protected plaintext available only to the controlling owner and approved people/processing contexts under a declared threat model. A SaaS storage operator should not gain a decryption path merely by running the platform. Organization-approved custodians/executors are authorities within the organization profile; they do not receive personal-domain authority.

Separate storage, key custody, authentication/recovery and execution. Customer-managed keys or encryption at rest do not establish operator blindness when ordinary provider-controlled code can request decryption. Client software/update delivery, remote measurements, metadata, debug/logging, external model calls and output handling belong inside the evaluated boundary.

Candidate later profiles include owner/customer-side compute over encrypted storage, organization-controlled execution, or separately qualified protected remote execution. [Attestation-bound key release](https://docs.aws.amazon.com/enclaves/latest/user/kms.html) is an example mechanism, not a RefactoredMemory selection or proof. A conventional hosted plaintext executor has a different trust profile. No general performant encrypted graph computation is assumed.

## Delegation and recovery

Preserve authorizer and acting agent separately. A bounded standing grant can authorize background lookup/index cleanup without a prompt on every read. It constrains domain/resources, operations, actor/audience, executor/profile, expiry, output destinations and onward delegation. Trusted tools and execution boundaries enforce those limits; a prompt is not a security boundary.

Align key access with the grant. A dataset key given to an untrusted actor defeats an item-only cryptographic claim; use qualified finer-grained keys or trusted mediation. Read, propose correction, rebuild index, export, purge and transfer are distinct rights. An external model receiving plaintext is an approved recipient only when its use and destination are authorized.

Keys and approved execution must be available for unattended work. Locked/offline clients or expired key leases may require a job to wait. Record protected audit metadata about actor, authorizing grant/policy, scope and result without logging plaintext or secrets.

Personal recovery may use owner backups and optional nominated trustees. Proposed default: Atlas operators cannot recover plaintext without the required owner-approved factors or custodians. Assistance can still be possible without giving operators unilateral recovery. If every authorized recovery path is lost, data may be unrecoverable. Organization recovery has its own explicitly approved authorities and does not unlock personal data.

## Verification

Personal v1 supplies no operator-blind or product content-encryption guarantee. Its ordinary client/processing authorization is tested independently. Later P01/P02/P04 qualify keys, clients/executors, delegation, egress, lost factors and compromised keys; P06 measures that exact profile. No hardware, KMS, key hierarchy or recovery service is required for v1 by this proposal.

# A14 Derived information revocation and retention

**Status:** Deferred cross-domain lifecycle/information-flow architecture. **V1:** Basic source lineage, current personal grants, honest retention/deletion behavior and restore correctness remain in A02/A06/A15. **Later:** Corporate/mixed-source ownership, advanced offline revocation, cryptographic erasure, key-release/escrow and P03–P06. This ADR's full machinery is not a v1 gate.

## Context and decision

Confidentiality applies to graph results and derivatives, not just source objects. Indexes, embeddings, summaries, prompt context, caches, telemetry, temporary files and backups need source/domain lineage and the selected protection profile.

Combining sources cannot silently remove restrictions. The [decentralized-label research](https://www.cs.cornell.edu/andru/papers/sp98/paper.html) motivates respecting multiple owners' information-flow policies for a future organizational product. Derived ownership, effective access and source restrictions are separate. Future mixed personal/work use needs the relevant domains' authorization and an approved persistent destination. This cross-domain machinery is deferred beyond the personal-v1 store.

Current policy governs every query, including historical valid-at/known-at reads. Past employment or historical policy state cannot restore current access. Authorized administrative policy auditing is separate from the ordinary knowledge-time selector.

## Revocation erasure and restore

Define the selected profile's revocation propagation, offline grant/key residency and policy-freshness bounds. Updated nodes stop new release/access; an offline reader may retain old keys and plaintext. Neither rotation nor audit can recall prior disclosure. Graph operation acceptance after stale-policy periods follows an explicit rejoin policy, not a caller's backdated timestamp.

Semantic correction/retraction, world invalidation, logical hiding, retention holds and physical/cryptographic erasure are different actions. Preserve history within the declared retention policy. A deliberate authorized purge can leave unavailable history or a permitted minimal stub; it must not be disguised as a world change or answered from current state.

Track dependencies to invalidate, rebuild or purge affected derivatives. A restored snapshot remains unserved until current authorization and deletion/retention state are reconciled. Old data/backup restoration cannot automatically revive old grants, erased content or deprecated key-release policy.

Cryptographic erasure depends on relevant key copies and prior plaintext, including recovery/escrow material. [NIST sanitization guidance](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-88r2.pdf) treats those prerequisites explicitly. Report managed-copy coverage and unrecallable exports rather than promising erasure everywhere.

## Verification

The personal subset of M18 checks current client authority across history, authorized outputs, safe restore and the selected personal peers' stated stale-policy bounds. Multi-owner information flow, employer lifecycle, enterprise revocation, cryptographic recovery/erasure and P03–P06 belong to later phases. Personal two-peer sync does not qualify those future guarantees.

# A15 Inspectable knowledge and memory controls

**Status:** Q6–Q10 personal behavior confirmed and exercised in synthetic workflows; actual-host/client qualification remains incomplete. **V1:** Proactive useful-knowledge capture and automatic acceptance within configured grants, explicit-owner correction preference with alternatives/evidence/history retained, MCP+CLI inspection with no browser UI, and all three day-one tasks. **Later:** Enterprise ownership, full forgetting/consolidation systems and protected lifecycle qualification.

## Context and proposed behavior

A useful personal knowledge store needs an explanation and control surface for what it retains and infers. Model-generated knowledge is not trusted merely because it is organized, summarized or placed in context. The temporal graph and personal-v1 scope govern the initial product; enterprise ownership is a later direction. Research mechanisms remain assessed in the overview (historical planning Page; authorized access required).

Keep derivation, automatic acceptance and human verification separate. Record source-stated observations, extraction and inference with evidence, authenticated actor, model/version when applicable, method and uncertainty. Acceptance within a configured grant records admission; it does not invent a human reviewer or certify truth. Any later owner confirmation/rejection names its claim and actual review event. Preserve underlying sources, correction lineage, competing claims and disputes. Neither acceptance nor verification grants new access, creates independent corroboration or authorizes identity/ownership merging.

Provide “Why do you believe this?” for evidence, method, review, alternatives, time and coverage. Explain which configured personal clients/agents can access it and where approved processing occurs, including the offline personal peers' stated limits. Do not require corporate domain selectors or claim encrypted/protected execution that v1 does not implement.

Keep personal correction/retraction, suppression of future personalization and authorized deletion distinct. Suppression is not deletion, and erasure is not a change to what once held in the world. Scope the available personal controls explicitly and show unavailable history/residual copies honestly. A14's corporate/mixed-source policy and cryptographic erasure machinery are deferred.

## Alternatives and consequences

A single confidence score or mutable profile obscures how a claim arose, was accepted or was later verified. A universal “forget” switch conflates suppression, correction and purge. Attribution/dependencies make errors and lifecycle actions traceable. Q6's automatic acceptance within grants is settled. Q7 confirms proactive capture within grants and Q8 confirms preference for explicit authorized owner corrections while retaining conflicts/evidence/history; future corporate mixed-source ownership and sensitive-inference controls remain separately scoped. Automatic identity merging is not implied.

C08/C20 establish personal inspection and provenance. V1 accepts inferred additions automatically within the owner's configured client/agent grants without per-item review, while retaining evidence, actor/model/derivation, uncertainty and history. A mandatory review queue is not a v1 prerequisite; optional later review records actual human verification separately. No worker can elevate source text into instructions/authority or silently erase earlier claims/corrections. Q8 prefers explicit authorized owner corrections in the applicable view while preserving disagreements and lineage. Q9 selects MCP+CLI inspection, and Q10's three tasks provide concrete usefulness fixtures. Advanced consolidation/lifecycle automation remain staged.

## Verification and revisit

M01/M12 verify personal provenance and inspection on synthetic data. Test an automatically accepted but wrong inference, a later owner correction, copied evidence, a revoked client grant and stale summary/restore; assert that automatic acceptance was not marked human-verified and that no per-item review blocked an in-grant addition. Deny out-of-grant operations and preserve disputed alternatives/history. Assert Q8's preferred explicit-owner correction at the requested knowledge frontier, unchanged earlier history, retained alternatives, and refusal to trust an owner label supplied by source text. M20 covers all three confirmed day-one tasks through MCP+CLI. Two-employer fixtures, corporate mixed-source controls and protected-deployment tests remain deferred.

A17 records the implemented Python/SQLite approach; the linked reports describe passing synthetic and protocol checks and remaining qualification. Personal-v1 scope, mandatory MCP, proactive capture, automatic inferred acceptance within grants, preferred explicit-owner corrections with retained conflicts/history, MCP+CLI-first inspection and all three day-one tasks are confirmed. No inference model or product cryptographic profile is selected, and the evidence does not establish full release acceptance.

# A16 Mandatory current-standard MCP integration

**Status:** Mandatory v1 product requirement; standard-library server implemented under A17. Modern protocol/schema checks and the real independent Python SDK legacy-stdio workflow pass; actual installed Praxis2 interoperability remains unverified. **Scope:** C24/M19. RefactoredMemory must expose true latest-stable MCP connections for Praxis2 and other compliant clients through the same personal graph and authorization contract. Deliver server conformance and independent-client evidence; do not alter either Praxis repository to resolve client-side availability.

The implementation verification pinned the official specification at commit `cf59bb0d8b43e711420f5f7313aa6cca3f1e1898`, which identifies 2026-07-28 as the latest published stable revision. Recheck for future upgrades rather than freezing that value indefinitely. Record the protocol, SDK and client versions and applicable conformance requirements. Do not inherit an older initialization handshake where the chosen revision uses per-request metadata and `server/discover`; support older client behavior only where a verified integration needs it. The selected initial implementation uses no external SDK installation. Implement the needed MCP server/tool surface directly, while verifying all applicable mandatory protocol requirements against the official specification; a partial feature surface is not permission to omit required base behavior.

Qualify local stdio and the agreed remote Streamable HTTP path with their applicable authentication/authorization rules. A locally tested remote transport does not authorize external deployment. Bound tools/results, preserve evidence/time/coverage, enforce configured personal grants and safe mutation retries, and keep peer replication/administration separate from consumer MCP authority. Source text and arguments cannot grant permissions. The official MCP specification permits custom authorization strategies. The current HTTP implementation uses owner-preconfigured opaque bearer grants; it does not implement the standard OAuth profile, protected-resource metadata discovery or OAuth-only host onboarding. OAuth is not an added v1 requirement for this selected profile; connecting clients must support the configured bearer strategy.

M19 requires latest-stable stdio/Streamable HTTP conformance and real independent-client workflows, with installed Praxis2 end-to-end qualification when a compatible connection is available: discovery, authorized sourced writes/corrections, automatic inferred additions within configured grants without per-item review, temporal retrieval with provenance, denied access and applicable version/schema/error/retry/interruption checks. Verify actor/model/derivation and uncertainty preservation and distinguish automatic acceptance from human verification. Record client versions and reproducible connection instructions. Mocks do not prove an unavailable client's integration; report installed Praxis2 as unverified until tested. Its hardcoded provider endpoints or approval paths are not an authorized or required change in either Praxis repository. No paid processing, new credentials or live personal-data ingestion follows from this ADR.

The owner has explicitly said “Proceed,” including the agreed graph and MCP implementation after document reconciliation. Implementation and passing checks now exist, as described in the conformance report. The independent SDK 1.29.0 passed over the separate 2025-11-25 stdio compatibility path; the installed Praxis2 app and actual modern-client connection remain unverified. Real-data ingestion, credentials, paid processing and external deployment retain their separate authorization boundaries.

# A17 Initial Python/SQLite and direct-sync implementation

**Status:** Implemented engineering direction with passing Linux synthetic correctness/recovery and scoped MCP evidence; actual-host/client and original-source release qualification remains incomplete. **Related:** A02, A04, A05, A06, A09, A16; C01–C25/M01–M20 as scoped by the PRD.

## Decision and rationale

Use Python 3.12+ and its standard library, with SQLite in WAL mode and `synchronous=FULL`. Keep immutable graph operations and an atomic semantic operation journal, with entity/assertion/evidence/lineage effects and application/replication eligibility committed together. Maintain rebuildable query projections and explicit local knowledge positions. Keep current local client grants separate from replicated history, so journal replay or an old graph snapshot cannot restore revoked authority.

Use explicit per-origin sequence/incarnation and dependency-based direct synchronization between the owner's Mac and Linux VM/container. Bound batches, authenticate admitted origin operations using HMAC, retain received-but-not-yet-applicable dependencies visibly, reject contradictory content under one operation identity, and apply complete groups atomically. HMAC is authentication within the declared trusted personal-peer key model; a holder of an authentication key can produce messages authenticated by it. It is not product content encryption, public non-repudiation or proof against a malicious trusted key holder. Cross-host transport still requires its appropriate protection and admission configuration.

Build the required MCP server/tool surface using the standard library without installing an external SDK. Verify the selected stable protocol and all applicable mandatory behavior against official sources, and maintain a conformance checklist. Required server behavior and real independent-client evidence cannot be waived because the implementation is hand-written or intentionally small. Record installed Praxis2 end-to-end behavior only when exercised through an available compatible connection; client code, endpoint or approval-path changes in either Praxis repository are outside this task. Clearly document unsupported optional features and client/version compatibility.

The rationale is operational simplicity, available tooling, portable local transactions and a testable path to temporal, durability and offline-sync correctness. The historical Atlas/SQLite selective-read comparison did not compare this implementation or the complete contract and does not establish a platform winner. No new package installation, production deployment or personal-data import is implied.

## Qualification and revisit

Run synthetic tests for atomic groups, acknowledged durability and failure recovery, dependency disorder, replay/gaps, origin admission, current grants, owner-correction preference, history rebuilding, imports and fixed-frontier convergence. Qualify actual Mac/Linux execution and official MCP behavior plus the required real clients; report unavailable access as unverified. Measure full operations and memory/storage costs before performance claims. `WAL`/`FULL` settings alone are not physical-power-loss certification.

Revisit the engine, protocol adapter or SDK choice if conformance, maintenance, correctness or measured workload constraints justify it. Preserve versioned graph/export contracts and source/temporal lineage. This ADR records the implementation approach and links the observed checks; it does not certify full v1 release acceptance or a production protection profile.

# Next work

Maintain the approved Q1/Q2/Q5–Q10 scope, the owner's explicit “Proceed,” and the implementation/evidence records in the repository and reconciled Pages. Q7 is proactive capture within grants; Q8 prefers explicit authorized owner corrections while retaining conflicts/history; Q9 is MCP+CLI first without a browser UI; Q10 includes project decisions/why, person relationships/evidence and changes since last month. Inventory legacy artifacts and qualify storage/sync/MCP against actual evidence. Passing Linux synthetic and independent SDK checks are recorded; the owner's actual Mac, installed Praxis2 application and full original-archive migration remain unverified. Live-data ingestion, original-key use and external deployment require their separate authorization. Linear work remains paused.

Retain the confirmed organization/personal ownership principle as a later roadmap item. Corporate custody, multi-employer offboarding, protected executors, keys/recovery and mixed-domain policy do not block personal v1. A personal store may contain facts about organizations without managing their data ownership.

Use historical selective-read results only within their limits; qualify the selected A17 stack against the complete personal contract, local durability/recovery, Mac/Linux offline convergence, imports and actual MCP clients. Third-hop mesh and corporate/cryptographic qualification are later. The explicit owner “Proceed” has been received; continue qualification without repeating that approval request. The passing checks recorded above do not establish full release acceptance or authorize real-data ingestion, original-key use, credential/permission changes, external deployment or resumed Linear work.
