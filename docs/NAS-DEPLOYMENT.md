# NAS-first deployment

The target is one personal store with two full writable peers: the owner's Mac and a Linux workload on the Synology RS822+. The NAS peer is the normal MCP endpoint; it is not the only writer or a replacement for backups. DSM and existing NAS services stay on the main LAN. The memory workload has a separate network identity and an isolated VLAN. Cloudflare is an optional transport to this workload, not the memory database or a third peer.

This document records the authorized deployment design. The actual DSM build, installed packages, available RAM, virtual switch, VLAN rules, storage and NAS behavior still require inspection after access is provided. A local Docker test is not proof that the NAS firewall or its filesystem behaves the same way.

## Isolation boundary

A small Linux VM with its own virtual NIC on the workload VLAN is preferred. Run the memory and optional tunnel containers inside that VM. This leaves DSM on its existing management network and gives the workload a separate address for router rules. The guest needs sufficient memory for its actual services; do not allocate resources based only on the NAS model name.

Direct Container Manager deployment is an alternative after verifying persistent VLAN attachment and host forwarding rules. It shares DSM's kernel and is a weaker boundary from the host. An internal Docker bridge alone does not establish isolation from DSM, other host interfaces or every LAN destination. Router rules also cannot distinguish containers if their traffic is NATed to the NAS address. A VLAN attached to the whole NAS does not, by itself, separate the workload from DSM.

The deployment must enforce these flows outside the application:

| Source | Allowed destinations |
| --- | --- |
| Tunnel connector | The fixed memory MCP endpoint and documented tunnel-provider destinations; narrowly required DNS/time services. |
| Memory process | Replies to established requests; no general outbound network access. OAuth verification uses local trusted configuration and a locally mounted public JWKS. |
| Authorized Mac peer | The private TLS sync listener only, using its dedicated peer grant. |
| Authorized management identity | SSH to the workload VM, with no route permission to DSM or the rest of the LAN. |
| Everything else | Denied, including new connections to DSM, NAS shares, SSH on the NAS host, router administration and unrelated LAN devices. |

Rules must cover IPv4, IPv6, all NAS interface addresses and same-VLAN traffic. Preserve explicit established-response rules so an allowed management connection can receive replies. Do not apply a generic firewall example to the NAS without checking the management path and preserving a recovery path.

## Services and storage

The NAS process uses `serve-nas`: one `Store` instance and two independent TLS listeners. Port 8765 is MCP plus protected-resource metadata; port 8766 is peer synchronization only. OAuth credentials cannot authenticate to sync, and peer credentials cannot call consumer tools. The MCP listener does not expose owner administration, import paths, backups or arbitrary file access.

The image runs as an unprivileged UID/GID. Its root filesystem is read-only, Linux capabilities are dropped, privilege escalation is disabled, and temporary storage, memory, CPU and process counts are bounded. Mount only the dedicated `/data` directory writable and the required configuration/certificates read-only. TLS files are mounted individually: memory cannot see Keycloak's private key and Keycloak cannot see memory's, even if runtime UIDs coincide. Do not mount the Docker socket, host devices, DSM directories, whole NAS volumes or general shared folders.

The concrete Compose files, image pins, private-file ownership, OAuth realm renderer and local smoke command are in [deploy/README.md](../deploy/README.md). Fixed-destination HAProxy ingress containers provide private TCP forwarding to the sync and optional authorization-admin listeners. TLS terminates in the destination service. This keeps the memory process on an internal-only network; tested Docker 29 did not provide working host-published forwarding directly on that network. Ingress and tunnel egress still require the external VM/router policy described here.

Use [NAS-COMMISSIONING.md](NAS-COMMISSIONING.md) for the clean-host operator sequence and recovery procedures. Bind mounts refuse missing host paths, a read-only preflight rejects symlinked/mistyped private paths, and the service validates existing database identity/schema read-only before startup. Missing, empty or foreign databases cannot create a replacement identity implicitly. Initialization/restoration use a separate explicit owner profile with networking disabled. Memory shutdown has a 30-second grace period for bounded accepted requests.

The live SQLite database, WAL and SHM files must be on the VM's local persistent filesystem, or a verified local NAS volume for the direct-container alternative. Do not put the live database on an SMB or NFS mount. A network share can receive a completed consistent backup after the backup operation finishes; copying an active database file is not a backup procedure.

