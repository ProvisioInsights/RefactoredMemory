# Personal v1 decisions

Updated 7 November 2026. This records accepted scope, not approval to implement.

| Decision | Status | Consequence |
| --- | --- | --- |
| Product identity | Accepted | RefactoredMemory; reuse this repository and the selected cloud environment. |
| V1 purpose | Accepted | One owner's personal knowledge store. People and organizations may be subjects of knowledge without becoming tenants or separate corporate owners. |
| Two personal peers (Q1) | Accepted | Both accept offline writes, query locally and synchronize. Convergence and recovery are v1 requirements. |
| First runtime pair (Q2) | Accepted | Owner's Mac plus a personally controlled Linux VM/container. This does not authorize new external provisioning. |
| MCP | Required v1 | Latest published stable revision, verified against actual Praxis and another independent MCP client. |
| Initial import (Q5) | Required v1 | Markdown/Logseq plus data from prior LivingAtlas runs. Inventory concrete legacy generations and available artifacts before defining adapters. |
| Inferred-write policy (Q6) | Awaiting owner answer | Decide whether inferred additions await review or can be accepted automatically within a configured grant. Explicit owner requests and model inference are separate cases. |
| Corporate ownership principle (Q3) | Retained for later phases | Organizations retain their data when people leave; people retain personal data. Corporate domain/offboarding implementation does not gate v1. |
| Product encryption and key recovery (Q4) | Deferred | No new content-encryption/key-custody system in v1. An encrypted legacy input may still need its original approved keys for import. |
| Documentation authority | Accepted | Repository docs are authoritative; companion Pages are reconciled. |
| Implementation transition | Explicit gate | Updated docs and answered questions are necessary; the owner must then explicitly say “proceed.” |

## Remaining design and evidence work

- Record the inferred-write answer consistently in the PRD, ADRs, importer and MCP contracts, fixtures and execution prompt.
- Locate and classify prior LivingAtlas stores, logs, snapshots, exports and imported records through authorized read-only discovery. Do not guess that a source generation has been reviewed or that data is available.
- Select a persistence engine, peer synchronization protocol and compatible MCP SDK using evidence and the personal-v1 contract. Existing selective-read measurements do not decide these choices.
- Define the client version/transport matrix and concrete import conversion/accounting plan. Missing client access or legacy artifacts must be explicit evidence gaps.
- Finish the requirement-to-verification mapping and resolve any implementation-blocking ambiguity. Then present readiness and wait for “proceed.”

## Deferred work

Multitenancy, corporate tenant administration, personal-versus-corporate custody, multi-organization federation, offboarding, enterprise recovery, product content encryption, protected compute, transitive relay mesh and distributed enterprise scale are later work. Keep migration considerations; do not fully design or implement them merely to complete personal v1.

The historical C22/M17 corporate fixtures and P01–P06 protected-profile gates are later. C23/M18 retain only applicable personal authority/history/restore behavior now. C24/M19 establish mandatory MCP. C14/M11 cover required source import and legacy migration. The PRD and ADR register contain the detailed classifications.
