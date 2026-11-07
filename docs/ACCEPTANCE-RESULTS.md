# Personal v1 acceptance evidence

This report records the implemented personal core and NAS/OAuth/automatic-sync extension. Current extension evidence appears first; earlier measurements remain historical and are not silently relabelled as new results.

All tests, examples and benchmarks in this record use synthetic data. Executed Linux checks are recorded separately from requirements that still need the owner's Mac, actual application access or original legacy artifacts. Passing a synthetic fixture does not establish those unavailable results.

## NAS extension local qualification

On 7 November 2026, **146 tests passed in 28.911 seconds with no skips** in the attached Linux workspace (Python 3.12.14, SQLite 3.53.1). [Raw native output](results/nas-linux-unittest.txt) includes the 86 baseline tests plus 15 OAuth, 9 HTTP-profile, 16 scheduler, 12 NAS/CLI/audit and 8 capacity tests. The three synthetic day-one demonstrations also ran successfully.

The runtime sources are committed at `a0ff34b8a7c64889e6110f878ddd8c8d454e7c84`; their SHA-256 is `2ad9d8ddd1954ae25b426e4d242f7d6e34aab334b8d25ecf78c51e2c4537a169` using sorted package filenames, NUL separators and file bytes. The independently hashed package inside the tested Docker image matches that digest. Documentation and deployment artifacts were still being finalized during the run.

| Extension | Executed evidence | Boundary |
| --- | --- | --- |
| OAuth | Real RS256 signatures; pinned issuer/audience; <=300-second lifetime; token type, subject/client and local grant checks; immediate local revocation; key rotation; unsafe files and forged tokens refused. | No live provider account connection. |
| MCP HTTP | Strict modern protocol plus explicitly enabled 2025-11-25; actual MCP SDK 1.29 HTTP capture/retry/query/evidence; protected-resource metadata and challenges. | SDK interoperability is not actual ChatGPT/Claude/Praxis2 acceptance. |
| Public/private separation | Real TLS subprocess tests and container tests keep OAuth MCP separate from peer-only sync; public routes do not expose sync or administration. | NAS routing/firewall rules still require device tests. |
| Automatic sync | Persisted Retry-After/backoff, private token reload, exclusive scheduler lock, safe status paths, cancellation, separate-process exchange and resume without duplicate writes. | Two direct peers; no transitive mesh or selective replication. |
| Capacity and import | Local/incoming write refusal, full transaction rollback, real SQLite pager-full failure, readable existing data, backup-space admission, import pause reporting and nonzero partial/failed exit. | Conservative guards are not disk quotas or a guarantee against concurrent external disk consumption. |
| Audit | Bounded private rotating JSONL, field allowlist, credential/content exclusion, collision/hardlink checks and static failure warning. | Operator must monitor runtime storage and maintain retention/backups. |

The full [Docker smoke test](../deploy/smoke_test.py) passed using real Keycloak/Postgres and TLS. It exercised authorization-code login with S256 PKCE, missing-PKCE/replayed-code rejection, access-token acceptance with ID/raw-grant rejection, sourced capture/query, bidirectional offline peer sync, persistence through container restart and current grant revocation. It inspected nonroot/read-only/capability/mount restrictions and verified a forbidden connection from memory into the separate authentication network. All disposable test containers, networks, volumes and private credentials were removed. [Raw container evidence](results/nas-docker-smoke.json) identifies images and commands. Both Cloudflare templates validated offline; no tunnel was published.

The container test is a reproducible local integration test, not a NAS installation or general penetration test. No actual DSM/VLAN/IPv6, hardware failure, owner Mac or hosted client connection has been qualified. No real personal data was ingested.

### Hosted Ubuntu and macOS qualification

