# RefactoredMemory

RefactoredMemory v1 is a single owner's personal temporal knowledge store, accessed through MCP by Praxis and other compatible clients. It runs on the owner's Mac and a personally controlled Linux VM/container; both peers accept offline writes and synchronize. Initial import covers Markdown/Logseq and data from previous LivingAtlas runs. Model-inferred additions are automatically accepted within configured client/agent grants, with their sources, uncertainty and correction history preserved; acceptance does not mean human verification.

**Status: research and documentation only. No product implementation is approved or present.** After consequential questions are resolved and the documents reconciled, implementation still requires the owner's explicit **“proceed.”**

Multitenancy, corporate-versus-personal ownership domains, multiple organizations, and product-level content encryption are later phases. Basic authentication, scoped client/peer authority, secure remote transport, safe local access and data hygiene remain v1 requirements.

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

**Linear setup is paused at the owner's request.** No Linear team, projects or issues were created in this work. The prepared backlog is kept in the repository; Linear is not a prerequisite for research, documentation or a later authorized implementation.
