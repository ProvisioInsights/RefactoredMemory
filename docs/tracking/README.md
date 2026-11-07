# Repository tracking and paused Linear setup

**Status: Linear setup is paused at the owner's request.** No Linear team, projects or issues were created in this work. No manual team-creation step is currently needed. Resume external setup only when the owner asks.

The repository keeps the prepared work breakdown available while research and documentation continue. Linear availability is not a readiness gate. The separate explicit owner **“proceed”** requirement for product implementation remains in force.

## Prepared artifacts

- [Readable backlog and coverage map](linear-plan.md): 44 planned items across research/documentation, personal v1 and the later roadmap.
- [Structured backlog](linear-plan.json): maintained planning data for the same items, dependencies, milestones and acceptance mappings.
- [Tracking charter](charter.md): authority, scope, completion rules and how to activate tracking later.

The structured backlog is the maintained source for tracking data; regenerate the Markdown view when it changes. Product authority remains with the [PRD](../PRD.md), [ADRs](../ADRS.md) and [decision register](../DECISIONS.md). A tracking change cannot silently amend those documents.

## Current state

| Area | State |
| --- | --- |
| Personal-v1 scope documentation | Baseline published; further design/evidence work remains. |
| Q6 inferred-write acceptance | Accepted and recorded under R03: automatic acceptance within configured grants, without per-item human review. No enforcement implementation or tests are claimed. |
| Q7 capture initiative | Awaiting owner answer: proactive capture versus explicit requests. |
| Q8 preferred-claim handling | Awaiting owner answer: owner-correction preference versus competing claims without a preferred result. |
| Q9 owner interface | Awaiting owner answer: MCP/CLI only versus a simple browser UI. |
| Q10 day-one outcomes | Awaiting owner answer: three concrete user tasks to prove end to end. |
| Research and documentation readiness | Not complete. |
| Product implementation | Not authorized; explicit “proceed” still required. |
| Linear setup item | Deferred by owner; not a v1 blocker. |
| V1 implementation work | Prepared backlog only; each item retains the explicit proceed dependency. |
| Corporate/encryption/broader-mesh work | Separate later roadmap; does not block v1. |

Q6 retains source/evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history. Automatic acceptance is not human verification or established truth and cannot create or widen grants. It does not settle Q7 capture triggers or the other pending choices. R01 and R03 are completed documentation/decision records only; every product implementation item and the explicit R09 proceed gate remain unfinished.

Planning keys such as `R03` and `G01` are internal references, not issued Linear identifiers. `state` fields describe planned or evidenced repository-work status, not a remote Linear object. No estimates, due dates, cycles or assignees have been invented.

## When external tracking is resumed

Recheck the intended workspace and existing team/projects/issues before creating anything. Reuse matching objects, map planning keys to actual IDs/URLs, verify dependencies and coverage, and only then mark external setup complete. Preserve the explicit proceed gate, deferred scope and evidence limits. Do not begin this process until requested.
