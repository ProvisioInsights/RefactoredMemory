# Research, evidence and scope reconciliation

Updated 7 November 2026. This is a public-safe research ledger and release-scope reconciliation. Keep confidential evidence and original private documents in their authorized source systems. No private source excerpts, source paths, credentials or personal datasets are published here.

## Evidence inspected

| Source | What is supported | Limitation |
| --- | --- | --- |
| Historical PRD, ADR and storage/research planning Pages | Detailed temporal model, original requirements, future privacy vision and reported experiments; reconciled to personal v1. | Planning documents are not implementation/test results. Access-controlled links remain in the private working prompt. |
| [LivingAtlas](https://github.com/ProvisioInsights/LivingAtlas) metadata, README and selected source at `e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d` | Existing assertion query scans the assertion collection and separately filters valid/recorded time; useful baseline semantics and history. | Selected-source review; no full implementation audit or test execution in this task. |
| Authorized legacy/current client memory architecture and selected implementation | Existing client memory/authority assumptions need reconciliation with RefactoredMemory and its required MCP boundary. | No private code copied; no end-to-end client integration claimed. |
| Official [MCP specification repository](https://github.com/modelcontextprotocol/modelcontextprotocol) at `cf59bb0d8b43e711420f5f7313aa6cca3f1e1898` | Documentation labels 2026-07-28 latest; versioning and transport specifications inspected. | Rechecked during implementation; modern protocol fixtures and independent SDK evidence are recorded separately in MCP-CONFORMANCE.md. |
| Benchmark archive referenced by historical evaluation | Archive identity, ZIP MIME and metadata confirmed. | Raw report/code/results were not unpacked through an authorized compatible tool; no independent rerun. |

The direct MCP website was unavailable from the selected environment during the initial check; the official GitHub specification supplied the cited evidence. Published memory-research references retained in the historical evaluation are research leads; do not represent them as freshly revalidated by this scope update.

## Historical benchmark boundary

At 110,000 assertions, the supplied M5 Max experiment reports Atlas median selective-read latency of **0.6814 ms current / 0.6845 ms historical**, and indexed SQLite **0.0377 / 0.0320 ms**. It reports 1,200 matching assertion-content comparisons and six reopen/count/idempotent-retry checks.

These are attributed supplied results. SQLite omitted coverage metadata and the full contract. Equivalent writes, concurrency, synchronization, failure recovery and scale-out were not compared. Reopen/retry checks are not crash/power-loss qualification. Keep this test distinct from the standalone SQLite and JavaScript reference experiments. The initial implementation selects SQLite for its transactional durability, portability, backup support and small operational footprint; these historical measurements do not establish that selection as a performance winner.

## Reconciled contradictions

| Earlier wording | Current interpretation |
| --- | --- |
| Personal plus two corporate domains required in the initial proof | Corporate/multi-tenant C22/M17 deferred. One personal owner now; organizations can be subjects of facts. |
| Mandatory privacy/custody foundations before the useful release | Personal access protection remains; product encryption, key custody and corporate recovery are later. |
| MCP as optional adapter | C24/M19 require latest-stable MCP and actual Praxis2 plus independent-client integration. |
| Unconditional broader mesh | Two writable personal peers and direct sync required; third-hop relay mesh is later. |
| Mac plus Linux merely a default | Confirmed first peer pair. This does not authorize provisioning a new remote host. |
| Initial importer and legacy migration optional | Markdown/Logseq and data from previous LivingAtlas runs are required v1 scope. |
| All former acceptance IDs block v1 | Retain IDs with explicit personal, later or conditional classification; do not discard temporal semantics. |

## Remaining research and source qualification

Inventory the actual available LivingAtlas source generations, formats and outputs. Determine conversions and fidelity limitations, preserving originals. Research should prioritize the personal graph, required MCP and two-peer sync contract, import compatibility, durable storage and practical operations. Compare eligible backends against the same complete personal-v1 semantics and durability assumptions.

Memory research from Apple, OpenAI, Anthropic and others may motivate later retrieval/consolidation experiments. Include source attribution, stale/corrected knowledge, evaluation quality and total maintenance cost. Do not select a mechanism solely from provider claims or make enterprise/privacy research completion a prerequisite for personal v1.

Q6 now confirms automatic acceptance of model-inferred additions within configured client/agent grants, without per-item human review; source/evidence, attribution, uncertainty, conflicts and correction history remain required. Acceptance is not human verification or established truth. Q7–Q10 are now accepted: proactive capture, preferred explicit owner corrections with conflicts retained, MCP/CLI first, and the three day-one tasks. The owner explicitly said “Proceed” on 7 November 2026. Implementation and synthetic qualification are authorized; deployments, live data and credential changes remain separately controlled. See CONTRACT.md for selected engineering decisions and ACCEPTANCE-RESULTS.md for their measured limits.


## Implementation evidence added after authorization

The initial engine now implements the complete personal operation path in Python/SQLite, including transactional admission, source-linked temporal query, direct signed synchronization, and verified replay recovery. The synthetic benchmark measures this actual implementation and records its source digest and raw samples; see [acceptance evidence](ACCEPTANCE-RESULTS.md). It is not a comparative engine experiment.

The current legacy-code inventory identified old plaintext/encrypted object envelopes and journal/snapshot forms, plus newer committed assertion and identity segment formats. [Import formats](IMPORT-FORMATS.md) records which can be structurally converted and which remain preserved-only or unavailable. Original personal archives and their keys were not used.

Official MCP latest-stable requirements were rechecked. An already installed independent Python SDK exercised the real server without an installation. Praxis2 is the confirmed target. Read-only client inspection identified current protocol wire compatibility and provider-specific onboarding restrictions; actual installed Praxis2 use remains unverified. The owner explicitly prohibits any changes to either Praxis repository. All implementation stays in RefactoredMemory; future connection validation requires an available compatible configuration, not client changes by this work.
