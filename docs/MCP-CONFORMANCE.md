# MCP implementation and qualification

The NAS extension in [NAS-CONTRACT.md](NAS-CONTRACT.md) is implemented: optional maintained-AS OAuth resource verification, separate public/private TLS listeners and explicit legacy HTTP compatibility. [Acceptance evidence](ACCEPTANCE-RESULTS.md) records current executed checks and keeps historical baseline, local synthetic tests and unqualified real apps/devices distinct.

Verified 7 November 2026 against the official specification at commit
[`cf59bb0d8b43e711420f5f7313aa6cca3f1e1898`](https://github.com/modelcontextprotocol/modelcontextprotocol/tree/cf59bb0d8b43e711420f5f7313aa6cca3f1e1898).
The official documentation configuration identifies **2026-07-28** as the latest
published stable revision. RefactoredMemory implements its base protocol over
stdio and stateless Streamable HTTP. Local grants and the optional OAuth resource
profile are described below. Stdio compatibility and the opt-in
`--allow-legacy-http` profile implement the **2025-11-25** initialization lifecycle
for existing clients; modern metadata is still independently validated.

## Selected implementation

The server transport uses Python's standard library. No runtime MCP SDK installation
is required. OAuth verification uses the declared optional PyJWT/cryptography
dependencies. CI installs pinned test dependencies; tests never install software
themselves. The independent Python `mcp` SDK **1.29.0** uses
the 2025-11-25 lifecycle, so it supplies a real independent-client test of the
legacy stdio path. Its installed version does not establish support for the newer
revision. The modern path is checked directly against official protocol rules and
the official JSON Schema; those checks are protocol evidence, not another real
client integration claim.

`Dispatcher(service).dispatch(message, token)` uses `Service.authenticate` on
every request. `Service.call` additionally checks the tool's current grant.
Protocol `clientInfo`, `clientCapabilities`, source text and submitted actor
fields do not create authority. `run_stdio(service, token)` binds the process to
an explicitly configured local grant. `make_handler(service, ...)` returns the
HTTP handler, allowing the host to compose the separate `/sync` endpoint.

The server publishes tools and instructions for proactive capture within grants,
source-linked retrieval, history and corrections. Capture is initiated by the
connected client; the server does not observe arbitrary conversations or execute
an external model. Acceptance remains distinct from human verification.

## Authorization profile and interoperability boundary

The latest specification expressly permits alternate authentication strategies.
The [base protocol Auth section](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/cf59bb0d8b43e711420f5f7313aa6cca3f1e1898/docs/specification/2026-07-28/basic/index.mdx#auth)
says HTTP implementations **SHOULD** conform to its authorization framework and
that clients and servers **MAY** negotiate their own custom authentication and
authorization strategies. The [authorization requirements](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/cf59bb0d8b43e711420f5f7313aa6cca3f1e1898/docs/specification/2026-07-28/basic/authorization/index.mdx#protocol-requirements)
also state that authorization is **OPTIONAL** for MCP implementations, and that
stdio implementations **SHOULD NOT** use that HTTP authorization framework and
should retrieve credentials from the environment.

Two explicit authentication profiles are implemented. Local stdio and the local
`serve` profile use owner-issued opaque grants. Stdio reads its grant from
`REFACTOREDMEMORY_TOKEN` or a private token file; local HTTP uses the Authorization
header. These local grants remain a custom strategy, without OAuth discovery.

The `serve-nas` public listener uses `OAuthAuthenticator` and publishes RFC 9728
protected-resource metadata at `/.well-known/oauth-protected-resource/mcp`.
Its Bearer challenge includes `resource_metadata`; metadata names the pinned
resource, maintained authorization server, header transport and supported scopes.
Login, authorization-code/PKCE processing, client registration and token issuance
belong to that maintained server. RefactoredMemory does not implement a password
or token issuer. The supplied Keycloak reference deployment is separate from
actual hosted-app qualification; see [deployment](NAS-DEPLOYMENT.md).

The resource validates RS256 signatures against administrator-selected local
JWKS, exact issuer/resource audience, access-token type, required issued/expiry
times and a maximum 300-second lifetime. The default 5-second clock skew can be
configured up to 30 seconds. It never fetches token-selected key URLs. A signed
subject and client ID must map to a private local **agent** grant; owner and peer
grants cannot bind. `memory:read`, `memory:write` and `memory:correct` are intersected
with that grant's current local scopes. Local revocation takes effect on the next
request, including historical queries. Bindings require restart; JWKS and private
grant files are reread on each call for controlled rotation.

Missing/invalid credentials return 401. Valid bound tokens missing the requested
OAuth scope return 403 `insufficient_scope` with the required scope. A current
local grant restriction remains a denied tool operation; obtaining a wider token
cannot override local policy. The resource profile accepts the documented signed
access-token forms, not arbitrary OIDC ID tokens or every issuer format.

The public listener never serves peer `/sync`; the private TLS listener accepts
only current peer-scoped grants. Query-string tokens, protocol metadata and source
content cannot create authority. An implemented OAuth resource profile alone does
not prove a provider's registration, callback or account-entitlement behavior.
Actual Praxis2, ChatGPT and Claude app/API connections remain unqualified until
those clients complete their own synthetic onboarding and tool workflow.

## Applicable conformance checklist

| Contract | Implemented behavior and verification |
| --- | --- |
| Modern request metadata | Every request requires `params._meta["io.modelcontextprotocol/protocolVersion"]` and `clientCapabilities`. Missing fields return `-32602`; unsupported versions return `-32022` with `supported` and `requested`. `clientInfo` is optional and never trusted for permissions. Prior requests do not establish modern context. |
| Discovery | `server/discover` returns supported versions, tools capability, server identity, usage instructions, `resultType: complete`, `ttlMs: 0` and `cacheScope: private`. |
| Tool catalog | Deterministic bounded `tools/list`; current authorization is checked even for listing. One page, invalid cursors rejected. No list-change capability is advertised. Tool input schemas use JSON Schema 2020-12. Capture exposes strict entity, source and assertion alternatives through `oneOf`, including evidence, relationships, corrections, temporal fields, provenance and uncertainty. The service enforces its published finite schema keywords, including `oneOf`, `const`, `enum` and `uniqueItems` with JSON equality that distinguishes booleans from numbers. Semantic references and permission checks remain server responsibilities. Arbitrary caller schemas and external `$ref` resolution are not accepted. |
| Tool results and errors | Success returns text plus structured content. Domain validation and denied tool operations return `isError: true`; unknown tools return `-32602`, unknown methods `-32601`. Internal exceptions, tokens, raw rejected payloads and stack traces are not returned. |
| Result schema | Modern discovery, list and call results were checked with the installed JSON Schema validator against official `schema/2026-07-28/schema.json` (blob `0b9ba317f95c3bc4b44724d65790f7aaaf557dbb`). Results carry `resultType` and server metadata. |
| Streamable HTTP | `POST /mcp`, one request per body, JSON response; clients must accept JSON and SSE. JSON single-response mode is supported without advertising notification streams. GET `/mcp`, DELETE and OPTIONS return 405; only the configured OAuth metadata GET is public. No protocol sessions are minted; session/resumption headers do not establish context. |
| Header/body consistency | Validate required `MCP-Protocol-Version`, `Mcp-Method` and applicable `Mcp-Name`; decode the specified Base64 sentinel before comparison. Missing, duplicate or mismatched fields are rejected before dispatch with `-32020`/HTTP 400. No custom parameter headers are advertised. |
| HTTP status | Unsupported revision/invalid metadata/header mismatch: 400; unknown method: 404; absent/revoked bearer credential: 401; forbidden Host/Origin: 403. Accepted notifications return 202 with no body and cannot invoke graph tools. |
| Local and remote access | Numeric loopback/local host binding is the default. Present Origin must be explicitly allowed; Host must name the local endpoint or an explicitly allowed host. Non-loopback requests require a TLS socket. The local-grant and optional OAuth resource strategies are specified above; live provider onboarding remains separate. |
| stdio | Strict newline-delimited JSON, no nonprotocol stdout. Reject duplicate keys, non-finite values, invalid IDs, oversized input and response bodies. Bounded work queue and worker count. EOF drains bounded work and exits. |
| Cancellation | stdio cancellation suppresses further response output and skips queued work. Already committed atomic writes are not undone; retry with the same application `request_id`. The HTTP server uses final JSON responses and starts no SSE stream to cancel. Client disconnect may leave a durable write with an unknown acknowledgment, so the same retry rule applies. |
| Legacy compatibility | Stdio supports `initialize` followed by 2025-11-25 tools/list, tools/call and ping. Opt-in `--allow-legacy-http` supports that lifecycle on HTTP; strict modern HTTP remains the default. Modern metadata requests remain independently validated. No protocol session is used as authorization. |
| Unadvertised features | Resources, prompts, sampling, elicitation, roots, subscriptions, tasks, progress streams and custom extensions are not advertised. No server-to-client request or model invocation is needed for the supported tools. |

The implementation bounds incoming messages at 2 MiB, outgoing messages at 4 MiB,
stdio outstanding requests at 32 with four workers, and HTTP concurrent calls at
16. The single-listener host permits 32 accepted connection workers; the NAS
profile uses independent pools of 16 for MCP and 16 for private sync, including
clients still performing TLS or sending headers. A 15-second idle socket timeout
and a 20-second absolute connection I/O deadline cover handshakes, headers and
bodies. Handshakes run in workers rather than blocking the accept loop. One
watchdog per listener shuts down expired I/O; the worker owns final socket closure,
and shutdown joins the workers before the watchdog exits. Slow-drip traffic cannot
extend its connection budget. This closes transport, not an in-flight Store
transaction. Expected TLS/connection failures close without raw tracebacks.
Synthetic tests cover slow TLS fragments, headers and bodies, independent pool
availability, expiry and watchdog cleanup. The graph imposes tighter action/query limits. HTTP uses
bounded reads and connection close responses. Those are personal-service limits,
not evidence of enterprise capacity or complete denial-of-service qualification.

## Reproducible checks

Run from the checkout:

```sh
python -m unittest discover -s tests -p test_mcp.py -v
python -m unittest discover -s tests -p test_oauth.py -v
python -m unittest discover -s tests -p test_http_profiles.py -v
python -m unittest discover -s tests -p test_nas_cli.py -v
```

The protocol, JWT, HTTP profile and CLI tests use only synthetic content. JWT tests use real signatures and cover audience/issuer/time/type validation, scope intersection, local revocation, key rotation and unsafe trust files. Current totals, independent-client transport results and maintained-AS runs are recorded in ACCEPTANCE-RESULTS.md. The independent SDK test runs when
the `mcp` package is already installed and otherwise reports a skip; no test
silently installs software. The wire tests cover latest discovery and direct
calls without initialization, required per-request metadata, current grant
revocation, structured errors, version mismatch, HTTP header/Origin/Host checks,
base64 header values, notification behavior, stdio parse recovery and cancellation.
The seven published tool input schemas were also checked with the already
installed JSON Schema 2020-12 validator: entity, source, fact, relationship and
correction examples validate, while malformed alternatives, forged actor fields,
invalid action kinds, duplicate evidence IDs and administrative actions do not.
Runtime regression tests also prove malformed capture variants, numeric
correction reasons and authority claims never reach store submission. This schema
check does not replace graph-semantic tests.

## Client compatibility and remaining evidence

| Client | Evidence | Remaining boundary |
| --- | --- | --- |
| Independent Python MCP SDK 1.29.0 | Historical baseline SDK subprocess connections passed over stdio at 2025-11-25 against both a protocol fixture and the real Store/Service. The latter covers sourced inferred capture, idempotent retry, temporal query, evidence/history, an authenticated owner correction, a later conflicting inference with the owner claim still preferred, forged actor rejection and read-only write denial. | This does not certify the SDK for 2026-07-28 or prove every LLM host's configuration behavior. |
| ChatGPT/Claude apps and APIs | Standards-based OAuth resource profile and local synthetic checks are implemented; Keycloak reference artifacts are provided. | Real account eligibility, client registration/callbacks and end-to-end hosted connections remain unverified; consult current acceptance evidence for local AS results. |
| Praxis2 | Authorized source inspection confirms 2026-07-28 per-request metadata, header mirroring, bearer authentication, JSON/SSE parsing and discovery/tool listing. RefactoredMemory implements those protocol requirements. | **Actual application connection and use are unverified.** No running Praxis2 application or usable Go toolchain is available in this environment. The inspected connection lifecycle selects provider-specific endpoints, so source inspection alone does not establish an available configuration path to this store. Qualification needs an actual Praxis2 revision that can connect to this MCP endpoint and use the configured grant strategy. No Praxis repository was modified and no private source was copied into this repository. |

The private client sources remain in their authorized repositories. A successful
protocol fixture or independent SDK call must not be relabelled as a passed
Praxis2 application integration. Praxis2 is the integration target; changes to
either Praxis repository are outside the authorized scope. The legacy stdio path
is independent-client compatibility evidence, not an earlier-Praxis requirement.
Once an actual compatible Praxis2 instance is available, configure its MCP
connection, run the same synthetic capture, correction, source/history retrieval
and denied-grant workflows, and record the application revision and configuration.
