# Running RefactoredMemory personal v1

For the accepted NAS-first deployment and scoped continuous maintenance access, see [NAS-DEPLOYMENT.md](NAS-DEPLOYMENT.md), [REMOTE-ADMIN.md](REMOTE-ADMIN.md) and [NAS-CONTRACT.md](NAS-CONTRACT.md). New deployment implementation and local evidence are pending at this documentation baseline. Do not treat commands for synthetic peers as authorization to publish a tunnel or change the NAS.

Use an existing Python 3.12+ interpreter on macOS or Linux. The runtime uses only the Python standard library and SQLite; run it directly from the repository checkout. No package installation, external deployment, real-data ingestion, or credentials from another service are required for the synthetic examples below.

The automated CLI qualification runs two independent Linux processes and exercises the production HTTP handler. These commands are portable to the intended Mac/Linux pair, but the owner's actual Mac, original archives and Praxis2 application still require their separate qualification evidence. See [acceptance results](ACCEPTANCE-RESULTS.md) and [MCP conformance](MCP-CONFORMANCE.md).

## Start with synthetic data

From the repository root:

```sh
python3 --version
python3 -m unittest discover -s tests -v
python3 examples/synthetic_demo.py
```

The demo creates a temporary store and answers the three agreed workflows: project decision and rationale, relationship context, and changes since last month. It retains the earlier decision after a correction. It does not read personal files.

For a persistent synthetic pair, use a new private directory outside the repository. The following shell variable names are task-specific; `umask` applies to new files created in this terminal.

```sh
umask 077
REFMEM_DATA="$(mktemp -d "${TMPDIR:-/tmp}/refactoredmemory-synthetic.XXXXXX")"
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" init --store-id synthetic-personal-store --peer-id synthetic-mac
python3 -m refactoredmemory --db "$REFMEM_DATA/linux.sqlite3" init --store-id synthetic-personal-store --peer-id synthetic-linux
```

These fixed IDs make this demonstration repeatable. For a later approved personal store, omit `--peer-id` to generate a fresh identity; create the second peer with the first peer's nonsecret `store_id` from `status`. Never copy a live database as a second writable peer or reuse its peer identity.

Create a synthetic submission and a client grant:

```sh
cat > "$REFMEM_DATA/capture.json" <<'JSON'
{
  "request_id": "synthetic-project-decision-1",
  "actions": [
    {"type":"entity","id":"northstar","entity_type":"project","label":"Synthetic Northstar"},
    {"type":"source","id":"meeting-1","uri":"synthetic://meeting/1","content":"We chose SQLite because local transactions simplify recovery.","metadata":{"synthetic":true}},
    {"type":"assertion","id":"decision-1","subject":"northstar","predicate":"decision","value":"Use SQLite for local durability","source_ids":["meeting-1"],"valid_from":"2026-10-01","time_precision":"day","provenance":{"method":"client-inference","model":"synthetic-fixture","rationale":"The supplied meeting note states the choice."},"uncertainty":{"band":"high"}}
  ]
}
JSON
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" grant --label synthetic-client --scopes read,write,correct --output "$REFMEM_DATA/client.token"
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" call memory_submit --args "@$REFMEM_DATA/capture.json" --token-file "$REFMEM_DATA/client.token"
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" call memory_query --args '{"subject":"northstar"}' --token-file "$REFMEM_DATA/client.token"
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" history --args '{"since":0}'
```

The request ID makes an identical retry safe. Reusing it for different content is an error. The grant defaults to `agent`; an accepted inferred claim is not marked human verified. `query`, `history`, `owner-submit`, pairing and grant commands are local owner administration and rely on OS access to the database. Consumer MCP calls always require their configured grant.

## Connect Praxis2 or another MCP client

Create a separate `read,write,correct` grant for each client. Use a read-only grant when capture is unnecessary. The token is written once to a new mode-0600 file and is never printed. Keep token files, databases, WAL/SHM files, backups and pairing material outside version control; the plaintext storage profile requires an approved host before real personal use.

A typical stdio client configuration is below. Replace each absolute path with the actual checkout, interpreter and local files. Use the client's normal MCP server configuration location; this generic example is not a verified Praxis2 configuration file. Do not edit either Praxis repository or its configuration as part of this implementation; the installed Praxis2 connection has not been exercised.

```json
{
  "mcpServers": {
    "refactoredmemory": {
      "command": "/absolute/path/to/python3",
      "args": [
        "/absolute/path/to/RefactoredMemory/launcher.py",
        "--db", "/absolute/private/path/mac.sqlite3",
        "serve-stdio",
        "--token-file", "/absolute/private/path/client.token"
      ]
    }
  }
}
```

