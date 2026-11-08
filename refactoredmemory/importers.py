"""Bounded, source-preserving import plans. No source is changed or executed.

The public plan is intentionally a Python object: raw source bytes stay in the
plan until apply. ``summary()`` is suitable for CLI output and omits content.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
from typing import Any

from .store import CapacityError

MAX_FILE_BYTES = 1024 * 1024
MAX_FILES = 500
MAX_RECORDS = 10000
MAX_NOTE_BYTES = 60 * 1024
SOURCE_CHARS = 16000
ACTIONS = {"assert", "correct", "retract", "invalidate", "reinstate"}


class ImportError(ValueError):
    """An unsafe, unsupported, or stale import plan."""


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _hash(value: str | bytes) -> str:
    return sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def mapped_id(namespace: str, kind: str, original: str) -> str:
    """Explicit collision-resistant mapping, stable across source copies/peers."""
    return f"import-{kind}-{_hash(_json([namespace, kind, original]))}"


def _pairs(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ImportError("duplicate-json-key")
        result[key] = value
    return result


def _decode(text: str) -> Any:
    def reject(value: str) -> None:
        raise ImportError("nonfinite-json-number")
    try:
        return json.loads(text, object_pairs_hook=_pairs, parse_constant=reject)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ImportError("invalid-json") from exc


def _safe_read(path: Path, root: Path, limit: int) -> bytes:
    # Reject symlinks in every component before opening. O_NOFOLLOW also prevents
    # a final-component symlink swap. The supplied source tree must be quiescent.
    if root.is_symlink():
        raise ImportError("symlink-approved-root")
    absolute = Path(os.path.abspath(path))
    try:
        relative = absolute.relative_to(root)
    except ValueError as exc:
        raise ImportError("outside-approved-root") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ImportError("symlink-input")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(absolute, flags)
    except OSError as exc:
        raise ImportError("unreadable-input") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ImportError("nonregular-input")
        if before.st_size > limit:
            raise ImportError("file-byte-limit")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(limit + 1)
        after = os.fstat(fd)
        if len(data) > limit:
            raise ImportError("file-byte-limit")
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
            raise ImportError("source-changed-during-read")
        return data
    finally:
        os.close(fd)


@dataclass
class ImportPlan:
    root: Path
    namespace: str
    files: list[dict] = field(default_factory=list)
    records: list[dict] = field(default_factory=list)
    max_file_bytes: int = MAX_FILE_BYTES

    def summary(self) -> dict:
        clean = lambda item: {k: v for k, v in item.items() if not k.startswith("_")}
        files = [clean(f) for f in self.files]
        records = [clean(r) for r in self.records]
        counts: dict[str, int] = {}
        for record in records:
            counts[record["status"]] = counts.get(record["status"], 0) + 1
        return {"schema": "refactoredmemory-import/1", "namespace": self.namespace,
                "approved_root": str(self.root),
                "files": files, "records": records, "counts": counts,
                "file_count": len(files), "record_count": len(records),
                "source_mutations": 0, "dry_run": True}


def _record(file_index: int, index: int, data: Any, *, status: str = "planned", reason: str = "") -> dict:
    return {"file_index": file_index, "record_index": index, "status": status,
            "reason": reason, "_data": data}


def _contains_quarantine(value: Any) -> bool:
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            if item.get("access_class") == "quarantine":
                return True
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return False


def _parse_json_records(value: Any) -> tuple[str, list[Any]]:
    if isinstance(value, dict) and value.get("schema_version") == 1 and isinstance(value.get("objects"), list):
        # Keep the snapshot envelope and its metadata as a source; records name
        # all current objects, plus retained operation records as metadata.
        if not isinstance(value.get("operation_records", []), list):
            raise ImportError("invalid-snapshot-operation-records")
        return "living-atlas-snapshot-v1", [*value["objects"], *[{"_snapshot_operation": r} for r in value.get("operation_records", [])]]
    if isinstance(value, list):
        return "living-atlas-record-array", value
    if isinstance(value, dict) and ("record_schema" in value or "payload" in value):
        return "living-atlas-record", [value]
    return "unrecognized-json", [value]


def _parse_lines(text: str, file_index: int) -> tuple[str, list[dict]]:
    lines = text.splitlines(keepends=True)
    rows = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            rows.append(_record(file_index, i, _decode(line)))
        except ImportError as exc:
            rows.append(_record(file_index, i, None, status="quarantined", reason=str(exc)))
    if not rows:
        return "empty-jsonl", []
    header = rows[0]["_data"]
    fmt = header.get("log_format") if isinstance(header, dict) else None
    if fmt not in {"atlas.segment-log:v1", "atlas.identity-log:v1"}:
        if all(isinstance(row["_data"], dict) and "object" in row["_data"] and "entry_hash" in row["_data"] for row in rows):
            for row in rows:
                row.update(status="preserved-only", reason="legacy-journal-replay-unqualified")
            return "living-atlas-journal-v1", rows
        for row in rows:
            row.update(status="unsupported", reason="unknown-jsonl-format")
        return "unrecognized-jsonl", rows
    identity = fmt == "atlas.identity-log:v1"
    member_kinds = {"entity", "alias", "observation"} if identity else {"assertion", "supersession"}
    marker = "group-commit" if identity else "submission"
    controls = {"header", "repair"} if identity else {"header", "watermark", "history-floor", "compaction", "repair"}
    pending: list[dict] = []
    broken = False
    for row in rows:
        data = row["_data"]
        if row["status"] == "quarantined" or not isinstance(data, dict):
            broken = True
            continue
        kind = data.get("record")
        if kind in member_kinds:
            pending.append(row)
        elif kind == marker:
            key = data.get("group_seq") if identity else (data.get("receipt") if isinstance(data.get("receipt"), dict) else {}).get("submission_id")
            keys = [r["_data"].get("group_seq" if identity else "submission_id") for r in pending]
            if not pending or key is None or any(k != key for k in keys):
                broken = True
            if not identity:
                bodies = [(r["_data"].get("assertion") if isinstance(r["_data"].get("assertion"), dict) else {}).get("assertion_id") for r in pending if r["_data"].get("record") == "assertion"]
                expected_ids = (data.get("receipt") if isinstance(data.get("receipt"), dict) else {}).get("assertion_ids", [])
                if (not isinstance(expected_ids, list) or any(not isinstance(x, str) for x in [*bodies, *expected_ids])
                        or sorted(bodies) != sorted(expected_ids)):
                    broken = True
            pending = []
            row.update(status="preserved-only", reason="commit-metadata")
        elif kind in controls:
            if kind == "header" and row is not rows[0]:
                broken = True
            if pending:
                broken = True
            row.update(status="preserved-only", reason="log-control-metadata")
        else:
            broken = True
    for row in pending:
        row.update(status="quarantined", reason="uncommitted-tail")
    if lines and not lines[-1].endswith("\n"):
        # Never infer a durable commit from bytes without the record terminator.
        broken = True
    if broken:
        for row in rows:
            row.update(status="quarantined", reason="invalid-or-incomplete-segment")
    return fmt, rows


def plan_import(path: str | Path, *, approved_root: str | Path, namespace: str = "personal-import",
                max_file_bytes: int = MAX_FILE_BYTES, max_files: int = MAX_FILES,
                max_records: int = MAX_RECORDS) -> ImportPlan:
    if not isinstance(namespace, str) or not namespace.strip() or len(namespace) > 200:
        raise ImportError("invalid-import-namespace")
    if not 0 < max_file_bytes <= MAX_FILE_BYTES or not 0 < max_files <= MAX_FILES or not 0 < max_records <= MAX_RECORDS:
        raise ImportError("invalid-import-bounds")
    raw_root = Path(os.path.abspath(approved_root))
    # OS-managed ancestor aliases are normal (macOS /var -> /private/var).
    # Pin that spelling once, while refusing a symlink chosen as the root itself.
    # Descendants are never resolved here: _safe_read must still see and reject
    # any symlinks that could cross the approved source boundary.
    if raw_root.is_symlink():
        raise ImportError("symlink-approved-root")
    root = raw_root.parent.resolve(strict=True) / raw_root.name
    if not root.is_dir():
        raise ImportError("approved-root-is-not-directory")
    named_target = Path(os.path.abspath(path))
    try:
        relative = named_target.relative_to(raw_root)
    except ValueError:
        # A caller may already hold the canonical spelling of the same root.
        # This is a lexical comparison, not resolution of an untrusted child.
        try:
            relative = named_target.relative_to(root)
        except ValueError as exc:
            raise ImportError("outside-approved-root") from exc
    target = root / relative
    current = root
    for part in target.relative_to(root).parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise ImportError("symlink-input")
    paths: list[Path] = []
    if target.is_dir() and not target.is_symlink():
        for base, dirs, files in os.walk(target, followlinks=False):
            for name in sorted(dirs):
                candidate = Path(base) / name
                if candidate.is_symlink():
                    paths.append(candidate)
            dirs[:] = sorted(d for d in dirs if not (Path(base) / d).is_symlink())
            paths.extend(Path(base) / name for name in sorted(files))
            if len(paths) > max_files:
                raise ImportError("file-count-limit")
    else:
        paths = [target]
    if len(paths) > max_files:
        raise ImportError("file-count-limit")
    plan = ImportPlan(root, namespace, max_file_bytes=max_file_bytes)
    for path_item in sorted(paths):
        index = len(plan.files)
        item = {"relative_path": path_item.relative_to(root).as_posix(), "status": "planned", "_path": path_item}
        plan.files.append(item)
        try:
            raw = _safe_read(path_item, root, max_file_bytes)
            item["sha256"] = _hash(raw)
            item["bytes"] = len(raw)
            text = raw.decode("utf-8", errors="strict")
            suffix = path_item.suffix.lower()
            if suffix in {".md", ".markdown"}:
                item["format"] = "markdown-logseq"
                if len(raw) > MAX_NOTE_BYTES:
                    raise ImportError("note-byte-limit")
                records = [_record(index, 0, {"_note": text})]
            elif suffix == ".json":
                item["format"], values = _parse_json_records(_decode(text))
                records = [_record(index, n, value) for n, value in enumerate(values)]
            elif suffix in {".jsonl", ".ndjson"}:
                item["format"], records = _parse_lines(text, index)
            else:
                raise ImportError("unsupported-file-type")
            item["_text"] = text
            # Quarantined legacy payloads must not leak through a raw-file source.
            if any(_contains_quarantine(r["_data"]) for r in records):
                item.update(status="quarantined", reason="contains-quarantined-content")
                for row in records:
                    row.update(status="quarantined", reason="contains-quarantined-content")
            for row in records:
                if row["status"] == "planned":
                    category, _ = _unwrap(row)
                    row["category"] = category
                    if category in {"opaque", "encrypted", "tombstone", "metadata"}:
                        row.update(status="preserved-only", reason={"opaque": "unrecognized-semantic-shape",
                                   "encrypted": "ciphertext-unavailable-not-decrypted",
                                   "tombstone": "legacy-tombstone-not-an-affirmed-claim",
                                   "metadata": "legacy-control-or-identity-metadata"}[category])
            plan.records.extend(records)
        except (ImportError, UnicodeDecodeError) as exc:
            reason = str(exc) if isinstance(exc, ImportError) else "invalid-utf8"
            item.update(status="unsupported", reason=reason)
            plan.records.append(_record(index, 0, None, status="unsupported", reason=reason))
        if len(plan.records) > max_records:
            raise ImportError("record-count-limit")
    return plan


def _existing(store: Any, kind: str, identifier: str) -> Any:
    return store.read(kind, identifier)


def _point(value: Any) -> tuple[str | None, str]:
    if isinstance(value, dict):
        kind = value.get("kind")
        if kind == "unknown":
            return None, "unknown"
        point, precision = _point(value.get("value"))
        return point, "approximate" if kind == "approximate" else precision
    if value is None or value == "unknown":
        return None, "unknown"
    if not isinstance(value, str):
        return None, "unknown"
    if value.startswith("~"):
        point, _ = _point(value[1:])
        return point, "approximate"
    if re.fullmatch(r"\d{4}(-\d{2})?", value):
        return None, "approximate"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value, "day"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T[^\s]+(?:Z|[+-]\d{2}:\d{2})", value):
        return value, "exact"
    return None, "unknown"


def _source_actions(plan: ImportPlan, file: dict) -> list[dict]:
    text = file["_text"]
    chunks = [text[i:i + SOURCE_CHARS] for i in range(0, len(text), SOURCE_CHARS)] or [""]
    actions = []
    for i, chunk in enumerate(chunks):
        sid = mapped_id(plan.namespace, "source", _json([file["relative_path"], file["sha256"], i]))
        actions.append({"type": "source", "id": sid,
                        "uri": f"import://{plan.namespace}/{file['relative_path']}#part={i}",
                        "content": chunk, "metadata": {"import_namespace": plan.namespace,
                        "relative_path": file["relative_path"], "source_sha256": file["sha256"],
                        "part": i, "parts": len(chunks), "format": file["format"],
                        "fidelity": "verbatim-utf8-source"}})
    return actions


def _provenance(row: dict, file: dict, original: dict) -> dict:
    original_provenance = original.get("provenance") if isinstance(original.get("provenance"), dict) else {}
    return {"method": "deterministic-import", "legacy_id": row.get("original_id"),
            "source_record_index": row["record_index"], "source_sha256": file["sha256"],
            "original_recorded_at": original.get("recorded_at", original.get("updated_at")),
            "original_recorded_at_fidelity": original_provenance.get("recorded_at_fidelity", "unknown"),
            "original_provenance": original_provenance,
            "original_evidence_available": False,
            "original_evidence_links": original.get("evidence_links", []),
            "original_valid_from": original.get("valid_from"), "original_valid_to": original.get("valid_to"),
            "original_record_schema": original.get("record_schema", original.get("schema")),
            "knowledge_time": "import-receipt-not-original-recorded-time"}


def _unwrap(row: dict) -> tuple[str, dict]:
    data = row["_data"]
    if not isinstance(data, dict):
        return "opaque", {}
    if "_note" in data:
        return "note", data
    if "_snapshot_operation" in data:
        return "metadata", data
    if data.get("record") == "entity":
        return ("entity", data["entity"]) if isinstance(data.get("entity"), dict) else ("opaque", data)
    if data.get("record") == "assertion":
        return ("assertion", data["assertion"]) if isinstance(data.get("assertion"), dict) else ("opaque", data)
    if data.get("record") in {"alias", "observation", "supersession"}:
        return "metadata", data
    if "object" in data and "entry_hash" in data:
        # The full raw journal and its digest are preserved. Its upstream hash
        # scheme is not re-certified here; source-record timestamps stay metadata.
        data = data["object"]
    if "payload" in data:
        if data.get("access_class") == "quarantine":
            return "quarantine", data
        if not isinstance(data.get("payload"), dict) or data["payload"].get("kind") != "plaintext-json":
            return "encrypted", data
        if isinstance(data.get("visible_metadata"), dict) and data["visible_metadata"].get("tombstone"):
            return "tombstone", data
        original = data
        data = data["payload"].get("data", {})
        if not isinstance(data, dict):
            return "opaque", original
        data = dict(data)
        data.setdefault("_envelope_id", original.get("object_id"))
        data.setdefault("_envelope_type", original.get("object_type"))
        data.setdefault("_namespace", (original.get("visible_metadata") if isinstance(original.get("visible_metadata"), dict) else {}).get("schema_namespace"))
    schema = data.get("record_schema", data.get("schema"))
    if schema == "atlas.entity:v1":
        return "entity", data
    if schema in {"atlas.assertion:v1", "atlas.fact:v1", "atlas.relationship:v2"}:
        return "assertion", data
    if data.get("_envelope_type") == "entity" or data.get("_namespace") in {
        "import/logseq-semantic/typed-endpoint", "import/logseq-topic-review/promoted", "import/connector-enrichment/promoted"
    }:
        return "entity", data
    if "edge_id" in data and all(key in data for key in ("source_object_id", "target_object_id", "predicate")):
        return "edge", data
    return "opaque", data


def apply_import(store: Any, plan: ImportPlan, *, actor: dict | None = None,
                 backup_path: str | Path | None = None) -> dict:
    """Apply a checked plan, returning complete accounting including failures.

    A pre-import backup is mandatory for writes. The caller decides where that
    backup belongs. Partial application is explicit and never deletes originals.
    """
    if not isinstance(plan, ImportPlan):
        raise ImportError("expected-import-plan")
    if backup_path is None:
        raise ImportError("backup-path-required")
    backup = Path(os.path.abspath(backup_path)).resolve(strict=False)
    if backup.is_relative_to(plan.root):
        raise ImportError("backup-inside-source-root")
    destination = getattr(store, "path", None)
    if destination and Path(os.path.abspath(destination)).resolve(strict=False).is_relative_to(plan.root):
        raise ImportError("destination-inside-source-root")
    for file in plan.files:
        if "sha256" in file:
            data = _safe_read(file["_path"], plan.root, plan.max_file_bytes)
            if _hash(data) != file["sha256"]:
                raise ImportError("source-changed-after-plan")
    # An administrative import is not a fresh human correction. Original actor
    # claims remain untrusted source provenance; the local writer is an importer.
    authorizer = actor.get("id", "local") if isinstance(actor, dict) else "local"
    import_actor = {"id": "importer:" + _hash(str(authorizer)), "kind": "agent"}
    rows = [dict(row) for row in plan.records]
    entities: dict[str, dict] = {}
    sources: dict[str, dict] = {}
    assertions: dict[str, dict] = {}
    owners: dict[str, list[dict]] = {}
    file_sources: dict[int, list[str]] = {}
    classifications: list[tuple[dict, str, dict]] = []
    for i, file in enumerate(plan.files):
        if file["status"] == "planned" and "_text" in file:
            source_actions = _source_actions(plan, file)
            file_sources[i] = [a["id"] for a in source_actions]
            for action in source_actions:
                sources[action["id"]] = action
    for row in rows:
        if row["status"] not in {"planned", "preserved-only"}:
            continue
        category, data = _unwrap(row)
        classifications.append((row, category, data))
        if row["status"] == "preserved-only":
            continue
        elif category == "metadata":
            row.update(status="preserved-only", reason="legacy-control-or-identity-metadata")
        elif category == "entity":
            original_id = data.get("entity_id", data.get("_envelope_id"))
            if not isinstance(original_id, str) or not original_id:
                row.update(status="unsupported", reason="missing-entity-identity")
                continue
            eid = mapped_id(plan.namespace, "entity", original_id)
            row.update(original_id=original_id, mapped_id=eid, fidelity="identity-mapped-original-source-retained")
            label = data.get("display_name", data.get("name", data.get("title", original_id)))
            entity_type = data.get("type", data.get("entity_type", "other"))
            entities[eid] = {"type": "entity", "id": eid, "entity_type": str(entity_type), "label": str(label)}
            owners.setdefault(eid, []).append(row)
        elif category in {"encrypted", "quarantine", "tombstone", "opaque"}:
            row.update(status="quarantined" if category == "quarantine" else "preserved-only",
                       reason={"encrypted": "ciphertext-unavailable-not-decrypted", "quarantine": "quarantined-source",
                               "tombstone": "legacy-tombstone-not-an-affirmed-claim", "opaque": "unrecognized-semantic-shape"}[category])
    for row, category, data in classifications:
        if row["status"] != "planned" or category == "entity":
            continue
        file = plan.files[row["file_index"]]
        evidence = file_sources.get(row["file_index"], [])
        if not evidence:
            row.update(status="unsupported", reason="source-evidence-unavailable")
            continue
        if category == "note":
            original_id = f"document:{file['relative_path']}"
            eid = mapped_id(plan.namespace, "entity", original_id)
            entities[eid] = {"type": "entity", "id": eid, "entity_type": "source-document", "label": file["relative_path"]}
            aid = mapped_id(plan.namespace, "assertion", _json([original_id, file["sha256"]]))
            # Current imported content heads only. Owner-authored corrections on
            # the same document are never silently designated import predecessors.
            prior = store.query(subject=eid, predicate="content", limit=1000).get("assertions", []) if _existing(store, "entity", eid) else []
            prior = [a["id"] for a in prior if a.get("provenance", {}).get("import_namespace") == plan.namespace and a["id"] != aid]
            action = {"type": "assertion", "id": aid, "subject": eid, "predicate": "content",
                      "value": data["_note"], "source_ids": evidence, "kind": "correct" if prior else "assert",
                      "predecessors": prior, "time_precision": "unknown",
                      "provenance": {"method": "source-text-import", "import_namespace": plan.namespace,
                                     "source_sha256": file["sha256"], "relative_path": file["relative_path"],
                                     "logseq_block_ids": re.findall(r"(?m)^\s*id::\s*(\S+)\s*$", data["_note"])}}
            if prior:
                action["reason"] = "Imported source text changed; previous source version remains available."
            row.update(original_id=original_id, mapped_id=aid, entity_id=eid, fidelity="verbatim-source-text")
        elif category in {"assertion", "edge"}:
            original_id = data.get("assertion_id", data.get("edge_id", data.get("_envelope_id")))
            subject = data.get("subject_entity_id", data.get("source_entity_id", data.get("source_object_id")))
            target = data.get("target_entity_id", data.get("target_object_id"))
            predicate = data.get("predicate")
            action_kind = data.get("lineage_action", "assert")
            if not all(isinstance(v, str) and v for v in [original_id, subject, predicate]) or action_kind not in ACTIONS:
                row.update(status="preserved-only", reason="unsupported-assertion-shape-or-action")
                continue
            if data.get("kind") in {"observation", "other"}:
                row.update(status="preserved-only", reason="unresolved-observation-not-promoted")
                continue
            sid = mapped_id(plan.namespace, "entity", subject)
            oid = mapped_id(plan.namespace, "entity", target) if isinstance(target, str) else None
            if (sid not in entities and not _existing(store, "entity", sid)) or (oid and oid not in entities and not _existing(store, "entity", oid)):
                row.update(status="preserved-only", reason="missing-referenced-entity")
                continue
            aid = mapped_id(plan.namespace, "assertion", original_id)
            predecessors = data.get("supersedes", [])
            if not isinstance(predecessors, list) or any(not isinstance(p, str) for p in predecessors):
                row.update(status="preserved-only", reason="invalid-lineage")
                continue
            row.update(original_id=original_id, mapped_id=aid)
            action = {"type": "assertion", "id": aid, "subject": sid, "predicate": predicate,
                      "source_ids": evidence, "kind": action_kind,
                      "predecessors": [mapped_id(plan.namespace, "assertion", p) for p in predecessors],
                      "provenance": _provenance(row, file, data), "uncertainty": data.get("confidence", {"band": "unknown"})}
            if oid:
                action["object"] = oid
            elif "value" in data:
                action["value"] = data["value"]
            else:
                row.update(status="preserved-only", reason="missing-assertion-value")
                continue
            if action_kind != "assert":
                if not predecessors:
                    row.update(status="preserved-only", reason="missing-lineage-predecessors")
                    continue
                action["reason"] = "Preserved legacy semantic action; original reason/provenance remains in source."
            start, precision = _point(data.get("valid_from"))
            action["valid_from"] = start
            if "valid_to" in data:
                end, end_precision = _point(data["valid_to"])
                action["valid_to"] = end
                if end_precision in {"unknown", "approximate"}:
                    precision = end_precision
            action["time_precision"] = precision
            if action_kind == "invalidate" and action.get("valid_to") is None:
                row.update(status="preserved-only", reason="invalidation-end-not-representable")
                continue
            row["fidelity"] = "retained-claim-and-lineage; legacy-knowledge-time-is-metadata; original-evidence-not-resolved"
        else:
            continue
        previous = assertions.get(action["id"])
        semantic_fields = {"subject", "predicate", "value", "object", "kind", "predecessors", "valid_from", "valid_to", "time_precision", "uncertainty"}
        if previous is not None and any(previous.get(k) != action.get(k) for k in semantic_fields):
            row.update(status="failed", reason="duplicate-legacy-id-content-conflict")
            for earlier in owners.get(action["id"], []):
                earlier.update(status="failed", reason="duplicate-legacy-id-content-conflict")
            continue
        assertions.setdefault(action["id"], action)
        owners.setdefault(action["id"], []).append(row)
    # An immutable legacy ID with different bytes is a conflict, not a last-write
    # winner. Deduplicate identical source identities through the core contract.
    actions = []
    for table, kind in [(sources, "source"), (entities, "entity")]:
        for key, action in table.items():
            exists = _existing(store, kind, key)
            if exists:
                # Existing entity name/type snapshots remain evidence; identity
                # itself cannot be destructively overwritten by an import.
                for row in owners.get(key, []):
                    row.update(status="unchanged", reason="existing-identity")
            else:
                actions.append(action)
    remaining = dict(assertions)
    available = set()
    while remaining:
        ready = [key for key, a in remaining.items() if all(p in available or _existing(store, "assertion", p) for p in a.get("predecessors", []))]
        if not ready:
            for key in remaining:
                for row in owners.get(key, []):
                    row.update(status="preserved-only", reason="missing-or-cyclic-lineage")
            break
        for key in sorted(ready):
            action = remaining.pop(key)
            exists = _existing(store, "assertion", key)
            if exists:
                # Preserve an exact earlier import without needing its receipt
                # identity. Any changed immutable claim is detected explicitly.
                fields = {"subject", "predicate", "value", "object", "valid_from", "valid_to", "time_precision"}
                # Markdown unchanged versions may already be corrections. Their
                # content identity remains immutable; do not recreate lineage.
                if action["predicate"] != "content":
                    fields.update({"kind", "predecessors", "uncertainty"})
                comparable = {k: exists.get(k) for k in fields}
                expected = {k: action.get(k) for k in fields}
                if comparable != expected:
                    for row in owners.get(key, []):
                        row.update(status="failed", reason="legacy-id-content-conflict")
                    continue
                for row in owners.get(key, []):
                    row.update(status="unchanged", reason="identical-existing-assertion")
            else:
                actions.append(action)
            available.add(key)
    if any(r["status"] == "failed" for r in rows):
        return _result(plan, rows, backup_path=None, batches=0, status="failed")
    if not actions:
        for row in rows:
            if row["status"] == "planned":
                row.update(status="unchanged", reason="no-new-semantic-actions")
        return _result(plan, rows, backup_path=None, batches=0, status="unchanged")
    # Separate planner and destination. Backup must precede every mutation.
    store.backup(str(backup_path))
    batches = 0
    pending = []
    pending_bytes = 0
    failed = False
    pause = None
    def flush() -> None:
        nonlocal pending, pending_bytes, batches, failed, pause
        if not pending or failed:
            return
        ids = [a["id"] for a in pending]
        request_id = "import:" + _hash(_json(pending))
        try:
            store.submit(pending, actor=import_actor, request_id=request_id)
        except Exception as exc:
            failed = True
            if isinstance(exc, CapacityError):
                pause = {"error": exc.code, "reason": exc.reason,
                         "retry_after_seconds": exc.retry_after_seconds}
            for action in pending:
                for row in owners.get(action["id"], []):
                    row.update(status="failed", reason=f"graph-rejected-{type(exc).__name__}")
        else:
            batches += 1
            for identifier in ids:
                for row in owners.get(identifier, []):
                    row.update(status="imported", reason="")
        pending = []
        pending_bytes = 0
    for action in actions:
        size = len(_json(action).encode("utf-8")) + 1
        if size > 900000:
            failed = True
            for row in owners.get(action["id"], []):
                row.update(status="failed", reason="record-operation-byte-limit")
            break
        if pending and (len(pending) >= 450 or pending_bytes + size > 900000):
            flush()
        if failed:
            break
        pending.append(action)
        pending_bytes += size
    flush()
    for row in rows:
        if row["status"] == "planned":
            row.update(status="failed", reason="not-applied-after-batch-failure" if failed else "no-semantic-mapping")
    report = _result(plan, rows, backup_path=str(backup_path), batches=batches,
                     status="partial" if failed and batches else "failed" if failed else "complete")
    if pause is not None:
        report["pause"] = pause
    return report


def _result(plan: ImportPlan, rows: list[dict], *, backup_path: str | None, batches: int, status: str) -> dict:
    report = ImportPlan(plan.root, plan.namespace, plan.files, rows, plan.max_file_bytes).summary()
    metadata_only = {"commit-metadata", "log-control-metadata", "legacy-control-or-identity-metadata"}
    gaps = [r for r in rows if r["status"] in {"failed", "unsupported", "quarantined"}
            or r["status"] == "preserved-only" and r.get("reason") not in metadata_only
            or "original-evidence-not-resolved" in r.get("fidelity", "")]
    report.update(dry_run=False, status=status, semantic_complete=not gaps, fidelity_gap_count=len(gaps),
                  original_evidence_resolution="not-qualified; original records and evidence IDs retained",
                  backup_path=backup_path, committed_batches=batches,
                  rollback="Restore backup into a fresh isolated destination; originals are unchanged.")
    return report


def import_path(store: Any, path: str | Path, *, approved_root: str | Path,
                namespace: str = "personal-import", actor: dict | None = None,
                dry_run: bool = True, backup_path: str | Path | None = None) -> dict:
    plan = plan_import(path, approved_root=approved_root, namespace=namespace)
    return plan.summary() if dry_run else apply_import(store, plan, actor=actor, backup_path=backup_path)
