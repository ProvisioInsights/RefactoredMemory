"""Disposable network-none owner bootstrap/backup/recovery and host preflight test."""
import json
import os
from pathlib import Path
import secrets
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    if os.geteuid() == 0:
        raise SystemExit("Run this disposable test as an unprivileged local Docker operator")
    env = os.environ.copy()
    for key in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"):
        env.pop(key, None)
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    project = "refmemops" + secrets.token_hex(4)
    checks = []

    def run(args, expected=0, expected_error=None):
        result = subprocess.run(args, text=True, capture_output=True, env=env, timeout=45)
        if (expected == 0 and result.returncode) or (expected != 0 and result.returncode == 0):
            raise RuntimeError(f"Unexpected command outcome: {args[0]} exit {result.returncode}: {result.stderr[-1500:]}")
        if expected_error is not None:
            assert f'"error": "{expected_error}"' in result.stderr, "Container guard did not reject before application startup"
        return result.stdout

    with tempfile.TemporaryDirectory(prefix="refmem-operator-") as temporary:
        root = Path(temporary)
        backups = root / "backups"
        backups.mkdir(mode=0o700)

        def setup(name):
            private = root / name
            private.mkdir(mode=0o700)
            for item in ("data", "config", "exports"):
                (private / item).mkdir(mode=0o700)
            envfile = private / "operator.env"
            envfile.write_text("\n".join([f"REFMEM_PRIVATE_DIR={private}", f"REFMEM_BACKUP_DIR={backups}",
                f"REFMEM_UID={os.getuid()}", f"REFMEM_GID={os.getgid()}", "REFMEM_MCP_HOST=synthetic.example.invalid"]) + "\n")
            envfile.chmod(0o600)
            compose = docker + ["compose", "-p", project, "--env-file", str(envfile), "-f", str(ROOT / "deploy/compose.yaml"),
                "-f", str(ROOT / "deploy/compose.owner.yaml"), "--profile", "owner"]
            return private, envfile, compose

        private, envfile, compose = setup("original")
        recovery, recovery_env, recovery_compose = setup("recovery")

        def owner(command, expected=0, target=compose):
            return run(target + ["run", "--rm", "--no-deps", "owner", *command], expected)

        def preflight(path=envfile, expected=0):
            return run([sys.executable, str(ROOT / "deploy/preflight.py"), "--env-file", str(path), "--owner"], expected)

        try:
            config = json.loads(run(compose + ["config", "--format", "json"]))["services"]["owner"]
            assert config["network_mode"] == "none" and config["read_only"]
            assert config["cap_drop"] == ["ALL"]
            preflight()
            (private / "exports").rmdir()
            preflight(expected=1)
            owner(["status"], expected=1)
            assert not (private / "exports").exists(), "Compose silently created a missing bind path"
            (private / "exports").mkdir(mode=0o700)
            (private / "data").rename(private / "real-data")
            (private / "data").symlink_to(private / "real-data", target_is_directory=True)
            preflight(expected=1)
            (private / "data").unlink()
            (private / "real-data").rename(private / "data")
            (private / "exports").chmod(0o755)
            preflight(expected=1)
            (private / "exports").chmod(0o700)
            (private / "config/synthetic-link").symlink_to("/synthetic-missing-key")
            preflight(expected=1)
            (private / "config/synthetic-link").unlink()
            (private / "config/secrets").mkdir(mode=0o700)
            (private / "config/secrets/wrong-mode.token").write_text("synthetic-preflight-not-a-credential")
            (private / "config/secrets/wrong-mode.token").chmod(0o644)
            preflight(expected=1)
            (private / "config/secrets/wrong-mode.token").chmod(0o600)
            preflight()
            owner(["status"], expected=1)
            assert not (private / "data/memory.sqlite3").exists()
            (private / "data/memory.sqlite3").touch(mode=0o600)
            owner(["init"], expected=1)
            assert (private / "data/memory.sqlite3").stat().st_size == 0
            def invalid_existing_store():
                database = private / "data/memory.sqlite3"
                before = database.read_bytes()
                names = sorted(p.name for p in database.parent.iterdir())
                run(compose + ["run", "--rm", "--no-deps", "owner", "status"], expected=1, expected_error="container_precondition")
                run(compose + ["run", "--rm", "--no-deps", "--entrypoint", "python", "owner", "/operator/container_entrypoint.py", "serve", "serve-nas",
                    "--mcp-cert-file", "/missing.crt", "--mcp-key-file", "/missing.key", "--sync-cert-file", "/missing.crt", "--sync-key-file", "/missing.key", "--oauth-config", "/missing.json"],
                    expected=1, expected_error="container_precondition")
                assert database.read_bytes() == before and sorted(p.name for p in database.parent.iterdir()) == names, "Rejected database was changed"
            invalid_existing_store()
            (private / "data/memory.sqlite3").unlink()
            with sqlite3.connect(private / "data/memory.sqlite3") as foreign:
                foreign.execute("CREATE TABLE unrelated_notes(value TEXT)")
                foreign.execute("INSERT INTO unrelated_notes VALUES ('synthetic foreign database')")
            invalid_existing_store()
            (private / "data/memory.sqlite3").unlink()
            with sqlite3.connect(private / "data/memory.sqlite3") as partial:
                partial.execute("CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
                partial.executemany("INSERT INTO metadata VALUES (?,?)", [("schema", "1"), ("store_id", "synthetic"), ("peer_id", "synthetic"), ("key_hex", "0" * 64), ("position", "0")])
            invalid_existing_store()
            (private / "data/memory.sqlite3").unlink()
            (private / "data/memory.sqlite3-wal").symlink_to("/synthetic-dangling-wal")
            owner(["init"], expected=1)
            (private / "data/memory.sqlite3-wal").unlink()
            (private / "data/memory.sqlite3-journal").symlink_to("/synthetic-dangling-journal")
            owner(["init"], expected=1)
            (private / "data/memory.sqlite3-journal").unlink()
            checks += ["missing bind source is rejected without creating it", "host bind symlink is rejected by preflight",
                "unsafe private-directory/token modes and nested config symlink rejected",
                "status and service reject zero-byte, foreign SQLite and missing-journal databases unchanged",
                "status cannot silently initialize a missing database", "init refuses existing empty DB and dangling WAL/rollback journal"]

            initialized = json.loads(owner(["init", "--store-id", "synthetic-operator"]))
            owner(["init"], expected=1)
            owner(["identity", "--output", "/exports/original.identity.json"])
            owner(["grant", "--label", "synthetic-agent", "--scopes", "read,write", "--output", "/exports/client.token"])
            assert (private / "exports/client.token").stat().st_mode & 0o777 == 0o600
            actions = [
                {"type": "entity", "id": "operator-note", "entity_type": "note", "label": "Synthetic recovery note"},
                {"type": "source", "id": "operator-source", "uri": "synthetic://operator", "content": "Synthetic backup evidence"},
                {"type": "assertion", "id": "operator-fact", "subject": "operator-note", "predicate": "state",
                 "value": "retained", "source_ids": ["operator-source"]},
            ]
            (private / "exports/actions.json").write_text(json.dumps(actions))
            (private / "exports/actions.json").chmod(0o600)
            owner(["owner-submit", "--actions", "@/exports/actions.json", "--request-id", "synthetic-operator-write"])
            status = json.loads(owner(["status"]))
            receipt = json.loads(owner(["backup", "/backups/synthetic.sqlite3"]))
            assert receipt["known_position"] == status["known_position"] > 0
            snapshot = (backups / "synthetic.sqlite3").read_bytes()
            owner(["backup", "/backups/synthetic.sqlite3"], expected=1)
            assert (backups / "synthetic.sqlite3").read_bytes() == snapshot
            restored = json.loads(owner(["restore", "/backups/synthetic.sqlite3", "/data/memory.sqlite3"], target=recovery_compose))
            assert restored["store_id"] == status["store_id"]
            assert restored["peer_id"] != initialized["peer_id"]
            assert restored["known_position"] == status["known_position"]
            answer = owner(["query", "--args", '{"subject":"operator-note"}'], target=recovery_compose)
            assert "retained" in answer
            owner(["restore", "/backups/synthetic.sqlite3", "/data/memory.sqlite3"], expected=1, target=recovery_compose)
            (recovery / "exports/client.token").write_bytes((private / "exports/client.token").read_bytes())
            (recovery / "exports/client.token").chmod(0o600)
            auth_probe = "from pathlib import Path\nfrom refactoredmemory.store import Store,AuthorizationError\nwith Store('/data/memory.sqlite3') as s:\n try:s.authenticate(Path('/exports/client.token').read_text().strip())\n except AuthorizationError:pass\n else:raise AssertionError('Stale client grant active after restore')"
            run(recovery_compose + ["run", "--rm", "--no-deps", "--entrypoint", "python", "owner", "-c", auth_probe])
            preflight(recovery_env)
            checks += ["explicit network-none container bootstrap and private credential export",
                "consistent backup receipt and no-overwrite destination",
                "fresh-directory restore retains evidence with a new peer identity",
                "restored snapshot does not reactivate an old client grant"]
            print(json.dumps({"result": "passed", "environment": "local Linux Docker; disposable synthetic data",
                "checks": checks, "limits": ["No actual NAS filesystem or off-device backup transfer", "No real-data restoration or public tunnel"]}, indent=2))
        finally:
            run(compose + ["down", "--remove-orphans"])


if __name__ == "__main__":
    main()
