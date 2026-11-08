"""Bounded automatic sync scheduling, using synthetic stores and deterministic time."""
from __future__ import annotations

import io
import json
import os
import shutil
from pathlib import Path
import tempfile
import threading
import time
import unittest
import urllib.error
from unittest.mock import patch

from refactoredmemory.sync import SyncError, SyncRunner, _AttemptDeadline, _post, _retry_after, sync_once


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class FakeStore:
    def __init__(self, path):
        self.path = str(path)
        self.frontier = {"local": 1}
        self.receipts = 0

    def configure_capacity(self, **options):
        self.capacity = options

    def status(self):
        return {"store_id": "synthetic-store", "peer_id": "local", "frontier": dict(self.frontier),
                "pending": 0, "rejected": 0}

    def export_operations(self, frontier=None, limit=100):
        return {"operations": [], "frontier": dict(self.frontier), "more": False}

    def receive(self, operations, peer_id):
        self.receipts += 1
        return {"pending": 0, "rejected": 0}


def result(complete=True, reason="shared_frontier"):
    return {"complete": complete, "reason": reason, "frontier": {"local": 1},
            "sent": 0, "received": 0, "pending": 0, "rejected": 0}


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.token = self.root / "peer.token"
        self.token.write_text("synthetic-peer-token\n")
        self.token.chmod(0o600)
        self.store = FakeStore(self.root / "store.sqlite")
        self.clock = Clock()
        self.config = {"version": 1, "url": "https://nas.example.invalid/sync", "expected_peer": "remote",
                       "token_file": str(self.token), "status_file": str(self.root / "sync-status.json"),
                       "interval_seconds": 5, "max_backoff_seconds": 60, "min_free_bytes": 0}

    def runner(self, **kwargs):
        return SyncRunner(self.store, self.config, clock=self.clock, **kwargs)

    def test_persisted_retry_after_survives_restart_and_early_calls_do_not_send(self):
        with patch("refactoredmemory.sync.sync_once", side_effect=SyncError("rate_limited", "HTTP 429", retry_after_seconds=120)) as sync:
            state = self.runner().step()
            self.assertEqual(state["state"], "backoff")
            self.assertEqual(state["next_attempt_at"], 1120)
            self.runner().step()
            self.assertEqual(sync.call_count, 1)
        self.clock.now = 1120
        self.store.frontier = {"local": 4}
        with patch("refactoredmemory.sync.sync_once", return_value=result()) as sync:
            state = self.runner().step()
            self.assertEqual(sync.call_count, 1)
            self.assertEqual(state["frontier"], {"local": 4})
            self.assertEqual(state["failures"], 0)
        self.assertEqual(os.stat(self.config["status_file"]).st_mode & 0o777, 0o600)
        self.assertNotIn("synthetic-peer-token", Path(self.config["status_file"]).read_text())

    def test_clean_stop_resumes_without_skipping_saved_backoff(self):
        event = threading.Event()
        runner = self.runner(stop_event=event)
        with patch("refactoredmemory.sync.sync_once", side_effect=SyncError("transport_error", "offline")):
            state = runner.step()
        deadline = state["next_attempt_at"]
        event.set()
        self.assertEqual(runner.step()["state"], "stopped")
        resumed = self.runner()
        with patch("refactoredmemory.sync.sync_once", return_value=result()) as sync:
            self.assertEqual(resumed.step()["state"], "backoff")
            self.assertEqual(sync.call_count, 0)
            self.assertEqual(resumed.status["next_attempt_at"], deadline)
            self.clock.now = deadline
            self.assertEqual(resumed.step()["state"], "waiting")
            self.assertEqual(sync.call_count, 1)

    def test_transport_backoff_increases_and_is_capped(self):
        runner = self.runner()
        delays = []
        with patch("refactoredmemory.sync.sync_once", side_effect=SyncError("transport_error", "failed")):
            for _ in range(6):
                state = runner.step()
                delays.append(state["next_attempt_at"] - self.clock.now)
                self.clock.now = state["next_attempt_at"]
        self.assertEqual(delays, [5, 10, 20, 40, 60, 60])

    def test_capacity_pause_waits_without_ack_or_network(self):
        runner = self.runner()
        with patch.object(runner, "_disk_guard", side_effect=SyncError("capacity_paused", "low disk", retry_after_seconds=300)), patch("refactoredmemory.sync.sync_once") as sync:
            state = runner.step()
            self.assertEqual(state["state"], "backoff")
            self.assertEqual(state["last_error"], "capacity_paused")
            self.assertEqual(state["next_attempt_at"], 1300)
            self.assertEqual(self.store.receipts, 0)
            sync.assert_not_called()
            runner.step()
            sync.assert_not_called()

    def test_store_capacity_error_uses_same_deferred_state(self):
        class CapacityFailure(Exception):
            code = "capacity_paused"
            reason = "store_limit"
            retry_after_seconds = 300
        with patch("refactoredmemory.sync.sync_once", side_effect=CapacityFailure()):
            state = self.runner().step()
        self.assertEqual(state["state"], "backoff")
        self.assertEqual(state["next_attempt_at"], 1300)

    def test_auth_failure_pauses_until_restart_then_reloads_token(self):
        runner = self.runner()
        with patch("refactoredmemory.sync.sync_once", side_effect=SyncError("http_error", "HTTP 401", http_status=401)) as sync:
            state = runner.step()
            self.assertEqual(state["state"], "paused")
            self.clock.now = 2000
            runner.step()
            self.assertEqual(sync.call_count, 1)
        self.token.write_text("rotated-synthetic-token\n")
        with patch("refactoredmemory.sync.sync_once", return_value=result()) as sync:
            self.runner().step()
            self.assertEqual(sync.call_args.args[2], "rotated-synthetic-token")

    def test_fresh_runner_waits_for_persisted_auth_pause_deadline(self):
        with patch("refactoredmemory.sync.sync_once", side_effect=SyncError("http_error", "HTTP 401", http_status=401)):
            self.runner().step()
        stopping = threading.Event()
        runner = self.runner(stop_event=stopping)
        waits = []
        def advance(delay):
            waits.append(delay)
            self.clock.now += delay
            return stopping.is_set()
        def succeeded(*args, **kwargs):
            stopping.set()
            return result()
        with patch.object(stopping, "wait", side_effect=advance), \
                patch("refactoredmemory.sync.sync_once", side_effect=succeeded) as sync:
            state = runner.run()
        self.assertEqual(waits[0], 5)
        self.assertEqual(sync.call_count, 1)
        self.assertEqual(state["state"], "stopped")

    def test_cancellation_interrupts_wait_and_releases_lock(self):
        stopping = threading.Event()
        runner = self.runner(stop_event=stopping)
        def done(*args, **kwargs):
            stopping.set()
            return result()
        with patch("refactoredmemory.sync.sync_once", side_effect=done):
            state = runner.run()
        self.assertEqual(state["state"], "stopped")
        other = self.runner()
        self.assertTrue(other._acquire())
        other._release()

    def test_second_runner_cannot_overlap_store_cycle(self):
        first, second = self.runner(), self.runner()
        first._acquire()
        try:
            with self.assertRaisesRegex(SyncError, "Another sync runner"):
                second.step()
        finally:
            first._release()

    def test_private_tokens_symlinks_and_wrong_status_identity_fail_closed(self):
        self.token.chmod(0o644)
        with patch("refactoredmemory.sync.sync_once") as sync:
            state = self.runner().step()
            self.assertEqual(state["state"], "paused")
            self.assertEqual(state["last_error"], "private_file_error")
            sync.assert_not_called()
        self.token.chmod(0o600)
        status_path = Path(self.config["status_file"])
        state = json.loads(status_path.read_text())
        state["identity"] = "another-peer"
        status_path.write_text(json.dumps(state))
        with self.assertRaisesRegex(SyncError, "different configuration"):
            self.runner().step()
        status_path.unlink()
        original = self.root / "actual.token"
        self.token.rename(original)
        self.token.symlink_to(original)
        with patch("refactoredmemory.sync.sync_once") as sync:
            self.assertEqual(self.runner().step()["state"], "paused")
            sync.assert_not_called()

    def test_json_config_relative_paths_and_bounded_options(self):
        config = {**self.config, "token_file": "peer.token", "status_file": "state.json"}
        path = self.root / "sync.json"
        path.write_text(json.dumps(config))
        runner = SyncRunner(self.store, path, clock=self.clock)
        # The configuration directory is pinned canonically; macOS exposes
        # temporary paths through the normal /var -> /private/var alias.
        self.assertEqual(runner.config["token_file"], str(self.token.resolve()))
        for update in ({"interval_seconds": 0}, {"batch_size": True}, {"unknown": 1},
                       {"expected_peer": "local"}, {"version": 2}):
            with self.subTest(update=update), self.assertRaises(SyncError):
                SyncRunner(self.store, {**self.config, **update}, clock=self.clock)

    def test_status_path_cannot_replace_store_credentials_or_configuration(self):
        for protected in (self.store.path, self.store.path + "-wal", self.store.path + "-shm",
                          self.store.path + ".sync.lock", str(self.token)):
            with self.subTest(protected=protected), self.assertRaisesRegex(SyncError, "separate"):
                SyncRunner(self.store, {**self.config, "status_file": protected}, clock=self.clock)
        alias = self.root / "credential-alias"
        os.link(self.token, alias)
        with self.assertRaisesRegex(SyncError, "separate"):
            SyncRunner(self.store, {**self.config, "status_file": str(alias)}, clock=self.clock)
        path = self.root / "same-config.json"
        path.write_text(json.dumps({**self.config, "status_file": str(path)}))
        with self.assertRaisesRegex(SyncError, "separate"):
            SyncRunner(self.store, path, clock=self.clock)
        self.assertEqual(self.token.read_text(), "synthetic-peer-token\n")

    def test_private_file_must_belong_to_runtime_user(self):
        from types import SimpleNamespace
        import stat
        foreign = SimpleNamespace(st_mode=stat.S_IFREG | 0o600, st_size=20, st_uid=os.geteuid() + 1)
        with patch("os.fstat", return_value=foreign), self.assertRaises(SyncError):
            SyncRunner._private_bytes(self.token, 4096)

    def test_cancelled_response_does_not_apply_fetched_operations(self):
        stopping = threading.Event()
        def response(*args, **kwargs):
            stopping.set()
            return {"protocol": "refactoredmemory-sync/1", "store_id": "synthetic-store", "peer_id": "remote",
                    "frontier": {"local": 1}, "operations": [], "more": False, "receipt": {"pending": 0}}
        with patch("refactoredmemory.sync._post", side_effect=response), self.assertRaisesRegex(SyncError, "cancelled"):
            sync_once(self.store, self.config["url"], "synthetic", stop_event=stopping)
        self.assertEqual(self.store.receipts, 0)

    def test_http_budget_retry_after_is_returned_without_burst_retries(self):
        for status, body, expected in ((503, b'{"error":"capacity_paused","reason":"low_disk"}', "capacity_paused"),
                                        (429, b'{"error":"busy"}', "rate_limited")):
            error = urllib.error.HTTPError("https://peer.invalid/sync", status, "paused",
                                          {"Retry-After": "120"}, io.BytesIO(body))
            with self.subTest(status=status), patch("urllib.request.build_opener") as opener:
                opener.return_value.open.side_effect = error
                with self.assertRaises(SyncError) as caught:
                    _post("https://peer.invalid/sync", "synthetic", {}, 1, 5)
                self.assertEqual(caught.exception.code, expected)
                self.assertEqual(caught.exception.retry_after_seconds, 120)
                self.assertEqual(opener.return_value.open.call_count, 1)
        with patch("refactoredmemory.sync.time.time", return_value=0):
            self.assertEqual(_retry_after("Thu, 01 Jan 1970 00:02:00 GMT"), 120)
        self.assertIsNone(_retry_after("invalid"))

    def test_slow_header_body_and_cancellation_have_wall_clock_bounds(self):
        from http.server import BaseHTTPRequestHandler
        from refactoredmemory.cli import PeerHTTPServer
        for stage in ("headers", "body", "cancel", "rate_limit"):
            with self.subTest(stage=stage):
                requests = []
                class SlowHandler(BaseHTTPRequestHandler):
                    def do_POST(self):
                        requests.append(self.path)
                        self.rfile.read(int(self.headers["Content-Length"]))
                        body = b'{"synthetic":"' + b"a" * 100 + b'"}'
                        try:
                            if stage == "headers":
                                data = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 2\r\n\r\n{}"
                            else:
                                self.send_response(429 if stage == "rate_limit" else 200)
                                if stage == "rate_limit":
                                    self.send_header("Retry-After", "120")
                                self.send_header("Content-Type", "application/json")
                                self.send_header("Content-Length", str(len(body)))
                                self.end_headers()
                                data = body
                            for byte in data:
                                self.wfile.write(bytes([byte]))
                                self.wfile.flush()
                                time.sleep(0.02)
                        except (OSError, ValueError):
                            pass

                    def log_message(self, *args):
                        pass

                server = PeerHTTPServer(("127.0.0.1", 0), SlowHandler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                stopping = threading.Event()
                timer = threading.Timer(0.15, stopping.set) if stage == "cancel" else None
                if timer:
                    timer.start()
                try:
                    start = time.monotonic()
                    with self.assertRaises(SyncError) as caught:
                        _post(f"http://127.0.0.1:{server.server_port}/sync", "synthetic", {},
                              5 if stage == "cancel" else 0.15, 0, stop_event=stopping)
                    self.assertLess(time.monotonic() - start, 0.75)
                    self.assertEqual(caught.exception.code, "cancelled" if stage == "cancel" else
                                     "rate_limited" if stage == "rate_limit" else "transport_timeout")
                    if stage == "rate_limit":
                        self.assertEqual(caught.exception.retry_after_seconds, 120)
                    self.assertEqual(requests, ["/sync"])
                    self.assertFalse(any(t.name == "refactoredmemory-sync-deadline" for t in threading.enumerate()))
                finally:
                    if timer:
                        timer.cancel()
                        timer.join()
                    server.shutdown()
                    server.server_close()
                    thread.join(2)

    def test_stalled_dns_worker_is_terminated_and_reaped(self):
        import subprocess
        real_popen = subprocess.Popen
        children = []
        def capture(*args, **kwargs):
            child = real_popen(*args, **kwargs)
            children.append(child)
            return child
        start = time.monotonic()
        with patch("refactoredmemory.sync._RESOLVER_CODE", "import time; time.sleep(30)"), \
                patch("subprocess.Popen", side_effect=capture):
            with self.assertRaises(SyncError) as caught:
                with _AttemptDeadline(0.15) as deadline:
                    deadline.resolve("synthetic.invalid", 443)
        self.assertEqual(caught.exception.code, "transport_timeout")
        self.assertLess(time.monotonic() - start, 0.75)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll())
        self.assertFalse(any(t.name == "refactoredmemory-sync-deadline" for t in threading.enumerate()))

    def test_resolver_validates_addresses_and_literal_ip_needs_no_worker(self):
        with patch("subprocess.Popen") as child:
            with _AttemptDeadline(1) as deadline:
                self.assertEqual(deadline.resolve("127.0.0.1", 443)[0][-1], ("127.0.0.1", 443))
            child.assert_not_called()
        rows = [[2, 1, 6, ["127.0.0.1", 443]], [10, 1, 6, ["::1", 443, 0, 0]]]
        import socket
        rows[1][0] = int(socket.AF_INET6)
        code = "print(" + repr(json.dumps(rows)) + ")"
        with patch("refactoredmemory.sync._RESOLVER_CODE", code):
            with _AttemptDeadline(1) as deadline:
                resolved = deadline.resolve("synthetic.invalid", 443)
            self.assertEqual(len(resolved), 2)
        bad = "print('[ [2,1,6,[\\\"127.0.0.1\\\",444]] ]')"
        with patch("refactoredmemory.sync._RESOLVER_CODE", bad):
            with self.assertRaises(SyncError):
                with _AttemptDeadline(1) as deadline:
                    deadline.resolve("synthetic.invalid", 443)

    def test_stalled_tls_handshake_is_interrupted_and_cleanup_is_joined(self):
        import socket
        for cancel in (False, True):
            with self.subTest(cancel=cancel):
                listener = socket.socket()
                listener.bind(("127.0.0.1", 0))
                listener.listen(1)
                listener.settimeout(2)
                server_done = threading.Event()
                def accept_without_handshake():
                    try:
                        connection, _ = listener.accept()
                        with connection:
                            server_done.wait(2)
                    except OSError:
                        pass
                server = threading.Thread(target=accept_without_handshake, daemon=True)
                server.start()
                stopping = threading.Event()
                timer = threading.Timer(0.15, stopping.set) if cancel else None
                if timer:
                    timer.start()
                try:
                    start = time.monotonic()
                    with patch("urllib.request.getproxies", return_value={}), self.assertRaises(SyncError) as caught:
                        _post(f"https://127.0.0.1:{listener.getsockname()[1]}/sync", "synthetic", {},
                              5 if cancel else 0.15, 0, stop_event=stopping)
                    self.assertEqual(caught.exception.code, "cancelled" if cancel else "transport_timeout")
                    self.assertLess(time.monotonic() - start, 0.75)
                    self.assertFalse(any(t.name == "refactoredmemory-sync-deadline" for t in threading.enumerate()))
                finally:
                    if timer:
                        timer.cancel()
                        timer.join()
                    server_done.set()
                    listener.close()
                    server.join(2)

    @unittest.skipUnless(shutil.which("openssl"), "OpenSSL generates a synthetic TLS certificate")
    def test_deadline_https_keeps_original_hostname_and_certificate_verification(self):
        import ssl
        import subprocess
        from http.server import BaseHTTPRequestHandler
        from refactoredmemory.cli import PeerHTTPServer
        cert, key = self.root / "synthetic.crt", self.root / "synthetic.key"
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                        "-keyout", str(key), "-out", str(cert), "-days", "1", "-subj", "/CN=localhost",
                        "-addext", "subjectAltName=DNS:localhost"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert, key)
        received = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                received.append(self.headers["Authorization"])
                data = b'{"synthetic":"tls"}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            def log_message(self, *args):
                pass
        server = PeerHTTPServer(("127.0.0.1", 0), Handler, context)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.dict(os.environ, {"SSL_CERT_FILE": str(cert)}), patch("urllib.request.getproxies", return_value={}):
                response = _post(f"https://localhost:{server.server_port}/sync", "synthetic", {}, 2, 0)
                self.assertEqual(response, {"synthetic": "tls"})
                # Same trusted certificate has no IP SAN: using the numeric host
                # must fail, proving hostname verification was not weakened.
                with self.assertRaises(SyncError):
                    _post(f"https://127.0.0.1:{server.server_port}/sync", "synthetic", {}, 2, 0)
            self.assertEqual(received, ["Bearer synthetic"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(2)

    def test_real_store_reserve_failure_does_not_ack_and_resume_uses_durable_frontier(self):
        from types import SimpleNamespace
        from refactoredmemory.store import Store
        with Store(self.root / "real.sqlite", store_id="synthetic-store", peer_id="local") as local, \
                Store(self.root / "remote.sqlite", store_id="synthetic-store", peer_id="remote") as remote:
            local.admit_peer("remote", remote.identity()["key_hex"])
            remote.submit([{"type": "entity", "id": "note", "entity_type": "note", "label": "Synthetic note"}])
            exported = remote.export_operations()
            response = {"protocol": "refactoredmemory-sync/1", "store_id": "synthetic-store", "peer_id": "remote",
                        **exported, "receipt": {"pending": 0, "rejected": 0}}
            config = {**self.config, "min_free_bytes": 100}
            runner = SyncRunner(local, config, clock=self.clock)
            with patch("refactoredmemory.sync._post", return_value=response), \
                    patch("shutil.disk_usage", return_value=SimpleNamespace(free=101)):
                state = runner.step()
            self.assertEqual(state["state"], "backoff")
            self.assertEqual(state["last_reason"], "low_disk")
            self.assertEqual(state["frontier"], {})
            self.assertEqual(local.status()["known_position"], 0)
            self.assertEqual(local.status()["pending"], 0)
            self.assertIsNone(local.get_entity("note"))
            self.clock.now = state["next_attempt_at"]
            with patch("refactoredmemory.sync._post", return_value=response):
                state = SyncRunner(local, config, clock=self.clock).step()
            self.assertEqual(state["state"], "waiting")
            self.assertTrue(state["last_result"]["complete"])
            self.assertEqual(local.status()["known_position"], 1)
            self.assertEqual(state["frontier"], {"remote": 1})

    def test_real_two_peer_http_cycle_and_restart(self):
        from refactoredmemory.store import Store
        from test_sync import peer_server
        remote_path = self.root / "http-remote.sqlite"
        with Store(self.root / "http-local.sqlite", store_id="synthetic-http", peer_id="local") as local:
            with Store(remote_path, store_id="synthetic-http", peer_id="remote") as remote:
                local.admit_peer("remote", remote.identity()["key_hex"])
                remote.admit_peer("local", local.identity()["key_hex"])
                token = remote.create_grant("synthetic scheduler", ["sync"], kind="peer", peer_id="local")
                remote.submit([{"type": "entity", "id": "remote-note", "entity_type": "note", "label": "Remote synthetic note"}])
            self.token.write_text(token)
            local.submit([{"type": "entity", "id": "local-note", "entity_type": "note", "label": "Local synthetic note"}])
            with peer_server(remote_path) as url:
                config = {**self.config, "url": url}
                state = SyncRunner(local, config, clock=self.clock).step()
                self.assertTrue(state["last_result"]["complete"])
                self.clock.now = state["next_attempt_at"]
                repeated = SyncRunner(local, config, clock=self.clock).step()
                self.assertEqual(repeated["last_result"]["sent"], 0)
                self.assertEqual(repeated["last_result"]["received"], 0)
            with Store(remote_path) as remote:
                self.assertEqual(local.status()["frontier"], remote.status()["frontier"])
                self.assertIsNotNone(remote.get_entity("local-note"))
                self.assertIsNotNone(local.get_entity("remote-note"))


if __name__ == "__main__":
    unittest.main()
