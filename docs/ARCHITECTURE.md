# Personal v1 architecture

**Status:** implementation authorized on 7 November 2026. The initial runtime is Python 3.12+ standard library with SQLite WAL/FULL transactions and an immutable operation journal. The [implementation contract](CONTRACT.md) defines APIs, direct sync, local grants and knowledge semantics; qualification remains to be established.

V1 has one owner and two full peers: the owner's Mac and a personally controlled Linux VM/container. Each peer has local durable knowledge, local queries, MCP access and authenticated peer synchronization. It can accept writes while disconnected. A peer may be implemented as one process; diagram boxes describe responsibilities, not required services.

```mermaid
flowchart TB
    C["Praxis and another MCP client"] -->|"required MCP"| A
    F["Markdown / Logseq"] --> IMP["Required source importer and legacy migration"]
    L["Prior LivingAtlas data"] --> IMP
    IMP -->|"authorized, source-linked operations"| A
    subgraph MAC["Personal peer A — owner's Mac"]
        A["MCP and owner authorization"] --> G["Temporal graph and correction lineage"]
        G --> D["Durable history, sources and sync journal"]
        D --> I["Rebuildable query indexes"]
        A --> Q["Time, graph, source and history queries"]
        Q --> G
        Q --> I
        G <--> S["Personal peer admission and synchronization"]
    end
    S <-->|"authenticated operations and dependencies"| B["Personal peer B — Linux VM/container<br/>same contract; independent local writes and queries"]
    C -->|"configured MCP connection"| B
    W["Optional later consolidation"] -.->|"scoped proposals"| A
```

The [editable diagram](diagrams/personal-v1.mmd) describes the same required topology. Public-safe diagrams do not contain personal endpoints, credentials or source paths.

## Knowledge contract

Stable entity IDs represent identities. Assertions represent sourced facts and typed relationships; changing names or affiliations are assertions, not destructive identity edits. Preserve unresolved observations without inventing entities or dates. Evidence identifies the source and captured version. Separate direct source statements, extraction, model inference and review attribution.

World time describes when a claim held. Knowledge time describes when a specific peer acquired/applied the claim or correction. Retain origin metadata separately from each peer's receipt/application history. Queries name a local knowledge position or shared causally closed frontier. At a shared frontier, semantic answers converge; the peers' earlier local-known histories may differ. Unknown dates are not sortable sentinel values, and half-open interval/precision rules must be consistent across search and traversal.

Correction, retraction, invalidation and reinstatement are distinct semantic operations. Competing sources are not automatically revisions of one claim. Concurrent revisions retain branches until an authorized resolution. Administrative deletion and physical erasure are separate from changing a historical belief. Return evidence, lineage, unresolved alternatives, temporal fidelity and coverage with answers. Derived indexes and summaries never become a second source of truth.

## Durable operation and personal sync

An admitted semantic operation group and its required local metadata become durable before acknowledgment and visible atomically. Received operations wait for required dependencies. Use stable operation identities and safe retries. Clock skew, duplicate delivery and delivery order must not silently discard a correction.

Peers authenticate each other and operate within the owner's admitted store. Test offline writes on both, concurrent corrections, interrupted exchange, missing dependencies, stale rejoin, restart and restore. A successful two-peer test does not establish a transitive relay mesh. Fine-grained subscriptions and larger meshes are separate later choices.

## Import and migration

V1 supports Markdown/Logseq and prior LivingAtlas data. First inventory the actual generations and available artifacts without altering originals. Define explicit conversions for source identity, original world/knowledge semantics, evidence, correction lineage, IDs or ID mappings, and import-time knowledge. Do not backdate when RefactoredMemory itself learned imported material.

Unchanged reimports are idempotent; changed source versions preserve earlier evidence and use declared correction/update rules. Inventory every input with imported, unchanged, unsupported, quarantined or failed status. Preserve unresolved content and fidelity gaps rather than guessing equivalence or silently skipping it. Keep an original backup, versioned mappings and a rollback path.

Legacy decryption support is an import compatibility concern when an existing source is encrypted. Use only authorized original keys in the approved environment. It does not require a new v1 encryption architecture. Missing artifacts or keys remain explicit blockers for the affected migration path; development uses synthetic fixtures until real-data access is separately authorized.

## Personal protection and later evolution

V1 requires local access controls, scoped MCP client/agent grants, authenticated peers, HTTPS/TLS for remote transport, bounded inputs/queries, and safe logs. Source text cannot grant permissions or execute tools. Current authority applies to historical queries. Model-inferred additions are automatically accepted within configured client/agent grants, without per-item human review. Preserve evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history; acceptance is not human verification or established truth. Q7 authorizes proactive client capture within grants. Q8 prefers explicit authenticated owner corrections while retaining contradictory claims and evidence. Q9 selects MCP and CLI first. Q10 requires the project-decision, relationship-evidence and recent-changes journeys.

Product content encryption, corporate ownership boundaries and multitenancy are deferred. Stable IDs, versioned semantic contracts, provenance and portable export preserve a practical migration path. Future tenancy/custody must not introduce a prerequisite enterprise framework into personal v1.
