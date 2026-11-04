#!/usr/bin/env python3
"""Migrate legacy Wyckoff Event CSV to a conservative normalized event ledger.

This migration intentionally does NOT invent cycle_id, attempt_id, candidate_id,
feature snapshots, UTC timestamps, or outcome labels. It preserves legacy IDs and
marks fields that cannot be recovered from the legacy event log as unknown.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = {
    "ServerTime",
    "EA_Version",
    "Symbol",
    "InitialBalance",
    "SetupID",
    "Direction",
    "Event",
    "Details",
    "RangeHigh",
    "RangeLow",
    "PositionID",
}

OUTPUT_COLUMNS = [
    "event_id",
    "event_type",
    "symbol",
    "direction",
    "server_time_raw",
    "server_timezone",
    "event_time_utc",
    "source_bar_open_utc",
    "source_bar_close_utc",
    "available_at_utc",
    "decision_time_utc",
    "range_id",
    "group_id",
    "cycle_id",
    "attempt_id",
    "candidate_id",
    "decision_id",
    "trade_id",
    "legacy_setup_id",
    "legacy_position_id",
    "ea_version",
    "initial_balance",
    "range_high",
    "range_low",
    "details",
    "source_path",
    "source_row_number",
    "source_file_sha256",
    "timestamp_semantics",
    "range_identity_basis",
]


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw[:2] in (bytes((255, 254)), bytes((254, 255))):
        return raw.decode("utf-16")
    return raw.decode("utf-8-sig")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_source(path: Path) -> tuple[list[dict[str, str]], str]:
    raw = path.read_bytes()
    text = read_text(path)
    reader = csv.DictReader(text.splitlines())
    fieldnames = set(reader.fieldnames or [])
    missing = sorted(REQUIRED_COLUMNS - fieldnames)
    if missing:
        raise ValueError(f"Missing required CSV columns: {missing}")
    rows = list(reader)
    if not rows:
        raise ValueError("Source CSV has no data rows.")
    for index, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"Malformed CSV row {index}: extra fields detected.")
        if not row.get("Event"):
            raise ValueError(f"Malformed CSV row {index}: Event is empty.")
    return rows, sha256_bytes(raw)


def normalize_row(
    row: dict[str, str],
    row_number: int,
    source_path: str,
    source_sha256: str,
) -> dict[str, str]:
    symbol = (row.get("Symbol") or "").strip()
    ea_version = (row.get("EA_Version") or "").strip()
    legacy_setup_id = (row.get("SetupID") or "").strip()
    event_type = (row.get("Event") or "").strip()
    server_time = (row.get("ServerTime") or "").strip()

    try:
        setup_number = int(legacy_setup_id)
    except (TypeError, ValueError):
        setup_number = 0

    # The source EA increments g_setupCounter when a Range is found. This ID
    # therefore identifies the legacy Range/state-machine context, not a trade
    # candidate or independent Spring/UTAD attempt.
    range_id = ""
    identity_basis = "UNRESOLVED"
    if setup_number > 0 and symbol and ea_version:
        range_id = f"LEGACY_RANGE:{ea_version}:{symbol}:{setup_number}"
        identity_basis = "LEGACY_SETUP_COUNTER_RANGE_LEVEL"

    canonical_row = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    event_seed = f"{source_sha256}|{row_number}|{canonical_row}".encode("utf-8")
    event_id = hashlib.sha256(event_seed).hexdigest()

    return {
        "event_id": event_id,
        "event_type": event_type,
        "symbol": symbol,
        "direction": (row.get("Direction") or "").strip(),
        "server_time_raw": server_time,
        "server_timezone": "UNKNOWN",
        "event_time_utc": "",
        "source_bar_open_utc": "",
        "source_bar_close_utc": "",
        "available_at_utc": "",
        "decision_time_utc": "",
        "range_id": range_id,
        "group_id": range_id,
        "cycle_id": "",
        "attempt_id": "",
        "candidate_id": "",
        "decision_id": "",
        "trade_id": "",
        "legacy_setup_id": legacy_setup_id,
        "legacy_position_id": (row.get("PositionID") or "").strip(),
        "ea_version": ea_version,
        "initial_balance": (row.get("InitialBalance") or "").strip(),
        "range_high": (row.get("RangeHigh") or "").strip(),
        "range_low": (row.get("RangeLow") or "").strip(),
        "details": (row.get("Details") or "").strip(),
        "source_path": source_path,
        "source_row_number": str(row_number),
        "source_file_sha256": source_sha256,
        "timestamp_semantics": "LEGACY_SERVER_LOG_TIME_NOT_UTC_OR_SOURCE_BAR_TIME",
        "range_identity_basis": identity_basis,
    }


def migrate(source: Path, output_dir: Path) -> dict[str, Any]:
    rows, source_hash = parse_source(source)
    source_rel = str(source)
    normalized = [
        normalize_row(row, idx, source_rel, source_hash)
        for idx, row in enumerate(rows, start=2)
    ]
    output_dir.mkdir(parents=True, exist_ok=True)

    ledger_path = output_dir / "events_normalized.csv"
    with ledger_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(normalized)

    event_counts = Counter(row["event_type"] for row in normalized)
    range_ids = sorted({row["range_id"] for row in normalized if row["range_id"]})
    manifest: dict[str, Any] = {
        "schema_version": "1.1-draft",
        "migration_name": "legacy_wyckoff_event_csv_v1",
        "source_path": source_rel,
        "source_sha256": source_hash,
        "source_rows": len(rows),
        "normalized_rows": len(normalized),
        "event_type_counts": dict(sorted(event_counts.items())),
        "unique_legacy_range_ids": len(range_ids),
        "candidate_ids_created": 0,
        "cycle_ids_created": 0,
        "attempt_ids_created": 0,
        "decision_ids_created": 0,
        "trade_ids_created": 0,
        "feature_snapshots_created": 0,
        "labels_created": 0,
        "timestamp_policy": {
            "server_time_raw_preserved": True,
            "server_timezone": "UNKNOWN",
            "event_time_utc_created": False,
            "source_bar_times_created": False,
            "available_at_created": False,
            "decision_time_created": False,
            "reason": "Legacy CSV does not contain timezone/offset or source-bar availability timestamps; source EA logs TimeCurrent()."
        },
        "identity_policy": {
            "legacy_setup_id_preserved": True,
            "range_id_synthesized": True,
            "range_id_basis": "Source EA increments g_setupCounter when RANGE_FOUND is created.",
            "candidate_id_inferred": False,
            "cycle_id_inferred": False,
            "attempt_id_inferred": False,
            "trade_id_inferred": False,
            "legacy_position_id_preserved": True
        },
        "limitations": [
            "This is an Event Ledger migration only, not an ML training dataset.",
            "No candidate_id, cycle_id, attempt_id, feature snapshot, or outcome label is inferred.",
            "Server timestamps are retained as raw broker/server strings; they are not converted to UTC.",
            "Legacy SetupID maps to a Range/state-machine context, not an independent Candidate.",
            "Legacy PositionID is preserved but not promoted to trade_id without a verified order/deal join."
        ],
        "output_file": ledger_path.name,
        "output_sha256": sha256_bytes(ledger_path.read_bytes())
    }
    manifest_path = output_dir / "migration_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    manifest = migrate(args.input, args.output_dir)
    print(json.dumps({
        "status": "PASS",
        "source_rows": manifest["source_rows"],
        "normalized_rows": manifest["normalized_rows"],
        "unique_legacy_range_ids": manifest["unique_legacy_range_ids"],
        "candidate_ids_created": manifest["candidate_ids_created"],
        "labels_created": manifest["labels_created"],
        "output_file": manifest["output_file"],
        "output_sha256": manifest["output_sha256"]
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
