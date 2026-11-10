# Relationship brief contract

**Owner-selected direction:** 9 November 2026. The light Relationship Brief is the visual target: a concise answer, a small grouped set of relevant records, inline standard fields, and an evidence-backed explanation of the selected connection. This document precedes implementation. See [A26](ADRS.md#a26-answer-focused-relationship-briefs).

## Product behavior

**10 November usability refinement:** default to a compact answer and named links. Keep fields, source excerpts, qualifiers, provenance and the selected graph closed until requested. A record opens the shared fields; evidence/history remain one tab away, and the connection explanation is an explicit action. Avoid repeating the same reason in the row, sidebar and warning copy. Material status, ambiguity and stale-state warnings still apply. This changes presentation and read timing, not saved data, grants or the wire contract.

Explore opens a brief rather than drawing every available neighbor. The selected record can be inspected and corrected inline using the existing field contract. A small connection path explains why that record appears. Evidence and history remain available. Records remains the general identity browser. No RM conversation list, chat composer, model picker or automatic source sharing is added.

An external client selects the useful records and prepares the explanation. RM validates references, bounded paths, pinned inputs and current access. It neither calls a model nor treats client-written prose as verified fact. Without a prepared brief, show a plainly labeled bounded collection of direct connections; do not invent a question answer or claim exhaustive relevance.

## Wire contract

`memory_schema.relationship_brief.schema` discovers `refactoredmemory.relationship-brief:v1` independently of the unchanged field-v1 catalog.

`memory_derive` accepts an optional `view` with that schema and `groups`. Each group has a short `title` and `items`. Each item has `entity_id`, `claim_ids` and `why`. At most four groups, six total items and 24 distinct claims are allowed. Each item must have a real path of at most two object-relationship hops from the brief's subject to its entity, using only that item's named claims. Additional value claims must belong to the supporting path. Identity matches and free text do not create graph edges. Repeated identities are rejected. No unrequested neighbors are fetched to construct the path.

All selected claims must be named assertion inputs to the existing derived artifact and visible at its declared input frontier. Inputs retain their actual hashes, evidence, authenticated connection and separately reported processor metadata. Group titles, `why`, artifact title and summary remain attributed client interpretation. They confer no owner-review status, grants or factual verification. Existing idempotency, task input boundaries and correction history remain in force.

`memory_graph(start=..., brief_id=...)` reads the exact active derived revision for that subject. It rehydrates the named records/claims and checks current input freshness. It returns the existing graph envelope plus `brief` metadata. Source text remains behind explicit evidence reads. A stale brief returns no client explanation or selected paths; the interface requests refresh and offers ordinary current connections. An edit does not silently transfer an old explanation to a new claim revision.

Without `brief_id`, the existing bounded graph remains supported. Its rows are direct recorded connections, with actual predicate, claim/source references and reported validity; these are not client-ranked answers. Both paths retain alternatives, unknown dates, legacy qualification and explicit partial coverage. Source reference counts never imply independent corroboration or current investor status.

### Client example

After discovery and authorized reads of these synthetic existing identities and claims, a client can submit:

```json
{
  "subject": "project",
  "title": "Who is connected?",
  "text": "Alex participates in this project; Jamie also introduced Alex.",
  "inputs": [
    {"kind": "assertion", "id": "alex-project"},
    {"kind": "assertion", "id": "jamie-project"},
    {"kind": "assertion", "id": "intro"}
  ],
  "input_frontier": {"synthetic-peer": 7},
  "view": {
    "schema": "refactoredmemory.relationship-brief:v1",
    "groups": [{"title": "Selected people", "items": [{
      "entity_id": "alex",
      "claim_ids": ["alex-project", "jamie-project", "intro"],
      "why": "A named participant with an introduction."
    }]}]
  },
  "reported": {"application": "Example client", "model": "client-reported model"},
  "request_id": "synthetic-relationship-brief-1"
}
```

Replace the frontier with the actually observed causally closed frontier; the placeholder is not executable seed state. The named claims must encode `alex`–`project`, `jamie`–`project` and `jamie`–`alex` paths. RM pins their actual hashes. Read the resulting derived assertion with `memory_graph` arguments `{"start":"project","brief_id":"<returned assertion ID>"}`. Keep that exact revision and stable request ID for retries; a replacement is an explicit new artifact or authorized correction, never a silent overwrite.

## Presentation and safety

- Render all client/source text as inert text. No raw HTML, executable links, hidden instructions or automatic model-context forwarding.
- Keep the default selected path small; expand or change focus deliberately. Explain actual predicate/direction and distinguish recorded links from the client's explanation.
- Reuse the same fields, missing states, current-grant checks and immutable corrections in inline/expanded views. Preserve exact-request retry and navigation locks across every new control and incoming host result.
- Preserve host light/dark themes; use the selected ivory/teal layout as the light baseline. Narrow layouts stack the explanation below the result without hiding actions.
- Save no example identities, sources, briefs or corrections into a personal store. Synthetic commissioning has its own fixture and host.

## Acceptance

RB01: independently discover the capability; validate saved view bounds, actual paths and exact input membership. Reject disconnected, duplicate, stale, deleted and out-of-task references atomically.

RB02: authenticate every read/write, retain authenticated and reported attribution separately, and expose no owner authority through a brief. Preserve existing derived-artifact retry semantics.

RB03: match the selected light visual hierarchy with grouped rows, inline standard fields and a small selected path. All search, brief selection, filters, record expansion, evidence, history and edit controls work or are explicitly unavailable under the current grant.

RB04: keep partial/default views honest; preserve unsupported legacy finance terms and unknown dates. Source counts and client prose never become verification.

RB05: after correction, stale explanations disappear; old source revisions remain historical. Test unknown save outcomes, late reads/host messages and identical retries without losing the form.

RB06: qualify synthetic desktop/narrow/dark/empty/display-only states, exact packaged UI, existing tests and deployment identities separately. A screenshot, test or source commit alone does not qualify a provider host or personal-store rollout.
