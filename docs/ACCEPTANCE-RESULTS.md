# Personal v1 acceptance evidence

All tests, examples and benchmarks in this record use synthetic data. Executed Linux checks are recorded separately from requirements that still need the owner's Mac, actual application access or original legacy artifacts. Passing a synthetic fixture does not establish those unavailable results.

## Combined final Linux run

The full suite passed **82 tests in 13.125 seconds**, with no skips, using `python -m unittest discover -s tests -v` on 7 November 2026. This includes 23 independent acceptance, 19 MCP, 17 sync, 16 importer, 5 real CLI subprocess and 2 additional storage-hardening tests. See the [raw unittest output](results/linux-unittest.txt). The runtime source digest matches the raw benchmark artifact linked below.

The first macOS CI run exposed normal parent-directory aliases in the importer and an opaque multiprocessing test startup failure. The importer now pins the canonical approved root while rejecting descendant symlinks; three new regressions cover those boundaries. The sync fixture now uses a plain independent interpreter subprocess with explicit readiness and failure diagnostics. Cross-platform CI results remain separately visible on the pull request.

The integrated run includes the installed independent MCP SDK, production HTTP/stdio paths, worker-isolated TLS handshakes, two separately writable peer processes, verified recovery, and the three selected day-one workflows. Actual owner's-Mac and installed-Praxis qualification remain open.

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

The final development run at `2026-11-07T19:12:30.429903+00:00` passed the benchmark's correctness checks. [Raw measurements and source identity](../benchmarks/results/personal-linux-1100.json) include all samples and the working-tree source digest; the Git commit identifies the preceding commit, while the digest identifies the measured working-tree code. This shared Linux environment was not a dedicated performance host. The benchmark ran separately from this agent's acceptance tests, but no machine-wide isolation or CPU-frequency control is claimed.

| Workload | p50 ms | p95 ms |
| --- | ---: | ---: |
| Acknowledged single correction | 0.686 | 1.227 |
| Current subject lookup | 0.685 | 1.215 |
| Historical subject lookup | 0.668 | 0.971 |
| Text search | 105.871 | 114.866 |
| Four-hop traversal | 11.710 | 13.953 |

One signed in-process transfer of 55 operations (339,352 serialized bytes) took **121.863 ms**. Rebuild took **93.105 ms**, backup **10.550 ms**, verified fresh-identity restore **142.726 ms**, and reopen **1.869 ms**. These are single operation measurements, not latency distributions. Signed transfer excludes HTTP/TLS and network delay. The observed main database was 1,179,648 bytes with 4,169,472 bytes in WAL at measurement time.

Text search and traversal remain visibly more expensive than selective subject lookup on this fixture. These results describe the implemented correctness/authority/history contract at this workload; they do not select an engine winner or establish larger-store capacity. They are not comparable to the historical 110,000-assertion selective-read test.

## Remaining qualification boundaries

- The available execution environment is Linux. Two local writable peers do not qualify the owner's physical Mac or its filesystem; that requires the documented cross-machine run.
- A protocol harness is not successful integration through the installed Praxis application or an independent MCP client. Actual-client evidence is recorded separately in the MCP conformance report.
- Synthetic legacy adapters do not establish successful migration of unavailable original archives or encrypted inputs. Each supported generation needs its own documented accounting/fidelity evidence.
- No private data was ingested, no external deployment was performed, and these fixtures do not authorize either action.
- No engine comparison, enterprise scale, transitive mesh, content encryption or production capacity is established by this evidence.
