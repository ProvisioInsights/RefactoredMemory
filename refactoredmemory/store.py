"""Transactional temporal graph and authenticated direct-peer operation journal.

Network callers must use Service. Store's actor argument is a trusted, in-process
boundary used by local administration and already authenticated adapters.
"""
from __future__ import annotations

import contextlib
import datetime as dt
import errno
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
import threading
import tempfile
import uuid
from . import knowledge

MAX_OPERATION = 1024 * 1024
MAX_ACTIONS = 500
MAX_TEXT = 65536
SCHEMA = 1
KNOWLEDGE_WRITER_GATE_SQL = """CREATE TRIGGER knowledge_writer_gate
            BEFORE INSERT ON operations BEGIN
            SELECT CASE WHEN refmem_knowledge_writer_profile() != 'refactoredmemory.knowledge:v1'
            THEN RAISE(ABORT,'Reconnect with a knowledge-profile-aware writer') END;
            END"""


class MemoryError(Exception):
    """Expected store error; contains no credential or raw input payload."""


class ValidationError(MemoryError, ValueError):
    pass


class AuthorizationError(MemoryError, PermissionError):
    pass


class ConflictError(MemoryError, ValueError):
    pass


class CapacityError(MemoryError):
    """A retryable local storage pause; no operation was acknowledged."""

    code = "capacity_paused"
    retry_after_seconds = 300

    def __init__(self, reason="low_disk"):
        self.reason = reason
        super().__init__("Storage capacity pause: " + reason)


