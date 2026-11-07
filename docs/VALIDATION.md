# Personal v1 validation and migration

This matrix defines qualification requirements. Actual executed results are recorded in [ACCEPTANCE-RESULTS.md](ACCEPTANCE-RESULTS.md), [MCP-CONFORMANCE.md](MCP-CONFORMANCE.md) and [SYNC-PROTOCOL.md](SYNC-PROTOCOL.md). The owner explicitly authorized implementation on 7 November 2026; new product code and tests are in scope. Tests, benchmarks and demonstration files are synthetic-only.

| V1 area | Required evidence | Historical mapping |
| --- | --- | --- |
| Personal graph | Create entities, sourced facts/relationships and unresolved observations; inspect after restart. | M01 |
| Two time axes | Independently query world time and peer-scoped knowledge; retain earlier beliefs and unknown/approximate time. Same semantics in search/traversal/history. | M13–M16 |
| Semantic actions | Distinguish correction, retraction, invalidation and reinstatement from deletion. Preserve source disputes and concurrent branches. | M04, M14–M16 |
| Personal authority | Reject malformed/unauthorized calls and peer admission; current client authority applies to historical queries; source text cannot expand grants. | M02, M09, personal M18 |
| Two-peer offline sync | Mac and Linux both write while disconnected. Vary delivery order, duplicates, gaps, missing dependencies and clock skew; compare semantic answers at shared frontiers. | M03–M05, relevant M09 |
| Recovery and local lifecycle | Fail around durable writes, receipt/application and checkpoints; restart, rebuild indexes, restore, and test deletion/stale rejoin without resurrection or invented progress. | M06, M07, relevant M10/M16/M18 |
| Markdown/Logseq import | Preserve source versions, parse supported facts conservatively, account for errors/unresolved records, reject unsafe source boundaries and retry unchanged/modified inputs safely. | C14/M11 |
| Prior LivingAtlas migration | Exercise fixtures for every supported inventoried generation; preserve IDs/mappings, world/knowledge meanings, provenance, lineage and declared query equivalence; verify accounting/rollback. | C14/M11 |
| MCP | Actual Praxis2 and an independent client; protocol, authority, schemas, temporal/provenance fidelity, retries, errors and transport behavior. | C24/M19 |
| Personal usability/performance | Bounded traversal, evidence/history/sync inspection, honest coverage, cold open/rebuild, acknowledged writes, read latency and storage/transfer cost on declared workloads. | M12 and applicable personal requirements |

M08 third-hop mesh is later; direct two-peer sync is required now. C22/M17 multi-organization fixtures and P01–P06 cryptographic/enterprise profiles are later. M10/M18 do not silently import corporate policy-epoch or encryption requirements into v1. The detailed PRD and ADRs govern the preserved legacy IDs.

## Import accounting and approval boundary

Inventory prior source artifacts read-only before selecting adapters. Test every claimed supported generation with isolated synthetic fixtures, including lossless opaque preservation when structured conversion is unsupported. Report missing/corrupt inputs, unknown fidelity and fields not represented by the new schema. An import is not complete merely because counts match.

Maintain original backups, stable source identities, repeat-safe import manifests and explicit ID mappings. Compare meaningful temporal/provenance answers before accepting a migration. Never overwrite the original archive as part of qualification. When original input is encrypted, test the adapter with synthetic keys and require approved original key access for any later live run. Do not request secrets in chat or commit them.

The requested v1 importer does not authorize using real personal data now. Prepare a concrete live-import plan and reviewable source inventory before requesting the separate data authorization. Q6 confirms automatic acceptance within configured client/agent grants, with no per-item human review. Test permitted automatic additions, rejection outside the grant, source-text attempts to expand authority, preserved evidence/actor/model/derivation attribution and uncertainty, and retained correction/conflict history. Acceptance must not be labelled human verification or established truth. Q7 requires proactive capture; Q8 requires preferred authenticated owner corrections with conflicts retained. Q9 selects MCP/CLI and Q10 requires all three day-one tasks: project decisions/why, relationship evidence, and recent changes.

## Performance evidence

Pin source commits, runtime/engine versions, machine/OS/filesystem, durability settings, fixtures, indexes, cache state, group sizes and sample method. Test correctness and comparable durability before ranking latency. Keep independent workloads/runs separate; report p50/p95, throughput, memory/storage, startup/rebuild and relevant transfer/recovery costs. A process kill is not physical-power-loss proof.

The historical 110,000-assertion selective-read benchmark favors the exercised indexed SQLite path, but does not establish full semantic/API equivalence, comparative writes, sync, concurrency or scale-out. Its raw ZIP has not been independently inspected in this planning work. Synthetic Linux qualification and real independent SDK workflows have now run; consult the evidence reports for exact results and unqualified Mac/Praxis2/original-archive boundaries.
