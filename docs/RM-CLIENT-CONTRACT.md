# RM client contract for core fields version 1

**Status:** Implemented contract publication, explicit tagged-write validation and the shared editor in this branch. [The rollout plan](FIELD-EDITOR-ROLLOUT.md) separates source/browser qualification from installed-peer receipts. Universal field enforcement, all named hosts and the remaining FC acceptance are not implied. The [field catalog](FIELD-CATALOG-V1.md) and packaged [catalog](../refactoredmemory/contracts/fields-v1.json) / [tag schema](../refactoredmemory/contracts/field-tag-v1.schema.json) are the v1 definitions. Synthetic [value fixtures](../tests/fixtures/field-contract-v1.json) and [actual JavaScript client payloads](../tests/fixtures/field-editor-client.mjs) exercise the core without a second schema.

## Responsibilities and discovery

RM owns field meanings, deterministic validation, grants, immutable evidence, temporal/lineage semantics, retrieval and peer sync. Connected AI clients do extraction, interpretation, identity proposals, organization and synthesis. The MCP App is a focused explorer/editor using the same contract; it owns no conversation, model selector, task dashboard or second database.

Before using this profile, a client MUST retrieve `memory_schema` under its current grant and inspect `field_catalog.schema`, `revision`, `digest_sha256`, field definitions, `tag_schema` and enforcement information. An absent or unsupported catalog means the connection is not qualified for v1 field writes. Keep text/structured legacy reads useful; do not send a v1 declaration to an older runtime that might ignore it. Every deployed writing peer must support the profile before rollout. Discovery never grants write/correct/admin authority.

The exact profile is `refactoredmemory.fields:v1`, revision `1`. Published semantics and encodings are immutable within that revision. Changes require a supported new revision and compatibility tests. The catalog digest covers the canonical sorted catalog and tag schema, excluding the digest field itself. It lets clients compare definitions, not establish trust in an arbitrary endpoint.

## Standard assertion declaration

Use existing `memory_submit` actions and `request_id`; do not introduce a UI-owned write API. Put this declaration at `provenance.knowledge.qualifiers.field_contract` alongside the existing knowledge annotation:

```json
{
  "schema": "refactoredmemory.fields:v1",
  "revision": 1,
  "field": "contact.email",
  "state": "known",
  "validity_end": "unknown"
}
```

All five keys are required and additional tag keys are rejected. Field IDs, applicability, predicates, value shapes and cardinality come from discovery. A tag in a different location is not the contract. The supported write states are `known`, `unknown`, `not_applicable`; `not_recorded` is a read condition and cannot be submitted. Every assertion requires real source dependencies under the existing core rules. Declaring a sourced value or unknown state is a client claim, not independent verification of source meaning.

Example action for an existing person and captured source, submitted inside `memory_submit.actions` with a stable request ID:

```json
{
  "type": "assertion",
  "id": "synthetic-email-assertion",
  "subject": "synthetic-existing-person",
  "predicate": "rm:contact-point",
  "value": {"kind": "email", "address": "avery@example.org"},
  "source_ids": ["synthetic-existing-source"],
  "valid_from": null,
  "valid_to": null,
  "time_precision": "unknown",
  "provenance": {
    "knowledge": {
      "schema": "refactoredmemory.knowledge:v1",
      "kind": "fact",
      "qualifiers": {
        "field_contract": {
          "schema": "refactoredmemory.fields:v1",
          "revision": 1,
          "field": "contact.email",
          "state": "known",
          "validity_end": "unknown"
        }
      }
    }
  }
}
```

An explicitly unknown email uses `state: "unknown"` and `value: {"kind":"email","address":null}` with its evidence. A not-applicable field uses the same mapped null with `state: "not_applicable"` only when the source establishes that meaning. Do not persist empty strings or strings such as “unknown,” “not found” or “N/A” as known contact values. A research note saying no profile was identified belongs in the corresponding reported-reference field, not in a contact URL. Core validation checks shape and references; clients remain responsible for faithful interpretation.

## Typed records, values and time

