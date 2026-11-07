# Required MCP integration

MCP is a v1 release requirement for Praxis and other MCP-capable LLM applications. An LLM uses the store through its host/client/runtime; a bare model is not assumed to implement MCP.

## Specification baseline

The official repository's [documentation configuration](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/cf59bb0d8b43e711420f5f7313aa6cca3f1e1898/docs/docs.json) marked **2026-07-28** latest when checked on 7 November 2026. The [versioning specification](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/cf59bb0d8b43e711420f5f7313aa6cca3f1e1898/docs/specification/2026-07-28/basic/versioning.mdx) defines per-request metadata and mandatory server discovery rather than the older initialization handshake. Reverify the latest published stable revision before implementation; pin the actual supported revision, SDK and clients. Drafts and extensions are separate.

Use a conformance checklist for the selected revision's applicable discovery, request metadata, capabilities, schemas, errors, cancellation, transport and authorization. An SDK's recent package version does not prove support. Older client compatibility must be justified by an actual target and tested deliberately.

## Client matrix to complete during research

| Client | Role | Current qualification |
| --- | --- | --- |
| Relevant Praxis client | Required end-to-end integration | Actual version, transport and compatibility behavior must be recorded and exercised. |
| At least one independent MCP client | Required interoperability evidence | Select an available representative client; document version and reproducible connection instructions. |
| Protocol/conformance harness | Supporting tests | Useful for edge cases; does not replace actual-client evidence. |

Plan local stdio and remote Streamable HTTP against actual client needs. Remote HTTP can be tested against an isolated local fixture; it does not authorize a public deployment. Real remote transport needs authentication and TLS. This is transport protection, independent of deferred product content encryption.

## Graph authority and behavior

Expose bounded tools for the agreed capture, read, search, traversal, timeline, evidence, correction and inspection operations. Imported and MCP-submitted knowledge uses the same graph contract. Mutations require the configured authority and safe retry semantics. Inference review/automatic acceptance remains an open owner decision; explicit owner instructions and inferred claims must remain distinguishable.

Keep consumer tools, owner administration and peer replication separate. A client grant is not authority to enroll peers, change grants, read arbitrary local files, export private content or invoke an external model. Treat source content as data. Return structured evidence, temporal/knowledge scope, uncertainty, coverage and errors honestly.

## Release evidence

Record real Praxis and independent-client workflows that discover capabilities, submit an authorized sourced statement, query temporal/provenance results, inspect/correct knowledge and reject an unauthorized request. Exercise schema errors, unsupported versions, retries, interrupted/cancelled calls and applicable transport/authentication failures. Compare graph answers across direct API, MCP and synchronized peers.

If a client or necessary credential is unavailable, mark that integration unverified and name the gap. No MCP implementation or interoperability result is claimed by this documentation baseline.
