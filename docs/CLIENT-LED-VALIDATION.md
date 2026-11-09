# Client-led workspace qualification

Executed on the owner's Mac on 9 November 2026 against fresh synthetic stores.
The implementation remains provider-independent and makes no internal model call.

| Requirement | Executed evidence | Limit |
| --- | --- | --- |
| LM01 | Real Service task→claim→checkpoint→attributed brief→completion; malformed and out-of-grant writes rejected | Synthetic external-processor fixture; no provider called |
| LM02 | Independent installed MCP SDK stdio flows, modern/legacy resource discovery and authenticated reads; offline peer fixed-frontier parity | Named hosted products are untested |
| LM03 | Verified connection versus reported model, activity filter, owner spoof/revocation denial, revision-scoped actual owner review | Historical missing model metadata remains unknown |
| LM04 | Pinned assertion/source bytes and frontier, correction marks brief stale, stale task output denied | No inferred source-version relationship across unrelated IDs |
| LM05 | Browser graph edge→evidence→comment→owner review→correction→history; real SDK AppBridge comment round trip; display-only host disables reads/writes | Reference host is synthetic, not installed Praxis/ChatGPT qualification |
| LM06 | Stable request replay, 110 checkpoints, concurrent SQLite claims, offline conflicting claims and owner resolution, restart/restore and revoked authority | No unattended worker was installed |

Validation commands:

- `operator/mcp-test-venv/bin/python -m unittest discover -s tests -v`:
  227 tests, 224 passed, three Linux address-space tests skipped on macOS.
- `python3 -m unittest tests.test_workspace -v`: 18 passed, including activity
  pagination without skipped operations and modern/legacy fixed resource checks.
- `python3 -m unittest tests.test_review_host -v`: six passed for key/session,
  origin/host/cross-site boundary, read-only/revoked grants, bounded requests,
  malformed routes and real comment readback.
- `npm run build` and `npm run build:reference`: passed.
- `npm audit --omit=dev`: zero known vulnerabilities at execution.
- Aikido scans of generated/changed source, tests and bundled resource: clear
  after replacing the demo's production-mode-sensitive assertion.

Local browser QA used the built-in browser. The ImageGen concept was compared
with the final 1488×1058 render using `view_image`. The white canvas, cool-gray
navigation, teal states, serif heading/sans controls, open graph and evidence
inspector were retained. Edge hit areas and node collisions were fixed; the
inspector and navigation proportions were aligned at desktop width. Evidence
source counts, revision review, boundedness and source-reference disclosures are
intentional additions required for honest memory review. Registered predicates
replace concept-only invented financial relationship names. Dynamic graph
positions and actual claim copy are data-driven, not a fixed illustrative image.

Responsive DOM checks at 390px showed 390px document/scroll width, with navigation
wrapping and inspector below the graph. The browser's emulated screenshot scaling
was inconsistent, so these checks do not certify a physical mobile device.
Temporary viewport/developer overrides were reset after QA.

This release does not establish live hosted app/API OAuth eligibility, public
Cloudflare publication, Gemini/Grok/local-model processing, or Praxis embedding.
Those require separate actual host/account tests and authorized data boundaries.
No personal-data rewrite, re-import or synthetic test insertion into personal
stores is part of qualification. Private deployment receipts record live peer
versions, backup consistency, unchanged record digests and operational checks.
