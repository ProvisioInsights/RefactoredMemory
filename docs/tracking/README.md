# Repository tracking and paused Linear setup

**Status: Linear setup is paused at the owner's request.** No Linear team, projects or issues were created in this work. No manual team-creation step is currently needed. Resume external setup only when the owner asks.

The repository keeps the work breakdown available while coordinated implementation proceeds. Linear availability is not a readiness gate. The owner answered Q7–Q10 and explicitly said **“Proceed” on 7 November 2026**. R09 records that authorization; remaining detailed-contract, evidence and qualification work stays open.

## Prepared artifacts

- [Readable backlog and coverage map](linear-plan.md): 44 tracked items across research/documentation, personal v1 and the later roadmap, covering C01–C25 and M01–M20.
- [Structured backlog](linear-plan.json): maintained planning data for the same items, dependencies, milestones and acceptance mappings.
- [Tracking charter](charter.md): authority, scope, completion rules and how to activate tracking later.

The structured backlog is the maintained source for tracking data; regenerate the Markdown view when it changes. Product authority remains with the [PRD](../PRD.md), [ADRs](../ADRS.md) and [decision register](../DECISIONS.md). A tracking change cannot silently amend those documents.

Praxis2 is the confirmed client target. Require true latest-published-stable MCP support in RefactoredMemory. Do not modify either Praxis or Praxis2 repository; client modifications are not prerequisites for MCP support. Installed Praxis2 integration remains unexecuted and is recorded separately from independent SDK evidence.

## Current state

| Area | State |
| --- | --- |
| Personal-v1 scope documentation | Baseline published; further design/evidence work remains. |
| Q6 inferred-write acceptance | Accepted and recorded under R03: automatic acceptance within configured grants, without per-item human review. Implementation and synthetic Linux evidence are linked from the affected delivery items; policy recording alone does not prove enforcement. |
| Q7 capture initiative | Accepted: proactive capture by configured clients/agents within their grants. |
| Q8 preferred-claim handling | Accepted: prefer explicit owner corrections while preserving conflicting claims, evidence and history. |
| Q9 owner interface | Accepted: MCP plus CLI first; no browser UI in v1. |
| Q10 day-one outcomes | Accepted: project decisions and why; relationships and evidence; changes since last month. |
| Research and documentation readiness | R06/R08 remain open for the detailed contract/evidence criteria; ADR A17 selects the Python/SQLite/direct-sync stack. |
| Product implementation | Authorized by explicit “Proceed” on 7 November 2026, recorded in R09. |
| Linear setup item | Deferred by owner; not a v1 blocker. |
| V1 implementation work | Core, MCP, import, direct sync and CLI implemented; full-criterion issues remain In Progress. Local Linux: all 86 tests passed, including both SDK tests. Hosted macOS/Ubuntu passed the 83-test suite at `ebb73d2`; hosted macOS skipped two optional SDK tests. The owner’s actual Mac/Linux pair, installed Praxis2 and full original archives remain unqualified. |
| Corporate/encryption/broader-mesh work | Separate later roadmap; does not block v1. |

Q6 retains source/evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history. Automatic acceptance is not human verification or established truth and cannot create or widen grants. Q7–Q10 now settle proactive capture, preferred corrections, MCP/CLI and day-one tasks. R01/R03 are completed documentation/policy records and R09 is completed authorization recording only. R06/R08 and full product qualifications remain open. C25/M20 map all three day-one tasks to existing items; A17 maps the selected runtime/storage/sync direction. Recorded local Linux and hosted macOS/Ubuntu results are evidence of exercised behavior, not qualification of the owner’s actual peer pair or complete release acceptance.

Evidence: [acceptance results](../ACCEPTANCE-RESULTS.md), [MCP conformance and client matrix](../MCP-CONFORMANCE.md), [import fidelity](../IMPORT-FORMATS.md), [sync protocol](../SYNC-PROTOCOL.md) and [runbook](../RUNBOOK.md). The owner’s actual Mac/Linux pair, installed Praxis2 application use and full original-archive migration remain unverified; no live-data import or external deployment is claimed.

Planning keys such as `R03` and `G01` are internal references, not issued Linear identifiers. `state` fields describe planned or evidenced repository-work status, not a remote Linear object. No estimates, due dates, cycles or assignees have been invented.

## When external tracking is resumed

Recheck the intended workspace and existing team/projects/issues before creating anything. Reuse matching objects, map planning keys to actual IDs/URLs, verify dependencies and coverage, and only then mark external setup complete. Preserve the recorded implementation authorization, deferred scope and evidence limits. Do not begin this process until requested.
