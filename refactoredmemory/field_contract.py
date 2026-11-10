"""Published field semantics and opt-in core admission for tagged v1 assertions.

This module never rewrites captured data, discovers identities or performs I/O
other than reading the fixed, operator-controlled packaged contract resources.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from functools import lru_cache
import hashlib
from importlib.resources import files
import json
import math
import re
from urllib.parse import urlsplit

SCHEMA = "refactoredmemory.fields:v1"
REVISION = 1
TAG = "field_contract"


@lru_cache(maxsize=1)
def _catalog():
    return json.loads(files("refactoredmemory").joinpath("contracts/fields-v1.json").read_text())


def catalog():
    """Return a caller-owned copy; discovery cannot mutate admission rules."""
    result = deepcopy(_catalog())
    result["tag_schema"] = json.loads(files("refactoredmemory").joinpath(
        "contracts/field-tag-v1.schema.json").read_text())
    result["digest_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True,
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    return result


def _qualifiers(action):
    provenance = action.get("provenance", {})
    knowledge = provenance.get("knowledge", {}) if isinstance(provenance, dict) else {}
    qualifiers = knowledge.get("qualifiers", {}) if isinstance(knowledge, dict) else {}
    return qualifiers if isinstance(qualifiers, dict) else {}


def declaration(action):
    return _qualifiers(action).get(TAG)


def _present(action):
    return TAG in _qualifiers(action)


def _text(value, maximum=65536):
    if (not isinstance(value, str) or not value.strip() or len(value) > maximum
            or any(ord(c) < 32 and c not in "\n\t" for c in value)):
        raise ValueError("Field needs nonempty bounded text")


def _calendar(value, precision):
    _text(value, 10)
    try:
        if precision == "year" and re.fullmatch(r"\d{4}", value):
            date(int(value), 1, 1)
        elif precision == "month" and re.fullmatch(r"\d{4}-\d{2}", value):
            date.fromisoformat(value + "-01")
        elif precision == "day" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            date.fromisoformat(value)
        else:
            raise ValueError("Reported calendar date disagrees with its precision")
    except (ValueError, OverflowError) as exc:
        raise ValueError("Invalid source-reported calendar date or precision") from exc


def _known(value, definition, raw):
    kind = definition["value_type"]
    if kind == "entity_type":
        if not isinstance(value, str) or value not in _catalog()["record_types"]:
            raise ValueError("Unsupported field entity type")
    elif kind == "text_list":
        if not isinstance(value, list) or not 1 <= len(value) <= 100:
            raise ValueError("Aliases need a nonempty bounded list")
        for item in value:
            _text(item, 1024)
        if len(set(value)) != len(value):
            raise ValueError("Duplicate aliases")
    else:
        _text(value, 320 if kind == "email" else 128 if kind == "phone_text" else 65536)
        if kind == "email" and (not re.fullmatch(r"[^@\s]+@[^@\s]+", value)
                                 or any(ord(c) < 32 for c in value)):
            raise ValueError("Invalid email syntax; ownership is unverified")
        if kind == "phone_text" and (not 3 <= sum(c.isdecimal() for c in value) <= 32
                                     or not re.fullmatch(r"[+0-9() .\-xXeEtT#;/]+", value)):
            raise ValueError("Invalid reported phone; no country code is inferred")
        if kind == "http_url":
            try:
                parsed = urlsplit(value)
                _ = parsed.port
            except ValueError as exc:
                raise ValueError("Invalid HTTP URL") from exc
            if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                    or parsed.username is not None or parsed.password is not None
                    or any(c.isspace() or ord(c) < 32 for c in value)):
                raise ValueError("URL needs HTTP(S), a host and no credentials")
        if kind == "calendar_date":
            _calendar(value, raw.get("precision"))


def validate_action(action):
    """Validate only explicit v1 declarations; untagged history is unchanged."""
    provenance = action.get("provenance", {})
    if isinstance(provenance, dict) and TAG in provenance:
        raise ValueError("Field contract tag belongs in knowledge.qualifiers")
    if not _present(action):
        return
    tag = declaration(action)
    if (not isinstance(tag, dict) or set(tag) != {"schema", "revision", "field", "state", "validity_end"}
            or tag.get("schema") != SCHEMA or type(tag.get("revision")) is not int
            or tag["revision"] != REVISION or not isinstance(tag.get("field"), str)):
        raise ValueError("Unsupported field contract declaration")
    definition = _catalog()["fields"].get(tag["field"])
    if definition is None or tag.get("state") not in definition["states"]:
        raise ValueError("Unsupported field or value state; not-recorded is read-only")
    if provenance["knowledge"].get("cardinality", definition["cardinality"]) != definition["cardinality"]:
        raise ValueError("Field cardinality disagrees with its core definition")
    if "valid_from" not in action or "time_precision" not in action:
        raise ValueError("Field writes require explicit validity start and precision")
    end = tag.get("validity_end")
    if not isinstance(end, str):
        raise ValueError("Unsupported validity end state")
    if (end == "unknown" and ("valid_to" not in action or action["valid_to"] is not None)
            or end == "ongoing" and "valid_to" in action
            or end == "known" and not isinstance(action.get("valid_to"), str)
            or end not in {"unknown", "ongoing", "known"}):
        raise ValueError("Validity end declaration disagrees with the operation")
    if action.get("valid_from") is None and action["time_precision"] != "unknown":
        raise ValueError("Unknown validity start needs unknown precision")
    if action.get("predicate") != definition["storage"]["predicate"]:
        raise ValueError("Field predicate disagrees with its core definition")
    if definition["value_type"] == "entity_reference":
        if "object" not in action or "value" in action:
            raise ValueError("Relationship field needs a target identity")
        qualifiers = provenance["knowledge"]["qualifiers"]
        for required in definition["required_context"]:
            if required == "valid_from":
                continue  # Explicit null is supported unknown; dates are not guessed.
            if required not in qualifiers:
                raise ValueError("Relationship context missing: " + required)
        if definition["storage"]["predicate"] == "invests-in":
            amount = qualifiers["amount"]
            if amount is not None:
                if (not isinstance(amount, dict) or set(amount) != {"value", "currency"}
                        or type(amount["value"]) not in {int, float}
                        or (type(amount["value"]) is float and not math.isfinite(amount["value"]))
                        or amount["value"] < 0
                        or not isinstance(amount["currency"], str)
                        or not re.fullmatch(r"[A-Z]{3}", amount["currency"])):
                    raise ValueError("Investment amount needs a finite value and explicit currency, or null")
            if (not isinstance(qualifiers["investment_status"], str) or
                    qualifiers["investment_status"] not in {"proposed", "discussed", "committed", "completed", "declined", "withdrawn", "unknown"}):
                raise ValueError("Unsupported source-reported investment status")
        return
    if "value" not in action or "object" in action:
        raise ValueError("Fact field needs a scalar or structured value")
    raw = action["value"]
    match = definition["storage"]["match"]
    if match:
        if not isinstance(raw, dict):
            raise ValueError("Field needs its mapped structured value")
        for key, expected in match.items():
            allowed = definition["legacy_properties"] if key == "property" else [expected]
            if raw.get(key) not in allowed:
                raise ValueError("Field discriminator disagrees with its definition")
        allowed_keys = set(match) | set(definition["storage"]["value_path"])
        if definition["value_type"] == "calendar_date":
            allowed_keys |= {"precision", "reported_value", "source_annotation"}
        if definition["storage"]["predicate"] == "rm:contact-point":
            allowed_keys |= {"label", "country_code"}
            if "country_code" in raw and raw["country_code"] is not None:
                _text(raw["country_code"], 16)
        if set(raw) - allowed_keys:
            raise ValueError("Keep legacy/derived metadata in history; it is not an editable field")
        for key in ("label", "reported_value", "source_annotation"):
            if key in raw:
                _text(raw[key])
        for key in definition["storage"]["value_path"]:
            if key not in raw:
                raise ValueError("Mapped field value is missing")
            raw = raw[key]
    if tag["state"] != "known":
        if raw is not None:
            raise ValueError("Unknown/not-applicable needs a sourced null, not a placeholder")
        if definition["value_type"] == "calendar_date" and action["value"].get("precision") != "unknown":
            raise ValueError("Unknown reported date needs unknown calendar precision")
    else:
        _known(raw, definition, action["value"])


def validate_subject(action, canonical_types):
    if not _present(action):
        return
    if declaration(action)["field"] == "identity.type" or is_withdrawal(action):
        # A supported type declaration repairs classification. Withdrawal does
        # not reaffirm a field after its subject was reclassified.
        return
    definition = _catalog()["fields"][declaration(action)["field"]]
    if len(canonical_types) != 1 or next(iter(canonical_types)) not in definition["applies_to"]:
        raise ValueError("Field subject type is unresolved or not applicable")


def is_withdrawal(action):
    return _present(action) and action.get("kind") in {"retract", "invalidate"}


def validate_predecessor(action, previous):
    """A field correction cannot silently move another field's lineage."""
    prior = declaration(previous)
    if prior is not None and not _present(action):
        raise ValueError("A field-contract lineage cannot discard its declaration")
    if not _present(action):
        return
    field = declaration(action)["field"]
    if is_withdrawal(action):
        if action.get("kind") == "invalidate" and prior is None:
            raise ValueError("A legacy ending cannot infer v1 qualification; retain its profile or explicitly qualify it first")
        for key in ("value", "object", "valid_from", "uncertainty"):
            if action.get(key) != previous.get(key):
                raise ValueError("Withdrawal must retain the original claim meaning")
        if action.get("time_precision", "exact") != previous.get("time_precision", "exact"):
            raise ValueError("Withdrawal must retain original time precision")
        current_q = dict(_qualifiers(action))
        previous_q = dict(_qualifiers(previous))
        current_q.pop(TAG, None); previous_q.pop(TAG, None)
        if current_q != previous_q:
            raise ValueError("Withdrawal must retain semantic qualifiers")
        if prior is not None and declaration(action)["state"] != prior["state"]:
            raise ValueError("Withdrawal cannot change the prior field value state")
        if prior is None and declaration(action)["state"] != "known":
            raise ValueError("Ambiguous legacy missing states need a legacy withdrawal")
        if action.get("kind") == "retract" and (
                ("valid_to" in action) != ("valid_to" in previous)
                or action.get("valid_to") != previous.get("valid_to")):
            raise ValueError("Retraction must retain the original interval")
    if prior is not None:
        if prior.get("field") != field:
            raise ValueError("Correction cannot move a field lineage; retract and create explicitly")
        return
    definition = _catalog()["fields"][field]
    raw = previous.get("value")
    for key, expected in definition["storage"]["match"].items():
        allowed = definition["legacy_properties"] if key == "property" else [expected]
        if not isinstance(raw, dict) or raw.get(key) not in allowed:
            raise ValueError("Legacy field meaning is unresolved or different; retain it separately")


