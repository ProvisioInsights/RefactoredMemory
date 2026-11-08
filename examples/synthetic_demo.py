"""Run the three accepted personal-memory journeys with synthetic data only.

    python -m examples.synthetic_demo

The default store lives in a temporary directory. --database requires a new path.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile

from refactoredmemory.store import Store


def run_demo(store: Store) -> dict:
    initial = store.submit([
        {"type": "entity", "id": "owner", "entity_type": "person", "label": "Synthetic owner"},
        {"type": "entity", "id": "rae", "entity_type": "person", "label": "Rae"},
        {"type": "entity", "id": "northstar", "entity_type": "project", "label": "Northstar"},
        {"type": "source", "id": "meeting-note", "uri": "synthetic://northstar-meeting",
         "content": "Rae introduced me to Northstar. We chose local persistence so notes remain available offline.",
         "metadata": {"synthetic": True}},
        {"type": "assertion", "id": "decision", "subject": "northstar", "predicate": "decision",
         "value": "Use local persistence", "source_ids": ["meeting-note"], "valid_from": "2026-10-01",
         "time_precision": "day", "provenance": {"method": "model_inference", "model": "synthetic-model",
          "rationale": "Keep notes available while either personal peer is offline."}, "uncertainty": "inferred"},
        {"type": "assertion", "id": "met-rae", "subject": "owner", "predicate": "knows", "object": "rae",
         "source_ids": ["meeting-note"], "valid_from": "2026-10-01", "time_precision": "day"},
        {"type": "assertion", "id": "rae-project", "subject": "rae", "predicate": "introduced_project",
         "object": "northstar", "source_ids": ["meeting-note"], "valid_from": "2026-10-01", "time_precision": "day"},
    ], actor={"id": "synthetic-capture-client", "kind": "agent"}, request_id="synthetic-demo-seed")
    store.submit([
        {"type": "source", "id": "owner-note", "uri": "synthetic://owner-correction",
         "content": "Correction: we decided on SQLite transactions, not just unspecified local files.",
         "metadata": {"synthetic": True}},
        {"type": "assertion", "id": "decision-corrected", "subject": "northstar", "predicate": "decision",
         "value": "Use SQLite transactions", "source_ids": ["owner-note"], "valid_from": "2026-10-01",
         "time_precision": "day", "kind": "correct", "predecessors": ["decision"],
         "reason": "Explicit owner clarification of the project decision."},
    ], actor={"id": "synthetic-owner", "kind": "owner"}, request_id="synthetic-demo-correction")
    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    return {
        "synthetic_only": True,
        "project_decision_and_why": {
            "current": store.query(subject="northstar", predicate="decision"),
            "before_correction": store.query(subject="northstar", predicate="decision", known_at=initial["known_position"]),
            "original_evidence": store.get_source("meeting-note"),
            "correction_evidence": store.get_source("owner-note"),
        },
        "how_do_i_know_this_person": store.traverse("owner", depth=2),
        "what_changed_since_last_month": {"since_receipt_time": month_ago, "changes": store.history(since=month_ago)},
        "correction_since_named_position": store.history(since=initial["known_position"]),
        "status": store.status(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, help="Optional new synthetic database path; existing files are refused")
    args = parser.parse_args()
    if args.database:
        if args.database.exists():
            parser.error("--database must be a new path; this demo does not modify an existing store")
        args.database.parent.mkdir(parents=True, exist_ok=True)
        with Store(args.database) as store:
            print(json.dumps(run_demo(store), indent=2, sort_keys=True))
    else:
        with tempfile.TemporaryDirectory(prefix="refactoredmemory-demo-") as directory:
            with Store(Path(directory) / "synthetic.sqlite3") as store:
                print(json.dumps(run_demo(store), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
