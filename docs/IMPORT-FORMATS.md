# Import formats and migration fidelity

The importer reads only an explicitly supplied root and never modifies its source files. Planning is read-only; applying a plan requires a consistent destination backup, checks that source hashes still match, and submits bounded operations through the graph contract. Use an isolated destination for a first migration. Development and verification use synthetic inputs only.

## Evidence inventory

The following formats were inspected in public LivingAtlas source at commit `e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d`. These are compatibility targets, not claims that any personal archive was opened or migrated.

| Generation | Inspected definition | Migration boundary |
| --- | --- | --- |
| Legacy object snapshot and journal | [local-graph-store.ts](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/packages/local-graph-store/src/local-graph-store.ts), [object-envelope.ts](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/packages/contracts/src/object-envelope.ts) | `schema_version:1`, `objects` snapshots and newline-delimited journal entries containing `object`. Known plaintext snapshot payloads can be interpreted. Journal files and retained operation records are preserved as source metadata; replay/hash qualification is still missing. Snapshot-only input cannot recover overwritten earlier versions. |
| Canonical payloads inside envelopes | [knowledge.ts](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/packages/contracts/src/knowledge.ts), [temporal.ts](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/packages/contracts/src/temporal.ts) | Known entity/fact/relationship payloads retain stable mappings and original provenance. Unknown payload shapes remain explicitly unconverted. |
| Immutable assertion segments | [log-record.ts](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/packages/atlas-core/src/log-record.ts), [assertion.ts](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/packages/atlas-core/src/assertion.ts) | `atlas.segment-log:v1` headers, assertion/supersession groups closed by submission receipts. Uncommitted tails cannot become assertions. |
| Immutable identity segments | [identity-record.ts](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/packages/atlas-core/src/identity-record.ts), [entity.ts](https://github.com/ProvisioInsights/LivingAtlas/blob/e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d/packages/atlas-core/src/entity.ts) | `atlas.identity-log:v1` entity/alias/observation groups closed by `group-commit`. Identity records are distinct from assertion history. |

No original run inventory, encrypted payload keys, or real personal dataset was available to this implementation task. Encrypted envelopes are reported as unavailable, without attempting decryption. Unknown formats, missing referenced evidence and compacted-away history remain explicit fidelity gaps. Raw source preservation is not semantic-equivalence qualification.

## Markdown and Logseq

Import readable `.md` and `.markdown` notes as document identities, immutable source versions, and source-linked content claims. Preserve the original text, links, properties and Logseq block identifiers; do not infer relationships or dates merely from prose. MCP clients can later submit attributed inferred knowledge under their grants. An unchanged import has no second semantic effect. Changed text appends a correction linked to earlier imported content; a missing file is never interpreted as erasure or retraction. Compare successive manifests to detect removed files explicitly.

Use a stable explicit import namespace when rerunning or copying the same source set between peers. Document identity is scoped by namespace and relative path; renaming a file requires an explicit mapping decision, rather than automatic identity merging. Names, IDs, original recorded timestamps, precision and missing-fidelity labels remain inspectable in the source metadata and manifest.

## Safety, accounting and rollback

Reject traversal outside the approved root, symlink inputs, nonregular files, excessive files/records/bytes, invalid UTF-8, duplicate JSON keys, nonfinite numbers and malformed commit groups. Never execute Markdown, follow embedded file links, load remote URLs, or treat source content as permission. Unsupported entries are counted with a named reason and left unchanged at the original location.

Normal operating-system aliases above the selected root, such as macOS `/var` pointing to `/private/var`, are resolved once when the plan is created. The manifest reports that pinned canonical `approved_root`; planned file paths use it even if an ancestor alias later changes. A root that is itself a symlink is refused, and descendant symlinks remain refused rather than resolved. The source tree must remain quiescent during reads; hash checks reject source-content changes between planning and application.

The manifest distinguishes planned, imported, unchanged, preserved-only, unsupported, quarantined and failed records. It includes source hashes, stable ID mappings, fidelity notes and a backup path. Bounded batches may leave a partial destination if a later batch fails; stop and report the exact committed batch count. Restore the pre-import backup into a fresh isolated destination using the normal restore workflow, then explicitly pair it if needed. Never replace or repair the legacy source archive as rollback.

Original legacy knowledge time remains attributed metadata. RefactoredMemory's own known position is the import receipt/application position and is never backdated. Exact full dates can enter world-time queries; partial, approximate and unknown legacy dates retain their original expression and cannot produce an invented definite exact-time match.

## Implemented interfaces and qualification

`plan_import(path, approved_root=..., namespace=...)` returns an `ImportPlan`; its `summary()` omits source content and performs no graph writes. `apply_import(store, plan, backup_path=..., actor=...)` rechecks input hashes, makes a new consistent backup, and applies dependency-ordered groups of at most 450 actions and 900,000 bytes. `import_path(...)` combines these with `dry_run=True` by default. Backup and destination paths must be outside the approved input root.

Current bounds are 500 files, 1 MiB per file, 10,000 inventoried records, and 60 KiB per Markdown note. Larger source sets can be explicitly divided into stable-namespace batches; unchanged identities are reused. Source text is split into bounded immutable parts with the whole-file SHA-256 and part count so it can be reconstructed and checked. No source link is fetched automatically.

An import always submits under an importer/agent actor, including when an owner authorizes the import. Imported correction records therefore cannot become new preferred owner corrections merely because the command ran with owner authority. The original source actor remains attributed metadata.

`status` describes batch execution; `semantic_complete` and `fidelity_gap_count` separately describe compatibility gaps. Unknown/unsupported/ciphertext/tombstoned records, unrepresented lineage and unresolved original evidence prevent an unqualified semantic-completeness claim. Original evidence identifiers and provenance are retained, but discovering an assertion does not establish that its separately referenced evidence bytes were provided. Identity alias actions, old journal replay/hash verification, encrypted adapters, partial-date exact-match equivalence and compacted-away records require further source-specific qualification.

Run `python -m unittest tests.test_importers -v` for synthetic checks against the actual SQLite graph store. The checks cover note repetition and correction history, legacy identity/assertion mappings, committed-segment boundaries, temporal fidelity, unsupported-record accounting, rejected duplicate identities, source safety, interrupted batches, import actor attribution and backup restoration. They do not certify any real archive or original keys.
