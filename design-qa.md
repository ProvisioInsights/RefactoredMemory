# Relationship Brief design QA

**final result: passed**

## Evidence and state

- Source visual truth: `docs/design/relationship-brief-target.png`, the owner's selected light Relationship Brief.
- Browser-rendered implementation: `docs/design/relationship-brief-implemented.png`.
- Working synthetic host: `http://127.0.0.1:59262/`, official MCP Apps AppBridge with actual RM Service calls against a disposable in-memory store.
- Source: 1487 × 1058 pixels. Browser screenshot: 1487 × 1098 pixels at a 1487 × 1098 CSS viewport, 1 screenshot pixel per CSS pixel. The 40-pixel fixture toolbar is cropped, without scaling, to 1487 × 1058. The App's scrolling content area is 1472 × 1058 CSS pixels; its 15-pixel scrollbar is retained.
- Matched state: light theme, the three fictional people shown, Avery selected, Fields open, small supporting path and evidence beside it. Fixture counts and actual assertion predicates differ deliberately from conceptual text; no personal data is in either image.
- Full-view combined comparison: private `final-light-comparison.png`; source and implementation were opened together in the same comparison image. Focused field comparison: private `final-fields-comparison.png`. Captures live in the private commissioning run `relationship-brief-20261110T060734Z` outside Git.

## Findings and comparison history

1. **P2, first comparison: repeated field metadata displaced the other primary people below the fold.** Fixed with the same shared field editor's compact summary, one explicit review action, type badges and evidence/history on demand. The third and final captures show Avery, Jordan and Morgan together at the target viewport.
2. **P2, first comparison: the preparation/control stack competed with the answer.** Shortened the view selector and kept record creation on Records. Brief/Connections and prepared-view controls now appear only on Explore. Final browser readback verified populated and empty type filters and read-only creation being disabled.
3. **P2, first comparison: compact graph labels overlapped and names extended beyond their nodes.** Bounded the selected path, split names into readable lines and allocated separate relationship labels. The final full-view comparison shows three real identities and three actual assertion edges without label collisions.
4. **P2, source review: malformed display-only snapshots could throw during rendering.** Guarded group/item members and validated the graph envelope and directly rendered text before replacing state. Actual JavaScript fixture regressions reject malformed entities, claims and attribution. This fix changes no visible normal-state layout.

No actionable P0/P1/P2 finding remains in the compared states.

## Required fidelity surfaces

- **Typography:** retained the source's editorial serif hierarchy for the product name, answer, groups and names, paired with compact sans-serif controls and metadata. Full and focused comparisons confirm readable weights, wrapping and hierarchy. Small annotations are slightly more compact than the concept to accommodate real field/provenance information.
- **Spacing and layout:** ivory canvas, horizontal navigation, approximately two-thirds records and one-third explanation, thin dividers and modest rounding follow the selected composition. Fields remain inline; no conversation navigation was introduced. Additional evidence naturally scrolls.
- **Colors:** warm light surface, dark ink, muted secondary text and teal action/selection states match the intended palette. Host-selected dark mode was separately captured and inspected; meaning is also written in labels.
- **Images/assets:** this screen contains no photographic or illustrative assets. Existing library icons are reused. The path is a functional SVG rendering of actual graph data, not a substitute raster illustration or invented decorative network. Captures are sharp at 1:1 density.
- **Copy/content:** actual predicates, source-reference counts, uncertainty and attributed client interpretation replace the mock's implied certainty. “Funding discussed” does not mean completed funding; unknown amounts remain explicit. “Prepared view” selects saved client output, not an internal AI process.

## Interaction and responsive checks

Browser checks exercised search, Records, actual type filtering and empty state, row collapse/reopen, shared fields, evidence, history, minimal record creation and correction. A deliberately lost response after a committed save kept the form locked; retry sent identical arguments/request ID, recovered the receipt, and withheld the now-stale explanation. A late host result remained queued and was freshly read before opening. Display-only and actual read-only grants were checked separately. All edits used disposable synthetic data.

Narrow browser viewport 390 × 914 produced a 375 × 844 CSS App content area with equal client and scroll widths: no horizontal overflow. Host light/dark themes were inspected. Fresh normal reload produced zero new uncaught browser exceptions. Earlier deliberate connection-reset errors belong to the unknown-outcome test; they are not described as ordinary runtime success. These are browser/reference-host checks, not physical-device or named-provider qualification.

## Implementation checklist

- [x] Match the selected light hierarchy and native, bounded connection path.
- [x] Reuse core fields and existing authenticated CRUD semantics.
- [x] Preserve uncertainty, immutable history and current grant enforcement.
- [x] Test pending/unknown saves, stale client output and malformed snapshots.
- [x] Verify desktop, narrow, dark, display-only, read-only and empty states.
- [x] Keep the synthetic preview independent of personal stores.

## Follow-up polish and gaps

P3: adjust spacing for unusually long real-world names after actual use; keep their full identity accessible. Named ChatGPT, Codex, Claude and Praxis App rendering and physical mobile behavior remain separate qualification tasks. Source/browser acceptance does not itself establish a private installation upgrade.
