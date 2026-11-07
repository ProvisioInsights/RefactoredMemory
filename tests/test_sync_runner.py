"""Bounded automatic sync scheduling, using synthetic stores and deterministic time."""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
from unittest.mock import patch

from refactoredmemory.sync import SyncError, SyncRunner, _post, _retry_after, sync_once


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
        self.assertEqual(runner.config["token_file"], str(self.token))
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
