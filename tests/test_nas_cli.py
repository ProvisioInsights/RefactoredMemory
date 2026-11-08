"""Synthetic TLS processes, route separation, capacity and bounded private audit."""
from __future__ import annotations

import contextlib
import datetime as dt
from http.client import HTTPSConnection
import io
import ipaddress
import json
import os
from pathlib import Path
import select
import signal
import socket
import ssl
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from refactoredmemory.audit import AuditLog
from refactoredmemory.cli import _validate_audit_destination, main, parser
from refactoredmemory.store import Store, ValidationError

try:
    import jwt
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-07-28"
PREFIX = "io.modelcontextprotocol/"


class AuditTests(unittest.TestCase):
    def test_private_rotation_allowlist_and_runtime_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            log = AuditLog(path, max_bytes=1024)
            event = {"event": "secret-data", "request_id": "a" * 32, "route": "mcp",
                     "method": "tools/call", "tool": "memory_status", "grant_id": "b" * 32,
                     "status": 200, "token": "secret-token", "body": "secret-body",
                     "url": "https://secret.example", "address": "192.0.2.42"}
            for _ in range(15):
                log(event)
            files = [path, path.with_name(path.name + ".1")]
            for file in files:
                self.assertLessEqual(file.stat().st_size, 1024)
                self.assertEqual(stat.S_IMODE(file.stat().st_mode), 0o600)
                content = file.read_text()
                self.assertNotIn("secret", content)
                self.assertNotIn("192.0.2.42", content)
                for line in content.splitlines():
                    self.assertEqual(json.loads(line)["grant_id"], "b" * 32)
            output = io.StringIO()
            with mock.patch("refactoredmemory.audit.os.write", side_effect=OSError("secret-sink-path")), contextlib.redirect_stderr(output):
                log(event)
                log(event)
            self.assertEqual(log.failures, 2)
            self.assertEqual(output.getvalue().count("audit sink unavailable"), 1)
            self.assertNotIn("secret-sink-path", output.getvalue())
            log.close()

    def test_audit_refuses_symlink_public_file_and_unsafe_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            path = base / "target"
            path.write_text("do not change")
            path.chmod(0o644)
            with self.assertRaises(ValidationError):
                AuditLog(path)
            path.chmod(0o600)
            alias = base / "alias"
            alias.symlink_to(path)
            with self.assertRaises(ValidationError):
                AuditLog(alias)
            base.chmod(0o777)
            with self.assertRaises(ValidationError):
                AuditLog(base / "new")
            base.chmod(0o700)
            self.assertEqual(path.read_text(), "do not change")

    def test_audit_refuses_unrelated_private_content_and_reopens_its_own_log(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "content"
            for raw in (b"SQLite format 3\x00", b"private-token\n", b'{"private":"configuration"}\n'):
                path.write_bytes(raw)
                path.chmod(0o600)
                with self.assertRaises(ValidationError):
                    AuditLog(path)
                self.assertEqual(path.read_bytes(), raw)
            path.unlink()
            log = AuditLog(path)
            log({"request_id": "a" * 32, "route": "mcp", "status": 200})
            log.close()
            reopened = AuditLog(path)
            reopened({"request_id": "b" * 32, "route": "metadata", "status": 200})
            reopened.close()
            self.assertEqual(len(path.read_text().splitlines()), 2)

    def test_audit_rotation_and_hardlinks_cannot_target_protected_files(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            protected = base / "audit.1"
            protected.write_text("private")
            with self.assertRaises(ValidationError):
                _validate_audit_destination(base / "audit", [protected])
            alias = base / "hardlink"
            os.link(protected, alias)
            with self.assertRaises(ValidationError):
                _validate_audit_destination(alias, [protected])
            self.assertEqual(protected.read_text(), "private")


@unittest.skipUnless(HAS_CRYPTO, "optional OAuth dependencies are not installed")
class NasCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="refactoredmemory-nas-")
        self.base = Path(self.tmp.name)
        self.db = self.base / "nas.sqlite3"
        self.processes = []
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "synthetic.invalid")])
        now = dt.datetime.now(dt.timezone.utc)
        cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                .public_key(self.key.public_key()).serial_number(x509.random_serial_number())
                .not_valid_before(now - dt.timedelta(minutes=1)).not_valid_after(now + dt.timedelta(days=1))
                .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), critical=False)
                .sign(self.key, hashes.SHA256()))
        self.cert = self.base / "tls.crt"
        self.cert.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        self.private_key = self.base / "tls.key"
        self.private_key.write_bytes(self.key.private_bytes(serialization.Encoding.PEM,
                                    serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        self.private_key.chmod(0o600)
        jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(self.key.public_key()))
        jwk.update(kid="synthetic", alg="RS256", use="sig")
        (self.base / "keys.json").write_text(json.dumps({"keys": [jwk]}))
        with Store(self.base / "mac.sqlite3", store_id="nas-test", peer_id="mac") as peer:
            peer_identity = peer.identity()
        with Store(self.db, store_id="nas-test", peer_id="nas") as store:
            self.grant = store.create_grant("synthetic OAuth reader", ["read"])
            store.admit_peer("mac", peer_identity["key_hex"])
            self.peer_token = store.create_grant("synthetic Mac", ["sync"], kind="peer", peer_id="mac")
        token_path = self.base / "reader.token"
        token_path.write_text(self.grant)
        token_path.chmod(0o600)
        self.config = self.base / "oauth.json"
        self.config.write_text(json.dumps({
            "issuer": "https://issuer.synthetic", "resource": "https://memory.synthetic/mcp",
            "jwks_file": "keys.json", "bindings": [{"subject": "synthetic-owner", "client_id": "synthetic-client", "grant_token_file": "reader.token"}]}))

    def tearDown(self):
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
            process.stderr.close()
        self.tmp.cleanup()

    def access_token(self):
        now = int(time.time())
        return jwt.encode({"iss": "https://issuer.synthetic", "aud": "https://memory.synthetic/mcp",
                           "sub": "synthetic-owner", "client_id": "synthetic-client", "iat": now,
                           "nbf": now, "exp": now + 60, "scope": "memory:read"},
                          self.key, algorithm="RS256", headers={"kid": "synthetic", "typ": "at+jwt"})

    def command(self):
        return [sys.executable, "-m", "refactoredmemory", "--db", str(self.db), "serve-nas",
                "--mcp-host", "127.0.0.1", "--mcp-port", "0", "--sync-port", "0",
                "--mcp-cert-file", str(self.cert), "--mcp-key-file", str(self.private_key),
                "--sync-cert-file", str(self.cert), "--sync-key-file", str(self.private_key),
                "--oauth-config", str(self.config), "--allow-host", "memory.synthetic",
                "--allow-host", "sync.synthetic", "--min-free-bytes", "0",
                "--audit-log", str(self.base / "audit.jsonl")]

    def start(self, *extra):
        process = subprocess.Popen(self.command() + list(extra), cwd=ROOT,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        self.processes.append(process)
        self.assertTrue(select.select([process.stderr], [], [], 8)[0], "NAS CLI did not start")
        line = process.stderr.readline()
        try:
            state = json.loads(line)
        except ValueError:
            self.fail("NAS CLI startup failed: " + line)
        self.assertEqual(state["profile"], "nas")
        self.assertTrue(state["tls"])
        return process, state["mcp"]["listening"][1], state["sync"]["listening"][1]

    def request(self, port, path, *, token=None, body=None, method="POST", sync=False):
        context = ssl.create_default_context(cafile=str(self.cert))
        connection = HTTPSConnection("127.0.0.1", port, context=context, timeout=4)
        headers = {"Host": "sync.synthetic" if sync else "memory.synthetic", "Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        if path == "/mcp":
            headers.update({"Accept": "application/json, text/event-stream", "MCP-Protocol-Version": VERSION, "Mcp-Method": "tools/call", "Mcp-Name": "memory_status"})
        connection.request(method, path, json.dumps(body) if body is not None else None, headers)
        response = connection.getresponse()
        raw = response.read()
        result = (response.status, dict(response.getheaders()), json.loads(raw) if raw else None)
        connection.close()
        return result

    def test_separate_tls_routes_oauth_revocation_audit_and_shutdown(self):
        process, public, private = self.start()
        token = self.access_token()
        payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "memory_status", "arguments": {}, "_meta": {PREFIX + "protocolVersion": VERSION, PREFIX + "clientCapabilities": {}}}}
        code, _, result = self.request(public, "/mcp", token=token, body=payload)
        self.assertEqual(code, 200, result)
        self.assertEqual(result["result"]["structuredContent"]["store_id"], "nas-test")
        self.assertEqual(self.request(public, "/sync", token=self.peer_token, body={})[0], 404)
        self.assertEqual(self.request(private, "/mcp", token=token, body=payload, sync=True)[0], 404)
        metadata = "/.well-known/oauth-protected-resource/mcp"
        self.assertEqual(self.request(private, metadata, method="GET", sync=True)[0], 404)
        code, _, discovery = self.request(public, metadata, method="GET")
        self.assertEqual(code, 200)
        self.assertEqual(discovery["authorization_servers"], ["https://issuer.synthetic"])
        self.assertEqual(self.request(public, "/mcp", token=self.grant, body=payload)[0], 401)
        with Store(self.db) as store:
            store.revoke_grant(self.grant)
        self.assertEqual(self.request(public, "/mcp", token=token, body=payload)[0], 401)
        process.terminate()
        self.assertEqual(process.wait(timeout=8), 0)
        audit = (self.base / "audit.jsonl").read_text()
        self.assertNotIn(token, audit)
        self.assertNotIn(self.grant, audit)
        self.assertNotIn(self.peer_token, audit)
        self.assertTrue(any(json.loads(line)["grant_id"] for line in audit.splitlines()))
        with Store(self.db) as store:
            self.assertEqual(store.status()["known_position"], 0)

    def test_capacity_refusal_is_retryable_without_acknowledgement(self):
        process, public, private = self.start("--max-store-bytes", "1")
        with Store(self.base / "mac.sqlite3", store_id="nas-test", peer_id="mac") as peer:
            # Pairing fixture uses the actual generated signing key.
            with Store(self.db) as nas:
                nas.admit_peer("mac", peer.identity()["key_hex"])
            peer.submit([{"type": "entity", "id": "offline", "entity_type": "note", "label": "Synthetic offline note"}])
            payload = {"protocol": "refactoredmemory-sync/1", "store_id": "nas-test", "frontier": {},
                       "operations": peer.export_operations()["operations"], "limit": 10}
        code, headers, result = self.request(private, "/sync", token=self.peer_token, body=payload, sync=True)
        self.assertEqual(code, 503, result)
        self.assertEqual(result["error"], "capacity_paused")
        self.assertEqual(result["reason"], "store_limit")
        self.assertEqual(headers["Retry-After"], "300")
        with Store(self.db) as nas:
            self.assertEqual(nas.status()["known_position"], 0)
        process.terminate()
        self.assertEqual(process.wait(timeout=8), 0)
        _, _, private = self.start()
        code, _, result = self.request(private, "/sync", token=self.peer_token, body=payload, sync=True)
        self.assertEqual(code, 200, result)
        with Store(self.db) as nas:
            self.assertEqual(nas.status()["known_position"], 1)

    def test_bad_tls_fails_without_starting_listeners_or_leaking_token(self):
        self.private_key.write_text("invalid-key-with-private-material")
        completed = subprocess.run(self.command(), cwd=ROOT, capture_output=True, text=True, timeout=8)
        self.assertEqual(completed.returncode, 2)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertNotIn("invalid-key-with-private-material", completed.stderr)
        self.assertIn("TLS certificate or private key is unavailable or invalid", completed.stderr)

    def test_second_bind_failure_closes_first_listener(self):
        with socket.socket() as occupied, socket.socket() as reserved:
            occupied.bind(("127.0.0.1", 0))
            occupied.listen()
            reserved.bind(("127.0.0.1", 0))
            public_port = reserved.getsockname()[1]
            reserved.close()
            completed = subprocess.run(self.command() + ["--mcp-port", str(public_port),
                                       "--sync-port", str(occupied.getsockname()[1])],
                                       cwd=ROOT, capture_output=True, text=True, timeout=8)
            self.assertEqual(completed.returncode, 2)
            self.assertNotIn("Traceback", completed.stderr)
            with socket.socket() as check:
                check.bind(("127.0.0.1", public_port))

    def test_audit_cannot_use_store_or_oauth_grant_files(self):
        for destination in (self.db, self.base / "reader.token", self.config,
                            self.base / "keys.json", self.private_key, self.cert):
            before = destination.read_bytes()
            completed = subprocess.run(self.command() + ["--audit-log", str(destination)],
                                       cwd=ROOT, capture_output=True, text=True, timeout=8)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("Audit destination conflicts", completed.stderr)
            self.assertNotIn(self.grant, completed.stderr)
            self.assertEqual(destination.read_bytes(), before)


class SchedulerCliTests(unittest.TestCase):
    def test_import_and_owner_capacity_guards_preserve_uncommitted_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "notes"
            source.mkdir()
            note = source / "synthetic.md"
            note.write_text("# Synthetic ingress\n- Capacity guards preserve originals.\n")
            original = note.read_bytes()
            db = base / "store.sqlite3"
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main(["--db", str(db), "import", str(source), "--root", str(source),
                             "--apply", "--backup", str(base / "before.sqlite3"),
                             "--min-free-bytes", "0", "--max-store-bytes", "1"])
            self.assertEqual(code, 2)
            result = json.loads(output.getvalue())
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["committed_batches"], 0)
            self.assertEqual(result["pause"], {"error": "capacity_paused", "reason": "store_limit", "retry_after_seconds": 300})
            self.assertEqual(note.read_bytes(), original)
            with Store(db) as store:
                self.assertEqual(store.status()["known_position"], 0)
            error = io.StringIO()
            with contextlib.redirect_stderr(error):
                code = main(["--db", str(db), "owner-submit", "--actions",
                             '[{"type":"entity","id":"not-committed","entity_type":"note","label":"Synthetic"}]',
                             "--min-free-bytes", "0", "--max-store-bytes", "1"])
            self.assertEqual(code, 2)
            self.assertIn("CapacityError", error.getvalue())
            with Store(db) as store:
                self.assertEqual(store.status()["known_position"], 0)

    def test_sync_watch_wires_config_and_restores_signal_handlers(self):
        before = {number: signal.getsignal(number) for number in (signal.SIGINT, signal.SIGTERM)}
        with tempfile.TemporaryDirectory() as directory, mock.patch("refactoredmemory.sync.SyncRunner") as runner:
            runner.return_value.run.return_value = {"state": "stopped"}
            with contextlib.redirect_stdout(io.StringIO()):
                result = main(["--db", str(Path(directory) / "store.db"), "sync-watch", "--config", "private-config.json"])
            self.assertEqual(result, 0)
            self.assertEqual(runner.call_args.args[1], "private-config.json")
            self.assertFalse(runner.call_args.kwargs["stop_event"].is_set())
            self.assertEqual({number: signal.getsignal(number) for number in before}, before)

    def test_nas_defaults_keep_private_sync_on_loopback(self):
        args = parser().parse_args(["serve-nas", "--mcp-cert-file", "cert", "--mcp-key-file", "key",
                                   "--sync-cert-file", "cert", "--sync-key-file", "key", "--oauth-config", "oauth"])
        self.assertEqual(args.sync_host, "127.0.0.1")
        self.assertEqual(args.min_free_bytes, 536870912)
        self.assertFalse(args.allow_legacy_http)


if __name__ == "__main__":
    unittest.main()
