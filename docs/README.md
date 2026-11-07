# Documentation index

**Current stage:** implementation authorized on 7 November 2026. Q7–Q10 are accepted and the owner explicitly said **“Proceed.”** The [implementation contract](CONTRACT.md) fixes the initial runtime and shared APIs. Engineering evidence and real-environment qualification remain distinct from this approval.

**Tracking:** Linear setup is paused at the owner's request. Use the [repository tracking plan](tracking/README.md) meanwhile. No action to create a Linear team is currently needed, and Linear availability is not a product or documentation gate.

## Reading order and authority

| Document | Purpose | Status and authority |
| --- | --- | --- |
| [Decisions](DECISIONS.md) | Accepted scope, open owner questions and deferred work. | Start here to avoid reopening settled choices. |
| [Product requirements](PRD.md) | Personal-v1 behavior, requirements and acceptance cases. | Canonical requirements; preserved C/M identifiers distinguish v1 and later scope. |
| [Architecture decisions](ADRS.md) | Evidence, alternatives, rationale and decision status. | Each ADR carries its own accepted/proposed/deferred status. |
| [Architecture](ARCHITECTURE.md) | Personal Mac/Linux topology, temporal model, import and recovery boundaries. | Proposed implementation of accepted scope. [Editable diagram](diagrams/personal-v1.mmd). |
| [MCP integration](MCP.md) | Required protocol/client contract and interoperability evidence. | Requirement accepted; implementation and qualification pending. |
| [Validation](VALIDATION.md) | Synthetic fixtures, failure cases, import/migration and release evidence. | Planned checks, not passing results. |
| [Research](RESEARCH.md) | Source ledger, supplied measurements, limitations and outstanding research. | Public-safe summary; full historical private evidence remains in its authorized sources. |
| [Execution prompt](EXECUTION_PROMPT.md) | Instructions for continuing research, reconciliation and eventual authorized implementation. | Must agree with the requirements and explicit proceed gate. |
| [Implementation contract](CONTRACT.md) | Shared operation, temporal, authority and recovery APIs. | Implemented contract; limits remain explicit. |
| [Runbook](RUNBOOK.md) | No-install CLI, MCP setup, two peers and recovery. | Executable commands with synthetic-first guidance. |
| [Acceptance evidence](ACCEPTANCE-RESULTS.md) | Actual test and benchmark results plus remaining qualification. | Distinguishes executed Linux/SDK checks from unavailable Mac/Praxis/archive checks. |
| [MCP conformance](MCP-CONFORMANCE.md) | Latest protocol and actual client evidence. | Modern protocol checks plus independent legacy SDK integration; Praxis unverified. |
| [Import formats](IMPORT-FORMATS.md) | Inventoried legacy generations and conversion/fidelity limits. | Each input is accounted for; unsupported material is not silently promoted. |
| [Sync protocol](SYNC-PROTOCOL.md) | Bounded direct exchange and explicit recovery-origin admission. | Synthetic process, retry, conflict and recovery evidence. |
| [Tracking plan](tracking/README.md) | Prepared backlog, dependencies, requirement coverage and future Linear setup. | Planning aid; does not override requirements or authorize implementation. |

## Organization and maintenance

- Keep product requirements in the PRD, decisions and rationale in the ADRs/decision register, and supporting evidence in the research ledger. Update the affected documents together when an accepted decision changes.
- Keep architecture source in `diagrams/`; show a readable view in the architecture document. Avoid creating competing diagram versions with different scope.
- Keep tracking artifacts in `tracking/`. The structured plan is the maintained backlog source; its Markdown view is a readable export. These are prepared items, not actual Linear issue IDs or live statuses.
- Preserve C01–C25/M01–M20 and ADR identifiers when changing scope; classify later work explicitly. Corporate tenancy, product encryption and transitive mesh must not become accidental personal-v1 gates.
- Keep current unknowns visible. Q6 automatic acceptance and Q7–Q10 are confirmed; record remaining engineering and access gaps explicitly. A proposed default or completed documentation snapshot is not an accepted implementation design.
- Reconcile the historical planning Pages with accepted repository decisions without copying restricted source content into this public repository. Private source locations remain in the private working prompt.
- Record test/benchmark evidence only when it actually exists. Documentation organization, backlog preparation and supplied measurements are not product qualification.

No external tracker, assignment or real-data authorization is implied by this documentation structure. Implementation approval is the owner's explicit 7 November 2026 instruction.
