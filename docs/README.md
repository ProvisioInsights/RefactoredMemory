# Documentation index

**Client-led implementation, 9 November 2026:** The journal-backed workspace tools, pinned briefs, client task checkpoints and optional graph App are implemented in this branch. See [the workspace guide](CLIENT-LED-WORKSPACE.md) and [executed qualification](CLIENT-LED-VALIDATION.md). Historical requirements-only notes below describe their earlier documentation revision; named provider products still require separate live qualification.

**9 November 2026 design update:** [L01–L08/LM01–LM06](PRD.md#client-led-processing-and-review-direction) and [A22/A23](ADRS.md#a22-client-led-processing-and-provider-independent-memory-roles) make connected LLMs the current processing executors, define four memory roles and require portable tools, contributor attribution and a simple graph-review direction. Internal intelligence is optional future work. This requirements update does not refresh the historical qualification baseline below or claim new functionality/client passes.

**Current stage:** personal-v1 and the NAS/OAuth/automatic-sync extension are implemented and under qualification. The owner's 7 November 2026 **“Proceed”** and subsequent NAS build instruction remain in force. The [implementation contract](CONTRACT.md) and [NAS contract](NAS-CONTRACT.md) define the implemented boundaries; [acceptance evidence](ACCEPTANCE-RESULTS.md) records what actually ran. Actual owner Mac/NAS and hosted-client qualification remain separate.

**Tracking:** Linear setup is paused at the owner's request. Use the [repository tracking plan](tracking/README.md) meanwhile. No action to create a Linear team is currently needed, and Linear availability is not a product or documentation gate.

## Reading order and authority

**Current interface/core clarification:** A24 and L09–L12 make the shared field contract an RM-core responsibility. The MCP App is a focused graph/list explorer and CRUD client, not a conversation or model/task-management workspace. [Core fields and focused CRUD](CORE-FIELD-CONTRACT.md) defines missingness, typed operations and FC01–FC08; the starter catalog and opt-in validator exist in source; rollout, field-driven UI and full acceptance remain pending.

| Document | Purpose | Status and authority |
| --- | --- | --- |
| [Decisions](DECISIONS.md) | Accepted scope, open owner questions and deferred work. | Start here to avoid reopening settled choices. |
| [Product requirements](PRD.md) | Personal-v1 behavior, requirements and acceptance cases. | Canonical requirements; preserved C/M identifiers distinguish v1 and later scope. |
| [Architecture decisions](ADRS.md) | Evidence, alternatives, rationale and decision status. | Each ADR carries its own accepted/proposed/deferred status. |
| [Architecture](ARCHITECTURE.md) | Personal Mac/Linux topology, client-led processing, four memory roles, temporal model, import and recovery boundaries. | Personal-v1 implementation plus A22/A23 planned extensions; qualification remains separate. [Deployment diagram](diagrams/personal-v1.mmd), [processing diagram](diagrams/client-led-memory.mmd). |
| [MCP integration](MCP.md) | Required protocol/client contract and interoperability evidence. | Latest-stable server implemented; actual installed Praxis2 connection unverified. No changes to either Praxis repository. |
| [Validation](VALIDATION.md) | Synthetic fixtures, failure cases, import/migration and release evidence. | Requirement-to-test plan; executed results are in the acceptance report. |
| [Research](RESEARCH.md) | Source ledger, supplied measurements, limitations and outstanding research. | Public-safe summary; full historical private evidence remains in its authorized sources. |
| [Execution prompt](EXECUTION_PROMPT.md) | Instructions for continuing the authorized implementation and qualification. | Matches accepted requirements and the explicit Proceed already received. |
| [Implementation contract](CONTRACT.md) | Shared operation, temporal, authority and recovery APIs. | Implemented contract; limits remain explicit. |
| [Core field contract](CORE-FIELD-CONTRACT.md) | Shared field definitions, missingness, evidence, typed CRUD and focused UI. | A24 accepted direction; source catalog/tagged validation implemented; rollout, UI and complete FC acceptance pending. |
| [Field catalog v1](FIELD-CATALOG-V1.md) | Concrete 52-definition starter generated from packaged core definitions. | Published in source; no automatic legacy rewrite, universal activation or deployed/UI claim. |
| [RM client contract](RM-CLIENT-CONTRACT.md) | Exact discovery, v1 tags, typed operations, missing/time encodings and client obligations. | Explicit tagged assertions validate in the core; deployment and remaining FC acceptance stay separate. |
| [Field contract validation](FIELD-CONTRACT-VALIDATION.md) | Executed source, fixture, package, security and independent-review evidence. | 252 local tests, three platform skips; full FC, UI, client and deployed-peer qualification remain separate. |
| [NAS contract](NAS-CONTRACT.md) | Accepted NAS/OAuth/automatic-sync extension. | Implemented extension contract; actual deployment and hosted-client evidence remain separate. |
| [NAS deployment](NAS-DEPLOYMENT.md) | Isolated VM/container, tunnel and TLS deployment. | Device configuration requires actual NAS qualification. |
| [NAS commissioning](NAS-COMMISSIONING.md) | Explicit bootstrap, private credential handoff, stop/restart and memory/authorization-server recovery. | Locally exercised operator procedures; actual host execution pending. |
| [Maintenance access](REMOTE-ADMIN.md) | Private VPN and restricted SSH identity. | No broad DSM or Docker administrator grant. |
| [Runbook](RUNBOOK.md) | Core CLI, optional OAuth dependencies, two peers and recovery. | Executable commands with synthetic-first guidance. |
| [Acceptance evidence](ACCEPTANCE-RESULTS.md) | Actual test and benchmark results plus remaining qualification. | Distinguishes local Linux/SDK and hosted macOS/Ubuntu checks from unqualified owner-device/Praxis2/original-archive checks. |
| [MCP conformance](MCP-CONFORMANCE.md) | Latest protocol and actual client evidence. | Modern protocol, OAuth and explicit legacy HTTP checks; actual hosted apps and installed Praxis2 unverified. |
| [Import formats](IMPORT-FORMATS.md) | Inventoried legacy generations and conversion/fidelity limits. | Each input is accounted for; unsupported material is not silently promoted. |
| [Sync protocol](SYNC-PROTOCOL.md) | Bounded direct exchange and explicit recovery-origin admission. | Bounded automatic runner, persisted backoff, capacity pause, direct exchange and recovery evidence. |
| [Tracking plan](tracking/README.md) | Prepared backlog, dependencies, requirement coverage and future Linear setup. | Planning aid; does not override requirements or authorize implementation. |

## Organization and maintenance

- Keep product requirements in the PRD, decisions and rationale in the ADRs/decision register, and supporting evidence in the research ledger. Update the affected documents together when an accepted decision changes.
- A22/A23 preserve client-led processing and attribution; A24/L09–L12 put shared fields in the core and narrow the App to exploration and CRUD. Preserve Q6 automatic admission, Q8 owner-correction preference and legacy comment/job records. Q9's MCP+CLI-only scope is historical; host qualification remains separate. Keep FC01–FC08 planned until executed and do not relabel old LM evidence as new field/UI acceptance.
- Keep architecture source in `diagrams/`; show a readable view in the architecture document. Avoid creating competing diagram versions with different scope.
- Keep tracking artifacts in `tracking/`. The structured plan is the maintained backlog source; its Markdown view is a readable export. These are prepared items, not actual Linear issue IDs or live statuses.
- Preserve C01–C30/M01–M25 and ADR identifiers when changing scope; classify later work explicitly. Corporate tenancy, product encryption and transitive mesh must not become accidental personal-v1 gates.
- Keep current unknowns visible. Q6 automatic acceptance and Q7–Q10 are confirmed; record remaining engineering and access gaps explicitly. A proposed default or completed documentation snapshot is not an accepted implementation design.
- Reconcile the historical planning Pages with accepted repository decisions without copying restricted source content into this public repository. Private source locations remain in the private working prompt.
- Record test/benchmark evidence only when it actually exists. Documentation organization, backlog preparation and supplied measurements are not product qualification.

No external tracker, assignment or real-data authorization is implied by this documentation structure. Implementation approval is the owner's explicit 7 November 2026 instruction.
