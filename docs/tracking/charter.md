# RefactoredMemory tracking charter

## Intended home

- Workspace: Provisio Insights.
- Team: RefactoredMemory, proposed key RFM. External setup is paused by the owner; no Linear team, projects or issues were created. No manual team-creation action is currently needed.
- Repository: https://github.com/ProvisioInsights/RefactoredMemory
- Source baseline: documentation commit `7303a93aeed3b15f24dc03b411d043404100b13f`.

## Project structure

1. **Research and documentation gate** — source review, legacy-data inventory, the recorded Q6 automatic-acceptance decision, accepted Q7–Q10 choices, architecture/stack/MCP compatibility decisions, complete acceptance mapping, reconciled docs, and explicit owner authorization to proceed.
2. **Personal knowledge store v1** — personal temporal graph, durable storage and recovery, authenticated Mac/Linux offline peers, direct synchronization, required MCP clients, Markdown/Logseq import, migration from prior LivingAtlas runs, qualification and operating instructions.
3. **Later roadmap** — corporate/multi-tenant ownership, encrypted product profiles/custody, transitive relay mesh, advanced memory and larger deployment/scale. These do not block v1.

Use milestones to group each project's deliverables. Use issue dependencies for prerequisites and the implementation gate. Avoid artificial schedules, cycles, estimates or assignees until agreed.

## Authority and gate

Repository documentation is authoritative, and the repository backlog retains the planning record while Linear is paused. If external tracking is later activated, Linear can record execution/progress. Keep accepted scope and affected requirement/test IDs reconciled without making the tracker a source of new requirements.

External tracking creation is paused until a new owner request. Linear is not a readiness prerequisite. The owner explicitly said **“Proceed” on 7 November 2026** after answering Q7–Q10; personal-v1 implementation is authorized. Every v1 issue retains its direct dependency on R09, which now records that received authorization. R09 is separate from unfinished R06/R08 contract/readiness and source/client evidence work; receiving permission does not mark those criteria or product qualifications passed. Reconcile the accepted answers across the docs before core coding, then continue without requesting the same authorization again.

R01 records the completed documentation baseline, R03 records the accepted Q6 policy and R09 records explicit implementation authorization; Done means those records only. Q6 permits automatic acceptance of model-inferred additions within configured client/agent grants without per-item human review. Core, MCP, import, direct-sync and CLI implementations have synthetic Linux evidence, with 82 tests reported passing in the current coordinated run, including an independent real MCP SDK client. Delivery items remain In Progress against their full criteria. Actual Mac, actual Praxis and complete original-archive qualification remain incomplete; no complete release acceptance is claimed. Source inspection and supplied benchmark claims are not product qualification. Q7 authorizes proactive capture within grants; Q8 prefers explicit owner corrections while preserving conflicts/evidence/history; Q9 selects MCP plus CLI without browser UI; Q10 requires project decisions/why, relationships/evidence and changes since last month. Keep detailed-contract and readiness criteria open until actually verified. Deferred issues remain in the later-roadmap project.

## Issue content

Each issue should record the intended outcome, scope, observable acceptance criteria, relevant C/M/A identifiers, canonical document links, dependencies, and known evidence/access limits. Record reproducible test or review evidence when completing an issue. An unavailable client, missing legacy source or unverified result is a gap rather than a pass.

## V1 boundaries

One personal owner; Mac plus owner-controlled Linux VM/container, both offline writable with synchronization. Required latest-stable MCP integration with Praxis and an independent MCP client. Required Markdown/Logseq import and migration from discovered prior LivingAtlas source generations, preserving originals, provenance, temporal meanings, lineage and ID mappings.

Automatically accepted inferences retain source/evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history. Acceptance is not human verification or established truth, and neither source content nor a successful write can create or broaden a grant. Under Q7, configured clients/agents may proactively capture useful knowledge within their grants, without broadening source access or authorizing arbitrary monitoring/separate extraction services. Under Q8, explicit owner corrections are preferred while alternatives, evidence and history remain inspectable; attributed resolutions reference the heads considered. MCP plus CLI is the v1 surface under Q9; browser UI and richer graphical exploration remain later. All three Q10 workflows map to C25/M20 and existing integration/inspection/qualification items. ADR A17 records the selected Python/SQLite/direct-sync implementation; technology selection is not a platform-qualification pass.

Corporate tenants, personal-versus-corporate custody, product content encryption, protected compute and transitive relay mesh are later. Basic authentication, scoped clients/peers, secure remote transport and safe local access remain v1. Existing encrypted legacy inputs may need their original approved keys; this does not add a new encryption platform to v1.

Development/test fixtures are synthetic-only. Live data use, key access, external deployment and installation remain subject to the established authorizations. Do not put private datasets, credentials or private source excerpts in issues, logs or public repository files.

## Evidence records

Use [acceptance results](../ACCEPTANCE-RESULTS.md), [MCP conformance](../MCP-CONFORMANCE.md), [import fidelity](../IMPORT-FORMATS.md), [sync protocol](../SYNC-PROTOCOL.md) and the [runbook](../RUNBOOK.md) for exercised behavior and remaining boundaries. A current aggregate test count does not turn an unavailable host, client or archive into a passed requirement.

## Completion checks after external tracking is resumed

- Correct workspace and team verified; no duplicate projects/issues.
- All C01–C25 requirements and M01–M20 acceptance cases have an issue owner in the tracking map; later IDs are explicitly mapped to later work.
- Required issue dependencies and the proceed gate exist, with no dependency cycles.
- Project/milestone/status membership is verified by readback.
- Canonical documents and tracking links are discoverable from the team/project overview and repository.
