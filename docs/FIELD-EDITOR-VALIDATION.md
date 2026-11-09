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
| Hosted qualification at `914beca16987afeebee44124ce9da9e40f774a3c` | [Run 42701651437](https://github.com/ProvisioInsights/RefactoredMemory/actions/runs/42701651437) passed: Linux ran all 273 tests without skips; macOS ran 273 with three Linux-only skips. Both jobs passed the three day-one journeys. |
| Actual newly built NAS image | 43 field tests ran, OK with one absent Node fixture skip. This image retains the pinned Chainguard base and changes the source package only. |

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

## Private rollout observation

On 9 November 2026, both private peers were upgraded to sealed runtime `914beca16987afeebee44124ce9da9e40f774a3c`. The build-recipe compatibility commit changes no runtime package bytes relative to qualified `9953db4`. Consistent Mac/NAS snapshots and the authorization-service backup were completed before promotion. Only memory and private sync ingress were restarted on the VM; authorization service image IDs and start times were unchanged. The Mac HTTP, owner graph and sync agents resumed from the sealed release.

The Mac serves the exact sealed UI bundle. A fresh independent MCP SDK connection and the current native Codex connection discover the unchanged 52-definition catalog digest and `refactoredmemory.field-editor:v1`. Native Codex tool discovery now includes the new inspection/correction tools. The owner-authorized older adapters were stopped; the current chat reconnected and new adapters were observed. This is not a claim that a correction was performed or that every open chat exercised the tools.

Private TLS synchronization reached the same frontier with zero pending/rejected work on both peers. Targeted guest/container attempts to the approved DSM, NAS-share and router-administration endpoints were denied, as was container access to its observed host gateway's SSH port. IPv6 is disabled and IPv6 forwarding is off. IPv4 forwarding remains enabled for the existing Docker topology; the selected end-to-end denials and inspected VPN forwarding rules do not establish a universal transit-path test. Public transport remains off. Exact addresses, image/package identities, checksums, resource observations and recovery paths are in private operator reports outside Git.

After upgrade, complete read-only digests of both live immutable-record projections matched the pre-upgrade checkpoint: 1,253,227 records unchanged. This covers assertions, entity identities and captured sources; it does not describe grant tables, derived indexes or other operational metadata as immutable.

## Pilot and remaining boundaries

FE01–FE06 have the focused source/reference-host evidence above; FE07 has the private observations above. The full FC01–FC08 matrix, universal field activation, source-wide normalization, consumer archival and permanent erasure are not completed by these checks.

FE08 is partial: nine quoted contact/conditional-interest claims across six engagement identities matched their exact text offsets and quote hashes in nine captured sources. That establishes captured-source consistency, not independent confirmation, delivery, owner verification or current investor status. Four older investment links retain terms that do not fit v1 cash amount/status losslessly: equity/share ownership, bounded offers and conditions must not become completed cash funding. Keep those legacy values and their review state until a faithful representation is reviewed.

No personal semantic writes were performed during this rollout. Current Codex discovery reports read/add access with correction and owner review denied. The specific correction-grant decision remains pending. A denied correction grant is a real access dependency, never permission to use owner credentials or direct-store edits. Named provider App rendering, physical mobile qualification and completion of the investor pilot remain open.
