# Contract-driven editor qualification

**Scope:** A25 source, shared controls and disposable synthetic execution, 9 November 2026. This record qualifies the behaviors below. Live Mac/NAS release identities, backups and network receipts are private operational records; they are not inferred from a source commit. No personal-store rewrite or named-provider qualification is claimed here.

## Executed checks

| Check | Observed result |
| --- | --- |
| `python -m unittest discover -s tests -p test_field_editor.py -q` | 20 focused tests passed, including actual JavaScript wire payloads reaching core, partial/suppressed/legacy projection, state/time changes, grant failures, exact retries, relationship ending/reclassification, two offline writers with restart/convergence/fresh-identity restore, searchable corrections, historical name privacy and unresolved owner preference. |
| `python -m unittest discover -s tests -v`, macOS SDK environment | 273 tests ran; OK with three Linux-only address-space skips. |
| Same suite in the existing pinned Chainguard Linux runtime, source selected explicitly, network disabled, read-only root, UID10001, all capabilities dropped, 2 GiB memory and Linux-local disk scratch | 273 tests ran; OK with eight skips: Node client fixture, three optional independent-SDK tests and four synthetic-certificate cases requiring an OpenSSL executable. All three Linux address-space regressions passed. Node/SDK/certificate cases passed in the Mac environment. |
| `npm run build` and `npm run build:reference` | Bundled App and official-SDK reference host built. No new runtime/package dependency. |
| Aikido path scans | 22 changed product/code/config/fixture files: no reported issues after replacing the variable base with the specific qualified release. Operator/QA code was separately scanned privately. |
| Independent source review | Core/host closure, suppression, retry, legacy mapping, pending navigation, relationship display and temporal/name findings fixed and rechecked. No actionable source findings remained. Operator procedure was separately reviewed; execution is separate evidence. |
| Private compatibility copy | New-code reads over an isolated consistent backup retained all 1,253,227 immutable records unchanged. Targeted Forgence search was approximately 1.01 seconds and field inspection 0.05 seconds on that Mac copy. This is a bounded compatibility observation, not a load benchmark or NAS performance claim. |

The first Linux harness selected the image's old package; its results were discarded. A later harness used Mac-shared scratch, where the sync-lock exclusion case failed. Repeating on Linux-local disk passed that case and the full suite. Do not treat the failed fixtures as qualified runtime results.

## Browser evidence

Browser plugin unavailable; used the supported local Playwright CLI against the disposable official MCP Apps SDK reference host. The flow under test was graph/search → standard fields → typed save → authoritative readback/history, with the same field components reused inline and expanded.

- Created a minimal person without contacts; corrected its name, found the correction through core search, added a contact inline, and opened the same fields in the expanded record view.
- Round-tripped known → explicitly unknown → not applicable, withdrew the mistaken claim, revealed empty optional fields and hid them again without rewriting history.
- Seeded a deliberate synthetic type conflict through the authorized fixture API, resolved the displayed heads through the form, reclassified the subject and withdrew its unchanged old field after applicability changed.
- Added an investment discussion with a typed target, displayed its source-reported status and unknown amount, recorded an explicit relationship end and retained history. Discussed funding never displayed as completed funding.
- Dropped the response after a real synthetic commit. Existing search actions, tabs and graph navigation could not destroy the pending request; a delayed navigation read could not replace the locked form. The retry sent identical arguments/request ID, recovered the receipt and unlocked history. Its deliberate connection-reset console error is test evidence.
- Checked desktop 1440×1000 and narrow 390×844 App layouts, dark/light rendering and no narrow App-body horizontal overflow. Screenshots and tool receipts remain private. Emulation is not physical mobile qualification.

The reference fixture intentionally places its AppBridge in a same-origin iframe and produces the browser's sandbox warning; it is not a production-host sandbox qualification. Named ChatGPT/Codex, Claude, Gemini, Grok, local-model and Praxis products remain separate qualifications. No UI action automatically sent record/source contents into model context or used another identity after a denied save.

## Remaining boundaries

FE01–FE06 have the focused source/reference-host evidence above; actual peer deployment/network readbacks (FE07) and real-data pilot results (FE08) need their own receipts. The full FC01–FC08 matrix, universal field activation, source-wide normalization, consumer archival and permanent erasure are not completed by these checks. Unsupported legacy terms retain their originals and review state. A denied correction grant remains a real access dependency, never permission to use owner credentials or direct-store edits.