The server instructions tell connected clients to proactively save useful facts, preferences, decisions, rationale and relationships within their grant, attach evidence/uncertainty, and retrieve sources before answering. A host must actually follow that policy and invoke the tools; the server does not monitor unrelated conversations or run an extraction model. Tools include `memory_submit`, `memory_query`, `memory_history`, `memory_traverse`, `memory_source`, `memory_entity` and `memory_status`.

MCP `2026-07-28` requests use per-request metadata and `server/discover`. Explicit `2025-11-25` stdio compatibility is available for older clients. Remote HTTP is the modern protocol only and requires a client that can supply a preconfigured owner-issued bearer token. This custom authentication strategy does not implement OAuth discovery or OAuth-only host onboarding. Use the version/client matrix in [MCP conformance](MCP-CONFORMANCE.md); a successful protocol harness is not proof that a particular Praxis2 release works.

To revoke a client immediately on this peer:

```sh
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" revoke --token-file "$REFMEM_DATA/client.token"
```

Grants are local administration and are not replicated as graph data. Revoke corresponding local grants on each peer. Offline peers cannot learn a new revocation until their administration is updated. A revoked token cannot read old known-at history.

## Make an explicit owner correction

A client's `correct` permission lets it preserve correction lineage, but its inferences remain agent-authored. Preferred owner corrections require a deliberate local `owner-submit`; do not give an unattended inference client an owner-kind grant merely to let it write.

```sh
cat > "$REFMEM_DATA/owner-correction.json" <<'JSON'
[
  {"type":"source","id":"owner-note-1","uri":"synthetic://owner-note/1","content":"My clarification: use SQLite WAL with full durability for this project.","metadata":{"synthetic":true}},
  {"type":"assertion","id":"decision-owner-correction","subject":"northstar","predicate":"decision","value":"Use SQLite WAL with full durability","source_ids":["owner-note-1"],"kind":"correct","predecessors":["decision-1"],"reason":"Explicit owner clarification of the synthetic project choice.","valid_from":"2026-10-01","time_precision":"day"}
]
JSON
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" owner-submit --actions "@$REFMEM_DATA/owner-correction.json" --request-id synthetic-owner-correction-1
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" query --args '{"subject":"northstar","predicate":"decision"}'
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" query --args '{"subject":"northstar","known_at":1}'
```

Current reads prefer this owner correction while retaining contrary claims and sources. Known positions belong to the named local peer; another peer can have a different early receipt history. Use shared frontiers when comparing converged semantic answers.

## Pair and synchronize the two synthetic peers

Pairing identity files contain HMAC signing secrets. Export them only into private files and transfer them through an approved secure channel when the peers are on different machines. Do not paste them into chat or place them in client MCP configuration. The demonstration below keeps both independent databases on one machine.

```sh
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" identity --output "$REFMEM_DATA/mac.identity.json"
python3 -m refactoredmemory --db "$REFMEM_DATA/linux.sqlite3" identity --output "$REFMEM_DATA/linux.identity.json"
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" peer-admit --identity-file "$REFMEM_DATA/linux.identity.json"
python3 -m refactoredmemory --db "$REFMEM_DATA/linux.sqlite3" peer-admit --identity-file "$REFMEM_DATA/mac.identity.json"
python3 -m refactoredmemory --db "$REFMEM_DATA/linux.sqlite3" grant --label synthetic-mac-sync --kind peer --peer-id synthetic-mac --scopes sync --output "$REFMEM_DATA/linux-allows-mac.token"
```

In another terminal, set `REFMEM_DATA` to the same private directory, change to the checkout, and start the Linux peer:

```sh
python3 -m refactoredmemory --db "$REFMEM_DATA/linux.sqlite3" serve --host 127.0.0.1 --port 8765
```

Back in the first terminal:

```sh
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" sync --url http://127.0.0.1:8765/sync --token-file "$REFMEM_DATA/linux-allows-mac.token" --expected-peer synthetic-linux
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" status
python3 -m refactoredmemory --db "$REFMEM_DATA/linux.sqlite3" query --args '{"subject":"northstar"}'
```

One sync command exchanges both directions. Each peer can keep writing while the other is stopped; reconnect and run sync again. Sync is explicit, so schedule it using an approved local service only when desired. Use Ctrl-C to stop the foreground listener. The `/sync` endpoint accepts peer-scoped credentials only; client tokens cannot enroll or impersonate peers.

For the real Mac/Linux connection, use a previously approved TLS certificate and key covering the server hostname. Non-loopback listeners refuse startup without TLS. An example listener configuration, after replacing the paths and approved host, is:

