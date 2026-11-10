# Relationship Brief qualification

**Scope:** A26, client-selected bounded briefs and the focused light interface, 10 November 2026. This record describes executed source and synthetic reference-host evidence. Installed-peer revision, personal data and provider qualification are separate operational outcomes.

| Check | Observed result |
| --- | --- |
| `python -m unittest discover -s tests -p test_relationship_brief.py -q` | 14 passed, including actual JavaScript projection, path/input bounds, stale/deleted inputs, admitted attribution, task boundaries, exact retries and fresh-identity restore. Repeated after the final snapshot guards. |
| Full suite in the existing macOS SDK test environment | 287 tests ran; OK with three Linux-only skips. This preceded the final frontend snapshot guards; the focused tests above cover those later changes. |
| Full suite on pinned existing Chainguard Linux runtime, explicitly selected source, UID10001, read-only root, no network, all capabilities dropped, 2 GiB memory and Linux-local scratch | 287 tests ran; OK with nine skips for absent Node, optional SDK and OpenSSL executable. Mac covered those cases. Linux address-space regressions passed. This is synthetic runtime evidence, not a new NAS image receipt. |
| `npm --prefix apps/memory_graph run build` / `run build:reference` | App and official-SDK reference host built. Final App is approximately 571 kB, below the existing 1 MiB resource bound. No new runtime dependency. |
| Aikido path scan | No reported issues across 17 changed source/fixture paths; later snapshot-boundary changes were rescanned separately. This is scanner output, not proof that all security risks are absent. |
| Independent read-only review | Freshness race, authoritative actor attribution, malformed artifact envelope, queued host updates, creation compatibility and malformed display-only snapshots were addressed. Focused tests independently passed. |
| Visual acceptance | [Root design QA](../design-qa.md): passed, using combined source/render comparisons and actual browser checks. |

## Browser execution

Used the supported Codex in-app browser against the loopback, disposable in-memory reference host. The reference uses the official MCP Apps AppBridge; it is not a consumer-product sandbox certification.

- Loaded three client-selected people, their actual supporting path, attributed explanation and exact evidence reads. No graph-wide neighbor expansion or source forwarding to a model occurred.
- Corrected a fictional name, found the updated name through search, inspected retained history and created another minimal fictional person without optional contact fields.
- Dropped a response after a real synthetic relationship correction committed. Navigation remained locked, the incoming host result stayed queued, retry reused the exact arguments/request ID, and authoritative readback recovered the receipt. The old explanation/path remained withheld after correction and after replaying an older host result.
- Checked current and stale display-only snapshots, actual read-only grants, working and empty type filters, independent row collapse and a Records screen containing only relevant controls.
- Checked light/dark desktop and narrow browser rendering. The 375-pixel App content width had no horizontal overflow. A fresh normal reload produced zero new uncaught exceptions. Deliberate connection-reset errors are retained as failure-injection evidence.

## Contract and remaining boundaries

`memory_schema.relationship_brief` is separate from the unchanged field-v1 digest. Saving uses existing `memory_derive`; reading uses the exact derived assertion revision through `memory_graph.brief_id`. Titles, reasons and summaries are attributed interpretation. “Current” means pinned inputs remain active and available, not independent factual truth, owner verification or exhaustive relevance.

No personal semantic records, client grants or source imports were changed by this synthetic qualification. Existing model correction denial remains effective. Private Mac/NAS rollout, prepared personal briefs, full corpus normalization and actual named-provider App support require their own observed receipts. Public transport remains outside this source/browser qualification.

The first hosted run at `5360320` failed because the Node projection fixture indirectly imported the optional browser SDK before frontend dependency installation. Pure formatting was extracted into a dependency-free shared module; browser behavior and field meanings are unchanged. An initial NAS test mount also hid the sealed stage's root from UID10001. It was rejected as a harness failure; the corrected harness mounts only the sealed test/example directories and imports the actual image package. Neither failed attempt promoted a runtime.
