# Personal v1 decisions

Updated 9 November 2026. The owner's 7 November **“Proceed”** remains in force. The 9 November clarification selects client-led LLM processing, cross-provider access, simple graph review and contributor attribution under A22/A23. This records requirements and design direction; it does not claim that the new interfaces, lifecycle controls or client qualification are implemented.

| Decision | Status | Consequence |
| --- | --- | --- |
| Product identity | Accepted | RefactoredMemory; reuse this repository and the selected cloud environment. |
| V1 purpose | Accepted | One owner's personal knowledge store. People and organizations may be subjects of knowledge without becoming tenants or separate corporate owners. |
| Two personal peers (Q1) | Accepted | Both accept offline writes, query locally and synchronize. Convergence and recovery are v1 requirements. |
| First runtime pair (Q2) | Accepted | Owner's Mac plus a Linux workload on the RS822+ NAS. NAS is the normal MCP endpoint; both peers remain independently writable. DSM stays on the main LAN; isolate the workload separately. Actual NAS access/deployment remains pending. |
| MCP and target clients | Required v1 core; expanded target direction accepted 9 November | OpenAI ChatGPT/Codex, Anthropic Claude Chat/Cowork/Code, Gemini, Grok, local-model hosts/runners, Praxis and further compatible clients. Qualify each product/account independently; UI support is optional. No changes to either Praxis repository are included in this documentation update. |
| Initial import (Q5) | Required v1 | Markdown/Logseq plus data from prior LivingAtlas runs. Inventory concrete legacy generations and available artifacts before defining adapters. |
| Inferred-write policy (Q6) | Accepted | Automatically accept model-inferred additions within configured client/agent grants, without per-item human review. Preserve evidence, actor/model/derivation attribution, uncertainty, conflicts and correction history. Acceptance is not human verification or established truth. |
| Capture triggers (Q7) | Accepted | Configured clients/agents may proactively capture useful knowledge within their grants. This does not authorize arbitrary source access, continuous monitoring of unapproved sources or a separate extraction service. |
| Preferred claims (Q8) | Accepted | Prefer an explicit owner correction in answers while retaining conflicting claims, evidence and history. Preserve concurrent branches; an authorized, attributed resolution references the heads considered. Preference is not destructive overwrite or proof of truth. |
| Management surface (Q9 baseline; A23 extension) | Baseline retained; next interface direction accepted 9 November | MCP plus CLI remain useful without UI. Add a graph-centered evidence/comment/correction experience through an optional MCP App in capable hosts. The new review surface is required direction, not an implemented or qualified feature. |
| LLM processing placement (A22) | Accepted 9 November | Connected clients and authorized external runners perform model work. RM owns deterministic validation, memory, evidence, attribution, history, retrieval, grants and sync. No internal model runtime, provider credentials or autonomous processing fleet is required. |
| Memory roles (L03) | Accepted design; delivery mixed | Source records, structured temporal knowledge, derived memory and bounded working context share the graph contract. Maintained-summary freshness and richer context assembly remain further work. Roles are not trust grades or mandatory separate databases. |
| Contributor attribution and KISS review (A23) | Accepted design; further implementation required | Distinguish requester, authenticated connection, reported processor, evidence, change/admission/replication outcome and actual reviewer. Show a short attribution line, Why? and History; preserve Q6 automatic admission and Q8 scoped owner corrections. |
| Day-one workflows (Q10) | Accepted | Prove all three: retrieve project decisions and why; find relationships and their evidence; explain what changed since last month. Use synthetic end-to-end scenarios with source, time, correction and coverage fidelity. |
| Corporate ownership principle (Q3) | Retained for later phases | Organizations retain their data when people leave; people retain personal data. Corporate domain/offboarding implementation does not gate v1. |
| Product encryption and key recovery (Q4) | Deferred | No new content-encryption/key-custody system in v1. An encrypted legacy input may still need its original approved keys for import. |
| Remote app/API access | Accepted | The expanded target set uses separate revocable client grants and explicit processing/data-access boundaries. OAuth and actual client qualification are required; consumer subscriptions, one product's API support and an MCP connection do not prove another product's entitlement or unattended execution. |
| Cloudflare role | Accepted | Optional outbound tunnel only. Workers/Durable Objects storage, selective cloud replicas and third peers are deferred. No bulk cloud ingestion is required. |
| Automatic synchronization | Accepted | Bounded resumable Mac/NAS cycles, durable backoff, capacity guards, explicit paused/incomplete states and no tight-loop retries. |
| Maintenance access | Accepted design | Private VPN and dedicated unprivileged SSH account on the workload VM; no DSM administrator, Docker group or unrestricted sudo. Configure secrets through secure environment settings. |
| Documentation authority | Accepted | Repository docs are authoritative; companion Pages are reconciled. |
| Linear setup | Paused by owner | Preserve the prepared backlog under `docs/tracking/`; resume external setup only when requested. No team/projects/issues were created. Linear is not a readiness or implementation prerequisite. |
| Implementation transition | Authorized 7 November 2026 | Explicit “Proceed” received after the Q7–Q10 answers. Reconcile the accepted answers throughout the docs, then continue coordinated implementation without asking for this permission again. R09 records authorization only; remaining design/evidence work and release qualifications remain open. |

## Implemented choices and remaining evidence

- L01–L08/LM01–LM06 and A22/A23 clarify the next integration/review direction. They do not change the running service, add a background processor, enroll a client or mark an integration passed. Comments, shared processing checkpoints, a portable graph App and uniform activity/freshness controls need implementation evidence.

- Q6–Q10 are implemented in capture, preferred-claim, MCP/CLI and day-one acceptance paths. Do not reopen settled choices. Automatic/proactive capture stays inside configured grants and does not authorize a separate extraction service or source-text authority changes.
- Locate and classify prior LivingAtlas stores, logs, snapshots, exports and imported records through authorized read-only discovery. Do not guess that a source generation has been reviewed or that data is available.
- Retain the selected Python/SQLite operation contract and implemented NAS extension in NAS-CONTRACT.md. OAuth resource verification, split TLS listeners, bounded automatic sync, configured capacity guards and bounded audit logs are implemented; actual NAS isolation and provider onboarding remain unverified.
- Maintain the client version/transport matrix in MCP-CONFORMANCE.md and conversion/accounting contract in IMPORT-FORMATS.md. Missing client access or original legacy artifacts remain explicit evidence gaps.
- Finish detailed contracts, requirement-to-verification mapping and evidence collection while carrying out authorized work. Keep R06/R08 incomplete until their actual criteria are met. Raise only genuinely new consequential blockers, and continue independent work. The received “Proceed” is not a claim that all readiness or release criteria passed.
- Use synthetic data for development, tests, demonstrations and benchmarks. Live personal-data ingestion, new installations, external deployments/provisioning, credential or permission changes, agreements and private-data exposure retain their separate approval requirements.

## Deferred work

Multitenancy, corporate tenant administration, personal-versus-corporate custody, multi-organization federation, offboarding, enterprise recovery, product content encryption, protected compute, transitive relay mesh and distributed enterprise scale are later work. Keep migration considerations; do not fully design or implement them merely to complete personal v1.

The historical C22/M17 corporate fixtures and P01–P06 protected-profile gates are later. C23/M18 retain only applicable personal authority/history/restore behavior now. C24/M19 establish mandatory MCP. C14/M11 cover required source import and legacy migration. Embedded intelligence and automatic background consolidation remain future options; an optional graph MCP App is now the A23 interface direction. The PRD and ADR register contain the detailed classifications.
