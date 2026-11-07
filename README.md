# RefactoredMemory

RefactoredMemory v1 is a single owner's personal temporal knowledge store, accessed through MCP by Praxis2 and other compatible clients. It runs on the owner's Mac and a personally controlled Linux VM/container; both peers accept offline writes and synchronize. Initial import covers Markdown/Logseq and data from previous LivingAtlas runs. Model-inferred additions are automatically accepted within configured client/agent grants, with their sources, uncertainty and correction history preserved; acceptance does not mean human verification.

**Status: personal-v1 implementation, under qualification.** The temporal graph, MCP server, CLI, Markdown/Logseq and legacy adapters, direct offline peer sync, and verified backup/recovery are implemented. Synthetic Linux tests, hosted Ubuntu/macOS CI and an actual independent MCP SDK pass. The owner's Mac and installed Praxis2 application still require end-to-end qualification; legacy archive fidelity limits are explicit. No changes are made to either Praxis repository. HTTP uses preconfigured bearer grants; OAuth-only hosts are not yet supported. See [acceptance evidence](docs/ACCEPTANCE-RESULTS.md) and the [runbook](docs/RUNBOOK.md).

Multitenancy, corporate-versus-personal ownership domains, multiple organizations, and product-level content encryption are later phases. Basic authentication, scoped client/peer authority, secure remote transport, safe local access and data hygiene remain v1 requirements.

## Run it

Python 3.12+ is required; the runtime uses only the standard library. From this checkout:

```sh
python3 -m unittest discover -s tests -v
python3 -m examples.synthetic_demo
python3 -m refactoredmemory --db /tmp/refactoredmemory-demo.sqlite3 init
python3 -m refactoredmemory --db /tmp/refactoredmemory-demo.sqlite3 status
```

The synthetic demo uses a temporary database. The runbook covers private client grants, MCP connection configuration, two-peer pairing, TLS, imports, backups and recovery. Proactive capture is initiated by an authorized MCP client; the server does not watch unrelated conversations or call a model. Explicit owner corrections remain preferred while conflicting claims remain inspectable.

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