[The hosted CI run](https://github.com/ProvisioInsights/RefactoredMemory/actions/runs/42411467535) passed at `73ab9e8948de969854d74488445b6e37bf0175f0`: **146 tests without skips on each platform**, in 21.028 seconds on Ubuntu and 57.781 seconds on macOS. Both also passed the three synthetic demonstrations. Declared optional OAuth and independent MCP SDK dependencies were installed explicitly by CI. [Machine-readable summary](results/nas-hosted-ci.json).

The preceding macOS run found a test-only path comparison between `/var` and `/private/var`. The assertion now compares the expected canonical path; the runtime already pinned that configuration directory correctly. No runtime source changed for this correction. These hosted checks do not qualify the owner's actual Mac/NAS pair.

### Current contract benchmark

[Raw NAS-extension runtime benchmark](../benchmarks/results/nas-linux-1100.json) repeats the 1,100-entity contract workload and passes its correctness checks. It identifies the same runtime digest above. Core Store defaults are measured; this is not an OAuth, TLS, NAS-disk or end-to-end client benchmark. The shared Linux host also ran container qualification, so the timings do not establish a regression or improvement against earlier runs.

| Workload | p50 ms | p95 ms |
| --- | ---: | ---: |
| Acknowledged correction | 0.656 | 1.826 |
| Current subject lookup | 0.742 | 1.263 |
| Historical subject lookup | 0.711 | 3.064 |
| Text search | 123.347 | 261.129 |
| Four-hop traversal | 12.650 | 33.251 |

One signed in-process transfer of 55 operations took 163.900 ms; backup 12.322 ms, restore 148.365 ms, rebuild 67.021 ms and reopen 2.665 ms. These single measurements do not establish larger-store capacity or an engine winner. Text search remains a scan-oriented cost to measure against the owner's eventual corpus.

## Historical personal-core Linux run

The full suite passed **86 tests in 13.858 seconds**, with no skips, using `python -m unittest discover -s tests -v` on 7 November 2026. This includes 23 independent acceptance, 21 MCP, 18 sync, 16 importer, 5 real CLI subprocess and 3 additional storage-hardening tests. See the [raw unittest output](results/linux-unittest.txt). The runtime source digest matches the raw benchmark artifact linked below.

The first macOS CI run exposed normal parent-directory aliases in the importer and an opaque multiprocessing test startup failure. The importer now pins the canonical approved root while rejecting descendant symlinks; three new regressions cover those boundaries. The sync fixture now uses a plain independent interpreter subprocess with explicit readiness and failure diagnostics. Those diagnostics isolated startup at HTTP binding; the production listener now binds without the standard library's unnecessary reverse-DNS lookup, with a regression that forbids that lookup. The canonical-path repeat test uses the actual root returned by the plan, including macOS ancestor aliases. The subsequent [hosted Ubuntu and macOS CI run](https://github.com/ProvisioInsights/RefactoredMemory/actions/runs/42405593803) succeeded for both jobs at commit `ebb73d2baabb78ed52614ffd1ae98a3145392297`. The macOS job ran 83 tests in 48.517 seconds, with two optional independent-SDK tests skipped; those two SDK tests both passed in the local Linux run above. This CI evidence applies to that commit, before the richer MCP schema working-tree update measured below. Later CI results should be assessed separately.

The final local run also covers correction-reason validation and the published MCP tool schemas: malformed correction reasons are rejected, and the advertised schemas describe valid capture/correction payloads consistently with runtime validation. These regressions were added after the earlier 83-test hosted CI run; that earlier success is not presented as validation of the final schema changes.

The integrated run includes the installed independent MCP SDK, production HTTP/stdio paths, worker-isolated TLS handshakes, two separately writable peer processes, verified recovery, and the three selected day-one workflows. Actual owner's-Mac and installed-Praxis2 qualification remain open. Praxis2 is the application integration target. No edits to any Praxis repository are authorized or required for this RefactoredMemory server scope; connecting and exercising the installed Praxis2 application remains untested.

## Day-one user journeys

The owner selected all three workflows on 7 November 2026:

1. Retrieve a project's decisions and rationale, with source evidence and applicable time/history.
2. Explain how the owner knows a person using retained relationship paths and their sources.
3. Inspect what changed since last month or a named local knowledge position, including corrections without rewriting earlier knowledge.

Capture is proactive within configured client grants. Inferred additions are admitted without per-item human review. An explicit authenticated owner correction is preferred while contradictory evidence remains inspectable. MCP clients and command-line tools are the v1 inspection surface. The server does not independently monitor conversations or invoke a model.

## Independent acceptance results

Executed on 7 November 2026 in the provided Linux environment with Python 3.12.14 and SQLite 3.53.1:

```bash
python -m unittest discover -s tests -p test_acceptance.py -v
```

**23 tests passed in 0.571 seconds.** These tests exercise the public Store/Service boundary with independent synthetic fixtures; this count covers `test_acceptance.py`, not the separate MCP, import and synchronization suites.

| Evidence | Observed behavior | Requirement mapping |
| --- | --- | --- |
| Project decision and rationale | Current and earlier decision retain source links, model/actor attribution and explanation after restart. | M01, M12–M14 |
| Person/relationship path | Two-hop path retains the evidence for each edge. | M01, M12–M13 |
| Changes since last month | Receipt-time and explicit knowledge-position change queries return the expected operations. | M12–M16 |
| Owner correction and later inference | The explicit owner correction remains preferred; later contrary inference and earlier history remain visible. | M01, M14–M15 |
| Atomic invalid group and retry | Invalid dependent action leaves no partial projection or advanced knowledge position; identical request retry is idempotent and a changed retry is rejected. | M02, M05–M06 |
| Temporal selection | Half-open intervals, unknown/approximate bounds, invalidation versus retraction, and unavailable knowledge selectors behave distinctly. | M13–M16 |
| Same-group references | An assertion can name a predecessor appearing later in its atomic group. | M01, M05 |
| Concurrent identical reimport | Both peers converge deterministic attribution at a shared frontier while each earlier local-known view remains unchanged. Duplicate observations do not become independent corroboration. | M03, M05, M15–M16 |
| Historical traversal | A knowledge-position-zero traversal cannot expose an entity created later. | M13, M16 |
| Current authorization | Revocation denies historical reads; a write grant does not grant correction/admin scope; callers cannot forge an owner actor or human verification. Source instructions remain data. | M02, M18 |
| Deletion | Current administrative suppression applies to past-knowledge reads and graph paths. | M07, M18 |
| Restore | Restored graph has a fresh peer identity and no revived grants; missing journal history is rejected. New replica receipt/application times are current, while original replica positions/receipts remain separately attributed as inherited history. | M10, M16, M18 |
| Rebuild and abrupt process exit | Rebuilding preserves current/earlier answers; an acknowledged atomic group survives a subprocess's immediate `os._exit` without normal connection shutdown. | M06, M16 |

The independent regression fixtures exposed and then verified fixes for same-ID attribution convergence, out-of-order dependencies within an atomic group, future-entity leakage in historical traversal, and incomplete snapshot history. A process kill tests process-crash recovery; it does not prove physical power-loss durability.

The runnable example uses a temporary database by default and refuses to modify an existing database when a path is supplied:

```bash
python -m examples.synthetic_demo
```

Its output includes the current project decision, earlier belief, original/correction evidence, person-to-project path, changes since last month and changes since a named position. This command was executed successfully against the implementation.

## Benchmark reproduction

```bash
python -m benchmarks.personal_store --entities 1100 --samples 31 --output /tmp/refactoredmemory-benchmark-linux.json
```

The benchmark runs the actual graph contract with 1,100 synthetic entities/assertions, 31 owner corrections, 20 relationship edges, 31 samples per read workload and 50-entity seed transactions. It includes current and historical subject queries, text search, four-hop traversal, acknowledged writes, signed operation transfer, rebuilding, backup, fresh-identity restore and reopen. It verifies answers before reporting timings. Raw output records individual samples, p50/p95, Python/SQLite/platform, source digest, Git state, workload/cache assumptions and observed database/WAL sizes.

The final development run at `2026-11-07T19:28:49.236722+00:00` passed the benchmark's correctness checks. [Raw measurements and source identity](../benchmarks/results/personal-linux-1100.json) include all samples and the working-tree source digest; the Git commit identifies the preceding commit, while the digest identifies the measured working-tree code. The digest `82c9130acd28cfb753393290973657aa37095b2e32979c8f71ec6c62c452f279` was verified against the Python sources of that historical run, before the NAS extension. This shared Linux environment was not a dedicated performance host. The benchmark ran separately from this agent's acceptance tests, but no machine-wide isolation or CPU-frequency control is claimed.

| Workload | p50 ms | p95 ms |
| --- | ---: | ---: |
| Acknowledged single correction | 0.665 | 1.467 |
| Current subject lookup | 0.741 | 2.049 |
| Historical subject lookup | 0.714 | 1.108 |
| Text search | 107.191 | 124.376 |
| Four-hop traversal | 11.998 | 15.527 |

One signed in-process transfer of 55 operations (339,352 serialized bytes) took **130.427 ms**. Rebuild took **53.496 ms**, backup **9.169 ms**, verified fresh-identity restore **152.143 ms**, and reopen **1.585 ms**. These are single operation measurements, not latency distributions. Signed transfer excludes HTTP/TLS and network delay. The observed main database was 1,179,648 bytes with 4,169,472 bytes in WAL at measurement time.

Text search and traversal remain visibly more expensive than selective subject lookup on this fixture. These results describe the implemented correctness/authority/history contract at this workload; they do not select an engine winner or establish larger-store capacity. They are not comparable to the historical 110,000-assertion selective-read test.

## Remaining qualification boundaries

- Hosted Ubuntu and macOS CI succeeded at the cited commit. Hosted macOS and two local writable peer processes do not qualify the owner's actual Mac-plus-Linux pair, its configuration or its filesystem; that still requires the documented two-device run.
- The two independent-SDK integration tests passed locally, while the installed Praxis2 application remains untested. Protocol/SDK evidence and the required actual Praxis2 connection are distinguished in the MCP conformance report; no changes to Praxis repositories are part of this work.
- Synthetic legacy adapters do not establish successful migration of unavailable original archives or encrypted inputs. Each supported generation needs its own documented accounting/fidelity evidence.
- No private data was ingested, no external deployment was performed, and these fixtures do not authorize either action.
- No engine comparison, enterprise scale, transitive mesh, content encryption or production capacity is established by this evidence.
