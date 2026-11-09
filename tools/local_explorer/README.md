# Private local content explorer

A loopback-only, read-only view of an existing RefactoredMemory store: named identities, current structured claims, incoming/outgoing relationships, source excerpts, dated observations and a paginated review queue. It does not fetch providers, grant access, import content or write the store.

Build with `npm ci --ignore-scripts && npm run build` in this directory. Run `server.py --help` with the operator Python environment. Supply the explicit database, document index, corroboration audit, application source, built assets and private access-key file paths; host-specific paths and data belong outside Git. Port zero chooses an available loopback port. Use the URL printed at startup.

The content boundary is this Mac's owner account. The server binds only 127.0.0.1, requires a private owner-held access key plus its exact Host and same-origin browser requests, uses an HttpOnly SameSite=Strict session cookie, withholds historical control/test records, sends no-store/CSP headers and never logs queries or source text. All database connections use SQLite read-only mode and query_only. Source HTML is displayed as plain text, never executed; it has no outgoing links or external resources. The UI has no write controls.

The identity/document-link cache and incoming relationship cache reflect the launch snapshot. Current outgoing claims are read on selection. The audit records its baseline position and does not imply that later writes were assessed; restart/rebuild the audit after a subsequent enrichment. Separate documents and versions do not prove independent corroboration. Source dates, mailbox observations and world-time claims retain different meanings. Legacy confidence labels are source content, not fresh verification.

Preserve the existing private MCP listener and public/private network boundaries. This convenience viewer is not a public MCP endpoint or a substitute for its OAuth boundary. Do not bind it to a LAN/all-interface address or publish the built page with real content.
