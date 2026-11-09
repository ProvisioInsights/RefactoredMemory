# RefactoredMemory

**Current design direction, 9 November 2026:** Connected LLM applications do the processing; RM owns validated memory, evidence, contributor attribution, correction history, retrieval, permissions and sync. Internal intelligence is optional future work. The [updated requirements](docs/PRD.md#client-led-processing-and-review-direction) and [A22/A23 decisions](docs/ADRS.md#a22-client-led-processing-and-provider-independent-memory-roles) define the expanded client targets, four memory roles and next graph/evidence/review interface. These are design requirements, not claims that the new UI, lifecycle or integrations are delivered.

RefactoredMemory v1 is a single owner's personal temporal knowledge store, accessed through MCP by Praxis2 and other compatible clients. It runs on the owner's Mac and a personally controlled Linux VM/container; both peers accept offline writes and synchronize. Initial import covers Markdown/Logseq and data from previous LivingAtlas runs. Model-inferred additions are automatically accepted within configured client/agent grants, with their sources, uncertainty and correction history preserved; acceptance does not mean human verification.

**Status: personal-v1 implementation, under qualification.** Implemented features include the temporal graph, MCP server, CLI, Markdown/Logseq and legacy adapters, offline peer sync, verified recovery, a maintained-AS OAuth resource profile, separate public MCP/private sync listeners, bounded automatic sync, capacity guards and bounded audit logs. The owner's Mac/NAS and installed Praxis2, ChatGPT and Claude apps/API connections still require end-to-end qualification; legacy archive fidelity limits remain explicit. No changes are made to either Praxis repository. See [current executed evidence and remaining qualification](docs/ACCEPTANCE-RESULTS.md) and the [runbook](docs/RUNBOOK.md).

The accepted deployment target is now a normally available NAS-hosted Linux peer plus the Mac peer, with Cloudflare as optional tunnel transport only. The OAuth, deployment hardening and automatic-sync implementation follows [the NAS contract](docs/NAS-CONTRACT.md). [Deployment artifacts and isolation instructions](docs/NAS-DEPLOYMENT.md) are available; an actual NAS deployment remains separate from local synthetic tests.

Multitenancy, corporate-versus-personal ownership domains, multiple organizations, and product-level content encryption are later phases. Basic authentication, scoped client/peer authority, secure remote transport, safe local access and data hygiene remain v1 requirements.

## Run it

Python 3.12+ is required. The graph, local-grant MCP and sync runtime use the standard library; the optional OAuth profile uses the declared PyJWT/cryptography dependencies. CI installs pinned test dependencies so optional interoperability checks run. From an existing prepared checkout:

```sh
python3 -m unittest discover -s tests -v
python3 -m examples.synthetic_demo
python3 -m refactoredmemory --db /tmp/refactoredmemory-demo.sqlite3 init
python3 -m refactoredmemory --db /tmp/refactoredmemory-demo.sqlite3 status
```

The synthetic demo uses a temporary database. The runbook covers private client grants, `serve-nas` OAuth/TLS listeners, `sync-watch`, two-peer pairing, imports, backups and recovery. OAuth provisioning and secure continuous maintenance are described in the [NAS deployment](docs/NAS-DEPLOYMENT.md) and [private VPN/SSH access](docs/REMOTE-ADMIN.md) guides. Proactive capture is initiated by an authorized MCP client; the server does not watch unrelated conversations or call a model. Explicit owner corrections remain preferred while conflicting claims remain inspectable.

## Authoritative documentation

Start with the [documentation index and reading order](docs/README.md). It distinguishes accepted scope, proposed design, open decisions and future work.

- [Product requirements](docs/PRD.md)
- [Architecture decisions](docs/ADRS.md)
- [Personal v1 architecture](docs/ARCHITECTURE.md)
- [MCP integration](docs/MCP.md)
- [Validation and migration](docs/VALIDATION.md)
- [Research and evidence](docs/RESEARCH.md)
- [Accepted decisions and open questions](docs/DECISIONS.md)
- [Execution prompt](docs/EXECUTION_PROMPT.md)
- [Repository tracking plan and paused Linear setup](docs/tracking/README.md)

The historical planning Pages are reconciled companion views. Atlas/LivingAtlas identifies the predecessor and its historical evidence. This repository replaces neither those source repositories nor their data. Development, examples and tests use synthetic data; no personal data or secrets belong in this public repository.

**Linear setup is paused at the owner's request.** No Linear team, projects or issues were created in this work. The prepared backlog is kept in the repository; Linear is not a prerequisite for research, documentation or the authorized implementation.