Use a fresh peer identity for the NAS and the same nonsecret store ID as the Mac. Never copy the Mac's live writable database directory and start both under one identity. Recovery uses the documented fresh-identity restore/rejoin procedure. The private sync listener is not published through the public tunnel.

## OAuth and tunnel

The OAuth authorization server is a maintained external or self-hosted service. The resource server validates a configured issuer, resource audience, signature, expiry and client/subject binding, then applies the current local agent grant. Separate ChatGPT, Claude and API applications receive separate revocable bindings. An owner login does not turn an unattended model into an owner actor.

The optional Keycloak/PostgreSQL reference profile demonstrates a self-hosted authorization server. It is a separate workload with its own persistent data, patching, backups and memory requirements. Budget several additional GiB of available VM memory for the reference stack and measure it before adopting it on the NAS. If resources are tight, use an already approved authorization server instead. Do not run the reference authentication server with demonstration accounts or secrets in production.

The memory process does not fetch keys from a token's `jku`, `x5u` or other supplied URL. An administrator imports trusted public signing keys into the mounted JWKS through a controlled maintenance procedure. Key rotation therefore includes updating that file before the authorization server starts using a new signing key. Unknown keys fail closed.

Cloudflare Tunnel runs only when its optional profile is enabled. The named tunnel has fixed hostname-to-origin routing and a final deny rule. Forward only the MCP listener and the authentication service's explicitly required paths. Do not publish the peer-sync listener, DSM, SSH, general reverse-proxy routing or arbitrary upstream URLs. A tunnel does not replace OAuth or local grant checks. Its runtime credential is distinct from an account administration token.

Use verified TLS from the tunnel connector to the MCP listener, with a trusted origin CA and the expected origin server name. Do not disable TLS verification or make the application trust arbitrary forwarded-protocol headers. Private MCP responses must not be cached by the CDN, and ordinary logs must omit tokens and content.

TLS secures these network links; it is not owner-only end-to-end encryption through the tunnel and model provider. Cloudflare terminates the public HTTPS connection, and the chosen OpenAI/Anthropic client processes the content it retrieves. Whole-store access means a separately revocable grant can query the personal store; it does not automatically bulk-upload every record. Provider data controls and actual connector behavior remain part of connection qualification.

Disabling the tunnel stops remote transport, not local memory operation. The NAS and Mac can continue local operation and private synchronization. Removing a container does not remove its persistent data. Cloudflare Workers/Durable Objects storage, selective cloud caching and additional peers remain deferred.

## Before enabling real access

The deployment artifacts must be rendered into a private directory outside the checkout. Replace placeholder hostnames with the actual public MCP resource URL, issuer, private peer address and certificate names. Generate separate client/peer credentials with the owner CLI; never put them in the Compose file or repository. Bind the private sync port to the approved VM interface; its fail-closed default is loopback.

Before personal data is loaded, verify:

1. The effective container configuration has the intended unprivileged user, read-only rootfs, capability and resource limits, private mounts, networks and port bindings.
2. A synthetic OAuth request reaches the MCP listener; expired, wrong-audience, wrong-client and revoked credentials fail. Peer credentials and public requests cannot reach sync or administration.
3. Synthetic tests from the workload and tunnel network namespaces cannot open new connections to specific prohibited DSM/LAN/Internet endpoints. Use approved test targets; do not scan unrelated networks.
4. The same denials hold after container, VM, firewall and DSM restarts. Check actual Docker forwarding behavior, not only the DSM firewall UI.
5. The Mac and NAS exchange offline synthetic writes, converge, resume after interruption and correctly report insufficient disk space or a paused sync cycle.
6. An acknowledged write survives restart, a consistent backup restores under a fresh identity, and a stale restore cannot resurrect revoked grants or bypass newer deletion state.

Passing local container and authentication evidence is recorded in [the acceptance report](ACCEPTANCE-RESULTS.md) and [raw container result](results/nas-docker-smoke.json), separately from this NAS qualification. Public provider application access also remains unverified until exercised with the actual accounts.

For ongoing engineering access, use [REMOTE-ADMIN.md](REMOTE-ADMIN.md). The operator runbook remains [RUNBOOK.md](RUNBOOK.md).
