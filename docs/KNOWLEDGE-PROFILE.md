# Knowledge profile and migration boundary

The versioned `refactoredmemory.knowledge:v1` annotation restores structured
knowledge meaning without replacing immutable identities, signed operation
history, evidence, or the existing assertion envelope. The annotation lives in
`provenance.knowledge`; actor authority continues to come from the authenticated
operation, never from imported metadata. A successful write is not human
verification.

`memory_schema` publishes the actual kinds, categories, canonical endpoint
types, predicate cardinalities and endpoint rules. `memory_search_entities`
returns named identity candidates without merging equal labels. Entity reads
retain `entity_type` and expose separate canonical classification candidates.
`rm:canonical-type` is a sourced fact, not an in-place edit of the identity.

For example, a relationship annotation can carry:

```json
{"schema":"refactoredmemory.knowledge:v1","kind":"relationship",
 "category":"affiliation","cardinality":"multi-valued",
 "qualifiers":{"role":"advisor"}}
```

The profile separates `fact`, `relationship`, and `observation`. `has-type`
classifies what something is; `about` describes its subject matter. Relationship
endpoint types and categories are validated against the published contract.
Several values of a multi-valued predicate are not competing alternatives;
lineage conflicts are still returned. Unknown dates remain unknown.

New generic fact meanings use namespaced predicates. New relationship meanings
require a reviewed contract revision. A recovery annotation may retain legacy
context and explicit unresolved fields; those do not establish that the legacy
claims were independently verified or remain true today.

Captured `source-document` identities are exposed as canonical `observation`
endpoints, while their immutable physical type and text remain unchanged. The
additive `mentions` predicate connects an observation to a known entity. Its
qualifiers must distinguish header-reported participants and explicit source
links from inferred business relationships. A mention establishes neither an
investment, an introduction, nor employment. Source/evidence records themselves
do not become graph endpoints. Capture-layer classification and mention edges
are labeled `qualifiers.layer = capture` so they can be counted separately from
business relationships.

Observation parts can use `part-of` to point at the first captured part of the
same source version. This uses the existing same-kind composition rule; it does
not merge different source versions. Commit type-recovery facts before new
typed relationships that depend on them.

## Local operator enforcement

After a consistent backup, compatibility checks on every peer, and isolated
validation, the local operator can run:

```sh
python -m refactoredmemory --db /absolute/private/memory.sqlite3 knowledge-schema
python -m refactoredmemory --db /absolute/private/memory.sqlite3 knowledge-enforce
```

Enforcement records the acknowledged frontier. Older signed operations remain
replayable; newly introduced structured claims require profile annotations and
new entities require canonical types or `source-document`. Raw `content`
capture remains an observation and does not invent relationships. New incoming
peer operations are checked too, so an unupgraded writer can pause sync rather
than silently introduce untyped structured records. Upgrade both peers before
enabling this policy. The local policy is not a consumer MCP mutation.

A connection-local profile capability and persisted insertion trigger also
block already-open older writers. Their reads continue; new writes fail closed
until the client reconnects to the upgraded runtime. This is a compatibility
barrier for trusted local application connections, not an access boundary
against a local operator able to modify the database or runtime itself.

The policy is retained across the supported fresh-identity restore procedure.
Restore still revokes old consumer and peer admissions. A code rollback must
retain the semantic enforcement implementation; older code does not understand
this local policy. Do not roll a peer database backward in place.

Restore streams operation payloads instead of retaining the complete journal
in memory. The Linux regression restores more than 256 MiB of journal data
under a 256 MiB address-space limit; historical signatures and projection
equality are still verified.

Queries accept `knowledge_kind`, `category`, and optional `excerpt_chars`
(100 to 4096). Excerpt mode omits the large `content` value and returns its
original-character offset and source references. It does not remove full text.
Legacy assertions are labeled `legacy-unannotated`; readable does not mean
schema-qualified. Counts of imported records are not counts of reviewed facts.

## Restoring legacy context

An Atlas relationship can have both a target and a value containing attributes.
The original RM import retained the target but did not project that value.
Recovering explicit attributes therefore uses source-linked corrections of
active heads, with deterministic request IDs and unchanged subjects, predicates,
targets, world-time values and importer authority. Retractions and superseded
claims stay inactive. Missing upstream evidence bytes, ambiguous identity
versions, unresolved endpoint types and invalid dates remain review items.

Pin the source contract revision, save an outcome for every input record, test
the restoration against an independent isolated store, and retain a consistent
pre-change backup. Never treat plaintext preservation alone as semantic parity,
or turn a proposed introduction or conditional investment into a completed act.