def matching_field(action):
    """Resolve explicit native predicate/discriminators, never source meaning."""
    matches = []
    for name, definition in _catalog()["fields"].items():
        if action.get("predicate") != definition["storage"]["predicate"]:
            continue
        raw = action.get("value")
        if all(isinstance(raw, dict) and raw.get(key) in
               (definition["legacy_properties"] if key == "property" else [expected])
               for key, expected in definition["storage"]["match"].items()):
            matches.append(name)
    if len(matches) != 1:
        raise ValueError("Reclassification needs an explicit supported field mapping")
    return matches[0]


def project(entity, assertions, *, complete, selection_only=False, administrative_suppression=False):
    """Map bounded readable claims without qualifying or rewriting legacy data."""
    complete = bool(complete and not administrative_suppression)
    definitions = _catalog()["fields"]
    types = entity.get("classification", {}).get("canonical_types", [])
    fields, mapped, unmapped = {}, {}, []
    for name, definition in definitions.items():
        applicable = len(types) == 1 and types[0] in definition["applies_to"]
        if applicable or name in {"identity.type", "identity.name"}:
            fields[name] = {"claim_ids": [], "applicable": applicable,
                "empty_state": "not_recorded" if complete and not selection_only else "not_in_selection"}
    for assertion in assertions:
        tag = declaration(assertion)
        try:
            if _present(assertion):
                if (not isinstance(tag, dict) or set(tag) != {"schema", "revision", "field", "state", "validity_end"}
                        or tag.get("schema") != SCHEMA or type(tag.get("revision")) is not int
                        or tag["revision"] != REVISION or not isinstance(tag.get("field"), str)):
                    raise ValueError("Unrecognized historical declaration")
            name = tag["field"] if isinstance(tag, dict) else matching_field(assertion)
            if name not in definitions:
                raise ValueError("Unsupported field")
            if tag is not None and (tag.get("state") not in definitions[name]["states"]
                                    or tag.get("validity_end") not in {"unknown", "ongoing", "known"}):
                raise ValueError("Unrecognized historical field state")
        except (ValueError, KeyError, TypeError):
            unmapped.append(assertion["id"])
            continue
        entry = fields.setdefault(name, {"claim_ids": [], "applicable": False,
                                        "empty_state": "not_in_selection"})
        entry["claim_ids"].append(assertion["id"])
        mapped[assertion["id"]] = {"field": name,
            "qualification": "explicit_v1" if tag is not None else "legacy_unqualified",
            "state": tag["state"] if tag is not None else "legacy_unspecified",
            "editable_value_loaded": "object" in assertion or "value" in assertion}
    return {"schema": SCHEMA, "revision": REVISION,
            "digest_sha256": catalog()["digest_sha256"],
            "fields": fields, "claims": mapped, "unmapped_claim_ids": unmapped,
            "coverage": {"complete": bool(complete and not selection_only),
                         "selection_only": selection_only,
                         "administrative_suppression": administrative_suppression,
                         "meaning": "Mapping is not qualification. A declaration is not proof of historical validation. Absent claims in a partial selection are not proof of absence."}}


