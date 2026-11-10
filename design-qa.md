# Quiet Relationship Brief QA

**final result: passed**

## Tiered-map refinement, 10 November

The subsequent owner request adds outward context with partial/translucent neighbors. The concise List default remains. Map uses the existing depth1–2 API and at most16 returned nodes/edges; it does not widen a saved brief's selected answer. Solid focus, outlined direct neighbors and smaller/fainter indirect marks encode graph distance. Hover/keyboard focus/tap highlights an actual shortest path, retains edge direction and reveals the literal relationship. Focus here changes the local root; Nearby records provides a named fallback. No similarity-only edges or confidence scores are invented.

Evidence is in private run `tiered-map-20261110T081525Z`: initial/refined map captures01/02 are648×770 at1:1 density, combined in10-map-comparison.png and inspected together. The initial map hid two outer hints below the narrow viewport (P2); reducing chart height and using smaller outer marks fixed it. Desktop captures04/05 are1280×920. Narrow light/dark captures07/08 and final09 are390×914. After inspecting a42-pixel hit region in one scroll state, mobile targets were enlarged and a subsequent DOM read measured47.2pixels. No horizontal overflow was observed. Final09 was inspected at its saved size; its selected two-step path and controls remain readable without a full metadata panel.

Typography retains the existing serif names and high-contrast body/control text. Far labels are suppressed on narrow screens until selected; the named fallback and selected-record line retain full identity and relationship text. Spacing/radial position encode hop distance rather than importance. Existing light/dark tokens remain. These are functional SVG data marks, not image/decorative substitutes; no new assets/dependencies. Copy identifies faded marks as indirect, snapshots as supplied, and partial live results as bounded.

Browser checks: depth1→three direct neighbors; depth2→nine nearby records in the synthetic fixture; outer-node selection→the actual path and employment predicate; refocusing→a new root and its neighborhood; read-only live context; display-only fallback→only the three supplied neighbors. Fresh map loads/tier changes produced zero new uncaught exceptions. The List still contains only the original three selected records. Fifteen focused relationship tests passed, including the actual Node model receiving core graph results, distance/path/direction, no disconnected hints, fresh/stale/mismatched-frontier/subject/revision and budget guards. Twenty field-editor tests passed during the same refinement; builds and scans of all changed code passed. No full-suite rerun or personal deployment is claimed for this source revision. Source and synthetic preview only; personal peers/grants/data unchanged. Current final result remains passed for these compared states, with physical-device/full accessibility/provider-host qualification still separate.

## Current target and evidence

The owner's 10 November feedback supersedes the original default-open presentation: “too much distracting data” and “verbose mode.” Keep the selected ivory/teal visual language, but show the answer and relevant names first. Fields, evidence, history and the connection explanation open deliberately. The wire contract and stored knowledge remain unchanged.

Source visual references: `docs/design/relationship-brief-target.png` (original selected direction) and `docs/design/relationship-brief-implemented.png` (prior rendered baseline). Current implementation screenshot: `docs/design/relationship-brief-quiet.png`. The original screenshot's open fields/sidebar are intentionally removed from the default, rather than treated as fidelity requirements after this feedback.

The current preview is `http://127.0.0.1:59262/`, using actual RM Service calls, the official SDK AppBridge and disposable in-memory example data. Browser screenshot 1487×1098, 1 screenshot pixel per CSS pixel; its35-pixel test toolbar is cropped without scaling to1487×1058. App width1487 and scroll width1487. The prior baseline is1487×1058, with its original scrollbar retained. Theme and topic match; the default expansion state and shorter fixture copy change intentionally.

Combined full-view comparison `04-before-after.png` and focused row comparison `08-rows-comparison.png` were opened and judged with both versions in the same image. They are retained in the private commissioning run `brief-simplification-20261110T075137Z`. A current-run capture `01-before.png` separately records the large automatically displayed evidence region the user encountered; it is not presented as the same scroll state as the new default.

## Findings and fixes

- **P1: default-open fields, graph and evidence overwhelmed the selected answer.** Default selection/expansion is now empty. Opening a name reveals the existing shared fields; View connection and Map are explicit actions. Initial browser readback contains no field tabs, source excerpts, source counts or connection panel.
- **P2: each relationship repeated dates, qualifiers, source counts, reasons and Review actions.** Rows now contain one name and a short reason. Meaningful funding status and disputed identity type remain visible. Unknown/legacy investment terms stay inspectable and use “review terms” rather than implying completed funding.
- **P2: preparation and caution prose competed with results.** One saved view no longer repeats its title in a selector. Background attribution/coverage sits behind About this view. Stale-state and access limits remain explicit. A single name action replaces redundant Review/source-count actions.
- **P2: narrow rendering stacked a second verbose screen below the list.** The default has one content column and no trailing explanation. All three example records fit the narrow capture. The optional explanation can still stack when the user requests it.

No actionable P0/P1/P2 finding remains in these compared states. Earlier QA evidence remains in Git history and the private archived report; it does not claim this refinement was deployed to personal peers.

## Fidelity surfaces

- **Typography:** retained the serif product/name hierarchy, reduced heading size and changed supporting copy to compact sans-serif. Names remain readable links. The focused comparison confirms fewer competing weights and no truncation of the short examples.
- **Spacing/layout:** one centered list replaces the permanent split pane. Thin dividers, a small List/Map control and a single summary keep the original visual language. Whitespace follows the end of the answer instead of another panel of metadata.
- **Color/tokens:** existing warm paper, ink and teal remain; dark mode uses the same host tokens. Material status is written, not conveyed only by color.
- **Assets:** no new raster/decorative assets. Existing functional data SVG and icons remain. The small graph is available on request, rather than used as ambient decoration.
- **Copy/content:** fictional fixture prose is shorter and still distinguishes discussion from commitment. Real-client explanations are not automatically rewritten or summarized by RM. General fallback links remain labeled as recorded connections.

## Executed checks

- App and official-SDK reference builds passed. Fourteen relationship-brief tests and20 field-editor tests passed. These are focused checks, not a rerun of the full287-test suite for this source revision.
- Actual browser: initial compact list; click name→standard fields; Evidence tab→exact source; View connection→supporting path; Map edge→the correct record explanation; read-only fields/correction disabled; display-only initial snapshot.
- Deliberately dropped a200 response after an actual synthetic correction committed. List/Map, record navigation, field controls and View connection stayed disabled. Retry sent identical arguments/request ID and recovered the committed result. Only disposable fixture data was changed; the fixture was reset before handoff.
- Narrow390×914 browser capture: App width and scroll width both390; no horizontal overflow. Light/dark captures were inspected. Fresh normal reload produced zero new uncaught exceptions; the earlier deliberate reset is failure-injection evidence.
- Aikido scan of five changed code/fixture files reported no issues. Current git diff whitespace check passed.

## Scope and remaining polish

This refinement updates the source and synthetic preview only. The personal Mac/NAS installation remains at the prior qualified runtime; its data, grants and services were not changed. The saved brief/field API is unchanged. Actual named-provider rendering, full accessibility conformance and physical mobile behavior remain separately unverified. P3: unusually long real-world names still warrant a later focused layout pass in the optional graph.
