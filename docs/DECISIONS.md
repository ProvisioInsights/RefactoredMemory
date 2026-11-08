# Personal v1 decisions

Updated 7 November 2026. The owner answered Q7–Q10 and explicitly said **“Proceed”** on this date. Implementation of the agreed personal-v1 scope is authorized. This records scope and authorization; it does not claim that implementation, contracts, evidence collection or qualification are complete.

| Decision | Status | Consequence |
| --- | --- | --- |
| Product identity | Accepted | RefactoredMemory; reuse this repository and the selected cloud environment. |
| V1 purpose | Accepted | One owner's personal knowledge store. People and organizations may be subjects of knowledge without becoming tenants or separate corporate owners. |
| Two personal peers (Q1) | Accepted | Both accept offline writes, query locally and synchronize. Convergence and recovery are v1 requirements. |
| First runtime pair (Q2) | Accepted | Owner's Mac plus a Linux workload on the RS822+ NAS. NAS is the normal MCP endpoint; both peers remain independently writable. DSM stays on the main LAN; isolate the workload separately. Actual NAS access/deployment remains pending. |
| MCP | Required v1 | Latest published stable revision; Praxis2 is the confirmed target. No changes to either Praxis repository. Separate standards conformance and independent-client results from actual installed-Praxis2 validation, which remains unverified until a compatible connection is available. |
| Initial import (Q5) | Required v1 | Markdown/Logseq plus data from prior LivingAtlas runs. Inventory concrete legacy generations and available artifacts before defining adapters. |
| Inferred-write policy (Q6) | Accepted | Automatically accept model-inferred additions within configured client/agent grants, without per-item human review. Preserve evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history. Acceptance is not human verification or established truth. |
| Capture triggers (Q7) | Accepted | Configured clients/agents may proactively capture useful knowledge within their grants. This does not authorize arbitrary source access, continuous monitoring of unapproved sources or a separate extraction service. |
| Preferred claims (Q8) | Accepted | Prefer an explicit owner correction in answers while retaining conflicting claims, evidence and history. Preserve concurrent branches; an authorized, attributed resolution references the heads considered. Preference is not destructive overwrite or proof of truth. |
| Management surface (Q9) | Accepted | MCP plus CLI first. No browser UI is required in v1; richer graphical exploration remains later. |
| Day-one workflows (Q10) | Accepted | Prove all three: retrieve project decisions and why; find relationships and their evidence; explain what changed since last month. Use synthetic end-to-end scenarios with source, time, correction and coverage fidelity. |
| Corporate ownership principle (Q3) | Retained for later phases | Organizations retain their data when people leave; people retain personal data. Corporate domain/offboarding implementation does not gate v1. |
| Product encryption and key recovery (Q4) | Deferred | No new content-encryption/key-custody system in v1. An encrypted legacy input may still need its original approved keys for import. |
| Remote app/API access | Accepted | OpenAI and Anthropic apps plus APIs; full personal-store read within separate revocable agent grants. OAuth and actual client qualification are required; consumer subscriptions do not prove native-tunnel eligibility. |
| Cloudflare role | Accepted | Optional outbound tunnel only. Workers/Durable Objects storage, selective cloud replicas and third peers are deferred. No bulk cloud ingestion is required. |
| Automatic synchronization | Accepted | Bounded resumable Mac/NAS cycles, durable backoff, capacity guards, explicit paused/incomplete states and no tight-loop retries. |
| Maintenance access | Accepted design | Private VPN and dedicated unprivileged SSH account on the workload VM; no DSM administrator, Docker group or unrestricted sudo. Configure secrets through secure environment settings. |
| Documentation authority | Accepted | Repository docs are authoritative; companion Pages are reconciled. |
| Linear setup | Paused by owner | Preserve the prepared backlog under `docs/tracking/`; resume external setup only when requested. No team/projects/issues were created. Linear is not a readiness or implementation prerequisite. |
| Implementation transition | Authorized 7 November 2026 | Explicit “Proceed” received after the Q7–Q10 answers. Reconcile the accepted answers throughout the docs, then continue coordinated implementation without asking for this permission again. R09 records authorization only; remaining design/evidence work and release qualifications remain open. |

## Implemented choices and remaining evidence

- Q6–Q10 are implemented in capture, preferred-claim, MCP/CLI and day-one acceptance paths. Do not reopen settled choices. Automatic/proactive capture stays inside configured grants and does not authorize a separate extraction service or source-text authority changes.
- Locate and classify prior LivingAtlas stores, logs, snapshots, exports and imported records through authorized read-only discovery. Do not guess that a source generation has been reviewed or that data is available.
- Retain the selected Python/SQLite operation contract and implemented NAS extension in NAS-CONTRACT.md. OAuth resource verification, split TLS listeners, bounded automatic sync, configured capacity guards and bounded audit logs are implemented; actual NAS isolation and provider onboarding remain unverified.
- Maintain the client version/transport matrix in MCP-CONFORMANCE.md and conversion/accounting contract in IMPORT-FORMATS.md. Missing client access or original legacy artifacts remain explicit evidence gaps.
- Finish detailed contracts, requirement-to-verification mapping and evidence collection while carrying out authorized work. Keep R06/R08 incomplete until their actual criteria are met. Raise only genuinely new consequential blockers, and continue independent work. The received “Proceed” is not a claim that all readiness or release criteria passed.
- Use synthetic data for development, tests, demonstrations and benchmarks. Live personal-data ingestion, new installations, external deployments/provisioning, credential or permission changes, agreements and private-data exposure retain their separate approval requirements.

## Deferred work

Multitenancy, corporate tenant administration, personal-versus-corporate custody, multi-organization federation, offboarding, enterprise recovery, product content encryption, protected compute, transitive relay mesh and distributed enterprise scale are later work. Keep migration considerations; do not fully design or implement them merely to complete personal v1.

The historical C22/M17 corporate fixtures and P01–P06 protected-profile gates are later. C23/M18 retain only applicable personal authority/history/restore behavior now. C24/M19 establish mandatory MCP. C14/M11 cover required source import and legacy migration. The PRD and ADR register contain the detailed classifications.