```sh
python3 -m refactoredmemory --db /absolute/private/path/linux.sqlite3 serve --host 0.0.0.0 --port 8765 --cert-file /absolute/private/path/server.crt --key-file /absolute/private/path/server.key --allow-host memory.example.net:8765
```

The client URL is `https://memory.example.net:8765/sync` and must pass normal certificate/hostname validation. An approved private CA can be supplied with Python's `SSL_CERT_FILE` trust configuration; do not disable verification. Authentication tokens are never forwarded across redirects. A browser Origin is denied unless explicitly allowed; no browser UI is needed for v1. This runbook does not provision a VM, obtain certificates, change firewall rules, expose a public endpoint or start an external service.

The same listener serves modern MCP at `/mcp`; configure a separate consumer token. HTTP MCP requests require JSON, `Accept: application/json, text/event-stream`, the protocol/method headers, applicable `Mcp-Name`, and matching per-request metadata. Prefer a qualified MCP client rather than handcrafting production requests.

## Plan an import, then apply only the approved source set

Use synthetic notes for development. Real Markdown/Logseq or LivingAtlas files require separate source-set and processing-environment approval before use. A plan is read-only and does not create the destination database.

```sh
mkdir "$REFMEM_DATA/notes"
cat > "$REFMEM_DATA/notes/synthetic-project.md" <<'MARKDOWN'
# Synthetic project
- We chose SQLite WAL because durable local transactions simplify recovery.
  id:: synthetic-block-1
MARKDOWN
python3 -m refactoredmemory --db "$REFMEM_DATA/imported.sqlite3" import "$REFMEM_DATA/notes" --root "$REFMEM_DATA/notes" --namespace synthetic-notes
python3 -m refactoredmemory --db "$REFMEM_DATA/imported.sqlite3" import "$REFMEM_DATA/notes" --root "$REFMEM_DATA/notes" --namespace synthetic-notes --apply --backup "$REFMEM_DATA/before-import.sqlite3"
```

Review counts, per-record status, `semantic_complete` and fidelity gaps. A successful batch does not certify unsupported formats or missing original evidence. Keep the namespace stable on repeat imports; an unchanged import is idempotent. A changed note creates a source version and correction; disappearance of a file does not erase history. Importer-authored corrections do not become fresh owner corrections.

For legacy stores, supply a bounded directory or file and inspect [supported formats and limits](IMPORT-FORMATS.md). Unknown/encrypted/unsupported records are counted and preserved or left in the source with a reason. Original files are never repaired or overwritten. Symlinks, traversal outside the root and excessive inputs are refused. Backups and destination databases must be outside the source root. Save the returned manifest privately with the migration evidence.

## Backup, recovery and rollback

```sh
python3 -m refactoredmemory --db "$REFMEM_DATA/mac.sqlite3" backup "$REFMEM_DATA/mac-backup.sqlite3"
python3 -m refactoredmemory restore "$REFMEM_DATA/mac-backup.sqlite3" "$REFMEM_DATA/restored.sqlite3"
python3 -m refactoredmemory --db "$REFMEM_DATA/restored.sqlite3" status
```

A destination must be new. Restore verifies retained journal history and signatures, rebuilds projections, generates a fresh peer identity, and activates no old client grants or peer admissions. Keep the recovered store isolated until it has reconciled current deletions and local policy with a current peer. An offline backup cannot know deletions or revocations made after the snapshot.

Pair a recovered peer explicitly using newly exported identity files and new peer-scoped credentials. If it must forward signed operations from an older origin no longer directly admitted, the receiving owner uses `recovery-admit --sender NEW_PEER_ID --identity-file ORIGINAL_ORIGIN_IDENTITY_FILE` with independently retained, approved original pairing material. This is an explicit recovery delegation, not automatic admission from a snapshot; inspect [sync protocol](SYNC-PROTOCOL.md) first.

To roll back an interrupted import, restore its `before-import` backup into a fresh isolated destination and inspect it. Do not delete the partial destination or overwrite original legacy files as part of automatic rollback. Keep the manifest and partial store until the outcome is reconciled. `rebuild` reconstructs derived indexes from retained operations; it is not a replacement for backups or missing history.


## Container artifact

The repository includes a dependency-free runtime Dockerfile, but no image was built or externally deployed during this task. A container still needs a private persistent `/data` mount and approved TLS/credential files for any non-loopback listener. Do not put credentials or databases into the image. Qualify the image and its filesystem durability before using it as the personal Linux peer. Native Python commands above are the executed Linux path.
