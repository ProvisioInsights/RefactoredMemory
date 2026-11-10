# Contract-driven editor and two-peer rollout

**Owner direction:** 9 November 2026. Implement the shared editor, qualify and upgrade the private Mac/NAS peers, then complete an evidence-backed Forgence investor pilot. Front implementation with repository PRD/architecture decisions and retain exact execution evidence. This is the implementation plan for [A25](ADRS.md#a25-contract-driven-editor-and-controlled-two-peer-rollout), not a deployment receipt.

## Product boundary

The first complete journey is search → select a person → inspect standard fields and relationships → make an authorized correction with a reason → inspect retained evidence/history → verify the other peer receives the same change. The graph/detail pane and search-result editor reuse the same field components and core catalog. A minimal new person needs a name and type; contacts remain optional. No conversation, composer, model selector or processing dashboard is introduced. Comments/jobs keep their existing tool compatibility.

## Architecture contract

- Discover the catalog, revision and digest through `memory_schema`. An absent/unsupported catalog permits legacy reads, not field-v1 writes. Publish editor capabilities separately from the immutable field-v1 definitions.
- Extend `memory_inspect` with a bounded core field projection: stable field IDs, mapped current claims, explicit-v1 versus legacy qualification, per-value evidence/time, alternatives and honest partial coverage. Missing in a bounded response does not prove absence. Retain unmapped legacy claims separately.
- Use ordinary `memory_submit` for atomic typed creation and additional sourced assertions. Extend `memory_correct` with an explicitly discovered field update for state/time/context changes; validate it in the existing core admission path with the catalog digest, current scopes, observed heads, stable request IDs and sourced reasons. No second database, UI-only write service or direct-store fallback.
- The private loopback host retains its generic-capture denial. It permits `memory_submit` only for catalog-digest-matched groups containing explicitly declared typed assertions, followed by the full core validation and current grant checks. This is an authorized editor capability, never a fallback for a denied model connection. No credentials enter HTML or model context.
- Explicit legacy qualification is an attributed correction preserving its predecessor and evidence. Reading a legacy mapping does not qualify or normalize the original. Do not invent required relationship context, names, ownership, temporal precision or certainty.
- A corrected name is discoverable through core search and a derived display label. Preserve the immutable original label; competing names and incomplete coverage cannot choose an arbitrary preferred name. Search matches are candidates, never identity merges.
- Inputs derive from published value types/mappings: text, aliases, contact values, reported calendar precision, typed entity references and required relationship context. Show required missing values; optionally hide empty optional values. Sourced unknown/N/A, conflicts and partial coverage remain visible.
- Freeze identical tool arguments after an uncertain save and offer an identical retry. Reconcile stale heads/catalog rather than changing a retry. A denial is a denial; neither an owner UI token nor another transport may bypass a model/client denial. Opening/editing the App sends no automatic model context.

## Acceptance evidence

| ID | Required result |
| --- | --- |
| FE01 Discovery and projection | Two independent grants discover the same catalog; bounded projection distinguishes explicit v1, legacy, unmapped and incomplete data. Discovery cannot change admission policy. |
| FE02 Minimal creation | Create a sourced person without optional contacts; missing required values and invalid multi-action groups commit nothing. Identical retries create one operation. Name matches stay separate. |
| FE03 Typed editing | Correct contact/name/calendar/relationship values; round-trip known/unknown/N/A and explicit ongoing/unknown ends. Preserve qualifiers, sources, dates and competing claims. Resolve competing type heads and withdraw unchanged claims after reclassification; reject changed-meaning invalidation and invalid reinstatement. Wrong endpoint/context/value/state fails atomically. |
| FE04 Safe failure | Stale heads/catalog, revoked correction scope, capacity refusal and unknown save outcome produce visible actionable states without success or authority escalation. |
| FE05 Focused interface | Graph details and search-result CRUD share controls; required missing fields stay visible, optional blanks reveal on demand, keyboard/narrow/dark/light views work, and history/evidence remain accessible. Type resolution and same-meaning withdrawal stay usable despite ambiguous or changed applicability. Unsupported hosts stay read-only. |
| FE06 Peer lifecycle | Synthetic independent offline writes converge on upgraded peers; repeat after restart; consistent snapshot restores to a fresh identity; old writers cannot be represented as v1-qualified. Record rollback limits. |
| FE07 Private deployment | Record exact commit/image/UI identities and retained backups; upgrade only memory/private sync/owner UI as needed, preserve unrelated services/grants, verify catalogs, original-record digests, convergence and targeted network denials. |
| FE08 Investor pilot | Select real claim/source IDs privately, normalize evidence-supported values/links, flag ambiguous identities, retain history, answer the investor question with dated status and citations. Conditional or bounded offers, equity ownership and completed funding retain distinct meanings; unsupported terms and denied writes stay pending rather than losing context. |

These are focused cases under FC01–FC08. Passing a unit/build/reference-host test does not qualify a named provider app or actual deployed peers.

## Execution order and recovery

1. Update repository PRD/ADRs/architecture and review the intended boundary.
2. Implement core projection/edit support, shared controls and focused navigation. Run synthetic core, browser, packaging and security checks; record precisely what passed.
3. Complete Linux qualification in a disposable environment. Use existing pinned workload access only after verifying its trusted host-key/access record. Do not widen network or client grants to make checks pass.
4. Re-observe deployed runtime/operator-controlled paths. Take consistent snapshots and retain prior code/image/settings privately. Freeze reviewed source/image identities; production executables must not load from an engineering-writable checkout.
5. Pause only memory sync during coordinated upgrade; preserve independent console/SSH recovery. Upgrade both writing peers before allowing the profile. Verify listeners/catalogs and synthetic operations without adding test records to the personal store, then resume sync and verify original-record digests/frontiers. Keep public transport off.
6. Run the Forgence pilot through its authorized client grant. A correction denial is an access dependency, never a bypass opportunity. Continue read-only reconciliation and prepare precise proposed changes while it is pending.

Rollback replaces code/configuration only where compatible with the journal; it does not erase v1 assertions. After new semantics are admitted, prefer forward repair or isolated fresh-identity recovery to an older runtime that might ignore them. Never overwrite the live database or reuse a historical identity alongside its restore. Addresses, credentials, source contents and receipts belong in private reports outside Git.

## Execution status

Documentation and implementation scope were recorded before code changes. Core projection/editing, shared controls and focused Graph/Records navigation are implemented. [The client contract](RM-CLIENT-CONTRACT.md#shared-editor-capability) defines their exact wire behavior. Record test/browser results separately from actual deployment/pilot receipts; this plan itself certifies no installed service.

[The dated qualification record](FIELD-EDITOR-VALIDATION.md#private-rollout-observation) now records the private two-peer upgrade to `914beca16987afeebee44124ce9da9e40f774a3c`, successful catalog/tool readbacks, sync and targeted network checks. The investor pilot remains partial: captured-source quotations matched, while correction permission and lossless treatment of legacy finance terms remain separate dependencies. No personal semantic rewrite or universal activation occurred.

For this source-only container upgrade, [the runtime overlay](../deploy/runtime-overlay.Dockerfile) fixes the previous qualified A23 release and records its required exact local image ID. Verify that tag's image ID before build, freeze the source revision, and verify the result's revision/package/UI hashes. It executes no new source as root. Build/promote only from a sealed operator-controlled context, never an engineering-writable checkout. Preserve the existing user, read-only root, capability/network limits and root-owned configuration. A different base/dependency version needs a reviewed recipe and qualification; there is no arbitrary or moving-base argument.

The observed NAS uses Docker's legacy builder. The overlay retains the sealed context's read-only file/directory permissions and uses supported `COPY --chown`; it does not require BuildKit-only `--chmod`, a builder installation or a guest reboot. Probe package bytes and the unprivileged user in the built image before promotion.
