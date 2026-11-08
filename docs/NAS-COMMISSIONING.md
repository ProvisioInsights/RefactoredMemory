# Commissioning and operating the NAS peer

This is the operator sequence for the existing deployment artifacts. It does not report a completed NAS installation. Run these commands only on the approved Linux workload host, after its network isolation and storage paths are verified. Keep public tunneling and real-data ingestion disabled during synthetic commissioning. The normal engineering SSH account does not need Docker-root access or access to the production data directory; an approved deployment operator performs these steps.

## Record the actual host before installation

Record the RS822+ DSM build, installed VMM/Container Manager version, available RAM, guest Linux version, Docker/Compose versions, local filesystem and free space. Record the workload VLAN/interface/IP, every DSM address, private VPN endpoint and certificate names. These values are currently **unverified**. Test the agreed allowed/denied flows from [NAS-DEPLOYMENT](NAS-DEPLOYMENT.md), including IPv6 and Docker forwarding, before enabling a public route. Preserve an independent owner recovery path.

Verify an existing Python 3 interpreter for the standard-library preflight/realm-rendering scripts, and inspect numeric host UID mappings before assigning secret-file ownership. The engineering account must not share a host UID with a production runtime; the reference Keycloak UID 1000 commonly collides with a default VM user. Package installation and account changes belong to the later approved host setup, not these local test results.

The examples below assume the reviewed checkout is `/opt/refactoredmemory`, runtime UID/GID is `10001:10001`, runtime directory is `/srv/refactoredmemory`, and backups are `/srv/refactoredmemory-backups`. Replace those consistently with the approved values. The source checkout, Compose files and deployment scripts used by a privileged runtime must be root-owned and not writable by the maintenance account. No command here grants that account arbitrary Docker or sudo access.

## Prepare a fresh private directory

On a fresh deployment, the operator creates the directories explicitly. Compose refuses missing bind sources instead of creating root-owned directories for a missing key/configuration file.

```sh
sudo install -d -o 10001 -g 10001 -m 0700 /srv/refactoredmemory/data /srv/refactoredmemory/config /srv/refactoredmemory/config/secrets /srv/refactoredmemory/exports /srv/refactoredmemory-backups
sudo install -d -o root -g root -m 0755 /srv/refactoredmemory/tls
```

Copy `deploy/env.example` into `/srv/refactoredmemory/operator.env`, restrict it to the operator, and replace the hostnames/paths. It contains no passwords. Provision certificates and the maintained authorization server using [deploy/README](../deploy/README.md). Keep private keys in their documented runtime-owned mode-0400 files. Do not copy a live Mac database. The existing memory image includes its OAuth dependencies; the VM does not need a separate Python application installation for owner operations.

For the commands below, work from the reviewed checkout and define these shell functions once. They fix the same project name, env file and Compose files across invocations:

```sh
cd /opt/refactoredmemory
refmem() {
  docker compose --env-file /srv/refactoredmemory/operator.env -f deploy/compose.yaml "$@"
}
refmem_owner() {
  docker compose --env-file /srv/refactoredmemory/operator.env -f deploy/compose.yaml -f deploy/compose.owner.yaml --profile owner run --rm --no-deps owner "$@"
}
refmem_auth() {
  docker compose --env-file /srv/refactoredmemory/operator.env -f deploy/compose.yaml -f deploy/compose.oidc.yaml "$@"
}
```

These are operator conveniences, **not** safe sudo-allowlist helpers: they accept arbitrary arguments and must not be delegated as privileged commands. Production privileged maintenance requires the fixed, root-owned helper policy in [REMOTE-ADMIN](REMOTE-ADMIN.md).

Run `python3 deploy/preflight.py --env-file /srv/refactoredmemory/operator.env --owner` on this host with access to the private paths. Expected output is `"result": "passed"` and service `owner`. It checks the effective bind paths and rejects missing paths, symlink components, wrong types and unsafe private-directory ownership. It starts no containers. Before normal service/status operations, the container guard opens the existing database read-only to validate its identity metadata and required schema/journal. Missing, zero-byte, foreign or unsupported databases are refused without initialization or repair. This startup check does not replace full signed-journal verification during restore.

## Initialize and issue credentials explicitly

First create an empty peer with the Mac's **nonsecret** store ID and a freshly generated NAS peer ID:

