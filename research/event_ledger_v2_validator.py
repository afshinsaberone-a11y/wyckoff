"""Structural and identity validator for BOOT-003 Event Ledger v2 CSV files."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_COLUMNS = [
    "SchemaVersion", "RunID", "EventID", "EventSequence",
    "EventTimeServer", "ObservedAtServer", "TimeBasis", "SourceTimeframe",
    "SourceBarOpenServer", "Symbol", "EA_Version", "RangeID", "CycleID",
    "AttemptID", "CandidateID", "DecisionID", "OrderID", "DealID", "PositionID",
    "LegacySetupID", "Direction", "Event", "DecisionStatus", "ReasonCode",
    "Details", "RangeHigh", "RangeLow", "InitialBalance",
]
_TIME_FORMAT = "%Y.%m.%d %H:%M:%S"
_RUN_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def _parse_time(value: str, field: str, line: int, errors: list[str]) -> None:
    if not value:
        errors.append(f"line {line}: {field} is blank")
        return
    try:
        datetime.strptime(value, _TIME_FORMAT)
    except ValueError:
        errors.append(f"line {line}: {field} is not YYYY.MM.DD HH:MM:SS: {value!r}")


def validate_rows(
    fieldnames: list[str] | None,
    rows: list[dict[str, str]],
    expected_run_id: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if fieldnames != SCHEMA_COLUMNS:
        errors.append("CSV header does not match the exact 28-column v2 schema/order")
        return {
            "valid": False, "errors": errors, "warnings": warnings,
            "stats": {"rows": len(rows), "columns": len(fieldnames or [])},
        }

    if not rows:
        warnings.append("CSV contains header only; no events were exported")

    seen_event_ids: set[str] = set()
    seen_decision_ids: set[str] = set()
    candidate_created: set[str] = set()
    candidate_creation_count: dict[str, int] = {}
    run_ids: set[str] = set()
    previous_sequence = 0
    event_counts: dict[str, int] = {}
    candidate_ids_seen: set[str] = set()
    decision_sequence_by_candidate: dict[str, int] = {}
    decision_count = 0
    deal_event_count = 0

    for line, row in enumerate(rows, start=2):
        run_id = (row.get("RunID") or "").strip()
        run_ids.add(run_id)
        if not _RUN_ID_RE.fullmatch(run_id):
            errors.append(f"line {line}: invalid RunID {run_id!r}")
        if expected_run_id and run_id != expected_run_id:
            errors.append(f"line {line}: RunID differs from expected {expected_run_id!r}")

        if row.get("SchemaVersion") != "2":
            errors.append(f"line {line}: SchemaVersion must be 2")

        sequence_raw = row.get("EventSequence", "")
        try:
            sequence = int(sequence_raw)
            if sequence != previous_sequence + 1:
                errors.append(f"line {line}: EventSequence is not contiguous (expected {previous_sequence + 1})")
            previous_sequence = sequence
        except (TypeError, ValueError):
            errors.append(f"line {line}: invalid EventSequence {sequence_raw!r}")
            sequence = -1

        event_id = row.get("EventID", "")
        expected_event_id = f"{run_id}:EV{sequence}"
        if not event_id or event_id != expected_event_id:
            errors.append(f"line {line}: EventID must equal {expected_event_id!r}")
        if event_id in seen_event_ids:
            errors.append(f"line {line}: duplicate EventID {event_id!r}")
        seen_event_ids.add(event_id)

        _parse_time(row.get("EventTimeServer", ""), "EventTimeServer", line, errors)
        _parse_time(row.get("ObservedAtServer", ""), "ObservedAtServer", line, errors)
        if row.get("TimeBasis") != "BROKER_SERVER_RAW":
            errors.append(f"line {line}: TimeBasis must be BROKER_SERVER_RAW")

        source_tf = row.get("SourceTimeframe", "")
        source_bar = row.get("SourceBarOpenServer", "")
        if bool(source_tf) != bool(source_bar):
            errors.append(f"line {line}: SourceTimeframe and SourceBarOpenServer must both be set or both be blank")
        if source_bar:
            _parse_time(source_bar, "SourceBarOpenServer", line, errors)

        event = row.get("Event", "")
        event_counts[event] = event_counts.get(event, 0) + 1
        range_id = row.get("RangeID", "")
        cycle_id = row.get("CycleID", "")
        attempt_id = row.get("AttemptID", "")
        candidate_id = row.get("CandidateID", "")
        decision_id = row.get("DecisionID", "")
        status = row.get("DecisionStatus", "")
        reason = row.get("ReasonCode", "")

        if range_id and not re.fullmatch(re.escape(run_id) + r":R[1-9][0-9]*", range_id):
            errors.append(f"line {line}: malformed RangeID {range_id!r}")
        if cycle_id and (not range_id or not re.fullmatch(re.escape(range_id) + r":C[1-9][0-9]*", cycle_id)):
            errors.append(f"line {line}: CycleID is not nested under RangeID")
        if attempt_id and (not cycle_id or not re.fullmatch(re.escape(cycle_id) + r":A[1-9][0-9]*", attempt_id)):
            errors.append(f"line {line}: AttemptID is not nested under CycleID")
        if candidate_id and (not attempt_id or not re.fullmatch(re.escape(attempt_id) + r":E[1-9][0-9]*", candidate_id)):
            errors.append(f"line {line}: CandidateID is not nested under AttemptID")

        if event == "CANDIDATE_CREATED":
            if not candidate_id:
                errors.append(f"line {line}: CANDIDATE_CREATED has blank CandidateID")
            else:
                candidate_creation_count[candidate_id] = candidate_creation_count.get(candidate_id, 0) + 1
                candidate_created.add(candidate_id)
                candidate_ids_seen.add(candidate_id)
            if not (range_id and cycle_id and attempt_id):
                errors.append(f"line {line}: CANDIDATE_CREATED lacks Range/Cycle/Attempt identity")
            if row.get("Direction") not in ("BUY", "SELL"):
                errors.append(f"line {line}: CANDIDATE_CREATED direction must be BUY or SELL")
        elif candidate_id:
            if candidate_id not in candidate_created:
                errors.append(f"line {line}: CandidateID appears before its CANDIDATE_CREATED row")
            candidate_ids_seen.add(candidate_id)

        if status:
            if status not in ("ACCEPTED", "REJECTED"):
                errors.append(f"line {line}: invalid DecisionStatus {status!r}")
            if not candidate_id:
                errors.append(f"line {line}: decision status exists without CandidateID")
            if not decision_id or not reason:
                errors.append(f"line {line}: accepted/rejected decision needs DecisionID and ReasonCode")
            if decision_id and candidate_id and not re.fullmatch(re.escape(candidate_id) + r":D[1-9][0-9]*", decision_id):
                errors.append(f"line {line}: DecisionID is not nested under CandidateID")
            if decision_id and candidate_id:
                expected_decision = decision_sequence_by_candidate.get(candidate_id, 0) + 1
                expected_id = f"{candidate_id}:D{expected_decision}"
                if decision_id != expected_id:
                    errors.append(f"line {line}: DecisionID sequence should be {expected_id!r}")
                decision_sequence_by_candidate[candidate_id] = expected_decision
            if decision_id in seen_decision_ids:
                errors.append(f"line {line}: duplicate DecisionID {decision_id!r}")
            seen_decision_ids.add(decision_id)
            decision_count += 1
            if status == "ACCEPTED" and event != "ORDER_OPENED":
                errors.append(f"line {line}: ACCEPTED status is only valid for ORDER_OPENED")
            if status == "REJECTED" and not (event.startswith("REJECT_") or event == "ORDER_SEND_FAILED"):
                errors.append(f"line {line}: REJECTED status has a non-rejection event")
        elif decision_id or reason:
            errors.append(f"line {line}: DecisionID/ReasonCode must be blank without DecisionStatus")

        if event in ("TRADE_ENTRY_DEAL", "TRADE_PARTIAL_EXIT", "TRADE_CLOSED"):
            deal_event_count += 1
            if not row.get("DealID") or not row.get("PositionID"):
                errors.append(f"line {line}: trade deal event is missing DealID or PositionID")
            if not candidate_id or candidate_id not in candidate_created:
                errors.append(f"line {line}: trade deal event is not linked to a created CandidateID")
            if not row.get("OrderID"):
                warnings.append(f"line {line}: trade deal event has no OrderID from transaction")

        legacy_id = row.get("LegacySetupID", "")
        if legacy_id:
            try:
                if int(legacy_id) <= 0:
                    raise ValueError
            except ValueError:
                errors.append(f"line {line}: LegacySetupID must be a positive integer or blank")

    if len(run_ids) > 1:
        errors.append("CSV contains more than one RunID")
    for candidate_id, count in candidate_creation_count.items():
        if count != 1:
            errors.append(f"CandidateID {candidate_id!r} has {count} CANDIDATE_CREATED rows")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "rows": len(rows),
            "columns": len(fieldnames),
            "run_ids": sorted(run_ids),
            "unique_events": len(seen_event_ids),
            "unique_candidates": len(candidate_ids_seen),
            "candidate_creations": sum(candidate_creation_count.values()),
            "decisions": decision_count,
            "deal_events": deal_event_count,
            "event_counts": dict(sorted(event_counts.items())),
        },
    }


def validate_file(path: str | Path, expected_run_id: str | None = None) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_file():
        return {
            "valid": False, "errors": [f"file not found: {file_path}"],
            "warnings": [], "stats": {},
        }
    try:
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return validate_rows(reader.fieldnames, list(reader), expected_run_id)
    except (OSError, UnicodeError, csv.Error) as exc:
        return {
            "valid": False, "errors": [f"cannot read CSV: {exc}"],
            "warnings": [], "stats": {},
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a BOOT-003 Event Ledger v2 CSV")
    parser.add_argument("csv_file", help="Path to the exported v2 CSV")
    parser.add_argument("--expected-run-id", default=None)
    parser.add_argument("--output-json", default=None)
    args = parser.parse_args()

    report = validate_file(args.csv_file, args.expected_run_id)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output_json:
        try:
            Path(args.output_json).write_text(rendered + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"Cannot write JSON report: {exc}", file=sys.stderr)
            return 3
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