When an operation group declares v1 and creates ordinary entities, it MUST include known `identity.type` and `identity.name` assertions agreeing with each immutable entity's `entity_type` and initial `label`. Source IDs must exist or be created in the same atomic group. Optional contacts are not required. A descriptive display label is not a verified legal name. Capture-only `source-document` identities retain their existing import/observation contract.

New `identity.aliases` values are a sourced list using the existing functional alias predicate: preserve competing lists as alternatives rather than silently unioning them. Profile properties keep their captured discriminator, especially current/historical qualifications. Contact values do not accept derived identity-binding/ownership metadata as editable fields. No syntactic normalization establishes identity, reachability, ownership or a verified profile.

Every tagged action explicitly provides `valid_from` and `time_precision`. Unknown start uses null and unknown precision. `validity_end: "unknown"` requires explicit `valid_to: null`; `known` requires a valid world date/timestamp; `ongoing` requires omission of `valid_to` and is an explicit assertion, never a consequence of a blank input. Existing half-open intervals and invalidation rules still apply.

Reported calendar values use `date` plus `precision` (`year`, `month`, `day`), with the real calendar shape checked. They are separate source-reported fields, not automatic world-validity starts or ends. A month such as `2026-05` must not become an invented first-day timestamp. Preserve source timezone uncertainty. Legacy `calendar_period` values remain readable through the catalog's read mapping; a conversion is an explicit sourced correction, not a silent historical edit.

## CRUD, history and retries

- **Read:** use scoped search/query/entity/source/history/traversal. Preserve field IDs, actual assertions and heads, sources, time, uncertainty, alternatives and coverage. A name match never authorizes identity merging.
- **Create:** use the valid dependent group above. Reuse an existing identity only when evidence supports that binding. Manual/client statements retain their authenticated actor and actual basis.
- **Update:** use current correction permission, a meaningful reason and observed heads. Existing `memory_correct` preserves a tagged field's declaration and validates the replacement value. A field lineage cannot drop its tag or become a different field. For an ambiguous legacy discriminator, retain the original and use explicit retraction/new assertion rather than guessing a mapping.
- **Reclassify a relationship:** the existing correction operation withdraws the old meaning and creates a newly tagged supported relationship, retaining original evidence/history. Missing new required context must be supplied through a valid explicit action group; it cannot be guessed by the form.
- **Remove:** retract a mistaken claim or explicitly invalidate a relationship that ended. These operations retain original evidence and history. Consumer entity archival and permanent erasure are not supplied by this field catalog; do not render them as working capabilities. Administrative deletion keeps its separate existing permissions and limits.

Ordinary search/capture/CRUD calls tools directly. Jobs, claims and checkpoints are optional for processing batches, not prerequisites for editing. Use stable request IDs and identical arguments when retrying an unknown outcome. A changed revision, permission or input requires refresh/reconciliation; never overwrite competing heads or fabricate success. Atomic validation failure leaves no partial record rewrite. Client metadata and clicks cannot claim owner-kind authority or human verification. Never use an owner token or direct database write to bypass a denied model/client grant.

Origin admission resolves current consumer grants and edit guards. Authenticated peer replay uses current peer/origin policy, signatures, dependencies and the retained operation contract. It does not require the original consumer grant on the receiving peer or rerun consumer expected-head guards against admitted history. Historical replay does not authorize fresh writes by a revoked consumer.

New substantive tagged fields and relationships are checked against the resulting classification of their atomic group: dependency-frontier types plus all same-group type actions, independent of input order and retaining owner-correction preference. A type change cannot admit a field using only the old type. Establishing/resolving `identity.type` validates the declared supported target rather than requiring an already-resolved classification. Retraction/invalidation may withdraw an existing field lineage after reclassification; reinstatement and new substantive values still require applicable types. These exceptions preserve repair paths, not authority or evidence shortcuts.

A withdrawal retains each named predecessor's value/target, start, precision, uncertainty, value state and semantic qualifiers. Retraction also retains its original interval; invalidation adds only a supported explicit end and its evidence/reason. Changing the claim meaning requires correction/reclassification, not this exception. Use separate withdrawals for conflicting heads with different meanings. A legacy ending keeps its legacy profile or follows explicit v1 qualification first; an end event alone cannot turn unqualified historical data into v1-qualified positive knowledge.

