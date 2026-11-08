# NAS deployment artifacts

These artifacts target a Linux VM on the RS822+ with a separate VLAN/IP. They do not install anything on DSM, configure the router, create a Cloudflare tunnel or load personal data. Read [NAS-DEPLOYMENT](../docs/NAS-DEPLOYMENT.md) and [REMOTE-ADMIN](../docs/REMOTE-ADMIN.md) first. The NAS and actual provider connections still need qualification.

For container-only initialization, private path checks, stop/restart and backup/recovery procedures, follow [NAS-COMMISSIONING](../docs/NAS-COMMISSIONING.md). The optional `compose.owner.yaml` profile runs existing owner CLI commands with no network and only dedicated data/configuration/export/backup mounts. It never starts the public tunnel.

## Build and test locally

From the repository root, with Docker Engine and Compose already available:

```sh
docker build -t refactoredmemory:local .
docker build -f deploy/Keycloak.Dockerfile -t refactoredmemory-keycloak:local deploy
docker compose --env-file deploy/env.example -f deploy/compose.yaml -f deploy/compose.oidc.yaml config --quiet
python deploy/smoke_test.py
python deploy/operator_smoke_test.py
```

The smoke test needs the optional packages in `requirements-oauth.txt`. It starts a randomly named local project, creates synthetic users/data/certificates, exercises real Keycloak authorization-code + S256 PKCE and the memory service, and removes its containers, volumes and temporary credentials. It does not start `cloudflared`. First runs pull the pinned Postgres and HAProxy images. The test requires a Linux local Docker socket and an unprivileged UID 1000, matching the Keycloak reference image; it is not the Mac hardware qualification. The application image itself supports other configured UIDs. In this managed build environment, add `--secret id=proxy_ca,src="$CODEX_PROXY_CERT"` to the memory build command. That CA is a build-only secret and is not copied into the image.

Image identities are pinned in Dockerfiles/Compose: Chainguard Python starter runtime and builder (refresh both pinned digests together), Keycloak 26.8.2, PostgreSQL 17.11, HAProxy 3.2.26, cloudflared 2026.10.7. Review and refresh digests deliberately for security updates; pins do not update themselves. The optional crypto dependency versions are pinned separately. The builder removes pip, setuptools and wheel from the copied application environment; runtime dependency updates still require a vulnerability scan. No vulnerability scan is implied by successful builds. Run the Linux Keycloak smoke test and host-specific commissioning before promoting a new image. The free starter latest tags may change Python versions, so validate each digest update before deployment.

## Private operator configuration

Copy `env.example` to a private directory outside the checkout. Set `REFMEM_PRIVATE_DIR` to an absolute path. Keep deployment files root-owned if a privileged deployment helper reads them; a maintenance account must not be able to replace root-executed Compose files.

Prepare only these paths on the VM's local persistent filesystem:

| Path under the private directory | Ownership / access |
| --- | --- |
| `data/` | Memory runtime UID/GID, mode 0700; persistent database and audit log. |
| `exports/` and the separate `REFMEM_BACKUP_DIR` | Memory runtime UID/GID, mode 0700; owner-operation exports and snapshots. |
| `config/` and `config/secrets/` | Memory runtime UID/GID, mode 0700; read-only in the service. |
| `config/oauth.json`, `config/jwks.json` | Trusted administrator-managed configuration; readable by memory UID. |
| `config/secrets/*.token` | Memory runtime UID, mode 0400 or 0600, regular files without symlinks. |
| `tls/` | Traversable by required service UIDs (0755 is suitable); public certificates 0644. |
| `tls/memory.key` | Memory runtime UID, 0400. |
| `tls/keycloak.key` (optional) | UID 1000, 0400. |
| `auth/realm.json`, `auth/keycloak-password`, `auth/admin-password` (optional) | UID 1000, 0400. |
| `auth/postgres-password` (optional) | UID 70, 0400; same password bytes as `keycloak-password`. |
| `tunnel/tunnel.yaml`, `tunnel/tunnel.json` (optional) | Tunnel runtime UID, read-only; credentials 0400. |

Standalone Compose bind mounts preserve host ownership. Compose secret `uid` fields do not repair the owner of a host bind-mounted file. Do not make token or private-key files generally readable to bypass a startup error. The disposable smoke fixture uses its own UID and temporary secret directory; it is not a production permissions template.

Use the owner CLI in [RUNBOOK](../docs/RUNBOOK.md) to create a fresh NAS peer identity with the same store ID as the Mac, pair both identities and issue a distinct peer-only sync grant. Generate separate agent grants for each cloud client (usually read/write; correction only when deliberately granted). This setup happens before starting the long-lived service. Do not initialize by copying the Mac's active database.

Copy `oauth.example.json` to `config/oauth.json` and replace the issuer, exact HTTPS resource URL, owner subject and client IDs with verified values. The resource is exactly `https://your-host/mcp`. OAuth metadata is served at `/.well-known/oauth-protected-resource/mcp`. Bindings must point to current local **agent** grant files, never owner or peer tokens. A binding alone cannot manufacture a grant.

