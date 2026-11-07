# RefactoredMemory tracking charter

## Intended home

- Workspace: Provisio Insights.
- Team: RefactoredMemory, proposed key RFM. External setup is paused by the owner; no Linear team, projects or issues were created. No manual team-creation action is currently needed.
- Repository: https://github.com/ProvisioInsights/RefactoredMemory
- Source baseline: documentation commit `7303a93aeed3b15f24dc03b411d043404100b13f`.

## Project structure

1. **Research and documentation gate** — source review, legacy-data inventory, the recorded Q6 automatic-acceptance decision, pending Q7–Q10 choices, architecture/stack/MCP compatibility decisions, complete acceptance mapping, reconciled docs, and explicit owner authorization to proceed.
2. **Personal knowledge store v1** — personal temporal graph, durable storage and recovery, authenticated Mac/Linux offline peers, direct synchronization, required MCP clients, Markdown/Logseq import, migration from prior LivingAtlas runs, qualification and operating instructions.
3. **Later roadmap** — corporate/multi-tenant ownership, encrypted product profiles/custody, transitive relay mesh, advanced memory and larger deployment/scale. These do not block v1.

Use milestones to group each project's deliverables. Use issue dependencies for prerequisites and the implementation gate. Avoid artificial schedules, cycles, estimates or assignees until agreed.

## Authority and gate

Repository documentation is authoritative, and the repository backlog retains the planning record while Linear is paused. If external tracking is later activated, Linear can record execution/progress. Keep accepted scope and affected requirement/test IDs reconciled without making the tracker a source of new requirements.

External tracking creation is paused until a new owner request. Repository planning and documentation can continue; Linear is not a readiness prerequisite. No product implementation is authorized by this tracking plan. Every v1 implementation issue must be blocked by the explicit **owner “proceed”** gate, which depends on completed research/documentation readiness. Closing design issues or answering Q6 does not itself grant implementation permission.

R01 records the completed documentation baseline and R03 records the accepted Q6 policy; both may be Done as documentation evidence only. Q6 permits automatic acceptance of model-inferred additions within configured client/agent grants without per-item human review. Enforcement and product tests remain unimplemented/unexecuted; source inspection and supplied benchmark claims are not product qualification. Q7 capture initiative, Q8 owner-correction/claim preference, Q9 MCP/CLI versus a simple browser UI, and Q10 three day-one tasks remain unanswered. Track these in the existing contract/readiness issues rather than reopening Q6. Deferred issues remain in the later-roadmap project.

## Issue content

Each issue should record the intended outcome, scope, observable acceptance criteria, relevant C/M/A identifiers, canonical document links, dependencies, and known evidence/access limits. Record reproducible test or review evidence when completing an issue. An unavailable client, missing legacy source or unverified result is a gap rather than a pass.

## V1 boundaries

One personal owner; Mac plus owner-controlled Linux VM/container, both offline writable with synchronization. Required latest-stable MCP integration with Praxis and an independent MCP client. Required Markdown/Logseq import and migration from discovered prior LivingAtlas source generations, preserving originals, provenance, temporal meanings, lineage and ID mappings.

Automatically accepted inferences retain source/evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history. Acceptance is not human verification or established truth, and neither source content nor a successful write can create or broaden a grant. Q6 does not decide when capture is triggered, which conflicting claim is preferred, or the owner interface. A simple browser UI remains a pending Q9 v1 choice; advanced graphical/cinematic exploration remains later.

Corporate tenants, personal-versus-corporate custody, product content encryption, protected compute and transitive relay mesh are later. Basic authentication, scoped clients/peers, secure remote transport and safe local access remain v1. Existing encrypted legacy inputs may need their original approved keys; this does not add a new encryption platform to v1.

Development/test fixtures are synthetic-only. Live data use, key access, external deployment and installation remain subject to the established authorizations. Do not put private datasets, credentials or private source excerpts in issues, logs or public repository files.

## Completion checks after external tracking is resumed

- Correct workspace and team verified; no duplicate projects/issues.
- All v1 requirements and applicable acceptance cases have an issue owner in the tracking map; later IDs are explicitly mapped to later work.
- Required issue dependencies and the proceed gate exist, with no dependency cycles.
- Project/milestone/status membership is verified by readback.
- Canonical documents and tracking links are discoverable from the team/project overview and repository.
