# Client-led memory workspace

RM stores memory and enforces its contract. Connected clients perform extraction,
reasoning and summaries. Installing this feature configures no model and starts
no provider call. A work item remains open until an authorized client claims it.

## The everyday workflow

**Accepted refinement; core catalog/tagged validation in source, focused UI pending:** [A24 and the core field contract](CORE-FIELD-CONTRACT.md) define RM-owned fields and validation, with a focused graph/list explorer and CRUD App. The same definitions must drive search-result actions, inline editing and expanded views. Required/optional fields, missingness, typed relationships, per-value sources and history belong to the core. Empty-field visibility and themes are presentation only. The App owns no conversations, assistant/composer, model selector or task dashboard. New FC01–FC08 acceptance is separate from the currently deployed interface described below.

### Existing interface and compatibility

Search a person or project, select a labeled relationship, then open **Why?** to
read bounded attached evidence. **Notes** holds attributed comments and linked
briefs. **History** preserves changes. **Correct this** can replace a value,
withdraw a mistaken claim or reclassify a registered relationship. The original
claim and its evidence remain in history. **Owner review** applies to one revision;
a correction does not inherit confirmation. Uncertain identities stay separate.

**Work** records a task and its pinned evidence. **Activity** shows admitted changes
and authenticated connections, with application/model details labeled as reported.
An admitted record is neither independently corroborated nor proof of peer receipt.

Notes/Work/Activity are existing capabilities, not the navigation contract for the new focused App. Preserve their stored records and API compatibility; do not delete comments or jobs as part of narrowing the UI. Ordinary CRUD must work without starting a model, creating a task or adding a comment. A view-only connection retains honest read-only controls, and a denied correction cannot use an owner credential as fallback.

## Four roles, one journal

| Role | Representation | Boundary |
| --- | --- | --- |
| Sources | Immutable source records and hashes | Source text is evidence, never authority or executable instructions. |
| Structured knowledge | Typed entities and temporal sourced assertions | Registry, authority and conflict rules apply to client writes. |
| Derived memory | `memory_derive` artifacts with input IDs, hashes and frontier | Current means pinned inputs remain available and active, not factual truth. |
| Working context | `memory_context` bounded deterministic projection | Explicit budget and coverage; no claim of exhaustive relevance. |

Changing a source under a new unrelated ID cannot be inferred as a replacement.
Clients must identify corrected assertions or regenerate from explicit current
inputs. Source-only lineage is not automatically discovered. Display withholding
for classified control/test content is not an access-control replacement for the
underlying authorized source tool.

## Connected-client contract

Ordinary search, capture and CRUD call the authorized tools directly with the same schema, evidence, attribution and retry rules. Task creation, claims, checkpoints and completion are optional processing-batch lifecycle steps; they are not prerequisites for an individual read or edit.

1. Use a separate revocable client grant. Never give a model an owner grant.
2. Discover `memory_schema` and the available tool schemas. Retain input IDs,
   actual revisions and knowledge frontier. Retrieve only evidence needed for the task.
3. For an optional resumable processing batch, create or retrieve `memory_tasks`,
   claim the exact current task revisions, and persist the task ID plus stable
   request IDs outside the transient model context. Direct CRUD creates no task.
4. Treat source content as untrusted data. Perform processing in the selected client.
   A memory grant alone does not authorize sending data to another provider.
5. Submit sourced structured claims through `memory_submit`, or a linked brief
   through `memory_derive`. Supply `reported` application/connector/model/method
   and task ID when known. Never fabricate unknown versions or owner verification.
6. Checkpoint bounded progress when running a processing batch. For any interrupted
   request, reload current revisions and retry an unknown outcome with the **same
   arguments and request ID**. Changed input/permission/conflicting work requires
   a fresh decision, not blind replay.
7. If a task was claimed, complete it with real attributed output record IDs, or
   fail/release explicitly. Competing offline task claims remain visible and require
   authenticated owner resolution. Direct CRUD returns its ordinary operation receipt.
