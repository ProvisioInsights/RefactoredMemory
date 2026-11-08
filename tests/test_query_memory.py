"""Large legal operation groups must not multiply evidence into read memory."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from refactoredmemory.store import Store


ACTOR = {"id": "synthetic-agent", "kind": "agent"}


def large_group():
    # One legal <1 MiB / <500-action group. The old join copied its full
    # evidence 480 times (~428 MiB) even when the caller requested one result.
    return [
        {"type": "entity", "id": "project", "entity_type": "project", "label": "Synthetic"},
        *({"type": "source", "id": f"s{i}", "uri": f"synthetic:{i}", "content": "x" * 60000}
          for i in range(14)),
        *({"type": "assertion", "id": f"a{i}", "subject": "project", "predicate": "tag",
           "value": str(i), "source_ids": ["s0"]} for i in range(480)),
    ]


def memory_probe(mode):
    import resource
    with tempfile.TemporaryDirectory(prefix="refmem-read-memory-") as directory:
        with Store(Path(directory) / "synthetic.sqlite3") as store:
            store.submit(large_group(), actor=ACTOR)
            if mode == "status":
                store.submit([{"type": "delete", "id": "suppress", "entity_id": "project",
                               "reason": "Synthetic owner suppression"}])
            resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
            if mode == "query":
                result = store.query(subject="project", limit=1)
                assert len(result["assertions"]) == 1
                assert result["coverage"]["matched"] == 480
                assert result["assertions"][0]["actor"] == ACTOR
            else:
                result = store.status()
                assert result["deleted_entities"] == 1
                assert result["conflicts"] == {"items": [], "truncated": False}
            print(json.dumps({"mode": mode, "passed": True}))


class QueryMemoryTests(unittest.TestCase):
    def test_large_group_keeps_attribution_and_historical_views(self):
        with Store(":memory:") as store:
            original = store.submit(large_group(), actor=ACTOR)
            first = store.query(subject="project", limit=1)
            self.assertEqual(first["assertions"][0]["actor"], ACTOR)
            self.assertEqual(first["coverage"]["matched"], 480)
            self.assertTrue(first["coverage"]["has_more"])
            store.submit([{"type": "assertion", "id": "owner-correction", "subject": "project",
                           "predicate": "tag", "value": "Corrected", "source_ids": ["s0"],
                           "kind": "correct", "predecessors": ["a0"], "reason": "Synthetic correction"}])
            earlier = store.query(subject="project", known_at=original["known_position"], limit=1)
            self.assertEqual(earlier["assertions"][0]["id"], "a0")
            self.assertEqual(earlier["assertions"][0]["actor"], ACTOR)
            current = store.query(subject="project", text="Corrected")
            self.assertEqual([a["id"] for a in current["assertions"]], ["owner-correction"])
            self.assertTrue(current["assertions"][0]["preferred"])
            self.assertEqual(store.get_source("s13")["content"], "x" * 60000)

    def test_duplicate_attribution_does_not_reparse_large_journals_per_assertion(self):
        with Store(":memory:") as store:
            first = store.submit(large_group(), actor=ACTOR)
            second_actor = {"id": "second-synthetic-agent", "kind": "agent"}
            store.submit(large_group(), actor=second_actor)
            parsed_bytes = 0
            def bounded_json_extract(body, path):
                nonlocal parsed_bytes
                parsed_bytes += len(body.encode())
                if parsed_bytes > 3 * 1024 * 1024:
                    raise RuntimeError("Journal decoding exceeded the bounded query budget")
                self.assertEqual(path, "$.actor")
                return json.dumps(json.loads(body)["actor"])
            store.db.create_function("json_extract", 2, bounded_json_extract)
            current = store.query(subject="project", limit=1)
            self.assertEqual(len(current["assertions"][0]["attributions"]), 2)
            self.assertEqual(current["coverage"]["matched"], 480)
            self.assertLessEqual(parsed_bytes, 3 * 1024 * 1024)
            parsed_bytes = 0
            earlier = store.query(subject="project", known_at=first["known_position"], limit=1)
            self.assertEqual(earlier["assertions"][0]["attributions"], [{
                "actor": ACTOR, "operation_id": earlier["assertions"][0]["operation_id"]}])

    def _probe(self, mode):
        root = Path(__file__).resolve().parents[1]
        # RLIMIT_AS reliably bounds the isolated process on Linux. macOS has
        # different virtual-address accounting; portable semantics run above.
        process = subprocess.run(
            [sys.executable, "-c", "import runpy;runpy.run_path('tests/test_query_memory.py',run_name='__main__')",
             "--memory-probe", mode], cwd=root, text=True, capture_output=True, timeout=30)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout), {"mode": mode, "passed": True})

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux address-space-limit regression")
    def test_query_large_group_under_256_mib_address_space(self):
        self._probe("query")

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux address-space-limit regression")
    def test_status_after_delete_under_256_mib_address_space(self):
        self._probe("status")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--memory-probe":
        memory_probe(sys.argv[2])
    else:
        unittest.main()
