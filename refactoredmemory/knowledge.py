"""Versioned knowledge annotations; evidence and actor authority remain separate."""
from __future__ import annotations

PROFILE = "refactoredmemory.knowledge:v1"
TYPE_PREDICATE = "rm:canonical-type"
ATLAS_REVISION = "e36ebe821eafb3fc00093b6afcc2c4c6e0c4c30d"
ENDPOINT_TYPES = ["person","organization","project","location","occurrence","topic","offering","item"]
PREDICATES = {
    "employed-by": {
        "category": "employment",
        "direction": "directed",
        "domain": [
            "person"
        ],
        "range": [
            "organization"
        ],
        "required": [
            "valid_from"
        ],
        "cardinality": "multi-valued"
    },
    "member-of": {
        "category": "affiliation",
        "direction": "directed",
        "domain": [
            "person",
            "organization"
        ],
        "range": [
            "organization"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "part-of": {
        "category": "structural",
        "direction": "directed",
        "domain": [
            "occurrence",
            "project"
        ],
        "range": [
            "occurrence",
            "project"
        ],
        "required": [],
        "cardinality": "functional"
    },
    "contained-in": {
        "category": "geography",
        "direction": "directed",
        "domain": [
            "location"
        ],
        "range": [
            "location"
        ],
        "required": [],
        "cardinality": "functional"
    },
    "has-type": {
        "category": "taxonomy",
        "direction": "directed",
        "domain": [
            "person",
            "organization",
            "project",
            "location",
            "occurrence",
            "topic",
            "offering",
            "item"
        ],
        "range": [
            "topic"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "operated-by": {
        "category": "structural",
        "direction": "directed",
        "domain": [
            "location"
        ],
        "range": [
            "organization"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "based-in": {
        "category": "geography",
        "direction": "directed",
        "domain": [
            "person",
            "organization"
        ],
        "range": [
            "location"
        ],
        "required": [],
        "cardinality": "functional"
    },
    "occurred-at": {
        "category": "occurrence",
        "direction": "directed",
        "domain": [
            "occurrence"
        ],
        "range": [
            "location"
        ],
        "required": [],
        "cardinality": "functional"
    },
    "participant-in": {
        "category": "occurrence",
        "direction": "directed",
        "domain": [
            "person",
            "organization"
        ],
        "range": [
            "occurrence",
            "project"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "connects": {
        "category": "network",
        "direction": "symmetric",
        "domain": [
            "person",
            "organization"
        ],
        "range": [
            "person",
            "organization"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "owns": {
        "category": "commerce",
        "direction": "directed",
        "domain": [
            "person",
            "organization"
        ],
        "range": [
            "item",
            "offering",
            "organization"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "offered-by": {
        "category": "commerce",
        "direction": "directed",
        "domain": [
            "offering",
            "occurrence"
        ],
        "range": [
            "organization"
        ],
        "required": [],
        "cardinality": "functional"
    },
    "sold-by": {
        "category": "commerce",
        "direction": "directed",
        "domain": [
            "item",
            "offering",
            "occurrence"
        ],
        "range": [
            "organization"
        ],
        "required": [],
        "cardinality": "functional"
    },
    "purchased": {
        "category": "commerce",
        "direction": "directed",
        "domain": [
            "person"
        ],
        "range": [
            "item",
            "offering",
            "occurrence"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "customer-of": {
        "category": "customer",
        "direction": "directed",
        "domain": [
            "person",
            "organization"
        ],
        "range": [
            "organization"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "founder-of": {
        "category": "employment",
        "direction": "directed",
        "domain": [
            "person"
        ],
        "range": [
            "organization"
        ],
        "required": [
            "valid_from"
        ],
        "cardinality": "multi-valued"
    },
    "acquired-by": {
        "category": "structural",
        "direction": "directed",
        "domain": [
            "organization"
        ],
        "range": [
            "organization"
        ],
        "required": [
            "valid_from"
        ],
        "cardinality": "functional"
    },
    "invests-in": {
        "category": "capital",
        "direction": "directed",
        "domain": [
            "person",
            "organization"
        ],
        "range": [
            "organization"
        ],
        "required": [
            "amount",
            "investment_status"
        ],
        "cardinality": "multi-valued"
    },
    "about": {
        "category": "taxonomy",
        "direction": "directed",
        "domain": [
            "person",
            "organization",
            "project",
            "location",
            "occurrence",
            "topic",
            "offering",
            "item"
        ],
        "range": [
            "topic",
            "project"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "parent-of": {
        "category": "personal",
        "direction": "directed",
        "domain": [
            "person"
        ],
        "range": [
            "person"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "spouse-of": {
        "category": "personal",
        "direction": "symmetric",
        "domain": [
            "person"
        ],
        "range": [
            "person"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "sibling-of": {
        "category": "personal",
        "direction": "symmetric",
        "domain": [
            "person"
        ],
        "range": [
            "person"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "estranged-from": {
        "category": "personal",
        "direction": "symmetric",
        "domain": [
            "person"
        ],
        "range": [
            "person"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "introduced-by": {
        "category": "network",
        "direction": "directed",
        "domain": [
            "person"
        ],
        "range": [
            "person"
        ],
        "required": [],
        "cardinality": "multi-valued"
    },
    "created": {
        "category": "creation",
        "direction": "directed",
        "domain": [
            "person",
            "organization"
        ],
        "range": [
            "item",
            "offering"
        ],
        "required": [],
        "cardinality": "multi-valued"
    }
}
# The captured document identity is the observation; evidence remains a source
# record. This is the concrete consumer for Atlas v2's observation/mentions model.
ENDPOINT_TYPES = [*ENDPOINT_TYPES, "observation"]
for _predicate in ("has-type", "about"):
    PREDICATES[_predicate]["domain"] = [*PREDICATES[_predicate]["domain"], "observation"]
for _endpoint in ("domain", "range"):
    PREDICATES["part-of"][_endpoint] = [*PREDICATES["part-of"][_endpoint], "observation"]
PREDICATES["mentions"] = {"category": "taxonomy", "direction": "directed",
    "domain": ["observation"], "range": list(ENDPOINT_TYPES),
    "required": [], "cardinality": "multi-valued"}
KINDS = ("fact", "relationship", "observation")
CATEGORIES = tuple(sorted({entry["category"] for entry in PREDICATES.values()}))
# These labels are properties, not replacements for immutable entity identities.
FACT_PREDICATES = tuple(["name","alias","description","status","homepage","founded-on","acquired-on","phone","email","address","birth-date","last-contacted","identifier"]) + (TYPE_PREDICATE, "rm:alias")
FACT_DEFINITIONS = {
    name: {"kind": "fact", "cardinality": "multi-valued", "description": description}
    for name, description in {
        "rm:contact-point": "An independently sourced contact address or profile URL; ownership and reachability are separate checks.",
        "rm:profile-property": "A source-reported profile property with its original context and source version.",
        "rm:reported-date": "A source-reported date property; different properties and observations may coexist.",
        "rm:communication-record": "A dated mailbox record; receipt, delivery, reading and relationship validity are not inferred.",
        "rm:meeting-record": "A captured provider meeting record with its reported date; participant identity is separate.",
        "rm:conversation-reference": "A captured conversation address reference with explicit identity/time limitations.",
        "rm:relationship-date-note": "A named date field reported in legacy relationship context; not a replacement validity interval.",
        "rm:enrichment-review": "An independent source-linked issue requiring review.",
        "rm:legacy-reference": "An explicit legacy identifier mapping; no affirmation of the referenced claim.",
        "rm:contact-record": "A dated interaction observation within a scoped engagement.",
        "rm:prospect-record": "A source-reported prospect within a project; not an established conversation.",
        "rm:review-flag": "An independent source-linked quality review record.",
    }.items()
}


def annotation(action):
    provenance = action.get("provenance", {})
    return provenance.get("knowledge") if isinstance(provenance, dict) else None


def validate_annotation(action):
    value = annotation(action)
    if value is None:
        return
    if not isinstance(value, dict) or value.get("schema") != PROFILE:
        raise ValueError("Unsupported knowledge annotation schema")
    if set(value) - {"schema", "kind", "category", "cardinality", "qualifiers", "legacy_context", "evidence_status", "unresolved_fields"}:
        raise ValueError("Unsupported knowledge annotation field")
    if value.get("kind") not in KINDS:
        raise ValueError("Invalid knowledge kind")
    expected = "relationship" if "object" in action else "observation" if action["predicate"] == "content" else "fact"
    if value["kind"] != expected:
        raise ValueError("Knowledge kind disagrees with assertion shape")
    if not isinstance(value.get("qualifiers", {}), dict):
        raise ValueError("Knowledge qualifiers must be an object")
    definition = PREDICATES.get(action["predicate"])
    if expected == "relationship" and definition is None:
        # New meanings require a versioned contract addition, not a typo.
        raise ValueError("Relationship is not in the knowledge contract")
    if expected == "fact" and action["predicate"] not in FACT_PREDICATES and ":" not in action["predicate"]:
        raise ValueError("New fact predicates require a defined or namespaced label")
    if definition and value.get("category") != definition["category"]:
        raise ValueError("Knowledge category disagrees with predicate")
    if definition and value.get("cardinality", definition["cardinality"]) != definition["cardinality"]:
        raise ValueError("Knowledge cardinality disagrees with predicate")
    fact_definition = FACT_DEFINITIONS.get(action["predicate"]) if expected == "fact" else None
    if fact_definition and value.get("cardinality", fact_definition["cardinality"]) != fact_definition["cardinality"]:
        raise ValueError("Knowledge cardinality disagrees with fact predicate")
    if action["predicate"] == TYPE_PREDICATE and action.get("value") not in ENDPOINT_TYPES:
        raise ValueError("Unsupported canonical endpoint type")


def validate_endpoints(action, source_types, target_types):
    if annotation(action) is None or "object" not in action:
        return
    definition = PREDICATES[action["predicate"]]
    if len(source_types) != 1 or len(target_types) != 1:
        raise ValueError("Canonical endpoint type is unresolved")
    source, target = next(iter(source_types)), next(iter(target_types))
    if source not in definition["domain"] or target not in definition["range"]:
        raise ValueError("Relationship endpoint types violate the knowledge contract")
    if action["predicate"] == "part-of" and source != target:
        raise ValueError("Composition requires the same endpoint type")


def describe(action):
    """Labels describe structure, never human verification or source authority."""
    supplied = annotation(action)
    if isinstance(supplied, dict) and supplied.get("schema") == PROFILE:
        result = dict(supplied)
        if result.get("kind") == "fact" and action.get("predicate") in FACT_DEFINITIONS:
            result["cardinality"] = FACT_DEFINITIONS[action["predicate"]]["cardinality"]
        return result
    kind = "relationship" if "object" in action else "observation" if action.get("predicate") == "content" else "fact"
    result = {"kind": kind, "profile": "legacy-unannotated"}
    definition = PREDICATES.get(action.get("predicate"))
    if definition and kind == "relationship":
        result.update(category=definition["category"], cardinality=definition.get("cardinality", "multi-valued"))
    if kind == "fact" and action.get("predicate") in FACT_DEFINITIONS:
        result["cardinality"] = FACT_DEFINITIONS[action["predicate"]]["cardinality"]
    return result


def multi_valued(predicate):
    return (PREDICATES.get(predicate, {}).get("cardinality") == "multi-valued"
            or FACT_DEFINITIONS.get(predicate, {}).get("cardinality") == "multi-valued")


def excerpt_offset(content, folded_text, length):
    if not folded_text:
        return 0, False
    match = content.casefold().find(folded_text)
    if match < 0:
        return 0, False
    # Case folding can expand characters; offsets refer to the original text.
    position = 0
    for index, char in enumerate(content):
        if position >= match:
            return max(0, index - length // 3), True
        position += len(char.casefold())
    return 0, False


def contract():
    return {"schema": PROFILE, "atlas_revision": ATLAS_REVISION,
            "endpoint_types": list(ENDPOINT_TYPES), "knowledge_kinds": list(KINDS),
            "categories": list(CATEGORIES), "predicates": PREDICATES,
            "fact_predicates": FACT_DEFINITIONS,
            "type_predicate": TYPE_PREDICATE,
            "limits": ["An annotation is not owner verification.",
                       "Unknown dates are not definite as-of matches.",
                       "Classification and subject matter are distinct.",
                       "Legacy-unannotated claims remain readable."]}