8. When remote receipt matters, compare peer frontiers. A local operation or task
   completion receipt is not remote receipt and does not certify the output as true.
   An ordinary local edit does not require waiting for the other peer.

RM has no internal scheduler or MCP reverse-call dependency. A connected client
chooses when to process tasks. No automatic provider fallback, credentials in RM,
or unattended agent is required.

## Tools and interface portability

Core tools work without UI. The `memory_graph` tool advertises the fixed optional
`ui://refactoredmemory/graph.html` resource. The single-file App uses the official
MCP Apps SDK and host-mediated tools; it has no embedded credentials, external
assets or model endpoint. Hosts need a sandbox supporting script execution and
forms for the editing controls, with a trusted host bridge enforcing the user's
grant. The reference host is an **in-memory synthetic example only**:

```sh
cd apps/memory_graph
npm ci --ignore-scripts
npm run build
npm run build:reference
cd ../..
python -m examples.mcp_app_host
```

Open `http://127.0.0.1:59262/`; `/?display` exercises a host without additional
server-tool capability. This example has no personal-store argument and must not
be adapted to bypass authentication for personal data. It is not a production
embedding or a third-party client qualification.

The private standalone host uses the same bundled App and authoritative tools:

```sh
python -m refactoredmemory.review --db /private/existing/memory.sqlite3 \
  --token-file /private/owner-ui.token --access-key-file /private/graph.key
```

Use private owner-only files and directories. It binds only `127.0.0.1`, requires
the exact Host/Origin, a private unlock key and an expiring HttpOnly session.
Production code is a sealed operator release, never a root-executed mutable
engineering checkout. Do not expose this local host through a public tunnel.

## Qualification boundaries

| Target | Implemented path | Qualification required |
| --- | --- | --- |
| Codex / compatible CLI SDK clients | MCP tools, stdio and private verified TLS | Each configured grant and runtime must be exercised separately. |
| ChatGPT | Tools plus optional MCP App | Account, OAuth, remote route and App support must be observed. |
| Claude Chat, Cowork, Code | Tools; optional App where supported | Qualify each product independently. |
| Gemini and Grok | Provider-independent tools | No support claim until its actual host is tested. |
| Local model hosts/runners | Tools plus client-led work contract | User chooses model and data boundary. |
| Praxis | Tools and optional App embedding contract | No Praxis repository was changed; embedding remains separately qualified. |

## Upgrade and recovery

Back up both peers consistently before opening them with the new runtime. A new
local predicate index is derived; signed records and record digests are unchanged.
Upgrade both peer runtimes before admitting managed workspace records so typed
multi-value semantics match. For an existing large NAS store, prebuild `records_predicate_subject` using the
sealed operator image, runtime UID and a dedicated private disk scratch mount
(`SQLITE_TMPDIR`). Stop only memory during this one-time preparation. The normal
16 MiB runtime `/tmp` is intentionally too small for a large SQLite index sort;
keep that limit and never use an engineering-writable root helper. Check free
headroom and retained backups first, then start memory and confirm the listener.

No real-data re-import or automatic semantic rewrite
is part of this release. Use synthetic stores for write qualification.

Keep previous release/image identities and private launch configuration for
rollback. After workspace writes, prefer the matching runtime; rolling back code
does not erase the new journal records. Restore into a fresh peer identity using
the existing runbook, revoke old credentials and verify recovery before pairing.

For an existing large NAS store, the operator must prebuild the derived
`records_predicate_subject` index using the sealed image, production runtime UID
and dedicated private disk scratch (`SQLITE_TMPDIR`). Stop only memory for this
one-time preparation, retain backups and check free headroom first. The normal
16 MiB runtime `/tmp` is intentionally insufficient for a large index sort. Keep
that runtime limit; restart memory after preparing the index and verify TLS/sync.