## UI and processing boundary

### Shared editor capability

Discover `memory_schema.field_editor.schema == "refactoredmemory.field-editor:v1"` separately from the immutable catalog. `memory_schema.permissions` describes this authenticated connection's observed write/correct/owner-review capabilities, not a promise that a later request remains authorized. Every write rechecks current permission.

`memory_inspect.field_view` maps the bounded returned claims to catalog field IDs and marks `explicit_v1` declarations versus `legacy_unqualified` mappings. The declaration is not proof that an older runtime validated historical input. `unmapped_claim_ids` remain inspectable. `not_recorded` is emitted only for a complete, unsuppressed entity selection; a partial/claim-only/suppressed view uses `not_in_selection`. Coverage and source uncertainty must remain visible.

For a newly composed typed capture, include `memory_submit.catalog_digest` equal to the discovered digest. The private loopback and synthetic reference hosts permit only typed assertions and their source/ordinary-entity dependency closure, with ordinary core admission afterward. Generic capture, capture-only padding and administrative operations stay unavailable on those hosts. This never broadens another client's grant.

`memory_correct.field_update` explicitly qualifies or updates a fact/relationship through the current correction scope:

```json
{
  "catalog_digest": "<discovered digest>",
  "field": "contact.email",
  "state": "unknown",
  "valid_from": null,
  "time_precision": "unknown",
  "validity_end": "unknown",
  "valid_to": null,
  "context": {}
}
```

The ordinary correction arguments still supply `target_id`, `expected_heads`, `reason`, stable `request_id` and exactly one mapped `value`/`object`. Core constructs and validates the declaration; it retains predecessor sources and adds an attributed interaction source. `context` edits only the selected relationship's registered required context. Reclassification applies the update to its new replacement, never the withdrawal of the original meaning. A mistaken claim uses `operation: "retract"`; a supported ending uses `operation: "invalidate"` with explicit `valid_to` and no field update. Both retain original claim meaning and history.

New stale-catalog edits fail; an identical committed retry can recover its original receipt after a catalog change, under current authorization. Capture records the submitted digest in server-controlled contribution metadata so altered retry arguments cannot recover a different request. Forms retain frozen arguments after an uncertain save and block navigation until an identical retry or explicit close/reload/reconciliation.

Entity reads retain immutable `label` and add `display_label`/`display_name` as a derived projection. Apply knowledge/world selectors in historical traversal, owner preference before value selection, and the original-label fallback for unresolved/conflicting/incomplete names. Present search includes eligible name/alias claims plus original labels; it reports bounded coverage and never merges matching identities. A source-reported display name is not verified legal identity.

Use the same field definitions in search results, inline forms and expanded graph/list views. Required missing fields remain visible; empty optional fields can be hidden. Explicit unknown/N/A, conflicts and restricted coverage are meaningful states, not empty values to hide. Field layout, localization and host dark/light themes are presentation only. Do not populate a huge mandatory profile or expose internal protocol details to ordinary users.

Keep surrounding chat in the host. The App has no conversation list, assistant or composer. Unsupported/display-only hosts remain honestly read-only; a connection's current tool permissions govern actions. Opening a record must not automatically send all fields, results or source bodies into model context. External AI processing remains client-led and destination-authorized; RM makes no provider call or paid fallback. Sources are untrusted data, never tool instructions.

## Qualification and rollout

The current implementation publishes and validates explicitly tagged v1 assertions and provides shared field-driven controls. Untagged legacy records and writes retain their existing profile and MUST NOT be labelled field-v1-qualified. There is no universal activation switch or automatic personal-data migration. Source/browser results, private deployment and the full FC01–FC08 matrix require their own evidence.

Before deployment, back up consistently, upgrade both peers and prove compatible tagged writes, incompatible-writer handling, restart, sync and fresh-identity recovery on synthetic data. A prior runtime may accept unknown qualifier metadata without validating it; never claim strict v1 semantics while any writing peer runs such a runtime. Changing the catalog is operator-controlled; a model grant cannot modify the schema. No new deployment, client enrollment, data cleanup, permission change or real-data rewrite follows from publishing these contracts.