def apply_update(action, update):
    """Explicit correction metadata; normal core validation remains authoritative."""
    if update["catalog_digest"] != catalog()["digest_sha256"]:
        raise ValueError("Field catalog changed; reload before editing")
    definition = _catalog()["fields"].get(update["field"])
    if definition is None:
        raise ValueError("Unsupported field")
    context = update.get("context", {})
    if set(context) - (set(definition.get("required_context", [])) - {"valid_from"}):
        raise ValueError("Only registered relationship context can be edited")
    profile = action.setdefault("provenance", {}).get("knowledge")
    if not isinstance(profile, dict):
        profile = {"schema": "refactoredmemory.knowledge:v1",
                   "kind": "relationship" if "object" in action else "fact"}
        action["provenance"]["knowledge"] = profile
    qualifiers = dict(profile.get("qualifiers") or {})
    qualifiers.update(context)
    qualifiers[TAG] = {"schema": SCHEMA, "revision": REVISION,
        "field": update["field"], "state": update["state"],
        "validity_end": update["validity_end"]}
    profile["qualifiers"] = qualifiers
    if "category" in definition:
        profile["category"] = definition["category"]
    action.update(valid_from=update["valid_from"], time_precision=update["time_precision"])
    action.pop("valid_to", None)
    if "valid_to" in update:
        action["valid_to"] = update["valid_to"]
    validate_action(action)


