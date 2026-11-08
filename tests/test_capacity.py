"""Storage admission must preserve durable receipts under pressure."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from refactoredmemory.store import Store, CapacityError, ValidationError


def entity(name):
    return {"type": "entity", "id": name, "entity_type": "project", "label": name}


class CapacityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.a = Store(Path(self.temp.name) / "a.sqlite", store_id="synthetic", peer_id="a")
        self.b = Store(Path(self.temp.name) / "b.sqlite", store_id="synthetic", peer_id="b")
        self.addCleanup(self.a.close)
        self.addCleanup(self.b.close)
        self.b.admit_peer("a", self.a.identity()["key_hex"])

    def test_low_disk_refuses_local_write_and_retry_is_one_operation(self):
        self.a.configure_capacity(min_free_bytes=1024)
        with patch("refactoredmemory.store.shutil.disk_usage", return_value=SimpleNamespace(free=0)):
            with self.assertRaises(CapacityError) as error:
                self.a.submit([entity("x")], request_id="request")
        self.assertEqual(error.exception.reason, "low_disk")
        self.assertEqual(self.a.status()["frontier"], {})
        self.assertEqual(self.a.db.execute("SELECT count(*) FROM requests").fetchone()[0], 0)
        receipt = self.a.submit([entity("x")], request_id="request")
        with patch("refactoredmemory.store.shutil.disk_usage", return_value=SimpleNamespace(free=0)):
            duplicate = self.a.submit([entity("x")], request_id="request")
        self.assertEqual(receipt["operation_id"], duplicate["operation_id"])
        self.assertTrue(duplicate["duplicate"])

    def test_incoming_capacity_rolls_back_entire_group_and_resume_converges(self):
        self.a.submit([entity("one")])
        self.a.submit([entity("two")])
        operations = self.a.export_operations()["operations"]
        self.b.configure_capacity(min_free_bytes=1024)
        calls = 0

        def running_out(_path):
            nonlocal calls
            calls += 1
            return SimpleNamespace(free=10**9 if calls == 1 else 0)

        with patch("refactoredmemory.store.shutil.disk_usage", side_effect=running_out):
            with self.assertRaises(CapacityError):
                self.b.receive(operations, "a")
        self.assertEqual(self.b.status()["frontier"], {})
        self.assertEqual(self.b.db.execute("SELECT count(*) FROM operations").fetchone()[0], 0)
        result = self.b.receive(operations, "a")
        self.assertEqual(result["applied"], 2)
        self.assertEqual(result["frontier"], self.a.status()["frontier"])
        with patch("refactoredmemory.store.shutil.disk_usage", return_value=SimpleNamespace(free=0)):
            self.assertEqual(self.b.receive(operations, "a")["received"], 0)

    def test_existing_pending_projection_is_not_misclassified_as_invalid(self):
        self.a.submit([entity("one")])
        self.a.submit([entity("two")])
        operations = self.a.export_operations()["operations"]
        self.b.receive(operations[1:], "a")
        self.b.configure_capacity(min_free_bytes=1024)
        # Admit predecessor into the transaction, then refuse projection.
        with patch("refactoredmemory.store.shutil.disk_usage", side_effect=[SimpleNamespace(free=10**9), SimpleNamespace(free=0)]):
            with self.assertRaises(CapacityError):
                self.b.receive(operations[:1], "a")
        self.assertEqual(self.b.status()["rejected"], 0)
        self.assertEqual(self.b.status()["pending"], 1)
        self.assertEqual(self.b.status()["frontier"], {})
        self.assertEqual(self.b.receive(operations[:1], "a")["applied"], 2)

    def test_ceiling_does_not_block_reads_and_can_be_raised(self):
        self.a.submit([entity("one")])
        size = self.a.db.execute("PRAGMA page_count").fetchone()[0] * self.a.db.execute("PRAGMA page_size").fetchone()[0]
        self.a.configure_capacity(max_store_bytes=size)
        with self.assertRaises(CapacityError) as error:
            self.a.submit([entity("two")])
        self.assertEqual(error.exception.reason, "store_limit")
        self.assertEqual(self.a.get_entity("one")["label"], "one")
        self.a.configure_capacity(max_store_bytes=size + 1024 * 1024)
        self.a.submit([entity("two")])
        self.assertEqual(self.a.status()["frontier"], {"a": 2})

    def test_final_check_rolls_back_even_after_projection(self):
        self.a.configure_capacity(min_free_bytes=1024)
        with patch("refactoredmemory.store.shutil.disk_usage", side_effect=[SimpleNamespace(free=10**9), SimpleNamespace(free=0)]):
            with self.assertRaises(CapacityError):
                self.a.submit([entity("one")], request_id="retry")
        self.assertEqual(self.a.status()["counts"], {})
        self.assertEqual(self.a.status()["frontier"], {})

    def test_sqlite_full_rolls_back_and_becomes_a_capacity_pause(self):
        # Use SQLite's own pager limit to exercise real SQLITE_FULL behavior.
        pages = self.a.db.execute("PRAGMA page_count").fetchone()[0]
        self.a.db.execute(f"PRAGMA max_page_count={pages}")
        with self.assertRaises(CapacityError):
            self.a.submit([{"type": "source", "id": "big", "uri": "synthetic:big", "content": "x" * 60000}])
        self.assertFalse(self.a.db.in_transaction)
        self.assertEqual(self.a.status()["frontier"], {})
        self.assertEqual(self.a.status()["counts"], {})

    def test_invalid_config_refused(self):
        for value in (True, -1, 1.1, "1", None):
            with self.assertRaises(ValidationError):
                self.a.configure_capacity(min_free_bytes=value)
        with self.assertRaises(ValidationError):
            self.a.configure_capacity(max_store_bytes=0)

    def test_backup_reserves_its_own_destination_space_before_creation(self):
        self.a.submit([entity("one")])
        self.a.configure_capacity(min_free_bytes=1024)
        destination = Path(self.temp.name) / "snapshot.sqlite"
        with patch("refactoredmemory.store.shutil.disk_usage", return_value=SimpleNamespace(free=2048)):
            with self.assertRaises(CapacityError):
                self.a.backup(destination)
        self.assertFalse(destination.exists())
        self.a.backup(destination)
        with sqlite3.connect(destination) as snapshot:
            self.assertEqual(snapshot.execute("SELECT count(*) FROM operations").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
