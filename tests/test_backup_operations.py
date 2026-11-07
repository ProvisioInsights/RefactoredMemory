"""Operational backup receipts and publication under concurrent writes/failure."""
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from refactoredmemory.store import Store, ValidationError


def entity(name):
    return {"type": "entity", "id": name, "entity_type": "project", "label": name}


class BackupOperationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = Store(self.root / "live.sqlite")
        self.addCleanup(self.store.close)
        self.store.submit([entity("before")])
        self.destination = self.root / "snapshot.sqlite"

    def test_receipt_names_snapshot_position_when_another_writer_advances(self):
        writer = Store(self.store.path)
        self.addCleanup(writer.close)
        connect = sqlite3.connect

        class ConcurrentWrite(sqlite3.Connection):
            def execute(connection, sql, *args):
                result = super().execute(sql, *args)
                if sql == "PRAGMA integrity_check":
                    writer.submit([entity("after")])
                return result

        with patch("refactoredmemory.store.sqlite3.connect", side_effect=lambda *a, **k: connect(*a, factory=ConcurrentWrite, **k)):
            receipt = self.store.backup(self.destination)
        with sqlite3.connect(self.destination) as snapshot:
            position = int(snapshot.execute("SELECT value FROM metadata WHERE key='position'").fetchone()[0])
        self.assertEqual(position, 1)
        self.assertEqual(receipt["known_position"], position)
        self.assertEqual(self.store.status()["known_position"], 2)

    def test_destination_is_published_only_after_validation(self):
        connect = sqlite3.connect
        destination = self.destination
        seen = []

        class InspectPublication(sqlite3.Connection):
            def execute(connection, sql, *args):
                if sql == "PRAGMA integrity_check":
                    seen.append(destination.exists())
                return super().execute(sql, *args)

        with patch("refactoredmemory.store.sqlite3.connect", side_effect=lambda *a, **k: connect(*a, factory=InspectPublication, **k)):
            self.store.backup(destination)
        self.assertEqual(seen, [False])
        self.assertTrue(destination.exists())
        self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
        with sqlite3.connect(destination) as snapshot:
            self.assertEqual(snapshot.execute("PRAGMA journal_mode").fetchone()[0], "delete")
            self.assertEqual(snapshot.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_failed_validation_leaves_no_destination_and_can_be_retried(self):
        connect = sqlite3.connect

        class FailedIntegrity(sqlite3.Connection):
            def execute(connection, sql, *args):
                if sql == "PRAGMA integrity_check":
                    raise sqlite3.OperationalError("synthetic validation failure")
                return super().execute(sql, *args)

        with patch("refactoredmemory.store.sqlite3.connect", side_effect=lambda *a, **k: connect(*a, factory=FailedIntegrity, **k)):
            with self.assertRaises(ValidationError):
                self.store.backup(self.destination)
        self.assertFalse(self.destination.exists())
        self.assertFalse(list(self.root.glob(".snapshot.sqlite.*")))
        self.assertEqual(self.store.backup(self.destination)["known_position"], 1)

    def test_publication_never_replaces_a_destination_created_concurrently(self):
        connect = sqlite3.connect
        destination = self.destination

        class ConcurrentDestination(sqlite3.Connection):
            def execute(connection, sql, *args):
                result = super().execute(sql, *args)
                if sql == "PRAGMA integrity_check":
                    destination.write_text("other owner's file")
                return result

        with patch("refactoredmemory.store.sqlite3.connect", side_effect=lambda *a, **k: connect(*a, factory=ConcurrentDestination, **k)):
            with self.assertRaises(FileExistsError):
                self.store.backup(self.destination)
        self.assertEqual(self.destination.read_text(), "other owner's file")
        self.assertFalse(list(self.root.glob(".snapshot.sqlite.*")))


if __name__ == "__main__":
    unittest.main()