def is_typed_capture(arguments):
    """Private App capture boundary, not a replacement for core admission.

    A prior catalog digest can reach the core only to recover an exact committed
    retry; new stale writes are rejected there under the current consumer grant.
    """
    if not isinstance(arguments, dict):
        return False
    digest = arguments.get("catalog_digest")
    actions = arguments.get("actions")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest) or not isinstance(actions, list):
        return False
    if any(not isinstance(a, dict) or a.get("type") not in ("assertion", "source", "entity") for a in actions):
        return False
    assertions = [a for a in actions if a["type"] == "assertion"]
    if not assertions or any(not isinstance(declaration(a), dict) or a.get("kind", "assert") != "assert" for a in assertions):
        return False
    source_ids = [sid for a in assertions
                  for sid in (a.get("source_ids") if isinstance(a.get("source_ids"), list) else [])
                  if isinstance(sid, str)]
    references = [a.get(key) for a in assertions for key in ("subject", "object")]
    for action in actions:
        if action["type"] == "source" and action.get("id") not in source_ids:
            return False
        if action["type"] == "entity" and (action.get("entity_type") not in _catalog()["record_types"]
                                           or action.get("id") not in references):
            return False
    return True


def validate_group(actions):
    """A group declaring typed creation includes sourced type and display name."""
    tagged = [a for a in actions if isinstance(a, dict) and _present(a)]
    if not tagged:
        return
    for action in tagged:
        validate_action(action)
    for entity in actions:
        if not isinstance(entity, dict) or entity.get("type") != "entity":
            continue
        if entity.get("entity_type") in _catalog()["capture_only_types"]:
            continue
        fields = {declaration(a).get("field"): a for a in tagged
                  if isinstance(declaration(a), dict) and a.get("subject") == entity.get("id")}
        if not {"identity.type", "identity.name"} <= fields.keys():
            raise ValueError("Typed record creation needs sourced type and name in the same group")
        for field in ("identity.type", "identity.name"):
            if declaration(fields[field]).get("state") != "known":
                raise ValueError("Typed record creation needs known name and type")
        if (fields["identity.type"].get("value") != entity.get("entity_type")
                or fields["identity.name"].get("value") != entity.get("label")):
            raise ValueError("Typed creation identity and sourced fields disagree")
