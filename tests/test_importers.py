import json
from pathlib import Path
import tempfile
import unittest

from refactoredmemory.importers import ImportError, apply_import, import_path, mapped_id, plan_import
from refactoredmemory.store import Store


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.sources = self.base / "sources"
        self.sources.mkdir()
        self.store = Store(self.base / "memory.sqlite")
        self.counter = 0

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def write_json(self, name, value):
        path = self.sources / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def apply(self, path=None, **kwargs):
        self.counter += 1
        return import_path(self.store, path or self.sources, approved_root=self.sources,
                           dry_run=False, backup_path=self.base / f"backup-{self.counter}.sqlite", **kwargs)

    @staticmethod
    def entity(id="e-person", name="Rae", type="person"):
        return {"record_schema": "atlas.entity:v1", "entity_id": id, "type": type, "display_name": name,
                "registered_at": "2025-01-01T00:00:00.000Z", "updated_at": "2025-01-01T00:00:00.000Z"}

    @staticmethod
    def assertion(id="a-one", value="Draft", kind="assert", supersedes=None):
        return {"record_schema": "atlas.assertion:v1", "assertion_id": id, "kind": "fact",
                "lineage_action": kind, "subject_entity_id": "e-person", "predicate": "status", "value": value,
                "recorded_at": "2025-01-02T00:00:00.000Z", "supersedes": supersedes or [],
                "valid_from": {"kind": "exact", "value": "2025-01-01"},
                "evidence_links": [{"evidence_id": "legacy-source", "stance": "supports"}],
                "provenance": {"client_id": "old-agent", "recorded_at_fidelity": "authoritative"},
                "confidence": {"band": "medium"}}

    def test_markdown_dry_run_is_read_only_then_repeat_and_update_preserve_history(self):
        path = self.sources / "Project.md"
        first = "# Project\n- Chose SQLite because transactions are useful.\n  id:: block-one\n"
        path.write_text(first)
        before = path.read_bytes()
        plan = import_path(self.store, path, approved_root=self.sources)
        self.assertTrue(plan["dry_run"])
        self.assertNotIn(first, json.dumps(plan))
        self.assertEqual(self.store.status()["known_position"], 0)
        result = self.apply(path)
        self.assertEqual(result["status"], "complete")
        aid = result["records"][0]["mapped_id"]
        original = self.store.read("assertion", aid)
        self.assertEqual(original["provenance"]["logseq_block_ids"], ["block-one"])
        before_position = self.store.status()["known_position"]
        repeat = self.apply(path)
        self.assertEqual(repeat["status"], "unchanged")
        self.assertEqual(self.store.status()["known_position"], before_position)
        path.write_text(first.replace("SQLite", "SQLite WAL"))
        changed = self.apply(path)
        self.assertEqual(changed["status"], "complete")
        correction = self.store.read("assertion", changed["records"][0]["mapped_id"])
        self.assertEqual(correction["kind"], "correct")
        self.assertEqual(correction["predecessors"], [aid])
        self.assertEqual(self.store.read("assertion", aid)["value"], first)
        self.assertEqual(self.apply(path)["status"], "unchanged")
        self.assertEqual(before.decode(), first)

    def test_assertion_export_preserves_ids_world_time_lineage_and_original_known_time(self):
        first = self.assertion()
        correction = self.assertion("a-two", "Final", "correct", ["a-one"])
        correction["recorded_at"] = "2025-01-03T00:00:00.000Z"
        path = self.write_json("records.json", [correction, self.entity(), first])
        result = self.apply(path)
        self.assertEqual(result["status"], "complete")
        old = self.store.read("assertion", mapped_id("personal-import", "assertion", "a-one"))
        new = self.store.read("assertion", mapped_id("personal-import", "assertion", "a-two"))
        self.assertEqual(new["predecessors"], [old["id"]])
        self.assertEqual(new["valid_from"], "2025-01-01")
        self.assertEqual(new["provenance"]["original_recorded_at"], correction["recorded_at"])
        self.assertEqual(new["provenance"]["original_provenance"]["client_id"], "old-agent")
        current = self.store.query(subject=new["subject"], valid_at="2025-02-01")["assertions"]
        self.assertEqual([a["id"] for a in current], [new["id"]])
        self.assertEqual(self.apply(path)["status"], "unchanged")

    def test_partial_dates_never_invent_definite_world_match(self):
        a = self.assertion()
        a["valid_from"] = {"kind": "approximate", "value": "2025"}
        result = self.apply(self.write_json("partial.json", [self.entity(), a]))
        self.assertEqual(result["status"], "complete")
        mapped = self.store.read("assertion", mapped_id("personal-import", "assertion", "a-one"))
        self.assertIsNone(mapped["valid_from"])
        self.assertEqual(mapped["time_precision"], "approximate")
        self.assertEqual(mapped["provenance"]["original_valid_from"], a["valid_from"])
        self.assertEqual(self.store.query(valid_at="2025-06-01")["assertions"], [])

    def test_import_is_not_a_fresh_owner_correction_and_partial_batches_are_reported(self):
        self.write_json("correction.json", [self.entity(), self.assertion(), self.assertion("a-two", "Final", "correct", ["a-one"])])
        result = self.apply(actor={"id": "owner", "kind": "owner"})
        self.assertEqual(result["status"], "complete")
        claims = self.store.query()["assertions"]
        self.assertEqual(claims[0]["actor"]["kind"], "agent")
        self.assertFalse(claims[0]["preferred"])
        for i in range(200):
            (self.sources / f"note-{i}.md").write_text(f"Synthetic note {i}")
        original = self.store.submit
        called = 0
        def fail_second(actions, **kwargs):
            nonlocal called
            called += 1
            if called == 2:
                raise OSError("synthetic interrupted disk")
            return original(actions, **kwargs)
        self.store.submit = fail_second
        partial = self.apply()
        self.assertEqual(partial["status"], "partial")
        self.assertEqual(partial["committed_batches"], 1)
        self.assertGreater(partial["counts"]["failed"], 0)
        self.assertEqual(sum(partial["counts"].values()), partial["record_count"])

    def test_snapshot_envelopes_and_unknown_encrypted_records_are_accounted(self):
        def envelope(id, data):
            return {"schema_version": 1, "object_id": id, "object_type": "entity", "version": 1,
                    "visible_metadata": {"tombstone": False}, "payload": {"kind": "plaintext-json", "data": data}}
        e = envelope("old-person", {"schema": "atlas.entity:v1", "entity_id": "e-person", "type": "person", "name": "Rae"})
        ciphertext = {"object_id": "opaque", "payload": {"kind": "ciphertext-inline", "ciphertext": "SYNTHETIC"}}
        snapshot = {"schema_version": 1, "objects": [e, ciphertext, {"unsupported": True}], "operation_records": [{"operation_id": "retained-metadata"}]}
        result = self.apply(self.write_json("snapshot.json", snapshot))
        self.assertEqual(result["record_count"], 4)
        self.assertEqual(sum(result["counts"].values()), 4)
        self.assertEqual(result["counts"]["preserved-only"], 3)
        self.assertEqual(self.store.status()["counts"]["entity"], 1)
        self.assertEqual(self.store.query()["assertions"], [])

    def test_committed_segment_groups_only_and_receipt_mismatch_is_quarantined(self):
        self.write_json("identity.json", self.entity())
        body = self.assertion()
        header = {"record": "header", "log_format": "atlas.segment-log:v1", "segment_ordinal": 1,
                  "feed_epoch": "test", "history_floor": "2020-01-01T00:00:00.000Z"}
        member = {"record": "assertion", "submission_id": "s-one", "assertion": body}
        receipt = {"record": "submission", "receipt": {"submission_id": "s-one", "assertion_ids": ["a-one"]}}
        path = self.sources / "segment-000001.jsonl"
        path.write_text("".join(json.dumps(x) + "\n" for x in [header, member, receipt]))
        result = self.apply()
        self.assertEqual(result["status"], "complete")
        self.assertIsNotNone(self.store.read("assertion", mapped_id("personal-import", "assertion", "a-one")))
        receipt["receipt"]["submission_id"] = "wrong"
        path.write_text("".join(json.dumps(x) + "\n" for x in [header, member, receipt]))
        plan = plan_import(path, approved_root=self.sources).summary()
        self.assertEqual(plan["counts"], {"quarantined": 3})

    def test_identity_log_commit_boundary_and_alias_records_remain_visible(self):
        path = self.sources / "identity.jsonl"
        records = [
            {"record": "header", "log_format": "atlas.identity-log:v1", "segment_ordinal": 1},
            {"record": "entity", "group_seq": 1, "entity": self.entity()},
            {"record": "alias", "group_seq": 1, "row": {"old_id": "old", "canonical_id": "e-person"}},
            {"record": "group-commit", "group_seq": 1, "entity_ids": ["e-person"], "row_seqs": [1]},
        ]
        path.write_text("".join(json.dumps(x) + "\n" for x in records))
        result = self.apply(path)
        self.assertEqual(result["counts"], {"preserved-only": 3, "imported": 1})
        self.assertEqual(result["record_count"], 4)

    def test_missing_lineage_is_preserved_without_fabricated_initial_claim(self):
        a = self.assertion("a-two", "Final", "correct", ["absent"])
        result = self.apply(self.write_json("missing.json", [self.entity(), a]))
        self.assertEqual(result["records"][1]["status"], "preserved-only")
        self.assertEqual(result["records"][1]["reason"], "missing-or-cyclic-lineage")
        self.assertEqual(self.store.query()["assertions"], [])

    def test_duplicate_id_with_different_content_fails_without_partial_commit(self):
        first = self.assertion()
        changed = self.assertion(value="Different")
        result = self.apply(self.write_json("duplicate.json", [self.entity(), first, changed]))
        self.assertEqual(result["status"], "failed")
        self.assertEqual(self.store.status()["known_position"], 0)

    def test_stale_plan_and_source_root_destination_are_refused(self):
        path = self.sources / "note.md"
        path.write_text("First")
        plan = plan_import(path, approved_root=self.sources)
        path.write_text("Changed")
        with self.assertRaisesRegex(ImportError, "source-changed-after-plan"):
            apply_import(self.store, plan, backup_path=self.base / "backup.sqlite")
        with self.assertRaisesRegex(ImportError, "backup-inside-source-root"):
            apply_import(self.store, plan_import(path, approved_root=self.sources), backup_path=self.sources / "backup.sqlite")

    def test_symlinks_traversal_malformed_json_and_size_limits(self):
        outside = self.base / "outside.md"
        outside.write_text("Not approved")
        link = self.sources / "linked.md"
        link.symlink_to(outside)
        report = plan_import(link, approved_root=self.sources).summary()
        self.assertEqual(report["records"][0]["reason"], "symlink-input")
        with self.assertRaisesRegex(ImportError, "outside-approved-root"):
            plan_import(outside, approved_root=self.sources)
        duplicate = self.sources / "duplicate.json"
        duplicate.write_text('{"objects":[],"objects":[]}')
        report = plan_import(duplicate, approved_root=self.sources).summary()
        self.assertEqual(report["records"][0]["reason"], "duplicate-json-key")
        large = self.sources / "large.md"
        large.write_text("a" * 100)
        report = plan_import(large, approved_root=self.sources, max_file_bytes=10).summary()
        self.assertEqual(report["records"][0]["reason"], "file-byte-limit")

    def test_parent_alias_is_canonicalized_for_plan_apply_and_repeat(self):
        physical = self.base / "physical-parent"
        physical.mkdir()
        canonical_root = physical / "notes"
        canonical_root.mkdir()
        (canonical_root / "note.md").write_text("Synthetic note through a system-style parent alias")
        alias = self.base / "parent-alias"
        alias.symlink_to(physical, target_is_directory=True)
        named_root = alias / "notes"
        plan = plan_import(named_root / "note.md", approved_root=named_root)
        self.assertEqual(plan.root, canonical_root.resolve())
        self.assertEqual(plan.summary()["approved_root"], str(canonical_root.resolve()))
        self.assertEqual(plan.summary()["files"][0]["relative_path"], "note.md")
        result = apply_import(self.store, plan, backup_path=self.base / "alias-backup.sqlite")
        self.assertEqual(result["status"], "complete")
        # Use the observed canonical spelling; the temporary directory itself
        # can have an OS parent alias on macOS (/var -> /private/var).
        repeated = import_path(self.store, plan.root / "note.md", approved_root=named_root,
                               dry_run=False, backup_path=self.base / "alias-repeat-backup.sqlite")
        self.assertEqual(repeated["status"], "unchanged")

    def test_parent_alias_retarget_does_not_change_an_existing_plan(self):
        physical = self.base / "pinned-parent"
        physical.mkdir()
        canonical_root = physical / "notes"
        canonical_root.mkdir()
        (canonical_root / "note.md").write_text("Originally approved synthetic content")
        replacement = self.base / "replacement-parent"
        replacement.mkdir()
        (replacement / "notes").mkdir()
        (replacement / "notes" / "note.md").write_text("Unapproved replacement synthetic content")
        alias = self.base / "mutable-parent-alias"
        alias.symlink_to(physical, target_is_directory=True)
        plan = plan_import(alias / "notes", approved_root=alias / "notes")
        alias.unlink()
        alias.symlink_to(replacement, target_is_directory=True)
        result = apply_import(self.store, plan, backup_path=self.base / "pinned-backup.sqlite")
        self.assertEqual(result["status"], "complete")
        self.assertEqual(self.store.query()["assertions"][0]["value"], "Originally approved synthetic content")

    def test_parent_alias_does_not_allow_root_or_descendant_symlinks(self):
        physical = self.base / "bounded-parent"
        physical.mkdir()
        canonical_root = physical / "notes"
        canonical_root.mkdir()
        outside = self.base / "outside-directory"
        outside.mkdir()
        (outside / "note.md").write_text("Outside synthetic content")
        (canonical_root / "escape").symlink_to(outside, target_is_directory=True)
        (canonical_root / "linked.md").symlink_to(outside / "note.md")
        alias = self.base / "bounded-parent-alias"
        alias.symlink_to(physical, target_is_directory=True)
        named_root = alias / "notes"
        with self.assertRaisesRegex(ImportError, "symlink-input"):
            plan_import(named_root / "escape" / "note.md", approved_root=named_root)
        report = plan_import(named_root / "linked.md", approved_root=named_root).summary()
        self.assertEqual(report["records"][0]["reason"], "symlink-input")
        with self.assertRaisesRegex(ImportError, "outside-approved-root"):
            plan_import(outside / "note.md", approved_root=named_root)
        root_link = alias / "root-link"
        root_link.symlink_to(canonical_root, target_is_directory=True)
        with self.assertRaisesRegex(ImportError, "symlink-approved-root"):
            plan_import(root_link, approved_root=root_link)

    def test_quarantine_does_not_leak_through_source_content(self):
        path = self.write_json("quarantined.json", {"schema_version": 1, "objects": [
            {"object_id": "quarantine", "access_class": "quarantine", "payload": {"kind": "plaintext-json", "data": {"secret": "synthetic"}}}
        ]})
        result = self.apply(path)
        self.assertEqual(result["counts"], {"quarantined": 1})
        self.assertEqual(self.store.status()["counts"].get("source", 0), 0)

    def test_backup_is_usable_and_originals_remain_identical(self):
        path = self.sources / "note.md"
        path.write_text("Synthetic note")
        original = path.read_bytes()
        result = self.apply(path)
        self.assertTrue(Path(result["backup_path"]).is_file())
        restored = Store.restore(result["backup_path"], self.base / "restored.sqlite")
        if isinstance(restored, Store):
            self.assertEqual(restored.status()["known_position"], 0)
            restored.close()
        else:
            with Store(self.base / "restored.sqlite") as check:
                self.assertEqual(check.status()["known_position"], 0)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
