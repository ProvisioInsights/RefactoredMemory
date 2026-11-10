# Core field contract source validation

**Scope:** Source implementation of the version 1 starter catalog and explicitly tagged core assertions, 9 November 2026. No personal-store migration, deployed-peer upgrade, universal field activation or field-driven UI qualification was performed.

## Implemented and checked

- A packaged machine-readable catalog with 52 definitions, nine ordinary record types, all 26 registered relationships and all sixteen inventoried reported-profile property names. A canonical digest and JSON tag schema are published by `memory_schema.field_catalog`.
- Explicit field-tag validation through the existing core submit/correction paths, with sourced values, missing states, explicit validity ends, minimal atomic creation, retained cardinality and field lineage.
- Type establishment/conflict resolution and same-meaning withdrawals remain possible after reclassification. New substantive fields use resulting atomic-group types and owner preference. Changed target/value/context cannot use an invalidation exemption. Legal null legacy metadata remains compatible.
- Untagged legacy records/writes retain their existing profile. Consumer archival, permanent erasure, universal activation and the new UI remain outside this implementation.

## Executed validation

| Check | Observed result |
| --- | --- |
| `python -m unittest discover -s tests -p test_field_contract.py` | 23 dedicated tests passed; includes valid/invalid shared fixtures, core/service grants, retries, peer replay, correction/reclassification, repair and withdrawal regressions. |
| `python -m unittest discover -s tests -v` | 252 tests ran on macOS with the existing SDK test environment; OK, three Linux-only skips. |
| `python -m pip wheel --no-deps --no-cache-dir --wheel-dir <private-output> .` | Isolated build succeeded. Both contract resources and changed runtime modules match checkout bytes inside the wheel; isolated archive import publishes all 52 definitions and the digest. An initial no-build-isolation probe lacked setuptools; the isolated build resolved its own build tooling without modifying the production runtime. |
| Aikido path scan | All ten changed code/config/contract-fixture files scanned; no issues reported. |
| Independent review | Classification repair, same-group applicability, withdrawal-meaning and legacy-null findings fixed and rechecked; no actionable finding remains in the reviewed delta. |
| `git diff --check` and document links | Passed. |

Full logs, artifact hashes and the independent review are retained in private commissioning reports. The full FC01–FC08 matrix, actual named-client/host qualification, source-wide legacy field census and production rollout remain separate; these local tests do not pass those broader requirements.
