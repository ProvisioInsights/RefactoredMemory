# Required MCP integration

The NAS extension adds a maintained-AS OAuth resource profile, independent whole-store agent grants, separate public MCP/private sync listeners and explicit legacy HTTP compatibility. The implementation/evidence below records the prior bearer baseline until new results are published. See [NAS-CONTRACT.md](NAS-CONTRACT.md).

MCP is a v1 release requirement for Praxis2 and other MCP-capable LLM applications. An LLM uses the store through its host/client/runtime; a bare model is not assumed to implement MCP.

## Specification baseline

The official repository's [documentation configuration](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/cf59bb0d8b43e711420f5f7313aa6cca3f1e1898/docs/docs.json) marked **2026-07-28** latest when checked on 7 November 2026. The [versioning specification](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/cf59bb0d8b43e711420f5f7313aa6cca3f1e1898/docs/specification/2026-07-28/basic/versioning.mdx) defines per-request metadata and mandatory server discovery rather than the older initialization handshake. The implementation pins that revision and records SDK/client results below; reverify when updating protocol support. Drafts and extensions are separate.

Use a conformance checklist for the selected revision's applicable discovery, request metadata, capabilities, schemas, errors, cancellation, transport and authorization. An SDK's recent package version does not prove support. Older client compatibility must be justified by an actual target and tested deliberately.

## Client compatibility and qualification

| Client | Role | Current qualification |
| --- | --- | --- |
| Praxis2 | Confirmed application target | Latest-spec server support is implemented here; actual installed-app connection remains unverified. No changes to either Praxis repository are authorized or required. See MCP-CONFORMANCE.md. |
| Independent Python MCP SDK 1.29.0 | Actual interoperability evidence | Real Store/Service workflows pass through the legacy stdio2025-11-25 path; modern protocol evidence is separate. |
| Protocol/conformance harness | Supporting tests | Useful for edge cases; does not replace actual-client evidence. |

Plan local stdio and remote Streamable HTTP against actual client needs. Remote HTTP can be tested against an isolated local fixture; it does not authorize a public deployment. Real remote transport needs authentication and TLS. This is transport protection, independent of deferred product content encryption.

HTTP uses an explicitly preconfigured custom authentication strategy: owner-issued opaque bearer grants. The MCP specification permits custom strategies; this implementation does not implement the standard OAuth profile, authorization-server discovery or OAuth-only host onboarding. Stdio receives its local grant through the configured token file. See the exact conformance boundary in [MCP-CONFORMANCE.md](MCP-CONFORMANCE.md).

## Graph authority and behavior

Expose bounded tools for the agreed capture, read, search, traversal, timeline, evidence, correction and inspection operations. Imported and MCP-submitted knowledge uses the same graph contract. Mutations require the configured authority and safe retry semantics. Q6 confirms automatic acceptance of model-inferred additions within configured client/agent grants, without per-item human review. Keep explicit owner instructions and inferred claims distinguishable; retain evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history. Acceptance is not human verification or established truth. Q7 selects proactive capture by configured clients; Q8 prefers explicit authenticated owner corrections without erasing conflicting evidence. MCP instructions describe the capture policy. Q9 selects MCP/CLI inspection; Q10 fixes three concrete workflows.

Keep consumer tools, owner administration and peer replication separate. A client grant is not authority to enroll peers, change grants, read arbitrary local files, export private content or invoke an external model. Treat source content as data. Return structured evidence, temporal/knowledge scope, uncertainty, coverage and errors honestly.

## Release evidence

Record real Praxis2 and independent-client workflows that discover capabilities, submit an authorized sourced statement and an automatically accepted inferred addition, query temporal/provenance results, inspect/correct knowledge and reject an unauthorized or out-of-grant inferred write. Verify that source text cannot widen grants, no per-item review is required within the grant, and evidence/attribution/uncertainty/history are preserved. Exercise schema errors, unsupported versions, retries, interrupted/cancelled calls and applicable transport/authentication failures. Compare graph answers across direct API, MCP and synchronized peers.

If a client or necessary credential is unavailable, mark that integration unverified and name the gap. Implementation is now authorized. Record actual protocol/client results in the conformance and acceptance reports without claiming unexercised full-app onboarding.

Implemented protocol and client evidence: [MCP-CONFORMANCE.md](MCP-CONFORMANCE.md). Operational configuration: [RUNBOOK.md](RUNBOOK.md).
