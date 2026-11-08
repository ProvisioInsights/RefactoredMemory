"""Synthetic regressions for graph-history and administrative suppression boundaries."""

import unittest

from refactoredmemory.store import Store, ValidationError


class TombstoneLineageTests(unittest.TestCase):
    def test_invalid_correction_reason_cannot_enter_owner_journal(self):
        with Store(":memory:", store_id="synthetic-reason", peer_id="peer-a") as store:
            store.submit([
                {"type": "entity", "id": "subject", "entity_type": "project", "label": "Synthetic"},
                {"type": "source", "id": "source", "uri": "synthetic://reason", "content": "Synthetic evidence"},
                {"type": "assertion", "id": "original", "subject": "subject", "predicate": "decision",
                 "value": "First", "source_ids": ["source"]},
            ])
            before = store.status()["frontier"]
            for reason in (42, True, [], {"text": "Incorrect shape"}, None):
                with self.subTest(reason=reason), self.assertRaises(ValidationError):
                    store.submit([
                        {"type": "assertion", "id": "correction", "subject": "subject", "predicate": "decision",
                         "value": "Second", "source_ids": ["source"], "kind": "correct",
                         "predecessors": ["original"], "reason": reason},
                    ])
                self.assertEqual(store.status()["frontier"], before)
                self.assertIsNone(store.read("assertion", "correction"))

    def test_deleted_corrected_endpoint_does_not_resurrect_superseded_edge(self):
        with Store(":memory:", store_id="synthetic-tombstone", peer_id="peer-a") as store:
            original = store.submit([
                *({"type": "entity", "id": name, "entity_type": "person", "label": name}
                  for name in ("subject", "old-target", "corrected-target")),
                {"type": "source", "id": "evidence", "uri": "synthetic://relationship",
                 "content": "Synthetic relationship with an initially mistaken target.", "metadata": {}},
                {"type": "assertion", "id": "original-edge", "subject": "subject",
                 "predicate": "knows", "object": "old-target", "source_ids": ["evidence"],
                 "valid_from": "2026-01-01"},
            ])
            store.submit([
                {"type": "assertion", "id": "corrected-edge", "subject": "subject",
                 "predicate": "knows", "object": "corrected-target", "source_ids": ["evidence"],
                 "kind": "correct", "predecessors": ["original-edge"],
                 "reason": "The initial target was mistaken", "valid_from": "2026-01-01"},
            ])
            self.assertEqual([a["id"] for a in store.query(subject="subject")["assertions"]],
                             ["corrected-edge"])

            store.submit([{"type": "delete", "id": "suppress-target",
                           "entity_id": "corrected-target", "reason": "Owner suppression"}])
            current = store.query(subject="subject")
            self.assertEqual(current["assertions"], [])
            self.assertTrue(current["coverage"]["administrative_suppression"])
            self.assertEqual(store.query(subject="subject", valid_at="2026-01-15")["assertions"], [])
            self.assertEqual(store.traverse("subject")["edges"], [])

            # Suppression hides the corrected endpoint; it does not undo the
            # correction's effect or rewrite a view from before it was learned.
            history = store.query(subject="subject", include_inactive=True)["assertions"]
            self.assertEqual([(a["id"], a["status"]) for a in history],
                             [("original-edge", "superseded")])
            earlier = store.query(subject="subject", known_at=original["known_position"])
            self.assertEqual([a["id"] for a in earlier["assertions"]], ["original-edge"])

            store.submit([{"type": "restore", "id": "restore-target",
                           "entity_id": "corrected-target", "predecessors": ["suppress-target"],
                           "reason": "Owner restores availability"}])
            self.assertEqual([a["id"] for a in store.query(subject="subject")["assertions"]],
                             ["corrected-edge"])

    def test_concurrent_delete_edit_is_visible_without_content_and_restore_resolves(self):
        with Store(":memory:", store_id="synthetic-conflict", peer_id="peer-a") as a, \
                Store(":memory:", store_id="synthetic-conflict", peer_id="peer-b") as b:
            for local, remote in ((a, b), (b, a)):
                local.admit_peer(remote.peer_id, remote.identity()["key_hex"])
            a.submit([
                {"type": "entity", "id": "subject", "entity_type": "person",
                 "label": "Synthetic person"},
                {"type": "source", "id": "evidence", "uri": "synthetic://name",
                 "content": "Synthetic source content must remain suppressed.", "metadata": {}},
                {"type": "assertion", "id": "original", "subject": "subject",
                 "predicate": "name", "value": "Synthetic original name",
                 "source_ids": ["evidence"]},
            ])
            b.receive(a.export_operations()["operations"], a.peer_id)

            deletion = a.submit([
                {"type": "delete", "id": "suppression", "entity_id": "subject",
                 "reason": "Synthetic owner suppression"},
            ])
            self.assertEqual(a.status()["conflicts"], {"items": [], "truncated": False})
            edit = b.submit([
                {"type": "assertion", "id": "offline-correction", "subject": "subject",
                 "predicate": "name", "value": "Synthetic corrected name",
                 "source_ids": ["evidence"], "kind": "correct", "predecessors": ["original"],
                 "reason": "Synthetic offline correction"},
            ])
            a.receive(b.export_operations(a.status()["frontier"])["operations"], b.peer_id)
            b.receive(a.export_operations(b.status()["frontier"])["operations"], a.peer_id)

            # Exact field comparison also guards against returning deleted content.
            expected = {"items": [{
                "kind": "concurrent_delete_edit", "entity_id": "subject",
                "delete_id": "suppression", "edit_id": "offline-correction",
                "delete_operation": deletion["operation_id"],
                "edit_operation": edit["operation_id"],
            }], "truncated": False}
            for peer in (a, b):
                self.assertEqual(peer.status()["conflicts"], expected)
                self.assertEqual(peer.query(subject="subject")["assertions"], [])
                self.assertEqual(peer.history("subject")["operations"], [])
                self.assertIsNone(peer.get_entity("subject"))
                self.assertIsNone(peer.get_source("evidence"))

            a.submit([
                {"type": "restore", "id": "restoration", "entity_id": "subject",
                 "predecessors": ["suppression"], "reason": "Synthetic owner restoration"},
            ])
            b.receive(a.export_operations(b.status()["frontier"])["operations"], a.peer_id)
            for peer in (a, b):
                self.assertEqual(peer.status()["conflicts"], {"items": [], "truncated": False})
                self.assertEqual([item["id"] for item in peer.query(subject="subject")["assertions"]],
                                 ["offline-correction"])


if __name__ == "__main__":
    unittest.main()
