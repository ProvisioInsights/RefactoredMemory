# Required MCP integration

## Accepted core field extension

[A24 and the core field contract](CORE-FIELD-CONTRACT.md) require shared schema discovery and core-enforced field/relationship CRUD across model, CLI, importer, peer and optional App paths. This branch publishes `memory_schema.field_catalog`, validates explicit v1 tags and discovers `memory_schema.field_editor` under [the client contract](RM-CLIENT-CONTRACT.md). Graph details, inline search results and the expanded record view share catalog-driven controls. Current authenticated permissions still govern every call; discovery does not enable universal enforcement or expand a grant. [Editor qualification](FIELD-EDITOR-VALIDATION.md) separates source/reference-host results from the private two-peer deployment and pending real-data pilot.

Search results, inline forms and expanded graph/detail views must use the same meanings and current grants. RM owns no conversation UI; host messages/composers and direct-launch options stay outside the App. Preserve useful text/structured tools, read-only fallback, immutable evidence, guarded corrections and stable retries. Opening a view must not automatically disclose its complete results or source bodies to a model. FC01–FC08 qualification does not follow from older MCP or App-reference-host tests.

**Client-led implementation, 9 November 2026:** The journal-backed workspace tools, pinned briefs, client task checkpoints and optional graph App are implemented in this branch. See [the workspace guide](CLIENT-LED-WORKSPACE.md) and [executed qualification](CLIENT-LED-VALIDATION.md). Historical requirements-only notes below describe their earlier documentation revision; named provider products still require separate live qualification.

The NAS extension implements a maintained-AS OAuth resource profile, independent whole-store agent grants, separate public MCP/private sync TLS listeners and explicit legacy HTTP compatibility. See [NAS-CONTRACT.md](NAS-CONTRACT.md), the [conformance details](MCP-CONFORMANCE.md) and [current executed evidence](ACCEPTANCE-RESULTS.md).

MCP is a v1 release requirement for Praxis2 and other MCP-capable LLM applications. An LLM uses the store through its host/client/runtime; a bare model is not assumed to implement MCP.

