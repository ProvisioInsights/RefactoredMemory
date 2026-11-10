# Core field contract and focused CRUD

**Status:** Accepted owner direction, 9 November 2026. The [v1 catalog](FIELD-CATALOG-V1.md), [client contract](RM-CLIENT-CONTRACT.md), core projection/edit support and shared field-driven UI are implemented in source. [A24/A25](ADRS.md#a24-core-field-contract-and-focused-memory-crud) record the decisions; [editor qualification](FIELD-EDITOR-VALIDATION.md) records executed synthetic/core/browser evidence. Deployment needs private operator receipts; universal activation and complete FC01–FC08 remain separate. Synthetic concepts and reference-host results do not qualify a named AI product.

## Responsibilities

RM owns one versioned semantic contract for record types, fields, relationships, validation, permissions, evidence, time, corrections and synchronization. Connected AI applications perform extraction, interpretation, identity proposals, organization and synthesis. The optional MCP App renders and edits that same contract. A human or model uses the same authorized operations; admission never confers human verification.

Keep the implementation small: extend the existing registry and semantic operation path, discover it through MCP, and reuse a small set of typed controls. No separate UI database, parallel CRUD service, arbitrary form language, universal ontology, internal LLM or orchestration platform is required. Existing external-client task/checkpoint tools remain compatible infrastructure, not the explorer's navigation model.

## Versioned definitions in the core

The catalog needs stable field IDs, a contract revision, supported record/predicate applicability, value type, cardinality, requiredness by operation, permitted value states, bounded deterministic validation, and mapping to existing semantic assertions. Labels and concise help may accompany definitions; styling, theme, column visibility and layout are presentation choices. A client may translate a label without inventing another field or meaning.

Use the existing endpoint types, knowledge kinds, categories and predicate registry. These are distinct dimensions: `person` is an entity type, `relationship` is a knowledge kind, and `employment` is the category of `employed-by`. Do not invent a second category tree in the App. Preserve `source-document` capture identities and legacy-unannotated records under their existing compatibility rules.

The starter catalog covers the common identity/display fields, sourced names/aliases/descriptions, applicable email/phone/profile contact points, and the existing registered relationships with their endpoints, dates, evidence and uncertainty. Add further fields only for concrete records and reviewed semantics. A person's email, phone, location and profile URL are optional; missing contact information must not prevent creating a useful person identity. Required evidence and operation reasons still apply when admitting claims or corrections.

Fields are projections of sourced claims, not mutable columns inside an entity. Multiple contact points, dated affiliations and conflicting alternatives can coexist. Retain value-specific assertion IDs, sources, authority, time and lineage. A form must not flatten alternatives into one silently selected value or copy one field's evidence onto the whole record. An editable display name is a sourced assertion over a stable identity; changing it does not replace that identity.

## Missingness and dates

| State | Meaning | Write and display rule |
| --- | --- | --- |
| Not recorded | No applicable claim was captured in the selected view. | Display absence; do not persist a placeholder string, invent an unknown claim or infer falsity. A filtered or unauthorized view must not claim global absence. |
| Unknown | An authorized source explicitly reports that a value is unknown. | Preserve an explicit sourced state where the field contract supports it. Unknown is not an empty string, zero, false or a guessed value. |
| Not applicable | An authorized statement or deterministic applicability rule establishes that this field does not apply. | Preserve its basis. Never infer this from a blank field or a model's convenience. |
| Known | A sourced value exists. | Validate its type and preserve its evidence, precision, alternatives and current access boundary. |

The v1 client contract now publishes explicit tagged encodings for known, sourced unknown and not-applicable values; not-recorded is read-only. The core validates explicitly declared v1 writes, without silently qualifying untagged legacy values. Withheld, unavailable, conflicted and temporally unresolved are separate retrieval conditions, not aliases for missing. Full UI display behavior remains unqualified.

**Existing time compatibility:** the current operation contract treats omitted `valid_to` as ongoing and explicit `null` as unknown. Preserve that historical meaning. A new form's blank or “Not recorded” end must not accidentally omit `valid_to` and assert ongoing validity. Use an explicit supported unknown-end representation when appropriate, or reject an unrepresentable edit until the versioned adapter exists. No date-filtered answer may promote unknown time into a definite match. Date precision and timezone uncertainty stay explicit; do not invent a day or country/timezone to make a control look complete.

Requiredness is contextual and server-enforced. Show required missing fields even when optional empty fields are hidden. Preserve an invalid imported value and flag it for correction; never silently rewrite the original. Normalize only meaning-preserving formats under documented rules, retaining the captured value. An ambiguous identity, phone country code or source interpretation remains unresolved.

## Discovery and one admission path

`memory_schema.field_catalog` in this branch now publishes versioned field definitions, a tag schema/digest and semantic operation requirements. The existing search/query/entity/source/history and submit/correct paths remain authoritative. The v1 tag lives inside the existing knowledge qualifiers, without adding a UI-only write API. The client contract gives exact encodings and limits. Runtime deployment and universal enforcement remain separate; no new tool name is advertised.

Every newly governed write, whether from the MCP App, a model, CLI, importer or peer, must reach the same core validation before admission. Transport adapters may add stricter checks but cannot weaken semantics. Discovery is not authorization: resolve the current grant on each request, and preserve read/write/correct/administrative distinctions. Schema metadata must not disclose protected values or imply access to a record. Catalog changes are controlled deployment/migration changes, never ordinary model-generated data writes.

Typed requests must identify the catalog revision, target identities and expected claim heads, their sourced changes and a stable request identity through the documented adapter. Validate the whole dependent operation group before an atomic commit. A stale catalog, changed head, denied grant or invalid input produces a bounded actionable error, no partial record rewrite and no false success. Refresh and reconcile changed inputs; retry unknown outcomes only with the original request identity and arguments. This planned interface must preserve existing idempotency, conflict and capacity behavior.

These consumer checks apply at origin admission. Authenticated peer replay follows the current peer/origin admission policy and the recorded contract/enforcement frontier; it does not require the originating consumer grant to exist on the receiving peer. Do not rerun a fresh consumer edit's expected-head guard against an already admitted historical operation. Preserve signed history, dependency checks, idempotent delivery and concurrent branches; this does not authorize new writes by a revoked consumer.

## CRUD meanings

| User action | Core meaning |
| --- | --- |
| Create | Admit a stable identity/canonical type and any valid sourced claims as one dependent group. Search can suggest existing candidates; a matching name never authorizes a merge. Manual statements retain authenticated human/client attribution and their actual basis. |
| Read | Return authorized typed values, alternatives, missingness/coverage, dates and bounded evidence at the requested knowledge view. Graph, list and form read the same meaning. |
| Update | Append a correction, reclassification or other supported semantic action against the observed heads, retaining original claims/evidence and the reason. Type changes must account for affected endpoint validity without silently rewriting related records. |
| Remove | Explain the object and effect before commit. Retract a mistaken claim/relationship; invalidate one that actually ended, with its supported date. A record archive is a separate explicit visibility/lifecycle operation, not an inferred end event, access restriction or cascade deletion. Preserve dependencies and history. |

Do not make one ambiguous Delete button choose between retraction, ended validity, archive and erasure. Simple labels plus a short context-specific confirmation should expose the effect, affected claims and reason. Existing administrative delete/restore operations retain their actual scope; the new App must not assume it can archive entities or sources before the relevant core operation is implemented and authorized. Sources are immutable: corrections create or link a new source version rather than overwrite captured bytes. Permanent erasure needs its own explicit privileged workflow covering replicas, derivatives, backups and retention limits; archive/retraction does not promise erasure.

## Focused explorer and editor

The everyday flow is search, select, inspect evidence, create/edit/remove, and view history. Use graph and record-list views over the same authoritative records. Relationships are first-class editable records with typed endpoint pickers, registered predicates, their own dates, sources and history. Review flags appear on affected records and through filters. Existing annotations, client jobs and contributor diagnostics remain available through their proper interfaces; they do not turn RM into a conversation, task or model-management product.

The App has no conversation list, chat history, assistant, composer, internal model chooser or processing dashboard. A host may place it inside a conversation or offer direct/expanded launch; any surrounding messages/composer belong to that host. Launch/display modes are capability-dependent and separately qualified, not required for core CRUD. Keep meaningful text/structured tools without UI and honest read-only/display-only behavior.

The same core definitions drive search-result actions, inline forms and expanded graph/detail views. Reuse labels, controls, pickers, validation and missing-state meanings. Hide empty optional fields by preference during browsing; expose relevant optional fields on demand while editing. Hiding never deletes data, changes applicability or grants access. Use progressive disclosure for evidence/history, not a giant mandatory form. Styling may follow the host theme without changing field semantics.

UI controls invoke authenticated host-mediated tools with their current scopes. A click is not owner-kind authority, a failed save is not success, and a denial never permits an owner-token or direct-store fallback. Send only explicitly selected necessary context to the host model; opening or editing a form does not automatically transmit all fields, source bodies or search results to a model or another provider. Never place credentials in app HTML or model context.

## Compatibility and rollout

Do not bulk rewrite signed history or previously admitted imports to satisfy a new form. Preserve readable legacy values and annotate their qualification gaps. Add catalog/schema capability negotiation and compatibility tests to the current enforcement-frontier mechanism. Upgrade and validate both peers before enabling the new governed write profile; unsupported writers fail safely instead of admitting nonconforming records or silently stopping sync without a visible state.

Test a synthetic store first, then obtain a consistent backup before any separately authorized data cleanup or schema rollout. No production migration, data cleanup, grant change, deployment, provider enrollment or Praxis repository change is performed by this documentation revision. New capabilities remain planned until exact code, artifact and execution evidence exists.

## Acceptance before implementation is called complete

| Case | Required evidence; focused implementation results are recorded separately |
| --- | --- |
| FC01 Shared catalog | Two independent clients and the App discover the same revision and field meanings. Invalid types/cardinality/endpoints and attempts to mutate the catalog through a data grant fail in the core. |
| FC02 Minimal records | Create a useful person without optional contacts; reject missing required input without partial commits. Reject duplicate retry changes; name matches stay separate unless explicitly resolved. |
| FC03 Missingness and time | Exercise not-recorded, sourced unknown and not-applicable, withheld/conflicted coverage, hiding optional blanks and revealing them again. Round-trip ongoing versus unknown end, month precision and uncertain timezone without invented facts. |
| FC04 Consistent CRUD | Create/read/correct/retract through independent model/CLI and UI paths with equal semantics at a fixed frontier. Preserve per-value evidence, alternatives, correct reclassification and atomic multi-field failure. Test archive only once its core operation is explicitly defined. |
| FC05 Safe edits | Concurrent heads, stale catalog, expired/revoked scopes, denied corrections and capacity refusal preserve state, attribution and history. Retry an interrupted unknown-outcome save safely. Human clicks and client metadata cannot impersonate owner review. |
| FC06 Focused UI | From search results inspect, create, edit and remove a synthetic record/relationship inline, and repeat in an expanded view with the same controls and validation. Test read-only fallback, keyboard/focus, narrow layout, dark/light themes and visible errors without an internal conversation or model selector. |
| FC07 Compatibility | Retain original signed/imported bytes and history; test upgraded peers, unsupported older writes, restart, offline edits, convergence and fresh-identity restore. Rollback limits and any paused sync are explicit. |
| FC08 Data boundaries | Source versions remain immutable; selected UI context never exposes unauthorized fields/credentials or automatically sends whole results to a model. Distinguish retraction/archive from a separately authorized erasure and its backup/replica limits. |

Historical LM and runtime tests retain their original meaning; they do not pass FC01–FC08 or qualify any named host for the new field-driven UI.
