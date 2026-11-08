# Ongoing access to the memory workload

The preferred long-term path is **private VPN access plus a dedicated SSH identity on the isolated Linux workload VM**. It is not a public SSH port, a DSM administrator login or a general route into the home network. Tailscale is a suitable VPN when it is approved and configured on both the workload and the Codex execution environment; an existing equivalent private VPN can serve the same purpose.

The account should remain usable across authorized engineering sessions. That does not mean an agent is continuously running or monitoring the NAS. Each session still needs a live execution environment, a healthy private route, available credentials and task authorization. Monitoring or automatic unattended changes would be a separate explicitly configured service.

## Identity and network scope

- Create a dedicated unprivileged account, such as `refmem-maint`, on the workload VM. Do not reuse the owner's DSM account or personal SSH key.
- Choose a numeric UID distinct from every production runtime's effective host UID. The rootful reference uses UID 10001 for memory, 1000 for Keycloak and 70 for Postgres; UID 1000 is often an ordinary VM login. Different usernames do not prevent same-UID access to private files. Inspect actual host mappings if using rootless containers or user namespaces before assigning ownership.
- Give the Codex-side VPN identity permission to reach only the workload VM's SSH port. Do not advertise the home LAN as a subnet route or configure an exit node for this task.
- Restrict SSH access to approved VPN identities or addresses. Disable root login, password login, SSH agent forwarding and unnecessary TCP forwarding for this account.
- Pin the SSH server's host key in a dedicated known-hosts file. Verify its fingerprint through an independently trusted administrative path before the first connection. Do not use `StrictHostKeyChecking=no`.
- Store the private key or short-lived SSH credential in the execution environment's secret settings, not in chat, the repository or a Compose environment file. Public keys and host-key fingerprints are not secrets.
- Keep the VPN enrollment credential separate from the SSH identity. Prefer revocable, narrowly tagged and short-lived enrollment where the VPN supports it. Losing one engineering credential must not expose DSM or every device.

## Files and privilege

Give the account a working checkout and test directory for RefactoredMemory, and access only to service-specific diagnostics required for the task. Read permission on real memory content is a separate data-access decision; log access should not expose full source payloads or credentials.

Prefer a supported rootless container runtime inside the VM for the engineering workload. If production containers are managed by a privileged system runtime, membership in its `docker` group or access to its socket is effectively root-equivalent and is not the default access level.

For a privileged runtime, routine service control can instead use a narrow, root-owned helper that supports fixed actions such as status, restart and redacted logs for this service. The helper, its Compose configuration and every file it executes as root must be owned by root and not writable by the engineering account. It must not accept arbitrary commands, paths, environment overrides, Compose files, image names or Docker arguments. Granting sudo to `docker`, `docker compose`, a shell, or a script loaded from the writable checkout defeats this restriction.

Deployment promotion that changes privileged configuration or mounts remains an owner-controlled action. Reviewed image digests can be promoted through a fixed deployment process. Code editing and synthetic tests do not require DSM administration or a writable production data directory.

The shell conveniences and `compose.owner.yaml` profile in [NAS-COMMISSIONING](NAS-COMMISSIONING.md) are for the approved deployment operator. They deliberately perform owner operations on the private database and accept operation arguments; they are not safe substitutes for a fixed privileged helper delegated to the engineering account. Host preflight is read-only but may require the operator's permission to inspect private path ownership.

## Information needed when access is provided

Provide the workload's approved VPN hostname, SSH port, account name and verified host-key fingerprint. Enter secret credentials through the environment's secret interface. Also record the service checkout location, allowed diagnostic/control actions and the boundaries for reading real data.

For the managed Codex cloud environment, VPN setup belongs in the environment configuration. A VPN-enabled desired configuration is not proof of an established route. Verify current environment readiness, then an actual SSH connection with pinned host-key checking. Some execution environments reach private TCP endpoints through a supported forwarding proxy rather than a local VPN interface; follow that environment's documented path. Do not install a second VPN client or disable transport verification to bypass a missing route.

## Revocation and maintenance

Revoke the engineering VPN identity and SSH credential independently. Rotate credentials after suspected exposure and periodically according to the owner's policy. Record service changes and their reviewed commit/image digest. Keep a separate owner recovery path that does not depend on this account.

The first access session should verify the NAS model, exact DSM version, available RAM, Container Manager/Virtual Machine Manager availability, VLAN attachment and effective firewall behavior. The current repository does not claim those device-specific checks have passed.
