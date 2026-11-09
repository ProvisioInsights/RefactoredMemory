import copy
import json
from pathlib import Path
import unittest

from refactoredmemory import field_contract, knowledge
from refactoredmemory.store import Store, ValidationError
from refactoredmemory.service import Service
from refactoredmemory.store import AuthorizationError


def action(field, value=None, *, state="known", id="field", subject="person", **extra):
    definition = field_contract.catalog()["fields"][field]
    tag = {"schema": field_contract.SCHEMA, "revision": 1, "field": field,
           "state": state, "validity_end": "unknown"}
    k = {"schema": knowledge.PROFILE, "kind": "fact", "qualifiers": {"field_contract": tag}}
    result = {"type": "assertion", "id": id, "subject": subject,
              "predicate": definition["storage"]["predicate"], "value": value,
              "source_ids": ["source"], "valid_from": None, "valid_to": None,
              "time_precision": "unknown", "provenance": {"knowledge": k}}
    if definition["value_type"] == "entity_reference":
        result.pop("value"); result["object"] = "organization"
        k.update(kind="relationship", category=definition["category"])
    result.update(extra)
    return result


class FieldContractTests(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.store.submit([
            {"type": "entity", "id": "person", "entity_type": "person", "label": "Synthetic person"},
            {"type": "entity", "id": "organization", "entity_type": "organization", "label": "Synthetic organization"},
            {"type": "entity", "id": "topic", "entity_type": "topic", "label": "Synthetic topic"},
            {"type": "source", "id": "source", "uri": "synthetic://field-contract", "content": "Synthetic source evidence"}])

    def tearDown(self):
        self.store.close()

    def test_catalog_matches_live_registry_and_covers_inventory(self):
        c = self.store.knowledge_contract()["field_catalog"]
        self.assertEqual(len(c["fields"]), 52)
        self.assertEqual(c["record_types"], knowledge.ENDPOINT_TYPES)
        for predicate, expected in knowledge.PREDICATES.items():
            definition = c["fields"]["relationship." + predicate]
            self.assertEqual(definition["applies_to"], expected["domain"])
            self.assertEqual(definition["range"], expected["range"])
            self.assertEqual(definition["cardinality"], expected["cardinality"])
            self.assertEqual(definition["required_context"], expected["required"])
        aliases = [a for d in c["fields"].values() if d["storage"]["predicate"] == "rm:profile-property"
                   for a in d["legacy_properties"]]
        self.assertEqual(len(aliases), 16)
        self.assertEqual(len(set(aliases)), 16)
        self.assertEqual(set(c["tag_schema"]["properties"]["field"]["enum"]), set(c["fields"]))

    def test_discovery_returns_copy_not_mutable_admission_policy(self):
        c = field_contract.catalog()
        c["fields"]["contact.email"]["applies_to"].append("topic")
        c["fields"]["contact.email"]["storage"]["predicate"] = "name"
        with self.assertRaises(ValidationError):
            self.store.submit([action("contact.email", {"kind": "email", "address": "a@example.org"}, subject="topic")])

    def test_shared_synthetic_value_fixtures_reach_core(self):
        fixtures = json.loads((Path(__file__).parent / "fixtures/field-contract-v1.json").read_text())
        for fixture in fixtures["valid"]:
            with self.subTest(valid=fixture["id"]):
                self.store.submit([action(fixture["field"], fixture["value"], state=fixture["state"], id=fixture["id"], subject=fixture.get("subject", "person"))])
        for fixture in fixtures["invalid"]:
            with self.subTest(invalid=fixture["id"]):
                with self.assertRaises(ValidationError):
                    self.store.submit([action(fixture["field"], fixture["value"], state=fixture["state"], id=fixture["id"])])
                self.assertIsNone(self.store.read("assertion", fixture["id"]))

    def test_typed_create_is_minimal_atomic_and_repeat_safe(self):
        entity = {"type": "entity", "id": "new", "entity_type": "person", "label": "Avery Chen"}
        fields = [action("identity.type", "person", subject="new", id="new-type"),
                  action("identity.name", "Avery Chen", subject="new", id="new-name")]
        for incomplete in ([entity, fields[0]], [entity, fields[1]]):
            with self.assertRaises(ValidationError): self.store.submit(incomplete)
            self.assertIsNone(self.store.get_entity("new"))
        receipt = self.store.submit([entity, *fields], request_id="create-new")
        retry = self.store.submit([entity, *fields], request_id="create-new")
        self.assertEqual(receipt["operation_id"], retry["operation_id"])
        self.assertTrue(retry["duplicate"])
        self.assertEqual(self.store.query(subject="new", predicate="rm:contact-point")["assertions"], [])

    def test_semantics_reject_malformed_declarations_without_partial_write(self):
        original = action("contact.email", {"kind": "email", "address": "a@example.org"})
        for key, value in [("revision", True), ("revision", 2), ("field", {}), ("state", "not_recorded"), ("validity_end", {})]:
            bad = copy.deepcopy(original); bad["provenance"]["knowledge"]["qualifiers"]["field_contract"][key] = value
            with self.subTest(key=key, value=value):
                with self.assertRaises(ValidationError): self.store.submit([action("identity.description", "Should not commit", id="good"), bad])
                self.assertIsNone(self.store.read("assertion", "good"))
        bad = copy.deepcopy(original); bad["provenance"]["knowledge"]["qualifiers"]["field_contract"] = None
        with self.assertRaises(ValidationError): self.store.submit([bad])

    def test_validity_never_infers_ongoing_from_blank(self):
        a = action("relationship.employed-by")
        missing = copy.deepcopy(a); missing.pop("valid_to")
        with self.assertRaises(ValidationError): self.store.submit([missing])
        self.store.submit([a])
        self.assertIsNone(self.store.read("assertion", "field")["valid_to"])
        ongoing = copy.deepcopy(missing); ongoing["id"] = "ongoing"
        ongoing["provenance"]["knowledge"]["qualifiers"]["field_contract"]["validity_end"] = "ongoing"
        self.store.submit([ongoing])
        self.assertNotIn("valid_to", self.store.read("assertion", "ongoing"))

    def test_contact_cardinality_and_retraction_history(self):
        first = action("contact.email", {"kind": "email", "address": "a@example.org"}, id="a")
        second = action("contact.email", {"kind": "email", "address": "b@example.org"}, id="b")
        self.store.submit([first, second])
        rows = self.store.query(predicate="rm:contact-point")["assertions"]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(not r["alternatives"] and not r["human_verified"] for r in rows))
        remove = copy.deepcopy(first); remove.update(id="remove", kind="retract", predecessors=["a"], reason="Synthetic wrong address")
        self.store.submit([remove])
        self.assertEqual([r["id"] for r in self.store.query(predicate="rm:contact-point")["assertions"]], ["b"])
        self.assertEqual(self.store.read("assertion", "a")["value"], first["value"])

    def test_relationship_type_and_investment_context_are_explicit(self):
        with self.assertRaises(ValidationError):
            self.store.submit([action("relationship.employed-by", subject="organization", object="person")])
        a = action("relationship.invests-in")
        with self.assertRaises(ValidationError): self.store.submit([a])
        q = a["provenance"]["knowledge"]["qualifiers"]
        q.update(amount=None, investment_status="proposed")
        self.store.submit([a])
        for amount, status in [({"value": 10}, "completed"), ({"value": True, "currency": "USD"}, "completed"), (None, {})]:
            b = copy.deepcopy(a); b["id"] = "bad-investment"; b["provenance"]["knowledge"]["qualifiers"].update(amount=amount, investment_status=status)
            with self.assertRaises(ValidationError): self.store.submit([b])

    def test_untagged_legacy_values_remain_unchanged(self):
        a = {"type": "assertion", "id": "legacy", "subject": "person", "predicate": "rm:contact-point",
             "value": {"old_raw": "not-found", "unresolved": True}, "source_ids": ["source"]}
        self.store.submit([a])
        self.assertEqual(self.store.read("assertion", "legacy")["value"], a["value"])

    def test_service_discovery_and_denied_grants_share_contract(self):
        service = Service(self.store)
        reader = self.store.create_grant("synthetic-reader", ["read"])
        writer = self.store.create_grant("synthetic-writer", ["read", "write"])
        c = service.call("memory_schema", {}, reader)["field_catalog"]
        self.assertEqual(c["schema"], field_contract.SCHEMA)
        a = action("contact.email", {"kind": "email", "address": "a@example.org"})
        with self.assertRaises(AuthorizationError): service.call("memory_submit", {"actions": [a]}, reader)
        service.call("memory_submit", {"actions": [a], "request_id": "synthetic-field"}, writer)
        row = self.store.query(predicate="rm:contact-point")["assertions"][0]
        self.assertEqual(row["actor"]["kind"], "agent")
        self.assertFalse(row["human_verified"])
        self.store.revoke_grant(writer)
        with self.assertRaises(AuthorizationError): service.call("memory_submit", {"actions": [a]}, writer)

    def test_corrections_do_not_move_other_field_lineage(self):
        first = action("profile.role", {"property": "role", "reported_value": "Advisor"}, id="role")
        self.store.submit([first])
        changed = action("profile.organization", {"property": "org", "reported_value": "Grove Ventures"},
                         id="wrong-field", kind="correct", predecessors=["role"], reason="Synthetic wrong target")
        with self.assertRaises(ValidationError): self.store.submit([changed])
        self.assertEqual(self.store.query(predicate="rm:profile-property")["assertions"][0]["id"], "role")

    def test_peer_replay_does_not_require_original_consumer_grant(self):
        writer = self.store.create_grant("synthetic-writer", ["read", "write"])
        Service(self.store).call("memory_submit", {"actions": [action("contact.email", {"kind": "email", "address": "a@example.org"})]}, writer)
        self.store.revoke_grant(writer)
        peer = Store(":memory:", store_id=self.store.store_id)
        try:
            peer.admit_peer(self.store.peer_id, self.store._meta("key_hex"))
            operations = self.store.export_operations()["operations"]
            peer.receive(operations, self.store.peer_id)
            peer.receive(operations, self.store.peer_id)
            rows = peer.query(predicate="rm:contact-point")["assertions"]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["value"]["address"], "a@example.org")
        finally:
            peer.close()

    def test_existing_correction_tool_preserves_contract_and_checks_new_value(self):
        token = self.store.create_grant("synthetic-editor", ["read", "write", "correct"])
        service = Service(self.store)
        self.store.submit([action("contact.email", {"kind": "email", "address": "a@example.org"}, id="original")])
        args = {"target_id": "original", "expected_heads": ["original"], "reason": "Synthetic update", "request_id": "update"}
        with self.assertRaises(ValidationError):
            service.call("memory_correct", {**args, "value": {"kind": "email", "address": "invalid"}}, token)
        service.call("memory_correct", {**args, "value": {"kind": "email", "address": "b@example.org"}}, token)
        row = self.store.query(predicate="rm:contact-point")["assertions"][0]
        self.assertEqual(field_contract.declaration(row)["field"], "contact.email")
        downgrade = {k: v for k, v in row.items() if k in {"subject", "predicate", "value", "source_ids"}}
        downgrade.update(type="assertion", id="downgrade", kind="correct", predecessors=[row["id"]], reason="Cannot drop contract")
        with self.assertRaises(ValidationError): self.store.submit([downgrade])

    def test_typed_relationship_reclassification_uses_new_field_and_retains_old(self):
        token = self.store.create_grant("synthetic-editor", ["read", "write", "correct"])
        self.store.submit([action("relationship.employed-by", id="original")])
        Service(self.store).call("memory_correct", {"target_id": "original", "expected_heads": ["original"],
            "reason": "Synthetic membership, not employment", "request_id": "reclassify", "operation": "reclassify",
            "predicate": "member-of", "object": "organization"}, token)
        self.assertEqual(self.store.query(predicate="employed-by")["assertions"], [])
        row = self.store.query(predicate="member-of")["assertions"][0]
        self.assertEqual(field_contract.declaration(row)["field"], "relationship.member-of")
        self.assertEqual(field_contract.declaration(self.store.read("assertion", "original"))["field"], "relationship.employed-by")

    def test_generic_fact_cannot_claim_different_cardinality(self):
        a = action("identity.name", "Synthetic name")
        a["provenance"]["knowledge"]["cardinality"] = "multi-valued"
        with self.assertRaises(ValidationError): self.store.submit([a])

    def test_type_conflict_can_be_resolved_through_same_profile(self):
        actor = {"kind": "agent", "id": "synthetic-classifier"}
        self.store.submit([action("identity.type", "person", id="type")], actor=actor)
        for id, value in [("branch-a", "organization"), ("branch-b", "project")]:
            self.store.submit([action("identity.type", value, id=id, kind="correct", predecessors=["type"], reason="Synthetic branch")], actor=actor)
        self.assertTrue(self.store.get_entity("person")["classification"]["ambiguous"])
        self.store.submit([action("identity.type", "person", id="resolved", kind="correct", predecessors=["branch-a", "branch-b"], reason="Synthetic resolution")], actor=actor)
        self.assertEqual(self.store.get_entity("person")["classification"]["canonical_types"], ["person"])

    def test_reclassified_record_can_withdraw_old_field_but_not_reaffirm_it(self):
        email = action("contact.email", {"kind": "email", "address": "a@example.org"}, id="old-email")
        self.store.submit([email])
        self.store.submit([action("identity.type", "topic", id="type")])
        retract = copy.deepcopy(email); retract.update(id="remove", kind="retract", predecessors=["old-email"], reason="Withdraw obsolete field")
        self.store.submit([retract])
        self.assertEqual(self.store.query(predicate="rm:contact-point")["assertions"], [])
        reinstate = copy.deepcopy(email); reinstate.update(id="again", kind="reinstate", predecessors=["remove"], reason="Still wrong subject type")
        with self.assertRaises(ValidationError): self.store.submit([reinstate])

    def test_group_classification_cannot_bypass_new_field_applicability(self):
        for reversed_order in (False, True):
            change = action("identity.type", "topic", id="type")
            email = action("contact.email", {"kind": "email", "address": "a@example.org"}, id="email")
            actions = [change, email]
            with self.subTest(reversed_order=reversed_order):
                with self.assertRaises(ValidationError): self.store.submit(list(reversed(actions)) if reversed_order else actions)
                self.assertIsNone(self.store.read("assertion", "email"))
                self.assertIsNone(self.store.read("assertion", "type"))
        self.store.submit([action("identity.type", "topic", id="before")])
        change = action("identity.type", "person", id="after", kind="correct", predecessors=["before"], reason="Repair type")
        self.store.submit([email, change])
        self.assertEqual(self.store.get_entity("person")["classification"]["canonical_types"], ["person"])

    def test_reclassified_relationship_can_be_withdrawn(self):
        rel = action("relationship.employed-by", id="old-employment")
        self.store.submit([rel])
        self.store.submit([action("identity.type", "topic", id="subject-type"),
                           action("identity.type", "person", subject="organization", id="target-type")])
        retract = copy.deepcopy(rel); retract.update(id="withdraw", kind="retract", predecessors=["old-employment"], reason="Withdraw old employment")
        self.store.submit([retract])
        self.assertEqual(self.store.query(predicate="employed-by")["assertions"], [])

    def test_post_group_types_keep_owner_correction_preference(self):
        self.store.submit([action("identity.type", "person", id="original-type")])
        self.store.submit([action("identity.type", "topic", id="owner-type", kind="correct", predecessors=["original-type"], reason="Synthetic owner correction")])
        agent = {"kind": "agent", "id": "synthetic-classifier"}
        attempted = action("identity.type", "person", id="agent-type", kind="correct", predecessors=["owner-type"], reason="Cannot displace owner preference")
        email = action("contact.email", {"kind": "email", "address": "a@example.org"}, id="email")
        with self.assertRaises(ValidationError): self.store.submit([attempted, email], actor=agent)
        self.assertIsNone(self.store.read("assertion", "email"))
        self.assertEqual(self.store.get_entity("person")["classification"]["canonical_types"], ["topic"])

    def test_withdrawal_exemption_cannot_change_target_value_or_context(self):
        rel = action("relationship.employed-by", id="employment", valid_from="2020-01-01", time_precision="day")
        rel["provenance"]["knowledge"]["qualifiers"]["role"] = "advisor"
        email = action("contact.email", {"kind": "email", "address": "a@example.org"}, id="email", valid_from="2020-01-01", time_precision="day")
        self.store.submit([rel, email])
        self.store.submit([action("identity.type", "topic", id="new-type")])
        for variant in ("target", "start", "precision", "qualifier", "value"):
            old = email if variant == "value" else rel
            bad = copy.deepcopy(old); bad.update(id="bad-"+variant, kind="invalidate", predecessors=[old["id"]], reason="Synthetic end", valid_to="2021-01-01")
            q = bad["provenance"]["knowledge"]["qualifiers"]
            q["field_contract"]["validity_end"] = "known"
            if variant == "target": bad["object"] = "person"
            elif variant == "start": bad["valid_from"] = "2019-01-01"
            elif variant == "precision": bad["time_precision"] = "approximate"
            elif variant == "qualifier": q["role"] = "employee"
            else: bad["value"]["address"] = "b@example.org"
            with self.subTest(variant=variant):
                with self.assertRaises(ValidationError): self.store.submit([bad])
                self.assertIsNone(self.store.read("assertion", bad["id"]))
        end = copy.deepcopy(rel); end.update(id="ended", kind="invalidate", predecessors=["employment"], reason="Original relationship ended", valid_to="2021-01-01")
        end["provenance"]["knowledge"]["qualifiers"]["field_contract"]["validity_end"] = "known"
        self.store.submit([end])
        row = self.store.query(predicate="employed-by", valid_at="2020-06-01")["assertions"][0]
        self.assertEqual(row["object"], "organization")
        self.assertEqual(row["valid_to"], "2021-01-01")

    def test_ending_cannot_qualify_invalid_legacy_positive_knowledge(self):
        old = {"type": "assertion", "id": "legacy-edge", "subject": "topic", "predicate": "employed-by",
               "object": "person", "source_ids": ["source"], "valid_from": "2020-01-01", "valid_to": None, "time_precision": "day"}
        self.store.submit([old])
        end = action("relationship.employed-by", id="typed-ending", subject="topic", object="person", kind="invalidate",
                     predecessors=["legacy-edge"], reason="Cannot qualify via ending", valid_from="2020-01-01", valid_to="2021-01-01", time_precision="day")
        end["provenance"]["knowledge"]["qualifiers"]["field_contract"]["validity_end"] = "known"
        with self.assertRaises(ValidationError): self.store.submit([end])
        self.assertIsNone(self.store.read("assertion", "typed-ending"))

    def test_legacy_null_knowledge_can_be_withdrawn_without_crashing(self):
        legacy = {"type": "assertion", "id": "legacy-null", "subject": "person", "predicate": "rm:contact-point",
                  "value": {"kind": "email", "address": "a@example.org"}, "source_ids": ["source"],
                  "valid_from": None, "valid_to": None, "time_precision": "unknown", "provenance": {"knowledge": None}}
        self.store.submit([legacy])
        withdrawal = action("contact.email", legacy["value"], id="withdraw-null", kind="retract",
                            predecessors=["legacy-null"], reason="Explicit legacy withdrawal")
        self.store.submit([withdrawal])
        self.assertEqual(self.store.query(predicate="rm:contact-point")["assertions"], [])
        self.assertIsNone(self.store.read("assertion", "legacy-null")["provenance"]["knowledge"])


if __name__ == "__main__":
    unittest.main()