def canonical(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValidationError("Value must be finite, bounded JSON") from exc


def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def timestamp(value):
    if not isinstance(value, str) or len(value) > 64:
        raise ValidationError("Invalid time value")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if len(value) == 10:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        if parsed.tzinfo is None:
            raise ValueError("Timezone required")
        return parsed.astimezone(dt.timezone.utc)
    except ValueError as exc:
        raise ValidationError("Time must be an ISO date or timestamp with timezone") from exc


def identifier(value, label="identifier"):
    if not isinstance(value, str) or not value or len(value) > 256 or any(ord(c) < 32 for c in value):
        raise ValidationError(f"Invalid {label}")
    return value


def bounded_json(value, depth=0):
    if depth > 16:
        raise ValidationError("JSON nesting exceeds limit")
    if isinstance(value, str) and len(value.encode()) > MAX_TEXT:
        raise ValidationError("Text exceeds 64 KiB limit")
    if isinstance(value, dict):
        if len(value) > 1000:
            raise ValidationError("Object exceeds field limit")
        for k, v in value.items():
            if not isinstance(k, str):
                raise ValidationError("JSON keys must be strings")
            bounded_json(k, depth + 1)
            bounded_json(v, depth + 1)
    elif isinstance(value, list):
        if len(value) > 2000:
            raise ValidationError("Array exceeds limit")
        for item in value:
            bounded_json(item, depth + 1)
    canonical(value)


class Store:
    def __init__(self, path, *, store_id=None, peer_id=None):
        self.path = str(path)
        self._lock = threading.RLock()
        self._min_free_bytes = 0
        self._max_store_bytes = None
        if self.path != ":memory:":
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists():
                fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                os.close(fd)
        self.db = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False, timeout=30)
        self.db.row_factory = sqlite3.Row
        # Connection-local capability: older already-open writers do not know
        # this function and therefore fail closed once the policy is enabled.
        self.db.create_function("refmem_knowledge_writer_profile", 0,
                                lambda: knowledge.PROFILE, deterministic=True)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS operations(
            id TEXT PRIMARY KEY,origin TEXT NOT NULL,seq INTEGER NOT NULL,
            body TEXT NOT NULL,signature TEXT NOT NULL,received_at TEXT NOT NULL,
            position INTEGER UNIQUE,applied_at TEXT,rejected TEXT,
            UNIQUE(origin,seq));
        CREATE INDEX IF NOT EXISTS operations_position ON operations(position);
        CREATE INDEX IF NOT EXISTS operations_attribution ON operations(id,origin,seq,position);
        CREATE INDEX IF NOT EXISTS operations_metadata ON operations(position,rejected,origin,seq,id);
        CREATE TABLE IF NOT EXISTS records(
            kind TEXT NOT NULL,id TEXT NOT NULL,body TEXT NOT NULL,
            operation_id TEXT NOT NULL,subject TEXT,predicate TEXT,object TEXT,
            PRIMARY KEY(kind,id));
        CREATE TABLE IF NOT EXISTS record_events(
            kind TEXT NOT NULL,id TEXT NOT NULL,operation_id TEXT NOT NULL,
            PRIMARY KEY(kind,id,operation_id));
        INSERT OR IGNORE INTO record_events SELECT kind,id,operation_id FROM records;
        CREATE INDEX IF NOT EXISTS records_lookup ON records(kind,subject,predicate);
        CREATE INDEX IF NOT EXISTS records_object ON records(kind,object);
        CREATE TABLE IF NOT EXISTS requests(
            actor TEXT NOT NULL,id TEXT NOT NULL,digest TEXT NOT NULL,operation_id TEXT NOT NULL,
            PRIMARY KEY(actor,id));
        CREATE TABLE IF NOT EXISTS peers(id TEXT PRIMARY KEY,key TEXT NOT NULL,active INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS inherited_receipts(
            operation_id TEXT NOT NULL,replica TEXT NOT NULL,position INTEGER,
            received_at TEXT NOT NULL,applied_at TEXT,restored_at TEXT NOT NULL,
            PRIMARY KEY(operation_id,replica,restored_at));
        CREATE TABLE IF NOT EXISTS recovery_origins(
            sender TEXT NOT NULL,origin TEXT NOT NULL,key TEXT NOT NULL,PRIMARY KEY(sender,origin));
        CREATE TABLE IF NOT EXISTS grants(
            digest TEXT PRIMARY KEY,id TEXT NOT NULL,label TEXT NOT NULL,kind TEXT NOT NULL,
            scopes TEXT NOT NULL,peer_id TEXT,active INTEGER NOT NULL);
        """)
        with self._transaction():
            if self._meta("schema") is None:
                for key, value in {"schema": str(SCHEMA), "store_id": store_id or str(uuid.uuid4()),
                                   "peer_id": peer_id or str(uuid.uuid4()), "key_hex": secrets.token_hex(32),
                                   "position": "0"}.items():
                    self._setmeta(key, value)
            if self._meta("schema") != str(SCHEMA):
                raise ValidationError("Unsupported store schema")
            if store_id is not None and store_id != self._meta("store_id"):
                raise ConflictError("Store identity mismatch")
            if peer_id is not None and peer_id != self._meta("peer_id"):
                raise ConflictError("Peer identity mismatch")
            self.store_id = self._meta("store_id")
            self.peer_id = self._meta("peer_id")
            identifier(self.store_id)
            identifier(self.peer_id)
            if self._meta("knowledge_profile_cutoff"):
                self._ensure_knowledge_writer_gate()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        with self._lock:
            self.db.close()

    def configure_capacity(self, *, min_free_bytes=0, max_store_bytes=None):
        """Enable conservative graph-write admission without disabling reads.

        The ceiling measures allocated SQLite pages, not backup/log file size.
        Free-space checks reserve space for WAL/index growth. Other processes
        can still consume the disk after admission; SQLite failures roll back.
        """
        for value in (min_free_bytes, max_store_bytes):
            if value is not None and (type(value) is not int or value < 0):
                raise ValidationError("Capacity limits must be nonnegative byte counts")
        if min_free_bytes is None or max_store_bytes == 0:
            raise ValidationError("Invalid capacity limits")
        with self._lock:
            self._min_free_bytes = min_free_bytes
            self._max_store_bytes = max_store_bytes

    def _check_capacity(self, incoming_bytes=0, action_count=0):
        if not self._min_free_bytes and self._max_store_bytes is None:
            return
        # Conservative allowance for journal, projection, B-tree pages and WAL.
        reserve = 4 * incoming_bytes + 512 * action_count + (65536 if incoming_bytes else 0)
        if self._min_free_bytes and self.path != ":memory:":
            free = shutil.disk_usage(Path(self.path).resolve().parent).free
            if free < self._min_free_bytes + reserve:
                raise CapacityError("low_disk")
        if self._max_store_bytes is not None:
            allocated = self.db.execute("PRAGMA page_count").fetchone()[0] * self.db.execute("PRAGMA page_size").fetchone()[0]
            if allocated + reserve > self._max_store_bytes:
                raise CapacityError("store_limit")

    @contextlib.contextmanager
    def _transaction(self):
        with self._lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                yield
                self.db.execute("COMMIT")
            except BaseException as exc:
                # SQLITE_FULL may already have rolled back the transaction.
                if self.db.in_transaction:
                    self.db.execute("ROLLBACK")
                if isinstance(exc, sqlite3.OperationalError) and getattr(exc, "sqlite_errorcode", None) == sqlite3.SQLITE_FULL:
                    raise CapacityError("low_disk") from exc
                raise

    def _meta(self, key):
        row = self.db.execute("SELECT value FROM metadata WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    def _setmeta(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)", (key, str(value)))

    def identity(self):
        with self._lock:
            return {"store_id": self.store_id, "peer_id": self.peer_id, "key_hex": self._meta("key_hex")}

    def admit_peer(self, peer_id, key_hex):
        identifier(peer_id)
        try:
            valid = isinstance(key_hex, str) and len(key_hex) == 64 and len(bytes.fromhex(key_hex)) == 32
        except ValueError:
            valid = False
        if not valid or peer_id == self.peer_id:
            raise ValidationError("Invalid peer identity or key")
        with self._transaction():
            old = self.db.execute("SELECT key FROM peers WHERE id=?", (peer_id,)).fetchone()
            if old and not hmac.compare_digest(old[0], key_hex):
                raise ConflictError("Peer key changed; use a fresh peer identity")
            self.db.execute("INSERT OR REPLACE INTO peers VALUES (?,?,1)", (peer_id, key_hex))

    def admit_recovery_origin(self, sender, origin, key_hex):
        """Local-only permission for a restored peer to forward a named old origin."""
        identifier(sender)
        identifier(origin)
        try:
            if len(key_hex) != 64 or len(bytes.fromhex(key_hex)) != 32:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValidationError("Invalid recovery verification key")
        with self._transaction():
            row = self.db.execute("SELECT active FROM peers WHERE id=?", (sender,)).fetchone()
            if not row or not row[0] or origin == self.peer_id:
                raise AuthorizationError("Recovery sender must be admitted; local origin cannot be delegated")
            self.db.execute("INSERT OR REPLACE INTO recovery_origins VALUES (?,?,?)", (sender, origin, key_hex))

    def revoke_peer(self, peer_id):
        with self._transaction():
            self.db.execute("UPDATE peers SET active=0 WHERE id=?", (peer_id,))
            self.db.execute("UPDATE grants SET active=0 WHERE peer_id=?", (peer_id,))

    def create_grant(self, label, scopes, *, kind="agent", peer_id=None):
        identifier(label, "grant label")
        if not isinstance(scopes, (list, tuple, set)) or not scopes or not set(scopes) <= {"read", "write", "correct", "admin", "sync"}:
            raise ValidationError("Invalid grant scopes")
        if kind not in {"owner", "agent", "peer"}:
            raise ValidationError("Invalid grant kind")
        if kind != "owner" and "admin" in scopes:
            raise ValidationError("Administrative grants require owner kind")
        if kind == "peer":
            if set(scopes) != {"sync"} or not peer_id:
                raise ValidationError("Peer grants require sync-only scope and an admitted peer")
            row = self.db.execute("SELECT active FROM peers WHERE id=?", (peer_id,)).fetchone()
            if not row or not row[0]:
                raise AuthorizationError("Peer is not admitted")
        elif peer_id is not None or "sync" in scopes:
            raise ValidationError("Sync grants require a peer binding")
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).hexdigest()
        with self._transaction():
            self.db.execute("INSERT INTO grants VALUES (?,?,?,?,?,?,1)",
                            (digest, str(uuid.uuid4()), label, kind, canonical(sorted(set(scopes))), peer_id))
        return token

    def authenticate(self, token, scope=None):
        if not isinstance(token, str) or len(token) > 1024:
            raise AuthorizationError("Access denied")
        digest = hashlib.sha256(token.encode()).hexdigest()
        with self._lock:
            row = self.db.execute("SELECT * FROM grants WHERE digest=? AND active=1", (digest,)).fetchone()
            if not row:
                raise AuthorizationError("Access denied")
            scopes = json.loads(row["scopes"])
            if scope and scope not in scopes:
                raise AuthorizationError("Access denied")
            if row["peer_id"]:
                peer = self.db.execute("SELECT active FROM peers WHERE id=?", (row["peer_id"],)).fetchone()
                if not peer or not peer[0]:
                    raise AuthorizationError("Access denied")
            return {"id": row["id"], "kind": row["kind"], "scopes": scopes, "peer_id": row["peer_id"]}

    def revoke_grant(self, token):
        with self._transaction():
            self.db.execute("UPDATE grants SET active=0 WHERE digest=?", (hashlib.sha256(token.encode()).hexdigest(),))

    def _frontier(self, position=None):
        sql = "SELECT origin,MAX(seq) AS seq FROM operations INDEXED BY operations_metadata WHERE position IS NOT NULL"
        args = []
        if position is not None:
            sql += " AND position<=?"
            args.append(position)
        return {r["origin"]: r["seq"] for r in self.db.execute(sql + " GROUP BY origin", args)}

    def _actor(self, actor):
        actor = actor or {"id": "owner", "kind": "owner"}
        if not isinstance(actor, dict) or actor.get("kind") not in {"owner", "agent"}:
            raise ValidationError("Invalid submitting actor")
        identifier(actor.get("id"), "actor")
        return {"id": actor["id"], "kind": actor["kind"]}

    def _validate_actions(self, actions):
        if not isinstance(actions, list) or not 1 <= len(actions) <= MAX_ACTIONS:
            raise ValidationError("Operation needs 1–500 actions")
        bounded_json(actions)
        if len(canonical(actions).encode()) > MAX_OPERATION - 4096:
            raise ValidationError("Operation exceeds 1 MiB")
        seen = set()
        fields = {
            "entity": {"type", "id", "entity_type", "label"},
            "source": {"type", "id", "uri", "content", "metadata"},
            "assertion": {"type", "id", "subject", "predicate", "value", "object", "source_ids", "kind",
                          "predecessors", "reason", "valid_from", "valid_to", "time_precision", "provenance", "uncertainty"},
            "delete": {"type", "id", "entity_id", "reason"},
            "restore": {"type", "id", "entity_id", "predecessors", "reason"},
        }
        for action in actions:
            if not isinstance(action, dict) or action.get("type") not in fields:
                raise ValidationError("Unknown action type")
            kind = action["type"]
            if set(action) - fields[kind]:
                raise ValidationError("Unknown action fields")
            identifier(action.get("id"))
            if action["id"] in seen:
                raise ValidationError("Duplicate action ID in group")
            seen.add(action["id"])
            if kind == "entity":
                identifier(action.get("entity_type"), "entity type")
                if not isinstance(action.get("label"), str):
                    raise ValidationError("Entity label must be text")
            elif kind == "source":
                if not isinstance(action.get("uri"), str) or not isinstance(action.get("content"), str):
                    raise ValidationError("Source URI and content must be text")
                if not isinstance(action.get("metadata", {}), dict):
                    raise ValidationError("Source metadata must be an object")
            elif kind == "assertion":
                identifier(action.get("subject"), "subject")
                identifier(action.get("predicate"), "predicate")
                if ("value" in action) == ("object" in action):
                    raise ValidationError("Assertion requires exactly one of value or object")
                if "object" in action:
                    identifier(action["object"], "object")
                action_kind = action.get("kind", "assert")
                if action_kind not in {"assert", "correct", "retract", "invalidate", "reinstate"}:
                    raise ValidationError("Unknown assertion action")
                for key in ("source_ids", "predecessors"):
                    values = action.get(key, [])
                    if not isinstance(values, list) or len(values) > 100 or any(not isinstance(v, str) for v in values) or len(values) != len(set(values)):
                        raise ValidationError("Invalid reference list")
                    for value in values:
                        identifier(value)
                if not action.get("source_ids"):
                    raise ValidationError("Assertions require evidence")
                if "reason" in action and not isinstance(action["reason"], str):
                    raise ValidationError("Assertion reason must be text")
                if action_kind != "assert" and (not action.get("predecessors") or not action.get("reason")):
                    raise ValidationError("Semantic actions require predecessors and a reason")
                if action_kind == "assert" and action.get("predecessors"):
                    raise ValidationError("Initial assertions cannot supersede earlier claims")
                for key in ("valid_from", "valid_to"):
                    if action.get(key) is not None:
                        timestamp(action[key])
                if action.get("valid_from") is not None and action.get("valid_to") is not None:
                    if timestamp(action["valid_from"]) >= timestamp(action["valid_to"]):
                        raise ValidationError("World interval must be nonempty and half-open")
                if action_kind == "invalidate" and action.get("valid_to") is None:
                    raise ValidationError("Invalidation requires the explicit world-time ending")
                if action.get("time_precision", "exact") not in {"exact", "day", "approximate", "unknown"}:
                    raise ValidationError("Unsupported time precision")
                if not isinstance(action.get("provenance", {}), dict):
                    raise ValidationError("Provenance must be an object")
                try:
                    knowledge.validate_annotation(action)
                except ValueError as exc:
                    raise ValidationError(str(exc)) from exc
            else:
                identifier(action.get("entity_id"), "entity")
                if not isinstance(action.get("reason"), str) or not action["reason"]:
                    raise ValidationError("Administrative actions require reason")
                if kind == "restore":
                    preds = action.get("predecessors")
                    if not isinstance(preds, list) or not preds or len(preds) > 100:
                        raise ValidationError("Restore must name deletion actions")
                    for pred in preds:
                        identifier(pred)

    def read(self, kind, id):
        with self._lock:
            row = self.db.execute("SELECT body FROM records WHERE kind=? AND id=?", (kind, id)).fetchone()
            return json.loads(row[0]) if row else None

    def _reference_visible(self, kind, id, frontier):
        rows = self.db.execute("SELECT o.origin,o.seq FROM record_events e JOIN operations o INDEXED BY operations_attribution ON o.id=e.operation_id WHERE e.kind=? AND e.id=? AND o.position IS NOT NULL", (kind, id))
        return any(row["seq"] <= frontier.get(row["origin"], 0) for row in rows)

    def _check_dependencies(self, body):
        deps = body["dependencies"]
        for origin, seq in deps.items():
            if seq == 0:
                continue
            row = self.db.execute("SELECT body FROM operations WHERE origin=? AND seq=? AND position IS NOT NULL", (origin, seq)).fetchone()
            if row is None:
                raise ValidationError("Missing causal dependency")
            previous = json.loads(row[0])
            if any(deps.get(k, 0) < v for k, v in previous["dependencies"].items()):
                raise ValidationError("Operation dependencies are not causally closed")

    def _apply(self, body, position):
        self._check_dependencies(body)
        actions = body["actions"]
        # Topologically order all intra-group references, independent of wire order.
        ordered, remaining, available = [], list(actions), set()
        while remaining:
            progress = False
            for action in remaining[:]:
                refs = []
                if action["type"] == "assertion":
                    refs = [("entity", action["subject"])]
                    if "object" in action:
                        refs.append(("entity", action["object"]))
                    refs += [("source", x) for x in action["source_ids"]]
                    refs += [("assertion", x) for x in action.get("predecessors", [])]
                elif action["type"] in {"delete", "restore"}:
                    refs = [("entity", action["entity_id"])]
                    refs += [("delete", x) for x in action.get("predecessors", [])]
                if all(ref in available or self._reference_visible(*ref, body["dependencies"]) for ref in refs):
                    ordered.append(action)
                    remaining.remove(action)
                    available.add((action["type"], action["id"]))
                    progress = True
            if not progress:
                raise ValidationError("Missing or cyclic action dependency")
        cutoff = json.loads(self._meta("knowledge_profile_cutoff") or "null")
        strict = cutoff is not None and body["seq"] > cutoff.get(body["origin"], 0)
        canonical_type_cache = {}
        def canonical_types(entity_id):
            if entity_id not in canonical_type_cache:
                canonical_type_cache[entity_id] = self._canonical_types(entity_id, body["dependencies"])
            return canonical_type_cache[entity_id]
        for action in ordered:
            kind, id = action["type"], action["id"]
            old = self.read(kind, id)
            if old is not None:
                if old != action:
                    raise ConflictError("Immutable record ID has different contents")
                self.db.execute("INSERT OR IGNORE INTO record_events VALUES (?,?,?)", (kind, id, body["id"]))
                continue
            if strict and kind == "entity" and action["entity_type"] not in (*knowledge.ENDPOINT_TYPES, "source-document"):
                raise ValidationError("New entities require a canonical type; inspect memory_schema")
            if strict and kind == "assertion" and action["predicate"] != "content" and knowledge.annotation(action) is None:
                raise ValidationError("New structured claims require the knowledge profile; inspect memory_schema")
            if kind == "assertion":
                for entity in [action["subject"]] + ([action["object"]] if "object" in action else []):
                    if self.read("entity", entity) is None:
                        raise ValidationError("Missing entity dependency")
                for source in action["source_ids"]:
                    if self.read("source", source) is None:
                        raise ValidationError("Missing evidence dependency")
                for pred in action.get("predecessors", []):
                    previous = self.read("assertion", pred)
                    if previous is None:
                        raise ValidationError("Missing assertion predecessor")
                    if (previous["subject"], previous["predicate"]) != (action["subject"], action["predicate"]):
                        raise ValidationError("A correction cannot move a claim to another subject or predicate")
                if knowledge.annotation(action) is not None and "object" in action:
                    try:
                        knowledge.validate_endpoints(action,
                            canonical_types(action["subject"]), canonical_types(action["object"]))
                    except ValueError as exc:
                        raise ValidationError(str(exc)) from exc
            elif kind in {"delete", "restore"}:
                if self.read("entity", action["entity_id"]) is None:
                    raise ValidationError("Missing entity dependency")
                for pred in action.get("predecessors", []):
                    previous = self.read("delete", pred)
                    if previous is None or previous["entity_id"] != action["entity_id"]:
                        raise ValidationError("Restore must name matching deletion actions")
                if body["actor"]["kind"] != "owner":
                    raise AuthorizationError("Administrative actions require owner authority")
            self.db.execute("INSERT INTO records VALUES (?,?,?,?,?,?,?)", (kind, id, canonical(action), body["id"],
                            action.get("subject"), action.get("predicate"), action.get("object")))
            self.db.execute("INSERT OR IGNORE INTO record_events VALUES (?,?,?)", (kind, id, body["id"]))
        self.db.execute("UPDATE operations SET position=?,applied_at=? WHERE id=?", (position, utcnow(), body["id"]))
        self._setmeta("position", position)

    def submit(self, actions, *, actor=None, request_id=None):
        self._validate_actions(actions)
        actor = self._actor(actor)
        if request_id is not None:
            identifier(request_id, "request ID")
        digest = hashlib.sha256(canonical(actions).encode()).hexdigest()
        with self._transaction():
            if request_id:
                old = self.db.execute("SELECT * FROM requests WHERE actor=? AND id=?", (actor["id"], request_id)).fetchone()
                if old:
                    if old["digest"] != digest:
                        raise ConflictError("Request ID reused with different contents")
                    row = self.db.execute("SELECT position FROM operations WHERE id=?", (old["operation_id"],)).fetchone()
                    return {"operation_id": old["operation_id"], "known_position": row[0],
                            "action_ids": [a["id"] for a in actions], "duplicate": True}
            frontier = self._frontier()
            seq = frontier.get(self.peer_id, 0) + 1
            body = {"schema": SCHEMA, "id": f"{self.peer_id}:{seq}", "store_id": self.store_id,
                    "origin": self.peer_id, "seq": seq, "dependencies": frontier,
                    "actor": actor, "created_at": utcnow(), "actions": actions}
            encoded = canonical(body)
            if len(encoded.encode()) > MAX_OPERATION:
                raise ValidationError("Operation exceeds 1 MiB")
            self._check_capacity(len(encoded.encode()), len(actions))
            signature = hmac.new(bytes.fromhex(self._meta("key_hex")), encoded.encode(), hashlib.sha256).hexdigest()
            self.db.execute("INSERT INTO operations(id,origin,seq,body,signature,received_at) VALUES (?,?,?,?,?,?)",
                            (body["id"], self.peer_id, seq, encoded, signature, utcnow()))
            position = int(self._meta("position")) + 1
            self._apply(body, position)
            if request_id:
                self.db.execute("INSERT INTO requests VALUES (?,?,?,?)", (actor["id"], request_id, digest, body["id"]))
            self._check_capacity()
            return {"operation_id": body["id"], "known_position": position,
                    "action_ids": [a["id"] for a in actions], "duplicate": False}

    def _wire(self, row):
        body = json.loads(row["body"])
        return {**body, "signature": row["signature"]}

    def export_operations(self, frontier=None, limit=100):
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValidationError("Export limit must be 1–1000")
        frontier = frontier or {}
        self._validate_frontier_shape(frontier)
        with self._lock:
            found = []
            total_bytes = 0
            more = False
            # Read small covering metadata first. Acknowledged journals can be
            # nearly 1 MiB each; copying that prefix on every batch scales badly.
            for metadata in self.db.execute("SELECT id,origin,seq FROM operations INDEXED BY operations_metadata WHERE position IS NOT NULL ORDER BY position"):
                if metadata["seq"] <= frontier.get(metadata["origin"], 0):
                    continue
                if len(found) >= limit:
                    more = True
                    break
                row = self.db.execute("SELECT body,signature FROM operations WHERE id=?", (metadata["id"],)).fetchone()
                if found and total_bytes + len(row["body"].encode()) > 2 * MAX_OPERATION:
                    more = True
                    break
                found.append(self._wire(row))
                total_bytes += len(row["body"].encode())
            return {"operations": found, "frontier": self._frontier(), "more": more}

    def _validate_frontier_shape(self, frontier):
        if not isinstance(frontier, dict) or len(frontier) > 64:
            raise ValidationError("Invalid causal frontier")
        for origin, seq in frontier.items():
            identifier(origin, "origin")
            if not isinstance(seq, int) or isinstance(seq, bool) or seq < 0 or seq > 2**53 - 1:
                raise ValidationError("Invalid causal position")

    def receive(self, operations, peer_id):
        if not isinstance(operations, list) or len(operations) > 1000 or len(canonical(operations).encode()) > 4 * MAX_OPERATION:
            raise ValidationError("Replication batch exceeds limit")
        with self._transaction():
            peer = self.db.execute("SELECT * FROM peers WHERE id=? AND active=1", (peer_id,)).fetchone()
            if not peer:
                raise AuthorizationError("Peer is not admitted")
            received = applied = 0
            for wire in operations:
                if not isinstance(wire, dict) or set(wire) != {"schema", "id", "store_id", "origin", "seq", "dependencies", "actor", "created_at", "actions", "signature"}:
                    raise ValidationError("Invalid operation envelope")
                body = {k: v for k, v in wire.items() if k != "signature"}
                encoded = canonical(body)
                if len(encoded.encode()) > MAX_OPERATION:
                    raise ValidationError("Operation exceeds limit")
                if body["schema"] != SCHEMA or body["store_id"] != self.store_id:
                    raise ValidationError("Unsupported schema or foreign store")
                self._validate_frontier_shape(body["dependencies"])
                identifier(body["origin"])
                seq = body["seq"]
                if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1 or seq > 2**53 - 1 or body["id"] != f'{body["origin"]}:{seq}':
                    raise ValidationError("Invalid origin sequence")
                if body["dependencies"].get(body["origin"], 0) != seq - 1:
                    raise ValidationError("Origin predecessor sequence missing")
                if not isinstance(body["actor"], dict) or set(body["actor"]) != {"id", "kind"}:
                    raise ValidationError("Invalid actor envelope")
                self._actor(body["actor"])
                timestamp(body["created_at"])
                self._validate_actions(body["actions"])
                old = self.db.execute("SELECT * FROM operations WHERE id=?", (body["id"],)).fetchone()
                if old:
                    if old["body"] != encoded or old["signature"] != wire["signature"]:
                        raise ConflictError("Conflicting operation identity or cloned origin")
                    continue
                # Forwarding an old origin requires an explicit local recovery grant.
                key = peer["key"]
                if body["origin"] != peer_id:
                    recovery = self.db.execute("SELECT key FROM recovery_origins WHERE sender=? AND origin=?", (peer_id, body["origin"])).fetchone()
                    if not recovery:
                        raise AuthorizationError("Direct sync rejects an unadmitted origin")
                    key = recovery[0]
                expected = hmac.new(bytes.fromhex(key), encoded.encode(), hashlib.sha256).hexdigest()
                if not isinstance(wire["signature"], str) or not hmac.compare_digest(expected, wire["signature"]):
                    raise AuthorizationError("Invalid origin authentication")
                self._check_capacity(len(encoded.encode()), len(body["actions"]))
                self.db.execute("INSERT INTO operations(id,origin,seq,body,signature,received_at) VALUES (?,?,?,?,?,?)",
                                (body["id"], body["origin"], seq, encoded, wire["signature"], utcnow()))
                received += 1
            while True:
                progress = False
                frontier = self._frontier()
                pending = list(self.db.execute("SELECT * FROM operations WHERE position IS NULL AND rejected IS NULL ORDER BY origin,seq"))
                for row in pending:
                    body = json.loads(row["body"])
                    if any(frontier.get(origin, 0) < seq for origin, seq in body["dependencies"].items()):
                        continue
                    self._check_capacity(len(row["body"].encode()), len(body["actions"]))
                    # Savepoint prevents a malformed remote group exposing a partial projection.
                    self.db.execute("SAVEPOINT incoming")
                    try:
                        self._apply(body, int(self._meta("position")) + 1)
                    except MemoryError:
                        self.db.execute("ROLLBACK TO incoming")
                        self.db.execute("RELEASE incoming")
                        self.db.execute("UPDATE operations SET rejected='invalid_semantics' WHERE id=?", (body["id"],))
                        continue
                    self.db.execute("RELEASE incoming")
                    applied += 1
                    progress = True
                    frontier[body["origin"]] = body["seq"]
                if not progress:
                    break
            if received or applied:
                self._check_capacity()
            pending_count = self.db.execute("SELECT count(*) FROM operations WHERE position IS NULL").fetchone()[0]
            return {"received": received, "applied": applied, "pending": pending_count,
                    "rejected": self.db.execute("SELECT count(*) FROM operations INDEXED BY operations_metadata WHERE rejected IS NOT NULL").fetchone()[0], "frontier": self._frontier()}

    def _view(self, known_at=None, frontier=None):
        current = int(self._meta("position"))
        if known_at is not None and frontier is not None:
            raise ValidationError("Choose local knowledge position or causal frontier")
        if known_at is not None and (not isinstance(known_at, int) or isinstance(known_at, bool) or not 0 <= known_at <= current):
            raise ValidationError("Knowledge position is unavailable on this peer")
        if frontier is not None:
            self._validate_frontier_shape(frontier)
            have = self._frontier()
            if any(seq > have.get(origin, 0) for origin, seq in frontier.items()):
                raise ValidationError("Requested frontier is not available")
            for row in self.db.execute("SELECT origin,seq,body FROM operations WHERE position IS NOT NULL"):
                if row["seq"] <= frontier.get(row["origin"], 0):
                    deps = json.loads(row["body"])["dependencies"]
                    if any(frontier.get(k, 0) < v for k, v in deps.items()):
                        raise ValidationError("Requested frontier is not causally closed")
            return current, dict(frontier)
        position = current if known_at is None else known_at
        return position, self._frontier(position)

    def _deleted(self):
        deletes = {}
        restored = set()
        for row in self.db.execute("SELECT kind,id,body FROM records WHERE kind IN ('delete','restore')"):
            action = json.loads(row["body"])
            if row["kind"] == "delete":
                deletes[row["id"]] = action["entity_id"]
            else:
                restored.update(action["predecessors"])
        return {entity for id, entity in deletes.items() if id not in restored}

    def _rows(self, subject=None, predicate=None, object=None):
        # Cover journal metadata without revisiting large payload overflow pages.
        # Actor JSON is decoded once per operation by query(), after view filtering.
        # Start with the filtered record index. Without the explicit join order,
        # SQLite can start with every assertion's attribution and then fetch
        # large unrelated record bodies for each endpoint lookup.
        sql = "SELECT r.body,e.operation_id,o.origin,o.seq,o.position FROM records r CROSS JOIN record_events e ON e.kind=r.kind AND e.id=r.id JOIN operations o INDEXED BY operations_attribution ON o.id=e.operation_id WHERE r.kind='assertion'"
        args = []
        if subject is not None:
            identifier(subject, "subject")
            sql += " AND r.subject=?"
            args.append(subject)
        if predicate is not None:
            identifier(predicate, "predicate")
            sql += " AND r.predicate=?"
            args.append(predicate)
        if object is not None:
            identifier(object, "object")
            sql += " AND r.object=?"
            args.append(object)
        return self.db.execute(sql, args)

    def query(self, *, subject=None, predicate=None, object=None, text=None, valid_at=None,
              known_at=None, frontier=None, include_inactive=False, limit=100, offset=0,
              knowledge_kind=None, category=None, excerpt_chars=None):
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000 or not isinstance(offset, int) or isinstance(offset, bool) or not 0 <= offset <= 1000000:
            raise ValidationError("Invalid query bounds")
        if not isinstance(include_inactive, bool) or (text is not None and (not isinstance(text, str) or len(text) > 1024)):
            raise ValidationError("Invalid query filter")
        if knowledge_kind is not None and knowledge_kind not in knowledge.KINDS:
            raise ValidationError("Invalid knowledge kind filter")
        if category is not None and category not in knowledge.CATEGORIES:
            raise ValidationError("Invalid knowledge category filter")
        if excerpt_chars is not None and (not isinstance(excerpt_chars, int) or isinstance(excerpt_chars, bool) or not 100 <= excerpt_chars <= 4096):
            raise ValidationError("Excerpt length must be between 100 and 4096")
        at = timestamp(valid_at) if valid_at is not None else None
        with self._lock:
            position, view = self._view(known_at, frontier)
            deleted = self._deleted()
            # Object/text filters are applied after lineage so they cannot resurrect old heads.
            rows = self._rows(subject, predicate)
            visible = {}
            occurrences = {}
            actor_metadata = {}
            metadata_fields = ("id", "subject", "predicate", "object", "kind", "predecessors",
                               "valid_from", "valid_to", "time_precision")
            folded_text = text.casefold() if text else None
            for row in rows:
                if row["seq"] > view.get(row["origin"], 0):
                    continue
                original = json.loads(row["body"])
                # Retain lineage and filter results, not every document's text.
                # Selected payloads are hydrated only after applying the limit.
                a = {key: original[key] for key in metadata_fields if key in original}
                semantics = knowledge.describe(original)
                a["_matches_knowledge"] = ((knowledge_kind is None or semantics["kind"] == knowledge_kind)
                    and (category is None or semantics.get("category") == category))
                a["_matches_text"] = folded_text is None or folded_text in canonical(
                    {key: original.get(key) for key in ("value", "predicate", "reason", "provenance")}).casefold()
                if row["operation_id"] not in actor_metadata:
                    actor_metadata[row["operation_id"]] = self.db.execute(
                        "SELECT json_extract(body,'$.actor') FROM operations WHERE id=?",
                        (row["operation_id"],)).fetchone()[0]
                actor = json.loads(actor_metadata[row["operation_id"]])
                occurrences.setdefault(a["id"], []).append({"actor": actor, "operation_id": row["operation_id"]})
                a.update(actor=actor, operation_id=row["operation_id"], known_position=row["position"])
                # All views deterministically choose the same origin among visible occurrences.
                # Preserve other submissions as attribution, never independent corroboration.
                if a["id"] not in visible or a["operation_id"] < visible[a["id"]]["operation_id"]:
                    visible[a["id"]] = a
            for id, a in visible.items():
                occurrences[id].sort(key=lambda item: item["operation_id"])
                a["attributions"] = occurrences[id]
                # Owner corrections keep authenticated owner authority regardless of reimport order.
                owners = [o for o in occurrences[id] if o["actor"]["kind"] == "owner"]
                if owners and a.get("kind") == "correct":
                    a["actor"] = owners[0]["actor"]
            superseded = set()
            children = {}
            for a in visible.values():
                for predecessor in a.get("predecessors", []):
                    children.setdefault(predecessor, []).append(a["id"])
                    previous = visible.get(predecessor)
                    # An inferred update cannot override the explicitly corrected owner belief.
                    if previous and previous.get("kind") == "correct" and previous["actor"]["kind"] == "owner" and a["actor"]["kind"] != "owner":
                        continue
                    superseded.add(predecessor)
            heads = [a for a in visible.values() if a["id"] not in superseded and a.get("kind", "assert") != "retract"
                     and a["subject"] not in deleted and a.get("object") not in deleted]
            owner_keys = {(a["subject"], a["predicate"]) for a in heads if a.get("kind") == "correct" and a["actor"]["kind"] == "owner"}
            grouped = {}
            for a in heads:
                grouped.setdefault((a["subject"], a["predicate"]), []).append(a)
            result = []
            unknown = 0
            for a in visible.values():
                if a["subject"] in deleted or a.get("object") in deleted:
                    continue
                a["status"] = "superseded" if a["id"] in superseded else ("retracted" if a.get("kind") == "retract" else "ended" if a.get("kind") == "invalidate" else "active")
                if not include_inactive and a["status"] in {"superseded", "retracted"}:
                    continue
                if object is not None and a.get("object") != object:
                    continue
                if at is not None:
                    if a.get("valid_from") is None or ("valid_to" in a and a["valid_to"] is None) or a.get("time_precision") in {"approximate", "unknown"}:
                        unknown += 1
                        continue
                    if at < timestamp(a["valid_from"]) or (a.get("valid_to") is not None and at >= timestamp(a["valid_to"])):
                        continue
                if not a["_matches_text"] or not a["_matches_knowledge"]:
                    continue
                key = (a["subject"], a["predicate"])
                a["preferred"] = key in owner_keys and a.get("kind") == "correct" and a["actor"]["kind"] == "owner" and a["id"] not in superseded
                a["conflicts"] = sorted({child for pred in a.get("predecessors", []) for child in children.get(pred, []) if child != a["id"]})
                a["human_verified"] = False
                result.append(a)
            result.sort(key=lambda a: a["id"])
            total = len(result)
            from functools import lru_cache
            @lru_cache(maxsize=32)
            def assertion_value(id):
                return self.read("assertion", id).get("value")
            selected = []
            for metadata in result[offset:offset + limit]:
                a = self.read("assertion", metadata["id"])
                for key in ("actor", "operation_id", "known_position", "attributions", "status",
                            "preferred", "conflicts", "human_verified"):
                    a[key] = metadata[key]
                a["alternatives"] = [other["id"] for other in grouped.get((a["subject"], a["predicate"]), [])
                                     if not knowledge.multi_valued(a["predicate"]) and other["id"] != a["id"] and (assertion_value(other["id"]), other.get("object")) != (a.get("value"), a.get("object"))]
                a["knowledge"] = knowledge.describe(a)
                if excerpt_chars is not None and a["predicate"] == "content" and isinstance(a.get("value"), str):
                    content = a.pop("value")
                    start, matched = knowledge.excerpt_offset(content, folded_text, excerpt_chars)
                    a["excerpt"] = content[start:start + excerpt_chars]
                    a["content_reference"] = {"characters": len(content), "offset": start,
                        "truncated": len(content) > len(a["excerpt"]), "source_ids": a["source_ids"], "match_in_content": matched}
                selected.append(a)
            return {"assertions": selected, "coverage": {"complete": total <= offset + limit and unknown == 0,
                    "has_more": total > offset + limit, "next_offset": offset + limit if total > offset + limit else None,
                    "matched": total, "excluded_unknown_time": unknown, "administrative_suppression": bool(deleted),
                    "pending_operations": self.db.execute("SELECT count(*) FROM operations WHERE position IS NULL").fetchone()[0],
                    "inherited_history": json.loads(self._meta("restored_from") or "null")},
                    "frontier": view, "known_position": position}

    def _canonical_types(self, entity_id, frontier=None):
        entity = self.read("entity", entity_id)
        if entity is None:
            return set()
        # The operation's dependencies were validated by _check_dependencies.
        # Resolve only this identity's type claims, never rescan the full journal
        # to validate that same causal frontier for every relationship endpoint.
        view = self._frontier() if frontier is None else frontier
        claims, owners = {}, set()
        for row in self._rows(entity_id, knowledge.TYPE_PREDICATE):
            if row["seq"] > view.get(row["origin"], 0):
                continue
            claim = json.loads(row["body"])
            claims[claim["id"]] = claim
            actor = self.db.execute("SELECT json_extract(body,'$.actor.kind') FROM operations WHERE id=?", (row["operation_id"],)).fetchone()[0]
            if actor == "owner" and claim.get("kind") == "correct":
                owners.add(claim["id"])
        superseded = {pred for claim in claims.values() for pred in claim.get("predecessors", [])
                      if pred not in owners or claim["id"] in owners}
        heads = [claim for id, claim in claims.items() if id not in superseded
                 and claim.get("kind", "assert") not in {"retract", "invalidate"}]
        preferred = [claim for claim in heads if claim["id"] in owners]
        values = {claim.get("value") for claim in preferred or heads if isinstance(claim.get("value"), str)}
        native_type = "observation" if entity["entity_type"] == "source-document" else entity["entity_type"]
        return values or ({native_type} if native_type in knowledge.ENDPOINT_TYPES else set())

    def enable_knowledge_profile(self):
        """Local operator policy: grandfather acknowledged history, validate new writes."""
        with self._transaction():
            if not self._meta("knowledge_profile_cutoff"):
                self._setmeta("knowledge_profile_cutoff", canonical(self._frontier()))
            self._ensure_knowledge_writer_gate()
            return self.knowledge_contract()

    def _ensure_knowledge_writer_gate(self):
        # The exact function/profile is controlled by this release, never input.
        # A persisted SQL trigger guards stale connections without killing them.
        row = self.db.execute("SELECT sql FROM sqlite_master WHERE type='trigger' AND name='knowledge_writer_gate'").fetchone()
        if row is None:
            self.db.execute(KNOWLEDGE_WRITER_GATE_SQL)
        elif row[0] != KNOWLEDGE_WRITER_GATE_SQL:
            raise ValidationError("Unexpected knowledge writer gate")

    def knowledge_contract(self):
        with self._lock:
            return {**knowledge.contract(), "enforcement": {
                "new_structured_writes": bool(self._meta("knowledge_profile_cutoff")),
                "legacy_history": "retained; not silently reclassified",
                "raw_document_capture": "observation; no inferred relationships"}}

    def get_entity(self, entity_id):
        with self._lock:
            entity = None if entity_id in self._deleted() else self.read("entity", entity_id)
            if entity is not None:
                types = sorted(self._canonical_types(entity_id))
                entity["classification"] = {"canonical_types": types, "ambiguous": len(types) > 1,
                    "original_entity_type": entity["entity_type"]}
            return entity

    def search_entities(self, text, *, limit=25):
        if not isinstance(text, str) or not text.strip() or len(text) > 256 or not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
            raise ValidationError("Invalid entity search")
        with self._lock:
            deleted = self._deleted()
            # Names find candidates; they never establish shared identity.
            matches, total = [], 0
            for row in self.db.execute("SELECT id,body FROM records WHERE kind='entity' ORDER BY id"):
                entity = json.loads(row["body"])
                if entity["id"] not in deleted and text.casefold() in entity["label"].casefold():
                    total += 1
                    if len(matches) < limit:
                        matches.append(entity)
            return {"entities": [self.get_entity(e["id"]) for e in matches],
                    "matched": total, "has_more": total > limit,
                    "identity_warning": "Matching names are candidates, not a merge decision."}

    def get_source(self, source_id):
        with self._lock:
            source = self.read("source", source_id)
            if source is None:
                return None
            deleted = self._deleted()
            if deleted:
                refs = [json.loads(r[0]) for r in self.db.execute("SELECT body FROM records WHERE kind='assertion'")]
                relevant = [a for a in refs if source_id in a.get("source_ids", [])]
                if relevant and not any(a["subject"] not in deleted and a.get("object") not in deleted for a in relevant):
                    return None
            return source

    def history(self, entity_id=None, *, since=None, known_at=None, limit=100):
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValidationError("Invalid history limit")
        if since is not None and (isinstance(since, bool) or not isinstance(since, (int, str))):
            raise ValidationError("Invalid history start")
        if isinstance(since, str):
            timestamp(since)
        with self._lock:
            position, view = self._view(known_at)
            deleted = self._deleted()
            operations = []
            if entity_id in deleted:
                return {"operations": [], "coverage": {"complete": False, "administrative_suppression": True}, "frontier": view, "known_position": position}
            for row in self.db.execute("SELECT * FROM operations WHERE position IS NOT NULL AND position<=? ORDER BY position", (position,)):
                if isinstance(since, int) and row["position"] <= since:
                    continue
                if isinstance(since, str) and timestamp(row["applied_at"]) <= timestamp(since):
                    continue
                body = json.loads(row["body"])
                actions = [a for a in body["actions"] if a.get("subject", a.get("entity_id", a["id"])) not in deleted and a.get("object") not in deleted]
                # Do not return raw source text through history; sources have a separate access path.
                actions = [a for a in actions if a["type"] != "source"]
                if entity_id is not None:
                    actions = [a for a in actions if entity_id in (a.get("subject"), a.get("object"), a.get("entity_id"), a["id"])]
                if not actions:
                    continue
                inherited = [dict(r) for r in self.db.execute("SELECT replica,position,received_at,applied_at,restored_at FROM inherited_receipts WHERE operation_id=? ORDER BY restored_at,replica", (row["id"],))]
                operations.append({**body, "actions": actions, "known_position": row["position"], "received_at": row["received_at"], "applied_at": row["applied_at"], "inherited_receipts": inherited})
                if len(operations) > limit:
                    break
            return {"operations": operations[:limit], "coverage": {"complete": len(operations) <= limit, "has_more": len(operations) > limit,
                    "administrative_suppression": bool(deleted)}, "frontier": view, "known_position": position}

    def traverse(self, start, *, depth=2, limit=100, valid_at=None, known_at=None, frontier=None):
        identifier(start)
        if not isinstance(depth, int) or isinstance(depth, bool) or not 0 <= depth <= 8 or not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValidationError("Traversal bounds exceeded")
        with self._lock:
            position, view = self._view(known_at, frontier)
            entity = self.get_entity(start)
            if entity:
                events = self.db.execute("SELECT o.origin,o.seq FROM record_events e JOIN operations o ON o.id=e.operation_id WHERE e.kind='entity' AND e.id=?", (start,))
                if not any(row["seq"] <= view.get(row["origin"], 0) for row in events):
                    entity = None
            seen = {start} if entity else set()
            queue = [start] if entity else []
            edges = {}
            complete = True
            unknown = 0
            for _ in range(depth):
                next_level = []
                for node in queue:
                    result = self.query(subject=node, valid_at=valid_at, frontier=view, limit=1000)
                    complete &= result["coverage"]["complete"]
                    unknown += result["coverage"]["excluded_unknown_time"]
                    for edge in result["assertions"]:
                        target = edge.get("object")
                        if not target:
                            continue
                        if len(edges) >= limit and edge["id"] not in edges:
                            complete = False
                            continue
                        edges[edge["id"]] = edge
                        if target not in seen:
                            if len(seen) >= limit:
                                complete = False
                                continue
                            seen.add(target)
                            next_level.append(target)
                queue = next_level
            return {"entities": [self.get_entity(x) for x in sorted(seen)], "edges": list(edges.values()),
                    "coverage": {"complete": bool(complete), "depth": depth, "excluded_unknown_time": unknown},
                    "frontier": view, "known_position": position}

    def _delete_edit_conflicts(self, limit=100):
        """Expose causal conflicts as IDs only, without returning suppressed content."""
        deleted = self._deleted()
        if not deleted:
            return {"items": [], "truncated": False}
        removals, edits, restored = [], [], set()
        operation_metadata = {}
        for row in self.db.execute("SELECT r.kind,r.body,o.id AS operation_id,o.origin,o.seq,json_extract(o.body,'$.dependencies') AS dependencies FROM records r JOIN record_events e ON e.kind=r.kind AND e.id=r.id JOIN operations o ON o.id=e.operation_id WHERE r.kind IN ('delete','restore','assertion')"):
            action = json.loads(row["body"])
            # Causal comparison needs identity and dependencies, never source
            # content or every other action in the signed operation. Share even
            # this small metadata across all occurrences in the same operation.
            operation = operation_metadata.get(row["operation_id"])
            if operation is None:
                operation = {"id": row["operation_id"], "origin": row["origin"],
                             "seq": row["seq"], "dependencies": json.loads(row["dependencies"])}
                operation_metadata[row["operation_id"]] = operation
            if action["type"] == "restore":
                restored.update(action["predecessors"])
            elif action["type"] == "delete":
                removals.append((action, operation))
            elif action["subject"] in deleted or action.get("object") in deleted:
                edits.append((action, operation))
        conflicts, seen = [], set()
        for deletion, dop in removals:
            if deletion["id"] in restored:
                continue
            for edit, eop in edits:
                if deletion["entity_id"] not in (edit["subject"], edit.get("object")) or dop["id"] == eop["id"]:
                    continue
                concurrent = dop["dependencies"].get(eop["origin"], 0) < eop["seq"] and eop["dependencies"].get(dop["origin"], 0) < dop["seq"]
                identity = (deletion["id"], edit["id"], dop["id"], eop["id"])
                if concurrent and identity not in seen:
                    seen.add(identity)
                    conflicts.append({"kind": "concurrent_delete_edit", "entity_id": deletion["entity_id"],
                                      "delete_id": deletion["id"], "edit_id": edit["id"],
                                      "delete_operation": dop["id"], "edit_operation": eop["id"]})
                    if len(conflicts) > limit:
                        return {"items": conflicts[:limit], "truncated": True}
        return {"items": sorted(conflicts, key=lambda item: (item["entity_id"], item["delete_id"], item["edit_id"])), "truncated": False}

    def status(self):
        with self._lock:
            counts = {r[0]: r[1] for r in self.db.execute("SELECT kind,count(*) FROM records GROUP BY kind")}
            return {"store_id": self.store_id, "peer_id": self.peer_id, "frontier": self._frontier(),
                    "known_position": int(self._meta("position")), "pending": self.db.execute("SELECT count(*) FROM operations WHERE position IS NULL").fetchone()[0],
                    "rejected": self.db.execute("SELECT count(*) FROM operations INDEXED BY operations_metadata WHERE rejected IS NOT NULL").fetchone()[0],
                    "counts": counts, "storage_profile": "personal-plaintext; SQLite WAL synchronous FULL",
                    "deleted_entities": len(self._deleted()), "conflicts": self._delete_edit_conflicts(), "restored_from": json.loads(self._meta("restored_from") or "null")}

    def rebuild(self):
        with self._transaction():
            rows = list(self.db.execute("SELECT body,position,applied_at FROM operations WHERE position IS NOT NULL ORDER BY position"))
            self.db.execute("DELETE FROM records")
            self.db.execute("DELETE FROM record_events")
            for row in rows:
                self._apply(json.loads(row["body"]), row["position"])
                self.db.execute("UPDATE operations SET applied_at=? WHERE position=?", (row["applied_at"], row["position"]))
            return {"rebuilt_operations": len(rows), "known_position": int(self._meta("position"))}

    def backup(self, path):
        """Publish a verified standalone snapshot without replacing a destination.

        Work stays in a private sibling file until the copy has been validated
        and flushed. The receipt describes that snapshot, not a later live state.
        """
        destination = Path(path)
        if destination.exists() or destination.is_symlink() or str(destination.resolve()) == str(Path(self.path).resolve()):
            raise ConflictError("Backup destination must be new")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if self._min_free_bytes:
            with self._lock:
                allocated = self.db.execute("PRAGMA page_count").fetchone()[0] * self.db.execute("PRAGMA page_size").fetchone()[0]
            if shutil.disk_usage(destination.parent).free < self._min_free_bytes + allocated + 65536:
                raise CapacityError("low_disk")
        fd, temporary_name = tempfile.mkstemp(prefix="." + destination.name + ".", dir=destination.parent)
        os.close(fd)
        temporary = Path(temporary_name)
        try:
            with self._lock:
                target = sqlite3.connect(temporary)
                try:
                    self.db.backup(target)
                    if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValidationError("Backup integrity check failed")
                    position = int(target.execute("SELECT value FROM metadata WHERE key='position'").fetchone()[0])
                    # A completed backup is one portable file, not a live WAL set.
                    target.execute("PRAGMA journal_mode=DELETE")
                finally:
                    target.close()
            with temporary.open("rb") as stream:
                os.fsync(stream.fileno())
            # Hard-link publication is atomic and fails if another writer created
            # the destination meanwhile. rename/replace would overwrite it.
            os.link(temporary, destination)
            directory = os.open(destination.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                try:
                    os.fsync(directory)
                except OSError as exc:
                    if exc.errno not in {errno.EINVAL, errno.ENOTSUP}:
                        raise
            finally:
                os.close(directory)
            return {"path": str(destination), "known_position": position}
        except sqlite3.Error as exc:
            if getattr(exc, "sqlite_errorcode", None) == sqlite3.SQLITE_FULL:
                raise CapacityError("low_disk") from exc
            raise ValidationError("Backup copy or validation failed") from exc
        finally:
            temporary.unlink(missing_ok=True)
            for suffix in ("-wal", "-shm", "-journal"):
                Path(str(temporary) + suffix).unlink(missing_ok=True)

    @classmethod
    def restore(cls, snapshot_path, destination, *, peer_id=None):
        """Verify and replay a snapshot into new local authority, never copy SQL code."""
        dest = Path(destination)
        if dest.exists():
            raise ConflictError("Restore destination must be new")
        source = None
        restored = None
        created = False
        try:
            source = sqlite3.connect(Path(snapshot_path).resolve().as_uri() + "?mode=ro", uri=True)
            source.row_factory = sqlite3.Row
            source.execute("PRAGMA trusted_schema=OFF")
            if source.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValidationError("Snapshot is corrupt")
            for item in source.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE type IN ('trigger','view')"):
                if tuple(item) != ('trigger','knowledge_writer_gate','operations',KNOWLEDGE_WRITER_GATE_SQL):
                    raise ValidationError("Snapshot contains executable schema objects")
                # Never execute source SQL; rebuild the current gate only after
                # the signed journal has been verified and replayed.
            metadata = dict(source.execute("SELECT key,value FROM metadata"))
            if metadata.get("schema") != str(SCHEMA):
                raise ValidationError("Unsupported snapshot schema")
            keys = {metadata["peer_id"]: metadata["key_hex"]}
            keys.update({r["id"]: r["key"] for r in source.execute("SELECT id,key FROM peers")})
            # Recovery verification keys are evidence only; never restored as admission.
            try:
                keys.update({r["origin"]: r["key"] for r in source.execute("SELECT origin,key FROM recovery_origins")})
            except sqlite3.OperationalError:
                pass
            keys.update(json.loads(metadata.get("recovery_keys", "{}")))
            origins = {r[0] for r in source.execute("SELECT DISTINCT origin FROM operations")}
            fresh = peer_id or str(uuid.uuid4())
            identifier(fresh)
            if fresh in origins or fresh == metadata["peer_id"]:
                raise ConflictError("Restore requires a fresh peer identity")
            applied_count = source.execute("SELECT count(*) FROM operations WHERE position IS NOT NULL").fetchone()[0]
            contiguous = all(row[0] == number for number, row in enumerate(
                source.execute("SELECT position FROM operations WHERE position IS NOT NULL ORDER BY position"), 1))
            if not contiguous or int(metadata["position"]) != applied_count:
                raise ValidationError("Snapshot is missing acknowledged journal history")
            identifier(metadata["store_id"], "snapshot store")
            identifier(metadata["peer_id"], "snapshot peer")
            dest.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
            created = True
            restored = cls(destination, store_id=metadata["store_id"], peer_id=fresh)
            with restored._transaction():
                restored._setmeta("recovery_keys", canonical(keys))
                restore_time = utcnow()
                restored._setmeta("restored_from", canonical({"peer_id": metadata["peer_id"], "inherited_through": applied_count, "restored_at": restore_time}))
                try:
                    for inherited in source.execute("SELECT * FROM inherited_receipts"):
                        restored.db.execute("INSERT OR IGNORE INTO inherited_receipts VALUES (?,?,?,?,?,?)", tuple(inherited))
                except sqlite3.OperationalError:
                    pass
                frontier = {}
                def operation_rows():
                    # Sort only IDs, never multi-megabyte signed payloads. An
                    # ORDER BY expression over SELECT * can make SQLite retain
                    # gigabytes even when Python consumes its cursor lazily.
                    orders = ("WHERE position IS NOT NULL ORDER BY position",
                              "WHERE position IS NULL ORDER BY origin,seq")
                    for order in orders:
                        for item in source.execute("SELECT id FROM operations " + order):
                            yield source.execute("SELECT * FROM operations WHERE id=?", (item[0],)).fetchone()
                for row in operation_rows():
                    body = json.loads(row["body"])
                    if canonical(body) != row["body"] or body["store_id"] != restored.store_id or body["schema"] != SCHEMA:
                        raise ValidationError("Invalid snapshot operation encoding")
                    if row["id"] != body["id"] or row["origin"] != body["origin"] or row["seq"] != body["seq"] or body["id"] != f'{body["origin"]}:{body["seq"]}':
                        raise ValidationError("Snapshot journal identity mismatch")
                    key = keys.get(body["origin"])
                    if key is None or not hmac.compare_digest(hmac.new(bytes.fromhex(key), row["body"].encode(), hashlib.sha256).hexdigest(), row["signature"]):
                        raise ValidationError("Snapshot origin verification failed")
                    restored._validate_actions(body["actions"])
                    restored._actor(body["actor"])
                    restored._validate_frontier_shape(body["dependencies"])
                    if body["dependencies"].get(body["origin"], 0) != body["seq"] - 1:
                        raise ValidationError("Snapshot origin continuity failed")
                    restored.db.execute("INSERT INTO operations(id,origin,seq,body,signature,received_at,rejected) VALUES (?,?,?,?,?,?,?)",
                                        (row["id"], row["origin"], row["seq"], row["body"], row["signature"], restore_time, row["rejected"]))
                    restored.db.execute("INSERT INTO inherited_receipts VALUES (?,?,?,?,?,?)", (row["id"], metadata["peer_id"], row["position"], row["received_at"], row["applied_at"], restore_time))
                    if row["position"] is not None:
                        if body["seq"] != frontier.get(body["origin"], 0) + 1:
                            raise ValidationError("Snapshot origin history has a gap")
                        restored._apply(body, row["position"])
                        restored.db.execute("UPDATE operations SET applied_at=? WHERE id=?", (restore_time, row["id"]))
                        frontier[body["origin"]] = body["seq"]
                # Compare replay with stored immutable records: missing projections can be rebuilt;
                # extra or altered projections indicate corrupt/misleading snapshot contents.
                for row in source.execute("SELECT kind,id,body FROM records"):
                    if restored.read(row["kind"], row["id"]) != json.loads(row["body"]):
                        raise ValidationError("Snapshot projection does not match its journal")
            if metadata.get("knowledge_profile_cutoff"):
                restored.enable_knowledge_profile()
            return restored
        except (sqlite3.DatabaseError, KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, MemoryError):
                raise
            raise ValidationError("Invalid snapshot") from exc
        finally:
            import sys
            failed = sys.exc_info()[0] is not None
            if source is not None:
                source.close()
            if failed and restored is not None:
                restored.close()
            if failed and created:
                for suffix in ("", "-wal", "-shm"):
                    Path(str(dest) + suffix).unlink(missing_ok=True)
