"""Reproducible synthetic benchmark of the actual RefactoredMemory contract.

Run from the repository root: python -m benchmarks.personal_store --entities 1100
No comparator or production capacity claim is made by this benchmark.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import sqlite3
import statistics
import subprocess
import tempfile
import time

from refactoredmemory.store import Store


def summarize(samples: list[float]) -> dict:
    ordered = sorted(samples)
    return {
        "samples_ms": samples,
        "count": len(samples),
        "p50_ms": statistics.median(samples),
        "p95_ms": ordered[max(0, math.ceil(len(samples) * .95) - 1)],
        "total_ms": sum(samples),
    }


def measure(fn):
    start = time.perf_counter_ns()
    value = fn()
    return (time.perf_counter_ns() - start) / 1_000_000, value


def code_identity() -> dict:
    root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for file in sorted((root / "refactoredmemory").glob("*.py")):
        digest.update(file.name.encode())
        digest.update(b"\0")
        digest.update(file.read_bytes())
    result = {"python_sources_sha256": digest.hexdigest()}
    try:
        result["commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        result["working_tree_dirty"] = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        result["commit"] = "unavailable"
    return result


def pair(left: Store, right: Store):
    left_id, right_id = left.identity(), right.identity()
    left.admit_peer(right_id["peer_id"], right_id["key_hex"])
    right.admit_peer(left_id["peer_id"], left_id["key_hex"])


def transfer(sender: Store, recipient: Store) -> dict:
    batches = operations = bytes_sent = 0
    while True:
        batch = sender.export_operations(recipient.status()["frontier"], limit=100)
        if not batch["operations"]:
            break
        receipt = recipient.receive(batch["operations"], sender.status()["peer_id"])
        assert receipt["pending"] == 0, receipt
        batches += 1
        operations += len(batch["operations"])
        bytes_sent += len(json.dumps(batch["operations"], separators=(",", ":")).encode())
        if not batch["more"]:
            break
    return {"batches": batches, "operations": operations, "json_payload_bytes": bytes_sent}


def benchmark(entities: int = 1100, samples: int = 31) -> dict:
    with tempfile.TemporaryDirectory(prefix="refactoredmemory-benchmark-") as directory:
        base = Path(directory)
        database = base / "primary.sqlite3"
        primary = Store(database, store_id="synthetic-benchmark", peer_id="benchmark-a")
        secondary = Store(base / "secondary.sqlite3", store_id="synthetic-benchmark", peer_id="benchmark-b")
        try:
            pair(primary, secondary)
            primary.submit([{"type": "source", "id": "source", "uri": "synthetic://benchmark",
                             "content": "Synthetic benchmark evidence only.", "metadata": {"synthetic": True}}])
            seed_times = []
            for first in range(0, entities, 50):
                actions = []
                for index in range(first, min(first + 50, entities)):
                    actions.extend([
                        {"type": "entity", "id": f"entity-{index}", "entity_type": "project", "label": f"Synthetic project {index}"},
                        {"type": "assertion", "id": f"claim-{index}", "subject": f"entity-{index}", "predicate": "decision",
                         "value": f"Synthetic decision {index}", "source_ids": ["source"], "valid_from": "2026-01-01",
                         "time_precision": "day"},
                    ])
                duration, _ = measure(lambda a=actions: primary.submit(a))
                seed_times.append(duration)
            seed_frontier = primary.status()["frontier"]
            seed_position = primary.status()["known_position"]
            assert len(primary.query(subject="entity-0")["assertions"]) == 1
            write_times = []
            for index in range(min(samples, entities)):
                action = {"type": "assertion", "id": f"corrected-{index}", "subject": f"entity-{index}", "predicate": "decision",
                          "value": f"Corrected synthetic decision {index}", "source_ids": ["source"], "valid_from": "2026-01-01",
                          "time_precision": "day", "kind": "correct", "predecessors": [f"claim-{index}"],
                          "reason": "Synthetic owner correction"}
                duration, _ = measure(lambda a=action: primary.submit([a]))
                write_times.append(duration)
            chain = [{"type": "assertion", "id": f"edge-{i}", "subject": f"entity-{i}", "predicate": "related_to",
                      "object": f"entity-{i + 1}", "source_ids": ["source"], "valid_from": "2026-01-01", "time_precision": "day"}
                     for i in range(min(entities - 1, 20))]
            primary.submit(chain)
            query_times, historical_times, search_times, traverse_times = [], [], [], []
            for index in range(samples):
                subject = f"entity-{(index * 37) % entities}"
                elapsed, answer = measure(lambda s=subject: primary.query(subject=s, predicate="decision"))
                assert len(answer["assertions"]) == 1
                query_times.append(elapsed)
                elapsed, answer = measure(lambda s=subject: primary.query(subject=s, predicate="decision", known_at=seed_position))
                assert len(answer["assertions"]) == 1
                assert answer["assertions"][0]["id"].startswith("claim-")
                historical_times.append(elapsed)
                elapsed, answer = measure(lambda: primary.query(text="Corrected", predicate="decision", limit=1000))
                assert len(answer["assertions"]) == min(samples, entities)
                search_times.append(elapsed)
                elapsed, graph = measure(lambda: primary.traverse("entity-0", depth=4, limit=100))
                assert len(graph["edges"]) >= 4
                traverse_times.append(elapsed)
            sync_ms, transfer_result = measure(lambda: transfer(primary, secondary))
            for index in (0, entities - 1):
                left = primary.query(subject=f"entity-{index}", predicate="decision", frontier=seed_frontier)
                right = secondary.query(subject=f"entity-{index}", predicate="decision", frontier=seed_frontier)
                assert [a["value"] for a in left["assertions"]] == [a["value"] for a in right["assertions"]]
            before = primary.query(subject="entity-0")
            rebuild_ms, _ = measure(primary.rebuild)
            assert primary.query(subject="entity-0") == before
            backup_ms, _ = measure(lambda: primary.backup(base / "snapshot.sqlite3"))
            restore_ms, restored = measure(lambda: Store.restore(base / "snapshot.sqlite3", base / "restored.sqlite3"))
            try:
                assert [a["value"] for a in restored.query(subject="entity-0", predicate="decision")["assertions"]] == [a["value"] for a in primary.query(subject="entity-0", predicate="decision")["assertions"]]
            finally:
                restored.close()
            status = primary.status()
            storage_bytes = {suffix or "database": (Path(str(database) + suffix).stat().st_size if Path(str(database) + suffix).exists() else 0)
                             for suffix in ("", "-wal", "-shm")}
            primary.close()
            reopen_ms, primary = measure(lambda: Store(database))
            assert primary.status()["known_position"] == status["known_position"]
            with sqlite3.connect(database) as connection:
                journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
            return {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "synthetic_only": True,
                "code": code_identity(),
                "environment": {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
                                "os": platform.system(), "os_release": platform.release(), "architecture": platform.machine(),
                                "filesystem_block_bytes": __import__("os").statvfs(base).f_bsize,
                                "peak_rss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                "peak_rss_unit": "bytes" if platform.system() == "Darwin" else "KiB"},
                "workload": {"entities": entities, "initial_assertions": entities, "owner_corrections": len(write_times),
                             "relationship_edges": len(chain), "query_samples": samples, "seed_entities_per_transaction": 50,
                             "single_write_actions": 1, "read_cache": "warm after writes; no OS cache flushing",
                             "sync": "in-process signed operation transfer; excludes HTTP/TLS/network latency",
                             "journal_mode": journal_mode, "contract_synchronous": "FULL",
                             "group_limit": 500, "history_selection": "named local position and shared causal frontier"},
                "measurements": {"seed_transactions": summarize(seed_times), "acknowledged_single_corrections": summarize(write_times),
                                 "current_subject_reads": summarize(query_times), "historical_subject_reads": summarize(historical_times),
                                 "text_search": summarize(search_times), "four_hop_traversal": summarize(traverse_times),
                                 "signed_sync_ms": sync_ms, "signed_sync": transfer_result, "rebuild_ms": rebuild_ms,
                                 "backup_ms": backup_ms, "restore_ms": restore_ms, "reopen_ms": reopen_ms,
                                 "primary_observed_file_bytes": storage_bytes},
                "correctness": "Subject/current/historical results, four-hop traversal, shared-frontier convergence, rebuild, restore and reopen assertions passed.",
                "limits": ["One Linux/container run does not qualify the owner's Mac.",
                           "No engine comparison, physical power-loss proof, enterprise scale or production capacity claim.",
                           "Latency includes the current Python graph contract and integrity checks; workloads differ from the historical selective-read benchmark."],
            }
        finally:
            primary.close()
            secondary.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entities", type=int, default=1100)
    parser.add_argument("--samples", type=int, default=31)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 10 <= args.entities <= 100_000:
        parser.error("--entities must be between 10 and 100000")
    if not 3 <= args.samples <= 1000:
        parser.error("--samples must be between 3 and 1000")
    result = benchmark(args.entities, args.samples)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
