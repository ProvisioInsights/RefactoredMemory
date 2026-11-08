# NAS-first deployment contract

Accepted for implementation on 7 November 2026 after the owner requested documentation reconciliation, implementation and local testing. This contract extends the existing personal graph; it does not declare the new deployment tested before evidence exists.

## Deployment and authority

The normally available MCP endpoint is a Linux workload on the owner's Synology RS822+. DSM and existing NAS services remain on the main LAN. Prefer a small Linux VM with its own network identity and isolated VLAN, with hardened containers inside; direct Container Manager deployment is an alternative requiring separate host/forwarding isolation checks. The reported current DSM version, installed packages, RAM, VLAN wiring and real filesystem behavior need inspection on the NAS.

The Mac remains a complete independently writable peer. Primary endpoint does not mean exclusive writer or greater factual authority. A private authenticated sync listener exchanges original signed operations; it is not exposed through the public MCP tunnel. Cloudflare is an optional outbound tunnel to a fixed MCP endpoint, not a database or compute host. A Workers/Durable Objects peer, selective caches, transitive mesh and third peers remain deferred. No other repository is changed.

One process opens the NAS Store and serves separate TLS listeners: public MCP plus its exact protected-resource metadata path, and private peer-sync only. Public MCP cannot call sync, import files, change grants, perform owner administration or select arbitrary upstreams. Both listeners keep host/origin checks. Internal container traffic uses verified TLS; forwarded headers do not manufacture transport trust. Container root filesystems are read-only; only dedicated data/configuration/secrets paths are mounted. Application containers have no Docker socket, host networking or broad NAS-share access.

## OAuth resource profile

Use a maintained OAuth/OIDC authorization server for login, consent, PKCE, client registration and token issuance. The default deployment accepts an explicitly configured authorization server; a separately enabled Keycloak/Postgres reference profile documents a self-hosted option and its additional resource needs. This project does not implement a password database or authorization-code issuer. App connector availability for OpenAI Pro 500 and Claude Max 5x remains an account-specific qualification, not a subscription guarantee.

The optional Python OAuth adapter uses PyJWT and cryptography, pins an HTTPS issuer and resource audience, allows RS256 only, and validates token expiry, issue/not-before times and a bounded lifetime. A locally pinned JWKS file is re-read for key rotation; token-supplied URLs are never fetched. Accept only the documented access-token profile, including Keycloak's signed `typ: Bearer`; reject identity-token indicators.

Explicit subject/client bindings map a token to an existing private local agent-grant file. The subject, issuer and client identity must match; conflicting `azp` and `client_id` values fail. Token scopes `memory:read`, `memory:write` and `memory:correct` intersect the current local grant on every request. Inactive grants deny access immediately. Neither an owner login nor caller metadata makes an agent an owner. Owner and peer grant bindings are refused. Separate bindings serve each app/API connection. Full personal-store read permission is accepted; no selective-record sharing capability is claimed.

Protected-resource metadata and standards-based 401/403 challenges are public only at the configured exact path. Ordinary MCP calls require authorization. Latest stable MCP 2026-07-28 remains supported; explicitly enabled 2025-11-25 Streamable HTTP compatibility is tested separately with an independent SDK. No silent reinterpretation of modern requests is permitted.

## Automatic synchronization and capacity

A single scheduled sync runner per local store reads private configuration and a peer-token file. Each cycle has bounded batches, rounds, request timeout and retry delay. The Store's durable causal frontier supplies the resume position; a status file is observational and never becomes graph authority. Persist backoff deadlines so restarting cannot evade `Retry-After`. Authentication, identity and semantic errors pause for operator action. Cancellation is checked between requests and before applying newly fetched groups.

Low disk space and a configured database ceiling refuse new graph writes before acknowledgement. A capacity refusal returns a named pause reason and retry guidance. The Mac retains untransferred changes; neither client retries nor restart may create duplicate operations. Capacity limits are local operational guards, not a Cloudflare invoice cap. Background cloud ingestion, model extraction and repeated whole-store maintenance are not introduced by this deployment.

## Continuous maintenance access

Use a separate private VPN identity, preferably Tailscale with ACLs permitting only SSH to the workload VM. Do not advertise the home LAN as a subnet route or grant an exit-node role. Use a dedicated unprivileged SSH account, a pinned host key and a unique credential supplied through secure environment settings. Do not paste secrets into chat. The account may inspect project logs and operate approved project paths; Docker group membership, unrestricted sudo, DSM administrator access and broad NAS shares are excluded. Any privileged deployment helper must be root-owned, fixed in purpose, and unable to read a writable arbitrary Compose definition as root.

Persistent access means a configured route and credential are available when an authorized Codex task runs. It is not an always-running agent or permission for unrelated maintenance. Access must be independently revocable. This execution environment currently has no configured VPN; the owner will provide NAS access later.

## Qualification

First reconcile the PRD, ADRs, prompt, architecture, validation and tracking documents. Then implement and run synthetic tests in the attached Linux/Docker environment. Verify JWT signature/audience/expiry/client binding, current grant revocation, real maintained-AS token issuance, legacy/modern protocol separation, public/private route separation, resumable sync/backoff, capacity refusal, non-root/read-only containers and synthetic network isolation. Record optional dependencies and actual image identities.

Actual NAS VLAN/DSM reachability, actual Mac pairing, real ChatGPT/Claude/Praxis2 connections and real-data migration remain separate evidence until executed. No NAS installation, account permission change, tunnel publication or personal-data ingestion follows merely from a successful local test.
