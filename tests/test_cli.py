"""Actual CLI subprocesses and the production HTTP /mcp + /sync handler.

All stores, notes, identities and credentials are synthetic temporary fixtures.
No external endpoint, installation or real personal data is used.
"""
import json
import os
from pathlib import Path
import select
import stat
import subprocess
import sys
import tempfile
import unittest
from http.client import HTTPConnection

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-07-28"
PREFIX = "io.modelcontextprotocol/"


def rpc(method="server/discover", **params):
    return {"jsonrpc": "2.0", "id": 1, "method": method, "params": {
        **params, "_meta": {PREFIX + "protocolVersion": VERSION, PREFIX + "clientCapabilities": {}}}}


def actions(label):
    return [
        {"type": "entity", "id": label, "entity_type": "project", "label": label},
        {"type": "source", "id": label + "-source", "uri": "synthetic://" + label,
         "content": "Synthetic project decision and reason", "metadata": {"synthetic": True}},
        {"type": "assertion", "id": label + "-decision", "subject": label, "predicate": "decision",
         "value": "Use local transactions", "source_ids": [label + "-source"],
         "valid_from": "2026-10-01", "time_precision": "day"},
    ]


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="refactoredmemory-cli-")
        self.base = Path(self.tmp.name)
        self.db = self.base / "a.sqlite3"
        self.servers = []

    def tearDown(self):
        for server in self.servers:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
            server.stderr.close()
        self.tmp.cleanup()

    def cli(self, *args, db=None, input=None, expected=0):
        completed = subprocess.run(
            [sys.executable, "-m", "refactoredmemory", "--db", str(db or self.db), *map(str, args)],
            cwd=ROOT, input=input, text=True, capture_output=True, timeout=15,
        )
        self.assertEqual(completed.returncode, expected, completed.stderr)
        if expected:
            self.assertNotIn("Traceback", completed.stderr)
            return completed
        return json.loads(completed.stdout) if completed.stdout.strip() else None

    def grant(self, label, scopes="read,write,correct", *, db=None, kind="agent", peer=None):
        token = self.base / (label + ".token")
        command = ["grant", "--label", label, "--scopes", scopes, "--kind", kind, "--output", token]
        if peer:
            command += ["--peer-id", peer]
        result = self.cli(*command, db=db)
        self.assertEqual(result, {"written": str(token)})
        self.assertEqual(stat.S_IMODE(token.stat().st_mode), 0o600)
        self.assertNotIn(token.read_text().strip(), json.dumps(result))
        return token

    def start_server(self, db):
        process = subprocess.Popen(
            [sys.executable, "-m", "refactoredmemory", "--db", str(db), "serve", "--host", "127.0.0.1", "--port", "0"],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
        )
        self.servers.append(process)
        ready, _, _ = select.select([process.stderr], [], [], 5)
        self.assertTrue(ready, "CLI server did not announce a listening socket")
        line = process.stderr.readline()
        try:
            state = json.loads(line)
        except ValueError:
            self.fail("CLI server failed to start: " + line)
        self.assertEqual(state["endpoints"], ["/mcp", "/sync"])
        self.assertFalse(state["tls"])
        return state["listening"][1]

    def post(self, port, path, payload, token=None, headers=None):
        conn = HTTPConnection("127.0.0.1", port, timeout=5)
        request_headers = {"Content-Type": "application/json"}
        if token:
            request_headers["Authorization"] = "Bearer " + token.read_text().strip()
        request_headers.update(headers or {})
        conn.request("POST", path, json.dumps(payload), request_headers)
        response = conn.getresponse()
        body = response.read()
        result = json.loads(body) if body else None
        code = response.status
        conn.close()
        return code, result

    def test_init_grants_capture_owner_correction_and_revocation(self):
        initial = self.cli("init", "--store-id", "cli-personal-store", "--peer-id", "peer-a")
        self.assertEqual(initial["known_position"], 0)
        writer = self.grant("writer")
        saved = self.cli("call", "memory_submit", "--args", json.dumps({"actions": actions("project"), "request_id": "capture-one"}), "--token-file", writer)
        self.assertFalse(saved["duplicate"])
        reader = self.grant("reader", "read")
        denied = self.cli("call", "memory_submit", "--args", json.dumps({"actions": actions("denied")}), "--token-file", reader, expected=2)
        self.assertIn("AuthorizationError", denied.stderr)
        correction = {"type": "assertion", "id": "owner-correction", "subject": "project", "predicate": "decision",
                      "value": "Use SQLite WAL", "source_ids": ["project-source"], "kind": "correct",
                      "predecessors": ["project-decision"], "reason": "Explicit synthetic owner correction."}
        self.cli("owner-submit", "--actions", json.dumps([correction]), "--request-id", "correction-one")
        queried = self.cli("call", "memory_query", "--args", '{"subject":"project"}', "--token-file", reader)
        self.assertEqual(queried["assertions"][0]["id"], "owner-correction")
        self.assertTrue(queried["assertions"][0]["preferred"])
        self.cli("revoke", "--token-file", reader)
        self.cli("call", "memory_query", "--args", '{"known_at":1}', "--token-file", reader, expected=2)
        self.assertEqual(self.cli("status")["known_position"], 2)

    def test_actual_stdio_process_uses_protocol_without_stdout_logs(self):
        self.cli("init")
        token = self.grant("stdio-reader", "read")
        request = rpc("tools/call", name="memory_status", arguments={})
        request["id"] = 2
        stream = "\n".join(json.dumps(x) for x in [rpc(), request]) + "\n"
        result = subprocess.run([sys.executable, "-m", "refactoredmemory", "--db", str(self.db),
                                 "serve-stdio", "--token-file", str(token)], cwd=ROOT,
                                input=stream, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        replies = {r["id"]: r for r in map(json.loads, result.stdout.splitlines())}
        self.assertEqual(replies[1]["result"]["supportedVersions"], [VERSION])
        self.assertEqual(replies[2]["result"]["structuredContent"]["known_position"], 0)
        self.assertNotIn(token.read_text().strip(), result.stdout + result.stderr)

    def test_production_http_mcp_and_sync_two_offline_writers(self):
        second = self.base / "b.sqlite3"
        self.cli("init", "--store-id", "cli-shared", "--peer-id", "peer-a")
        self.cli("init", "--store-id", "cli-shared", "--peer-id", "peer-b", db=second)
        a_identity, b_identity = self.base / "a.identity.json", self.base / "b.identity.json"
        self.cli("identity", "--output", a_identity)
        self.cli("identity", "--output", b_identity, db=second)
        self.assertEqual(stat.S_IMODE(a_identity.stat().st_mode), 0o600)
        self.cli("peer-admit", "--identity-file", b_identity)
        self.cli("peer-admit", "--identity-file", a_identity, db=second)
        peer_token = self.grant("b-allows-a", "sync", db=second, kind="peer", peer="peer-a")
        client_token = self.grant("b-client", "read", db=second)
        # Both independent databases write before any server/connection exists.
        self.cli("owner-submit", "--actions", json.dumps(actions("offline-a")))
        self.cli("owner-submit", "--actions", json.dumps(actions("offline-b")), db=second)
        port = self.start_server(second)
        headers = {"Accept": "application/json, text/event-stream", "MCP-Protocol-Version": VERSION, "Mcp-Method": "server/discover"}
        code, response = self.post(port, "/mcp", rpc(), client_token, headers)
        self.assertEqual(code, 200, response)
        self.assertEqual(response["result"]["supportedVersions"], [VERSION])
        self.assertEqual(self.post(port, "/mcp", rpc(), headers=headers)[0], 401)
        self.assertEqual(self.post(port, "/mcp", rpc(), client_token, {**headers, "Origin": "https://untrusted.invalid"})[0], 403)
        peer_payload = {"protocol": "refactoredmemory-sync/1", "store_id": "cli-shared", "frontier": {}, "operations": [], "limit": 10}
        self.assertEqual(self.post(port, "/sync", peer_payload, client_token)[0], 401)
        self.assertEqual(self.post(port, "/sync", peer_payload)[0], 401)
        code, response = self.post(port, "/sync", {**peer_payload, "store_id": "wrong-store"}, peer_token)
        self.assertEqual(code, 400, response)
        exchanged = self.cli("sync", "--url", f"http://127.0.0.1:{port}/sync", "--token-file", peer_token,
                             "--expected-peer", "peer-b", "--batch-size", "1")
        self.assertEqual(exchanged["frontier"], {"peer-a": 1, "peer-b": 1})
        left = self.cli("query")
        right = self.cli("query", db=second)
        self.assertEqual({a["id"] for a in left["assertions"]}, {"offline-a-decision", "offline-b-decision"})
        self.assertEqual({a["id"] for a in left["assertions"]}, {a["id"] for a in right["assertions"]})
        self.assertEqual(left["frontier"], right["frontier"])
        self.cli("peer-revoke", "peer-a", db=second)
        self.assertIn(self.post(port, "/sync", peer_payload, peer_token)[0], [401, 403])

    def test_import_plan_apply_backup_restore_and_rebuild_are_real_commands(self):
        notes = self.base / "notes"
        notes.mkdir()
        (notes / "project.md").write_text("# Synthetic project\n- Chose SQLite WAL for durable transactions.\n")
        planned = self.cli("import", notes, "--root", notes)
        self.assertTrue(planned["dry_run"])
        self.assertFalse(self.db.exists(), "read-only planning created a destination")
        backup = self.base / "before-import.sqlite3"
        applied = self.cli("import", notes, "--root", notes, "--apply", "--backup", backup)
        self.assertEqual(applied["status"], "complete")
        self.assertTrue(applied["semantic_complete"])
        self.assertTrue(backup.is_file())
        before = self.cli("query")
        self.cli("rebuild")
        after = self.cli("query")
        self.assertEqual(before["assertions"], after["assertions"])
        snapshot = self.base / "snapshot.sqlite3"
        self.cli("backup", snapshot)
        restored_db = self.base / "restored.sqlite3"
        restored = self.cli("restore", snapshot, restored_db)
        self.assertNotEqual(restored["peer_id"], self.cli("status")["peer_id"])
        restored_query = self.cli("query", db=restored_db)
        self.assertEqual([a["id"] for a in before["assertions"]], [a["id"] for a in restored_query["assertions"]])
        self.cli("backup", snapshot, expected=2)
        self.cli("restore", snapshot, restored_db, expected=2)

    def test_nonloopback_plaintext_listener_is_refused(self):
        refused = self.cli("serve", "--host", "0.0.0.0", "--port", "0", expected=2)
        self.assertIn("require TLS", refused.stderr)


if __name__ == "__main__":
    unittest.main()
