"""Direct-peer transport and offline convergence with synthetic knowledge only."""

from __future__ import annotations

import json
import hashlib
import hmac
import multiprocessing
import sqlite3
import tempfile
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

from refactoredmemory.store import (
    AuthorizationError, ConflictError, Store, ValidationError, canonical, utcnow,
)
from refactoredmemory.sync import (
    MAX_BODY_BYTES, PROTOCOL, SyncError, decode_body, exchange, sync_once,
)


def _server_process(path, ready, stopping, initial_actions=None, drop_response=False):
    """An independent Store process using the production exchange function."""
    store = Store(path)
    if initial_actions:
        store.submit(initial_actions, request_id="synthetic-offline-change")
    dropped = False

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            nonlocal dropped
            try:
                if self.path != "/sync":
                    self.send_error(404)
                    return
                token = self.headers.get("Authorization", "").removeprefix("Bearer ")
                actor = store.authenticate(token, "sync")
                size = int(self.headers.get("Content-Length", "0"))
                if size > MAX_BODY_BYTES or size < 0:
                    self.send_error(413)
                    return
                payload = decode_body(self.rfile.read(size))
                response = exchange(store, payload, actor["peer_id"])
                if drop_response and payload["operations"] and not dropped:
                    dropped = True
                    self.close_connection = True
                    return
                body = json.dumps(response).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                # Test adapter never serializes payloads, tokens or source text.
                self.send_error(400)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    server.timeout = 0.1
    ready.send(server.server_address[1])
    ready.close()
    try:
        while not stopping.is_set():
            server.handle_request()
    finally:
        server.server_close()
        store.close()


@contextmanager
def peer_server(path, *, initial_actions=None, drop_response=False):
    context = multiprocessing.get_context("spawn")
    reader, writer = context.Pipe(duplex=False)
    stopping = context.Event()
    process = context.Process(target=_server_process,
                              args=(str(path), writer, stopping,
                                    initial_actions, drop_response))
    process.start()
    writer.close()
    try:
        if not reader.poll(10):
            raise AssertionError("Synthetic peer failed to start")
        port = reader.recv()
        yield f"http://127.0.0.1:{port}/sync"
    finally:
        stopping.set()
        process.join(5)
        if process.is_alive():
            process.terminate()
            process.join(5)
        reader.close()
        if process.exitcode not in (0, None):
            raise AssertionError(f"Synthetic peer exited with code {process.exitcode}")


def seed_actions():
    return [
        {"type": "entity", "id": "project", "entity_type": "project", "label": "Synthetic project"},
        {"type": "source", "id": "source-original", "uri": "synthetic:original",
         "content": "The synthetic project chose option A.", "metadata": {}},
        {"type": "assertion", "id": "decision-original", "subject": "project",
         "predicate": "decision", "value": "Option A", "source_ids": ["source-original"],
         "valid_from": "2026-01-01", "time_precision": "day"},
    ]


def correction(suffix):
    return [
        {"type": "source", "id": "source-" + suffix, "uri": "synthetic:" + suffix,
         "content": "An independent synthetic correction: " + suffix, "metadata": {}},
        {"type": "assertion", "id": "decision-" + suffix, "subject": "project",
         "predicate": "decision", "value": "Option " + suffix,
         "source_ids": ["source-" + suffix], "kind": "correct",
         "predecessors": ["decision-original"], "reason": "Synthetic offline owner correction",
         "valid_from": "2026-01-01", "time_precision": "day"},
    ]


class DirectPeerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path_a = Path(self.temp.name) / "a.sqlite"
        self.path_b = Path(self.temp.name) / "b.sqlite"
        self.a = Store(self.path_a, store_id="synthetic-sync", peer_id="peer-a")
        self.addCleanup(self.a.close)
        with Store(self.path_b, store_id="synthetic-sync", peer_id="peer-b") as b:
            identity_a, identity_b = self.a.identity(), b.identity()
            self.a.admit_peer(identity_b["peer_id"], identity_b["key_hex"])
            b.admit_peer(identity_a["peer_id"], identity_a["key_hex"])
            self.token = b.create_grant("synthetic direct peer", ["sync"], kind="peer",
                                        peer_id=identity_a["peer_id"])

    def test_offline_corrections_converge_over_paginated_process_exchange(self):
        self.a.submit(seed_actions())
        original_position = self.a.status()["known_position"]
        with peer_server(self.path_b) as url:
            first = sync_once(self.a, url, self.token, batch_size=1, expected_peer="peer-b")
        self.assertTrue(first["complete"])
        self.a.submit(correction("B"))
        before_receipt = self.a.status()["known_position"]
        with peer_server(self.path_b, initial_actions=correction("C")) as url:
            result = sync_once(self.a, url, self.token, batch_size=1, expected_peer="peer-b")
            repeat = sync_once(self.a, url, self.token, batch_size=1)
        self.assertTrue(result["complete"])
        self.assertTrue(repeat["complete"])
        self.assertEqual(repeat["sent"], 0)
        self.assertEqual(repeat["received"], 0)
        current = self.a.query(subject="project")
        self.assertEqual({x["id"] for x in current["assertions"]},
                         {"decision-B", "decision-C"})
        self.assertEqual({x["id"] for x in self.a.query(subject="project", known_at=original_position)["assertions"]},
                         {"decision-original"})
        self.assertEqual({x["id"] for x in self.a.query(subject="project", known_at=before_receipt)["assertions"]},
                         {"decision-B"})
        with Store(self.path_b) as b:
            self.assertEqual(self.a.status()["frontier"], b.status()["frontier"])
            self.assertEqual({x["id"] for x in current["assertions"]},
                             {x["id"] for x in b.query(subject="project")["assertions"]})
            self.assertEqual(len(self.a.export_operations()["operations"]),
                             len(b.export_operations()["operations"]))

    def test_lost_response_retries_durable_group_without_duplicate(self):
        self.a.submit(seed_actions())
        with peer_server(self.path_b, drop_response=True) as url:
            result = sync_once(self.a, url, self.token, batch_size=1, retries=1)
        self.assertTrue(result["complete"])
        with Store(self.path_b) as b:
            self.assertEqual(len(b.export_operations()["operations"]), 1)
            self.assertEqual(len(b.query(subject="project")["assertions"]), 1)
            self.assertEqual(b.status()["pending"], 0)

    def test_wrong_credential_does_not_apply_operations(self):
        self.a.submit(seed_actions())
        with peer_server(self.path_b) as url:
            with self.assertRaisesRegex(SyncError, "HTTP 400"):
                sync_once(self.a, url, "invalid-synthetic-token", retries=0)
        with Store(self.path_b) as b:
            self.assertEqual(b.status()["known_position"], 0)

    def test_wrong_store_is_rejected_before_receipt(self):
        self.a.submit(seed_actions())
        payload = {"protocol": PROTOCOL, "store_id": "different",
                   "frontier": {}, "operations": self.a.export_operations()["operations"], "limit": 10}
        with Store(self.path_b) as b:
            with self.assertRaisesRegex(SyncError, "different knowledge store"):
                exchange(b, payload, "peer-a")
            self.assertEqual(b.status()["known_position"], 0)

    def test_missing_predecessor_waits_durably_and_replay_is_idempotent(self):
        self.a.submit(seed_actions())
        self.a.submit(correction("B"))
        operations = self.a.export_operations()["operations"]
        self.assertEqual(len(operations), 2)
        with Store(self.path_b) as b:
            result = b.receive([operations[1]], peer_id="peer-a")
            self.assertEqual(result["pending"], 1)
            self.assertEqual(b.status()["known_position"], 0)
            self.assertEqual(b.query(subject="project")["assertions"], [])
        with Store(self.path_b) as b:
            self.assertEqual(b.status()["pending"], 1)
            b.receive([operations[0]], peer_id="peer-a")
            applied = b.status()["known_position"]
            self.assertEqual(b.status()["pending"], 0)
            self.assertEqual({x["id"] for x in b.query(subject="project")["assertions"]},
                             {"decision-B"})
            b.receive(operations, peer_id="peer-a")
            self.assertEqual(b.status()["known_position"], applied)

    def test_revoked_peer_cannot_exchange_even_empty_batches(self):
        with Store(self.path_b) as b:
            b.revoke_peer("peer-a")
            payload = {"protocol": PROTOCOL, "store_id": "synthetic-sync",
                       "frontier": {}, "operations": [], "limit": 10}
            with self.assertRaises(AuthorizationError):
                exchange(b, payload, "peer-a")

    def test_response_identity_change_is_rejected_before_application(self):
        response = {"protocol": PROTOCOL, "store_id": "synthetic-sync", "peer_id": "impostor",
                    "frontier": {}, "operations": [], "more": False,
                    "receipt": {"pending": 0}}
        with patch("refactoredmemory.sync._post", return_value=response):
            with self.assertRaisesRegex(SyncError, "identity"):
                sync_once(self.a, "https://peer.invalid/sync", self.token, expected_peer="peer-b")

    def test_nonloopback_cleartext_and_redirects_are_not_allowed(self):
        for url in ("http://peer.example/sync", "http://localhost/sync",
                    "http://192.0.2.1/sync"):
            with self.subTest(url=url):
                with self.assertRaisesRegex(SyncError, "HTTPS"):
                    sync_once(self.a, url, self.token)
        for url in ("https://user:password@example.test/sync", "https://example.test/sync?token=x",
                    "https://example.test/sync#fragment"):
            with self.subTest(url=url):
                with self.assertRaises(SyncError):
                    sync_once(self.a, url, self.token)

        paths = []

        class RedirectHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                paths.append(self.path)
                self.send_response(307)
                self.send_header("Location", "/credential-trap/sync")
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), RedirectHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with self.assertRaisesRegex(SyncError, "HTTP 307"):
                sync_once(self.a, f"http://127.0.0.1:{server.server_port}/sync", self.token)
            self.assertEqual(paths, ["/sync"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(2)

    def test_protocol_bounds_and_ambiguous_json_fail_closed(self):
        for raw in (b'{"a":1,"a":2}', b'{"x":NaN}', b'[]', b'\xff',
                    b' ' * (MAX_BODY_BYTES + 1)):
            with self.subTest(raw=raw[:30]):
                with self.assertRaises(SyncError):
                    decode_body(raw)
        base = {"protocol": PROTOCOL, "store_id": "synthetic-sync", "frontier": {},
                "operations": [], "limit": 10}
        with Store(self.path_b) as b:
            for changes in ({"limit": True}, {"limit": 1001}, {"frontier": {"x": -1}},
                            {"frontier": {"x": True}}, {"actor": "owner"},
                            {"operations": [None]}, {"protocol": "future"}):
                with self.subTest(changes=changes):
                    with self.assertRaises(SyncError):
                        exchange(b, base | changes, "peer-a")

    def test_stalled_dependency_queue_reports_incomplete(self):
        response = {"protocol": PROTOCOL, "store_id": "synthetic-sync", "peer_id": "peer-b",
                    "frontier": {}, "operations": [], "more": False,
                    "receipt": {"pending": 1}}
        with patch("refactoredmemory.sync._post", return_value=response) as post:
            result = sync_once(self.a, "https://peer.invalid/sync", self.token, max_rounds=100)
        self.assertFalse(result["complete"])
        self.assertEqual(result["reason"], "missing_dependencies")
        self.assertEqual(result["rounds"], 2)
        self.assertEqual(post.call_count, 2)

    def test_rejected_groups_report_semantic_failure_without_spinning(self):
        response = {"protocol": PROTOCOL, "store_id": "synthetic-sync", "peer_id": "peer-b",
                    "frontier": {}, "operations": [], "more": False,
                    "receipt": {"pending": 1, "rejected": 1}}
        with patch("refactoredmemory.sync._post", return_value=response) as post:
            result = sync_once(self.a, "https://peer.invalid/sync", self.token)
        self.assertFalse(result["complete"])
        self.assertEqual(result["reason"], "semantic_rejection")
        self.assertEqual(result["remote_rejected"], 1)
        self.assertEqual(post.call_count, 1)

    def test_undeclared_reference_dependency_is_rejected_regardless_of_receipt_order(self):
        self.a.submit(seed_actions())
        with Store(self.path_b) as b:
            key = b.identity()["key_hex"]
        body = {"schema": 1, "id": "peer-b:1", "store_id": "synthetic-sync",
                "origin": "peer-b", "seq": 1, "dependencies": {},
                "actor": {"id": "synthetic-owner", "kind": "owner"},
                "created_at": utcnow(), "actions": [{
                    "type": "assertion", "id": "undeclared-reference", "subject": "project",
                    "predicate": "decision", "value": "Unjustified causal reference",
                    "source_ids": ["source-original"],
                }]}
        wire = {**body, "signature": hmac.new(bytes.fromhex(key), canonical(body).encode(),
                                                hashlib.sha256).hexdigest()}
        first = self.a.receive([wire], peer_id="peer-b")
        self.assertEqual(first["applied"], 0)
        self.assertEqual(first["rejected"], 1)
        with self.assertRaises(ValidationError):
            self.a.query(frontier={"peer-b": 1})
        with Store(Path(self.temp.name) / "other.sqlite", store_id="synthetic-sync", peer_id="other") as other:
            other.admit_peer("peer-b", key)
            other.admit_peer("peer-a", self.a.identity()["key_hex"])
            second = other.receive([wire], peer_id="peer-b")
            self.assertEqual(second["rejected"], 1)
            other.receive(self.a.export_operations()["operations"], peer_id="peer-a")
            self.assertEqual({x["id"] for x in other.query()["assertions"]},
                             {x["id"] for x in self.a.query()["assertions"]})
            self.assertEqual(other.status()["frontier"], self.a.status()["frontier"])

    def test_restored_peer_requires_explicit_recovery_origin_and_original_signature(self):
        snapshot = Path(self.temp.name) / "snapshot.sqlite"
        with Store(self.path_b) as b:
            b.submit(seed_actions())
            old_key = b.identity()["key_hex"]
            b.backup(snapshot)
        with Store.restore(snapshot, Path(self.temp.name) / "restored.sqlite", peer_id="restored") as restored:
            restored_identity = restored.identity()
            self.a.admit_peer("restored", restored_identity["key_hex"])
            operations = restored.export_operations()["operations"]
            with self.assertRaises(AuthorizationError):
                self.a.receive(operations, peer_id="restored")
            self.a.admit_recovery_origin("restored", "peer-b", old_key)
            wire = dict(operations[0])
            original_body = {k: v for k, v in wire.items() if k != "signature"}
            wire["signature"] = hmac.new(bytes.fromhex(restored_identity["key_hex"]),
                                          canonical(original_body).encode(), hashlib.sha256).hexdigest()
            with self.assertRaises(AuthorizationError):
                self.a.receive([wire], peer_id="restored")
            receipt = self.a.receive(operations, peer_id="restored")
            self.assertEqual(receipt["applied"], 1)
            self.assertEqual({x["id"] for x in self.a.query()["assertions"]}, {"decision-original"})
            with self.assertRaises(AuthorizationError):
                restored.authenticate(self.token, "sync")
            with self.assertRaises(AuthorizationError):
                self.a.admit_recovery_origin("restored", "peer-a", self.a.identity()["key_hex"])

    def test_restore_rejects_original_or_historical_origin_identities(self):
        self.a.submit(seed_actions())
        snapshot = Path(self.temp.name) / "identity-snapshot.sqlite"
        with Store(self.path_b) as b:
            b.receive(self.a.export_operations()["operations"], peer_id="peer-a")
            b.backup(snapshot)
        for origin in ("peer-a", "peer-b"):
            destination = Path(self.temp.name) / ("reuse-" + origin + ".sqlite")
            with self.subTest(origin=origin):
                with self.assertRaises(ConflictError):
                    Store.restore(snapshot, destination, peer_id=origin)
                self.assertFalse(destination.exists())

    def test_snapshot_with_trigger_is_rejected_without_copying_sql_code(self):
        self.a.submit(seed_actions())
        snapshot = Path(self.temp.name) / "trigger-snapshot.sqlite"
        self.a.backup(snapshot)
        with sqlite3.connect(snapshot) as connection:
            connection.execute("CREATE TRIGGER restore_trap AFTER DELETE ON grants BEGIN UPDATE metadata SET value='forged' WHERE key='peer_id'; END")
        destination = Path(self.temp.name) / "trigger-restore.sqlite"
        with self.assertRaisesRegex(ValidationError, "executable schema"):
            Store.restore(snapshot, destination)
        self.assertFalse(destination.exists())

    def test_snapshot_with_acknowledged_position_gap_is_rejected(self):
        self.a.submit(seed_actions())
        self.a.submit(correction("B"))
        snapshot = Path(self.temp.name) / "gap-snapshot.sqlite"
        self.a.backup(snapshot)
        with sqlite3.connect(snapshot) as connection:
            connection.execute("DELETE FROM operations WHERE position=1")
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        destination = Path(self.temp.name) / "gap-restore.sqlite"
        with self.assertRaisesRegex(ValidationError, "missing acknowledged"):
            Store.restore(snapshot, destination)
        self.assertFalse(destination.exists())

    def test_snapshot_hmac_failure_removes_partially_created_destination(self):
        self.a.submit(seed_actions())
        snapshot = Path(self.temp.name) / "signature-snapshot.sqlite"
        self.a.backup(snapshot)
        with sqlite3.connect(snapshot) as connection:
            connection.execute("UPDATE operations SET signature=?", ("0" * 64,))
        destination = Path(self.temp.name) / "signature-restore.sqlite"
        with self.assertRaisesRegex(ValidationError, "origin verification"):
            Store.restore(snapshot, destination)
        for suffix in ("", "-wal", "-shm"):
            self.assertFalse(Path(str(destination) + suffix).exists())


if __name__ == "__main__":
    unittest.main()