Install a trusted public signing JWKS at `config/jwks.json`. Export it from the configured authorization server over authenticated/verified TLS. For Keycloak, select only RSA signing keys with `use: sig` and `alg: RS256`; its complete JWKS may also contain encryption keys that this adapter intentionally rejects. Keep `kid` values unique, at most 16 keys. Replace the local JWKS atomically before the issuer begins signing with a new key; retain an old key only for the approved rollover interval. No token-supplied URL is fetched.

Provision origin certificates under `tls/`. The memory certificate must include `memory` for the tunnel and the actual private sync hostname used by the Mac. The Keycloak certificate must include `keycloak` and its private admin hostname. `tls/ca.crt` is the public CA certificate; trust that CA on the Mac and in the tunnel container. Keep the CA private key elsewhere. Never set `noTLSVerify`.

## Run the memory peer

```sh
docker compose --env-file /private/path/refmem.env -f deploy/compose.yaml up -d memory sync-ingress
```

The memory process has no default outbound route. `sync-ingress` passes encrypted TCP only to `memory:8766`, preserving end-to-end TLS and application authorization. Its default host bind is loopback. Set the bind to the approved private VPN/interface address only after firewall testing. The allowlist includes the configured hostname plus externally selected sync port; use a hostname matching the certificate. Production MCP has no host-published port.

In the tested Docker 29 runtime, publishing a port on an internal-only network did not create a working host forwarding path. The small fixed-destination HAProxy ingress services bridge that path while leaving memory and Keycloak on internal networks. Their configuration caps connections/timeouts and contains no arbitrary proxy endpoint. The ingress/tunnel containers have an outbound-capable interface: VM/router egress policy is still required to block DSM/LAN access. Internal Docker networks alone are not proof of NAS isolation.

## Optional self-hosted OAuth server

An existing maintained authorization server avoids this additional workload. To use the reference stack, allow several additional GiB of VM capacity, choose public and private admin hostnames, supply the password/certificate files above, and render an initially empty realm:

```sh
python deploy/render_realm.py --resource https://memory.example.com/mcp --callbacks /private/path/callbacks.json --output /private/path/auth/realm.json
docker compose --env-file /private/path/refmem.env -f deploy/compose.yaml -f deploy/compose.oidc.yaml up -d postgres keycloak auth-admin-ingress
```

`callbacks.json` maps each of `refmem-chatgpt`, `refmem-claude`, `refmem-openai-api`, `refmem-anthropic-api` to a list of exact HTTPS callback URLs obtained from that client. No wildcards. The reference uses manually registered public clients, S256 PKCE, five-minute access tokens, rotated refresh tokens and explicit resource audience/subject claims. It does not enable anonymous dynamic client registration. Confirm that each actual app/API configuration supports this registration method; a client requiring a different discovery/registration flow is a remaining integration task, not grounds to weaken authorization.

The production realm contains **no users or passwords**. Access the admin console only over the private path, create the owner account and enroll MFA, configure the appropriate required authentication flow, then bind that account's exact subject in the resource config. Replace/remove the temporary bootstrap administrator through Keycloak's supported administration process. Do not use a test realm in production. Keycloak imports an absent realm at startup; editing the JSON does not migrate an existing realm. Apply later changes through controlled administration and back up the Postgres volume independently of memory backups. Local grant revocation takes effect on the next request; logging out at the authorization server alone does not invalidate an already signed access token before its short expiry.

## Optional public tunnel

The owner provisions a named, locally managed tunnel and DNS separately. Copy `tunnel.example.yaml` (external OAuth server) or `tunnel-with-auth.example.yaml` (self-hosted Keycloak) into the private `tunnel/` directory, replace hostnames/tunnel ID and supply only its tunnel-specific credential as `tunnel.json`. The final rule returns 404. The self-hosted template permits the selected realm's required discovery/login/token/key/logout routes and static assets. It excludes `/admin`, other realms and dynamic registration; neither template exposes sync, SSH or DSM.

Validate configuration without connecting externally:

```sh
docker compose --env-file /private/path/refmem.env -f deploy/compose.yaml --profile tunnel run --rm --no-deps tunnel tunnel --config /config/tunnel.yaml ingress validate
```

After the owner enables the public route and the NAS isolation checks pass:

```sh
docker compose --env-file /private/path/refmem.env -f deploy/compose.yaml --profile tunnel up -d tunnel
docker compose --env-file /private/path/refmem.env -f deploy/compose.yaml --profile tunnel stop tunnel
```

Include `-f deploy/compose.oidc.yaml` with the self-hosted authorization profile so the tunnel can reach its isolated auth network. Disabling the tunnel leaves the store and private sync running. Do not add Cloudflare Access browser-login redirects in front of MCP unless the actual clients support that extra flow; the resource already requires OAuth. Disable private-response caching and content/token logging at the edge. Traffic crosses Cloudflare and the chosen model provider; this is not end-to-end encryption hiding retrieved content from them.

## Verify actual isolation later

Use `firewall-policy.example.yaml` as an operator policy worksheet, not an executable router configuration. Resolve actual interfaces, private VPN addresses, NAS management addresses (all IPv4/IPv6), allowed DNS/time servers and the current tunnel provider destination requirements. Enforce forwarding as well as host input/output; Docker forwarding can bypass a host-only firewall rule. Test approved individual denied endpoints from the memory, ingress and tunnel network namespaces, repeat after restarts, and preserve an out-of-band recovery path. No script here changes the NAS/VM/router firewall.
