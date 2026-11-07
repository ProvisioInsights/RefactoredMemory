"""Deployment-only guard against silently creating a replacement peer identity."""
import json
import os
from pathlib import Path
import stat
import sqlite3
import sys
import time

DATABASE = Path("/data/memory.sqlite3")
OWNER_COMMANDS = {
    "init", "status", "identity", "peer-admit", "peer-revoke", "recovery-admit",
    "grant", "revoke", "owner-submit", "query", "history", "backup", "restore", "rebuild", "import",
}

# This profile requires an existing schema-1 identity and table layout. The
# guard performs no repair; restore performs full signed-journal verification.
TABLE_COLUMNS = {
    "metadata": {"key", "value"},
    "operations": {"id", "origin", "seq", "body", "signature", "received_at", "position", "applied_at", "rejected"},
    "records": {"kind", "id", "body", "operation_id", "subject", "predicate", "object"},
    "record_events": {"kind", "id", "operation_id"},
    "requests": {"actor", "id", "digest", "operation_id"},
    "peers": {"id", "key", "active"},
    "inherited_receipts": {"operation_id", "replica", "position", "received_at", "applied_at", "restored_at"},
    "recovery_origins": {"sender", "origin", "key"},
    "grants": {"digest", "id", "label", "kind", "scopes", "peer_id", "active"},
}


def validate_existing_database(path):
    """Inspect existing identity/schema read-only; never call Store or write SQL."""
    problem = "Existing database is not a supported RefactoredMemory peer; it was not initialized or repaired"
    connection = None
    try:
        with path.open("rb") as stream:
            if stream.read(16) != b"SQLite format 3\x00":
                raise ValueError(problem)
        for suffix in ("-wal", "-shm", "-journal"):
            sidecar = Path(str(path) + suffix)
            if sidecar.is_symlink() or (sidecar.exists() and not sidecar.is_file()):
                raise ValueError(problem)
        connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=2, isolation_level=None)
        deadline = time.monotonic() + 2
        connection.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
        connection.execute("PRAGMA trusted_schema=OFF")
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        if connection.execute("SELECT 1 FROM sqlite_master WHERE type IN ('trigger','view') LIMIT 1").fetchone():
            raise ValueError(problem)
        for table, columns in TABLE_COLUMNS.items():
            schema = connection.execute("SELECT type,sql FROM sqlite_master WHERE name=?", (table,)).fetchone()
            if not schema or schema[0] != "table" or not isinstance(schema[1], str) or not schema[1].lstrip().upper().startswith("CREATE TABLE"):
                raise ValueError(problem)
            if {row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')} != columns:
                raise ValueError(problem)
        rows = connection.execute("SELECT key,substr(value,1,257),length(value) FROM metadata WHERE key IN ('schema','store_id','peer_id','key_hex','position') LIMIT 6").fetchall()
        if len(rows) != 5 or any(length != len(value) for _, value, length in rows):
            raise ValueError(problem)
        metadata = {key: value for key, value, _ in rows}
        if set(metadata) != {"schema", "store_id", "peer_id", "key_hex", "position"} or metadata["schema"] != "1":
            raise ValueError(problem)
        for key in ("store_id", "peer_id"):
            value = metadata[key]
            if not isinstance(value, str) or not 1 <= len(value) <= 256 or any(ord(c) < 32 for c in value):
                raise ValueError(problem)
        key = metadata["key_hex"]
        if not isinstance(key, str) or len(key) != 64 or len(bytes.fromhex(key)) != 32:
            raise ValueError(problem)
        position = metadata["position"]
        if not isinstance(position, str) or not position.isascii() or not position.isdecimal() or len(position) > 19:
            raise ValueError(problem)
        if not 0 <= int(position) < 2**63 or str(int(position)) != position:
            raise ValueError(problem)
        latest = connection.execute("SELECT COALESCE(MAX(position),0) FROM operations").fetchone()[0]
        if latest != int(position):
            raise ValueError(problem)
    except (sqlite3.Error, TypeError, ValueError, KeyError) as error:
        raise ValueError(problem) from error
    finally:
        if connection is not None:
            connection.close()


def main(argv):
    if len(argv) < 2 or argv[0] not in {"serve", "owner"}:
        raise ValueError("Explicit container mode and operation are required")
    mode, command = argv[:2]
    if (mode == "serve" and command != "serve-nas") or (mode == "owner" and command not in OWNER_COMMANDS):
        raise ValueError("Operation is not available in this container profile")
    for directory in (DATABASE.parent, Path("/config")):
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("Data and configuration mounts must be existing directories, not symlinks")
    exists = DATABASE.exists() or DATABASE.is_symlink()
    if command in {"init", "restore"}:
        # Empty also excludes dangling WAL/SHM/rollback journals and other residue.
        if next(DATABASE.parent.iterdir(), None) is not None:
            raise ValueError("Initialization and recovery require a fresh data directory; existing data was not changed")
    elif not exists:
        raise ValueError("Database is missing; check the data mount before explicitly initializing or restoring a peer")
    elif DATABASE.is_symlink() or not stat.S_ISREG(DATABASE.stat().st_mode):
        raise ValueError("Database must be an existing regular file, not a symlink")
    else:
        validate_existing_database(DATABASE)
    os.execv(sys.executable, [sys.executable, "-m", "refactoredmemory", "--db", str(DATABASE), *argv[1:]])


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (OSError, ValueError) as error:
        print(json.dumps({"error": "container_precondition", "message": str(error)}), file=sys.stderr)
        sys.exit(2)
