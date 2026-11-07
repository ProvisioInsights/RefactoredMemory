# Research, evidence and scope reconciliation

Updated 7 November 2026. This is a public-safe research ledger and release-scope reconciliation. Keep confidential evidence and original private documents in their authorized source systems. No private source excerpts, source paths, credentials or personal datasets are published here.

## Evidence inspected

| Source | What is supported | Limitation |
| --- | --- | --- |
| Historical PRD, ADR and storage/research planning Pages | Detailed temporal model, original requirements, future privacy vision and reported experiments; reconciled to personal v1. | Planning documents are not implementation/test results. Access-controlled links remain in the private working prompt. |
| [LivingAtlas](https://github.com/ProvisioInsights/LivingAtlas) metadata, README and selected source at `e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d` | Existing assertion query scans the assertion collection and separately filters valid/recorded time; useful baseline semantics and history. | Selected-source review; no full implementation audit or test execution in this task. |
| Authorized legacy/current client memory architecture and selected implementation | Existing client memory/authority assumptions need reconciliation with RefactoredMemory and its required MCP boundary. | No private code copied; no end-to-end client integration claimed. |
| Official [MCP specification repository](https://github.com/modelcontextprotocol/modelcontextprotocol) at `cf59bb0d8b43e711420f5f7313aa6cca3f1e1898` | Documentation labels 2026-07-28 latest; versioning and transport specifications inspected. | Recheck at implementation; no SDK or client conformance result yet. |
| Benchmark archive referenced by historical evaluation | Archive identity, ZIP MIME and metadata confirmed. | Raw report/code/results were not unpacked through an authorized compatible tool; no independent rerun. |

The direct MCP website was unavailable from the selected environment during the initial check; the official GitHub specification supplied the cited evidence. Published memory-research references retained in the historical evaluation are research leads; do not represent them as freshly revalidated by this scope update.

## Historical benchmark boundary

At 110,000 assertions, the supplied M5 Max experiment reports Atlas median selective-read latency of **0.6814 ms current / 0.6845 ms historical**, and indexed SQLite **0.0377 / 0.0320 ms**. It reports 1,200 matching assertion-content comparisons and six reopen/count/idempotent-retry checks.

These are attributed supplied results. SQLite omitted coverage metadata and the full contract. Equivalent writes, concurrency, synchronization, failure recovery and scale-out were not compared. Reopen/retry checks are not crash/power-loss qualification. Keep this test distinct from the standalone SQLite and JavaScript reference experiments. SQLite remains a candidate; no engine is selected.

## Reconciled contradictions

| Earlier wording | Current interpretation |
| --- | --- |
| Personal plus two corporate domains required in the initial proof | Corporate/multi-tenant C22/M17 deferred. One personal owner now; organizations can be subjects of facts. |
| Mandatory privacy/custody foundations before the useful release | Personal access protection remains; product encryption, key custody and corporate recovery are later. |
| MCP as optional adapter | C24/M19 require latest-stable MCP and actual Praxis plus independent-client integration. |
| Unconditional broader mesh | Two writable personal peers and direct sync required; third-hop relay mesh is later. |
| Mac plus Linux merely a default | Confirmed first peer pair. This does not authorize provisioning a new remote host. |
| Initial importer and legacy migration optional | Markdown/Logseq and data from previous LivingAtlas runs are required v1 scope. |
| All former acceptance IDs block v1 | Retain IDs with explicit personal, later or conditional classification; do not discard temporal semantics. |

## Research still needed before implementation

Inventory the actual available LivingAtlas source generations, formats and outputs. Determine conversions and fidelity limitations, preserving originals. Research should prioritize the personal graph, required MCP and two-peer sync contract, import compatibility, durable storage and practical operations. Compare eligible backends against the same complete personal-v1 semantics and durability assumptions.

Memory research from Apple, OpenAI, Anthropic and others may motivate later retrieval/consolidation experiments. Include source attribution, stale/corrected knowledge, evaluation quality and total maintenance cost. Do not select a mechanism solely from provider claims or make enterprise/privacy research completion a prerequisite for personal v1.

The owner's inferred-write policy is still open. The documentation set is a reconciled scope baseline, not a completed architecture decision gate. No product code, deployments, keys, real-data ingestion or migration were changed by this update.
