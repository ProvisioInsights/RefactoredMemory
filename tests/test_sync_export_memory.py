"""Transport must not materialize acknowledged large journal payloads."""
import sqlite3
import unittest

from refactoredmemory.store import Store
from tests.test_query_memory import ACTOR, large_group


class SyncExportMemoryTests(unittest.TestCase):
    def test_acknowledged_payloads_do_not_cross_the_sqlite_boundary(self):
        with Store(":memory:") as store:
            for _ in range(8):
                store.submit(large_group(), actor=ACTOR)
            acknowledged = store.status()["frontier"]
            newest = store.submit(large_group(), actor=ACTOR)
            decoded_bytes = 0

            def measured_row(cursor, values):
                nonlocal decoded_bytes
                row = sqlite3.Row(cursor, values)
                if "body" in row.keys():
                    decoded_bytes += len(row["body"].encode())
                return row

            store.db.row_factory = measured_row
            exported = store.export_operations(frontier=acknowledged, limit=1)
            self.assertEqual([x["id"] for x in exported["operations"]], [newest["operation_id"]])
            self.assertFalse(exported["more"])
            self.assertLess(decoded_bytes, 2 * 1024 * 1024)
            decoded_bytes = 0
            empty = store.export_operations(frontier=exported["frontier"], limit=1)
            self.assertEqual(empty["operations"], [])
            self.assertFalse(empty["more"])
            self.assertEqual(decoded_bytes, 0)

    def test_metadata_reads_use_covering_indexes(self):
        with Store(":memory:") as store:
            store.submit(large_group(), actor=ACTOR)
            queries = []
            store.db.set_trace_callback(queries.append)
            self.assertEqual(store._frontier(), {store.peer_id: 1})
            self.assertTrue(store._reference_visible("entity", "project", {store.peer_id: 1}))
            store.db.set_trace_callback(None)
            for query in queries:
                plan = " ".join(row[3] for row in store.db.execute("EXPLAIN QUERY PLAN " + query))
                self.assertIn("COVERING INDEX", plan, query)


if __name__ == "__main__":
    unittest.main()