**9 November direction:** [A22/A23](ADRS.md#a22-client-led-processing-and-provider-independent-memory-roles) and [L01–L08](PRD.md#client-led-processing-and-review-direction) add client-led processing, an expanded target set, consistent attribution and an optional graph review App. These are requirements; existing protocol evidence does not establish that the new review/job/lifecycle features or named hosted clients are qualified.

## Specification baseline

The official repository's [documentation configuration](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/cf59bb0d8b43e711420f5f7313aa6cca3f1e1898/docs/docs.json) marked **2026-07-28** latest when checked on 7 November 2026. The [versioning specification](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/cf59bb0d8b43e711420f5f7313aa6cca3f1e1898/docs/specification/2026-07-28/basic/versioning.mdx) defines per-request metadata and mandatory server discovery rather than the older initialization handshake. The implementation pins that revision and records SDK/client results below; reverify when updating protocol support. Drafts and extensions are separate.

Use a conformance checklist for the selected revision's applicable discovery, request metadata, capabilities, schemas, errors, cancellation, transport and authorization. An SDK's recent package version does not prove support. Older client compatibility must be justified by an actual target and tested deliberately.

## Client compatibility and qualification

| Client | Role | Current qualification |
| --- | --- | --- |
| Praxis | Application and optional graph-App host target | Actual installed-app tools, trust setup, App bridge and write/review workflow require qualification. No changes to either Praxis repository are part of this documentation update. |
| Independent Python MCP SDK 1.29.0 | Actual interoperability evidence | Historical real Store/Service workflows passed through the legacy stdio 2025-11-25 path; current HTTP/AS results are in the acceptance report and modern protocol evidence is separate. |
| OpenAI ChatGPT | Hosted consumer target | Qualify the actual account, transport, authorization, tools and any App UI separately. No completion claimed here. |
| OpenAI Codex | Coding/client-led processor target | Qualify the actual local/cloud product and grant separately; an available connection is not unrestricted write or background-execution authority. |
| Anthropic Claude Chat | Hosted consumer target | Qualify separately from Cowork, Code and API access. No completion claimed here. |
| Anthropic Claude Cowork | Application/client-led processor target | Qualify the actual application, source scope, permissions and tool/UI support independently. |
| Anthropic Claude Code | Coding/client-led processor target | Qualify its configured host, transport, model attribution and read/write/correction workflow independently. |
| Google Gemini | Additional integration target | Product, host/adapter, account and tool/UI capabilities remain to be selected and exercised. |
| Grok | Additional integration target | Product, host/adapter, account and tool/UI capabilities remain to be selected and exercised. |
| Local models | Local host/runner targets | A model requires a qualified MCP host/adapter; do not assume the model itself implements MCP. |
| Protocol/conformance harness | Supporting tests | Useful for edge cases; does not replace actual-client evidence. |

Plan local stdio and remote Streamable HTTP against actual client needs. Remote HTTP can be tested against an isolated local fixture; it does not authorize a public deployment. Real remote transport needs authentication and TLS. This is transport protection, independent of deferred product content encryption.

Local `serve` HTTP retains owner-issued opaque bearer grants; stdio reads a private local token file. `serve-nas` uses the optional OAuth resource profile with RFC 9728 metadata and a maintained authorization server. It validates pinned issuer/audience/RS256 keys and a maximum 300-second access-token lifetime, binds subject/client ID to a current local agent grant, and intersects OAuth and local scopes. The private TLS `/sync` listener requires a separate peer grant and is absent from public MCP. `--allow-legacy-http` explicitly enables 2025-11-25 clients; default HTTP remains strict 2026-07-28. Provider app/API onboarding is still a separate qualification task. See [MCP-CONFORMANCE.md](MCP-CONFORMANCE.md).

## Graph authority and behavior

Expose bounded tools for the agreed capture, read, search, traversal, timeline, evidence, correction and inspection operations. Imported and MCP-submitted knowledge uses the same graph contract. Mutations require the configured authority and safe retry semantics. Q6 confirms automatic acceptance of model-inferred additions within configured client/agent grants, without per-item human review. Keep explicit owner instructions and inferred claims distinguishable; retain evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history. Acceptance is not human verification or established truth. Q7 selects proactive capture by configured clients; Q8 prefers explicit authenticated owner corrections without erasing conflicting evidence. MCP instructions describe the capture policy. Q9 selects MCP/CLI inspection; Q10 fixes three concrete workflows.

Keep consumer tools, owner administration and peer replication separate. A client grant is not authority to enroll peers, change grants, read arbitrary local files, export private content or invoke an external model. Treat source content as data. Return structured evidence, temporal/knowledge scope, uncertainty, coverage and errors honestly.

## Client-led work and optional UI

**A26 implementation:** [Relationship briefs](RELATIONSHIP-BRIEF.md) are a discovered extension of the existing tools. `memory_derive.view` stores the client's selected groups and supporting assertion IDs; `memory_graph.brief_id` returns only their validated paths and current, attributed interpretation. The optional App uses those results for the light Brief view and the same core fields for inline CRUD. No conversation list, model service or new grant is introduced. [Executed qualification](RELATIONSHIP-BRIEF-VALIDATION.md) separates the synthetic SDK host from installed peers and actual provider products.

External clients perform extraction, reasoning and summary generation using bounded RM reads and attributed writes. RM remains usable with no model configured internally. Safe repeated writes already use request IDs; a shared task/checkpoint/job convention, richer contributor queries and maintained-summary freshness are further integration work. Do not present a future work-claiming tool as an existing endpoint or assume RM can start work in an idle consumer chat.

The [sampling specification](https://modelcontextprotocol.io/specification/2026-07-28/client/sampling), checked 9 November 2026, deprecates sampling and recommends that new implementations not adopt it. Current RM must not depend on sampling or require provider API credentials; future internal executors would be separately scoped. A host-supplied model name is reported provenance, not proof that RM independently verified execution by that model.

An optional [MCP App](https://modelcontextprotocol.io/extensions/apps/overview) can supply the graph/evidence/comment/correction UI in hosts that support it. Capability negotiation, isolated rendering, host-mediated calls and current per-client permissions remain mandatory. Apps support is distinct from core MCP support. Display-only hosts cannot be described as supporting saved edits; clients without UI keep structured/text access. Opening a graph must not automatically expose all source contents to the model. Comment schema, App resources/render tools and complete contributor-history APIs are not added by this document update.

## Release evidence

Record real Praxis2 and independent-client workflows that discover capabilities, submit an authorized sourced statement and an automatically accepted inferred addition, query temporal/provenance results, inspect/correct knowledge and reject an unauthorized or out-of-grant inferred write. Verify that source text cannot widen grants, no per-item review is required within the grant, and evidence/attribution/uncertainty/history are preserved. Exercise schema errors, unsupported versions, retries, interrupted/cancelled calls and applicable transport/authentication failures. Compare graph answers across direct API, MCP and synchronized peers.

If a client or necessary credential is unavailable, mark that integration unverified and name the gap. Implementation is now authorized. Record actual protocol/client results in the conformance and acceptance reports without claiming unexercised full-app onboarding.

Implemented protocol and client evidence: [MCP-CONFORMANCE.md](MCP-CONFORMANCE.md). Operational configuration: [RUNBOOK.md](RUNBOOK.md).