```sh
refmem_owner init --store-id APPROVED_STORE_ID
refmem_owner status
refmem_owner identity --output /exports/nas.identity.json
```

Record the returned store and peer IDs privately. Expected initial counts are zero. `init` refuses an existing database, including an empty file or WAL/SHM residue. It is not a way to reset a deployment. The identity export is mode 0600 and contains signing secrets; transfer it through the approved private channel, not chat.

Place the Mac's approved identity file in the private `exports/` directory, owned by the runtime UID and mode 0600. Admit each identity on the opposite peer, then create a NAS credential for the Mac:

```sh
refmem_owner peer-admit --identity-file /exports/mac.identity.json
refmem_owner grant --label personal-mac-sync --kind peer --peer-id APPROVED_MAC_PEER_ID --scopes sync --output /exports/nas-allows-mac.token
refmem_owner grant --label chatgpt-personal --scopes read,write --output /exports/chatgpt.token
```

The grant command reports the output path, never the token. Give the peer token only to the Mac's private sync runner. Create distinct agent grants for the remaining cloud clients and move their new files into `config/secrets/`, retaining runtime ownership and mode 0400/0600. Do not overwrite an existing binding as part of repeating bootstrap. Explicit credential rotation consists of creating a new grant/file, updating the binding, verifying it, and revoking the old grant.

Complete `config/oauth.json` with the issuer, exact resource URL, owner subject and per-client grant paths. Import the trusted RSA signing JWKS. Real provider app enrollment and callback verification are separate qualification steps; the OAuth reference realm has no production users until the owner creates one and enrolls MFA.

## Start, check, stop and restart

```sh
python3 deploy/preflight.py --env-file /srv/refactoredmemory/operator.env
refmem up -d --no-build memory sync-ingress
refmem ps
refmem logs --tail 30 memory sync-ingress
refmem_owner status
```

Expected startup log is the sanitized NAS listener record; both listeners must be present. `Up` is only process status. Verify a synthetic authenticated MCP capture/query and a private TLS sync cycle using the configured certificate chain. Confirm the returned store/peer IDs match the recorded identity and that both peers converge. The automated disposable fixture is `python3 deploy/smoke_test.py`; its pass does not qualify the real host's routes or accounts.

To stop remote transport only, stop the optional tunnel service. To quiesce memory for maintenance, first stop the Mac sync runner and public tunnel, then stop the private ingress and memory process:

```sh
refmem --profile tunnel stop tunnel
refmem stop sync-ingress memory
refmem ps -a
```

The memory service has a 30-second stop grace period so bounded accepted requests can finish before SQLite closes. A normal stopped container should report exit code 0, not 137 (forced kill). An interrupted request can have committed before its client received the reply; retry with the same request ID, then check the result. Do not delete WAL/SHM files to force startup.

Restart with `refmem up -d --no-build memory sync-ingress`, verify identity/status and a synthetic query, then resume the Mac runner and optional tunnel. Use the same `-f deploy/compose.oidc.yaml` overlay for any command touching self-hosted authorization services. `stop` and ordinary `down` preserve data; **`down --volumes` deletes the self-hosted authorization database** and is only used by disposable tests. Do not use it for production maintenance.

## Back up the memory database

The owner backup command takes a consistent SQLite snapshot while the service is running. Choose a new filename for every backup:

```sh
refmem_owner backup /backups/nas-UNIQUE_TIMESTAMP.sqlite3
sha256sum /srv/refactoredmemory-backups/nas-UNIQUE_TIMESTAMP.sqlite3
```

Expected receipt contains the path and that snapshot's `known_position`. The destination must support same-directory hard links for atomic publication; use a verified local filesystem, then transfer the completed file off the VM. The final filename appears only after SQLite integrity validation, close and flush. A failed copy before publication must not leave a final-name snapshot. Do not back up by copying the active database/WAL files.

Keep the checksum, receipt, reviewed code/image identity and recovery pairing material with the protected backup record. Also protect separate copies of the operator configuration, trust material and authorization-server backup. A database snapshot is not a backup of the entire deployment. Backups contain personal data and signing material; apply the approved storage/transport controls. Perform restore drills before relying on them.

## Restore memory into a fresh isolated peer

