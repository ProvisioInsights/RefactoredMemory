# Direct personal-peer synchronization

The v1 exchange replicates immutable, signed graph operation groups between two admitted personal peers. Each has a separate database, local offline writes and local knowledge history. The exchange does not copy SQLite files, choose a wall-clock winner or provide a transitive relay mesh.

`refactoredmemory.sync.sync_once(store, url, token)` performs bounded push/pull exchanges. The server calls `exchange(store, payload, peer_id)` only after a dedicated peer bearer credential has resolved to an admitted peer ID. The credential binding is local configuration; a request body cannot select its own authority. The Store verifies operation origins and dependencies and makes received groups durable before acknowledging them.

## Wire contract

`POST /sync` uses `Authorization: Bearer <peer credential>` and JSON:

```json
{
  "protocol": "refactoredmemory-sync/1",
  "store_id": "synthetic-personal-store",
  "frontier": {"peer-a": 4, "peer-b": 2},
  "operations": [],
  "limit": 100
}
```

The response contains `protocol`, `store_id`, the server's `peer_id`, an `operations` batch, the server's applied `frontier`, a Boolean `more`, and the Store's durable `receipt`. The client identifies the expected peer when configured and rejects a changed identity or a response echoing its own peer ID. Store identity mismatches fail before applying graph changes.

The first exchange sends only metadata to obtain the remote frontier and pull missing operations. Subsequent exchanges push operations above that frontier and request missing remote operations above the local applied frontier. A group is never split. Batches contain at most 1,000 operation groups and bodies are bounded to 4 MiB; the default is 100 groups. Larger batches are reduced to fit the byte bound. A single oversized group is an explicit error.

The applied frontier advances only across contiguous, causally admissible operations. Received operations awaiting dependencies remain visible in Store status. A missing dependency does not become a successful synchronization merely because bytes were delivered. No transport cursor is persisted separately from durable Store state, so interruption or response loss causes safe redelivery. Origin-ID/content conflicts remain Store errors.

`complete: true` means both peers reported the same applied frontier, both pending queues are empty, and no further operations were advertised at the end of this exchange. It is a point-in-time result; either peer may write again immediately. The client stops at a bounded number of exchanges and reports `complete: false` if it cannot catch up. An unchanged pair of frontiers and pending counts across a full exchange reports `reason: missing_dependencies` instead of repeatedly retransmitting without progress. A local or remote rejected operation reports `reason: semantic_rejection` immediately, with separate rejection counts; rejected groups cannot masquerade as successful synchronization. Independent source disputes and concurrent correction branches remain semantic alternatives after synchronization.

## Transport and lifecycle

Cross-host synchronization requires HTTPS with certificate verification. Plain HTTP is permitted only for numeric loopback addresses for isolated tests and local process communication. Redirects are refused so a bearer credential cannot move to a server-chosen destination. Credentials, full remote errors and source payloads are excluded from normal errors. The server must enforce its own request-body bounds before reading the body.

Transport failures and transient HTTP failures permit a small bounded retry count. Authorization, malformed data, identity and operation-integrity errors are not retried as successes. Retry does not erase an already durable operation or claim that an unobserved acknowledgment was received.

Peer enrollment/revocation and client grants are local owner administration, separate from graph writes and consumer MCP tools. A copied live database directory must not run as a second writer under the same origin identity. Use the documented restore/rejoin flow with a new identity or a controlled, exclusive incarnation. Offline peers cannot observe a remote revocation instantaneously. Full plaintext peers remain trusted with the admitted personal store; transport authentication is not content encryption or operator blindness.

## Snapshot recovery and rejoin

`Store.restore(snapshot_path, destination, peer_id=...)` restores into a new destination and fresh peer identity. It verifies and replays the signed operation journal into a new schema. It rejects executable SQLite schema objects, missing acknowledged positions, invalid signatures, invalid causal history and mismatched immutable projections. Original or historical origin IDs cannot be reused. Failure removes a destination created by the attempt. Active client grants, peer admissions and recovery-forwarding permissions are not restored.

An old snapshot may contain offline operations that the surviving peer never received. Those operations keep their original origin IDs and signatures; the new peer cannot simply rewrite them as its own history. Conversely, the surviving peer may hold later operations from the retired origin that the snapshot lacks. Recover those histories explicitly:

1. Retire the old writer, preserve the original snapshot, and obtain the original origin verification keys through the approved local recovery/pairing procedure. Keep these secrets out of chat, source control, ordinary logs and MCP responses.
2. Restore to a fresh peer identity. Pair the surviving and restored peers using their current identities and create new dedicated sync credentials locally.
3. On each receiver that needs historical operations forwarded by its counterpart, authorize the exact mapping with `store.admit_recovery_origin(sender_peer_id, historical_origin_id, original_key_hex)`. The sender must already be admitted. The receiver's own active origin cannot be delegated. This is a local owner action, unavailable to consumer MCP tools and graph content.
4. Run direct synchronization. The receiver verifies each forwarded operation against the original origin key, not the new sender's key. Missing explicit permission or a replacement signature fails. Reconcile newer tombstones and current access state before using the restored store for ordinary work; a disconnected snapshot cannot know subsequent deletions or revocations.

Recovery admission is a narrow, explicit path for named historical origins. It does not enable arbitrary third-origin forwarding or a general transitive relay mesh. The same immutable IDs, causal dependencies, conflicts and current deletion suppression apply after recovery.

## Qualification boundary

Run the synthetic suite with:

```sh
python -m unittest discover -s tests -p test_sync.py -v
```

On 7 November 2026, all 17 cases passed on the available Linux runtime with Python 3.12.14. The tests use separate Store databases and an independent spawned Python server process, exercising paginated offline concurrent corrections, preservation of earlier local knowledge, duplicate-free replay after a lost durable acknowledgment, restart with a missing predecessor, revoked peers, wrong credentials/store/peer identities, malformed JSON and bounds, refusal of plaintext nonloopback destinations and redirects, and explicit incomplete reporting for stalled dependencies or semantic rejections. Regression cases cover causal references omitted from an operation's dependency frontier, explicit historical-origin recovery with the original signature, refusal to reuse old origins, malicious SQLite triggers, missing acknowledged journal positions, and cleanup after a failed signature check.

Actual Mac/Linux qualification and real client endpoints require the corresponding runtimes and access; these local Linux tests do not establish that the owner's Mac was exercised. The test HTTP adapter invokes production `exchange` and Store authentication but does not qualify deployment certificates or an externally running endpoint. Third-hop forwarding, automatic discovery, NAT traversal and selective partial replicas remain outside v1.