1. Stop the old memory/tunnel/sync path and preserve its data directory unchanged. Never run the recovered database under the old peer identity alongside the old instance.
2. Create a **new** private runtime tree with empty `data/`, separate exports and reviewed configuration. Create a separate operator env file pointing at it. Use that env file in all recovery commands; leave the production one unchanged until recovery is verified.
3. With the owner profile and recovery env file, run `restore /backups/APPROVED_SNAPSHOT.sqlite3 /data/memory.sqlite3`, then `status`. The restored store ID must match; the peer ID must be new. Client grants and peer admissions are inactive by design. Do not start the public service yet.
4. Export the new identity and pair with a current Mac peer. Where older signed origins must be forwarded, explicitly use the `recovery-admit` procedure from [RUNBOOK](RUNBOOK.md#backup-recovery-and-rollback) with independently retained original identity material. Reconcile newer deletions and revocations while the recovered store is isolated.
5. Issue fresh agent and peer grants, update OAuth binding files, verify synthetic reads/captures and convergence, and only then promote the recovered paths through the approved deployment process. The previous tree remains preserved until the owner accepts recovery.

The restore command refuses an existing destination. An offline snapshot cannot know later deletions or authorization changes; restoring the file alone is not completed recovery.

For step 3, the concrete commands with the new private tree are:

```sh
python3 deploy/preflight.py --env-file /srv/refactoredmemory-recovery/operator.env --owner
docker compose --env-file /srv/refactoredmemory-recovery/operator.env -f deploy/compose.yaml -f deploy/compose.owner.yaml --profile owner run --rm --no-deps owner restore /backups/APPROVED_SNAPSHOT.sqlite3 /data/memory.sqlite3
docker compose --env-file /srv/refactoredmemory-recovery/operator.env -f deploy/compose.yaml -f deploy/compose.owner.yaml --profile owner run --rm --no-deps owner status
```

## Back up and restore optional Keycloak state

Keycloak users, MFA enrollment, client state and signing keys live in Postgres. The realm JSON is a bootstrap template, not a substitute for this database backup. A fresh import can produce different owner subjects and signing keys, invalidating resource bindings.

For a consistent backup, the operator creates a **new** private output file (`umask 077`, shell noclobber) and runs:

```sh
umask 077
set -C
refmem_auth exec -T postgres pg_dump -U keycloak -d keycloak --format=custom > /srv/refactoredmemory-backups/keycloak-UNIQUE_TIMESTAMP.dump
```

Check the command exit status. A redirected dump file can exist after a failed command; quarantine/remove that incomplete file and do not mark it as a backup. Validate and checksum the completed file:

```sh
refmem_auth exec -T postgres pg_restore --list < /srv/refactoredmemory-backups/keycloak-UNIQUE_TIMESTAMP.dump
sha256sum /srv/refactoredmemory-backups/keycloak-UNIQUE_TIMESTAMP.dump
```

These commands use local database administration inside the isolated container; they do not expose Postgres or print a password. Keep the dump and manifest private.

A restore drill uses a **separate Compose project and new named volume** with new private configuration paths and distinct private admin port. First confirm that the project name below has never held production data, then define and run:

```sh
refmem_auth_restore() {
  docker compose -p refmem-oidc-restorecheck --env-file /srv/refactoredmemory-recovery/operator.env -f deploy/compose.yaml -f deploy/compose.oidc.yaml "$@"
}
refmem_auth_restore up -d --no-build postgres
refmem_auth_restore ps
refmem_auth_restore exec -T postgres pg_restore --exit-on-error --no-owner -U keycloak -d keycloak < /srv/refactoredmemory-backups/APPROVED_KEYCLOAK_SNAPSHOT.dump
refmem_auth_restore up -d --no-build keycloak auth-admin-ingress
```

Wait for Postgres to report healthy before restoring. Do not add `--clean` or restore into the live production database. Verify the realm/owner subject/signing keys and a synthetic OAuth flow; restore the matching local JWKS and binding configuration deliberately. Reapply newer account/client revocations and key-rotation decisions while isolated, because an AS snapshot cannot include later changes. A live recovery similarly keeps the old volume intact and private until accepted.

The local operator test exercises a dump and restore into a separate synthetic database and checks restored state. Actual backup transport, NAS storage behavior and a full production restoration remain host-specific qualification.
