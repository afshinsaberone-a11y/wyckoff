"""Compare C2 baseline and Ledger-v2 legacy event CSV streams for Replay A/B.

The comparison deliberately uses the shared 11-column legacy event CSV. The
Ledger-v2-only 28-column Event Ledger is not a like-for-like baseline stream.
EA_Version is ignored because the instrumentation build has a different label.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

CSV_COLUMNS = [
    "ServerTime", "EA_Version", "Symbol", "InitialBalance", "SetupID",
    "Direction", "Event", "Details", "RangeHigh", "RangeLow", "PositionID",
]
COMPARE_COLUMNS = [column for column in CSV_COLUMNS if column != "EA_Version"]
TRADE_EVENTS = {
    "ORDER_OPENED", "TRADE_ENTRY_DEAL", "TRADE_PARTIAL_EXIT", "TRADE_CLOSED",
}
IGNORED_SET_PREFIXES = ("InpLedger",)


class InputError(Exception):
    """Raised when an input file is incomplete or violates the expected schema."""


def read_legacy_csv(path: str | Path) -> tuple[list[dict[str, str]], str]:
    file_path = Path(path)
    if not file_path.is_file():
        raise InputError(f"CSV file not found: {file_path}")
    try:
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != CSV_COLUMNS:
                raise InputError(
                    f"{file_path}: header must exactly match the shared 11-column "
                    f"C2 schema and order; found {reader.fieldnames!r}"
                )
            rows: list[dict[str, str]] = []
            for line_number, row in enumerate(reader, start=2):
                if None in row:
                    raise InputError(f"{file_path}: line {line_number} has extra CSV fields")
                if any(row.get(column) is None for column in CSV_COLUMNS):
                    raise InputError(f"{file_path}: line {line_number} has fewer than 11 fields")
                rows.append({column: (row[column] or "").strip() for column in CSV_COLUMNS})
    except (OSError, UnicodeError, csv.Error) as exc:
        raise InputError(f"Cannot read {file_path}: {exc}") from exc

    if not rows:
        raise InputError(f"{file_path}: CSV contains a header only; refusing an empty comparison")
    symbols = {row["Symbol"] for row in rows}
    balances = {row["InitialBalance"] for row in rows}
    if len(symbols) != 1:
        raise InputError(f"{file_path}: expected one Symbol per run, found {sorted(symbols)}")
    if len(balances) != 1:
        raise InputError(
            f"{file_path}: InitialBalance changes within one run: {sorted(balances)}"
        )
    return rows, next(iter(symbols))


def normalize_set_value(value: str) -> str:
    value = value.strip()
    lowered = value.lower()
    if lowered in {"true", "false", "yes", "no", "on", "off"}:
        return lowered
    try:
        number = Decimal(value)
        if number == 0:
            return "0"
        return format(number.normalize(), "f")
    except (InvalidOperation, ValueError):
        return value


def read_set_file(path: str | Path) -> dict[str, str]:
    file_path = Path(path)
    if not file_path.is_file():
        raise InputError(f"SET file not found: {file_path}")
    values: dict[str, str] = {}
    try:
        lines = file_path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as exc:
        raise InputError(f"Cannot read {file_path}: {exc}") from exc

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith(("#", ";", "//")) or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        if key in values:
            raise InputError(f"{file_path}: duplicate input key {key!r} on line {line_number}")
        # MT5 .set files may append optimization metadata after the first ||.
        primary_value = raw_value.split("||", 1)[0]
        values[key] = normalize_set_value(primary_value)

    if not values:
        raise InputError(f"{file_path}: no key=value inputs found")
    return values


def compare_set_files(
    baseline_path: str | Path | None,
    ledger_path: str | Path | None,
) -> dict[str, Any]:
    if (baseline_path is None) != (ledger_path is None):
        raise InputError("Provide both --baseline-set and --ledger-set, or neither.")
    if baseline_path is None:
        return {
            "checked": False,
            "equal": None,
            "shared_keys": 0,
            "baseline_only_keys": [],
            "ledger_only_keys": [],
            "mismatched_keys": [],
            "note": "EA input settings were not checked because SET files were not supplied.",
        }

    baseline = read_set_file(baseline_path)
    ledger = read_set_file(ledger_path)  # type: ignore[arg-type]
    baseline = {
        key: value for key, value in baseline.items()
        if not key.startswith(IGNORED_SET_PREFIXES)
    }
    ledger = {
        key: value for key, value in ledger.items()
        if not key.startswith(IGNORED_SET_PREFIXES)
    }
    baseline_keys = set(baseline)
    ledger_keys = set(ledger)
    shared = baseline_keys & ledger_keys
    baseline_only = sorted(baseline_keys - ledger_keys)
    ledger_only = sorted(ledger_keys - baseline_keys)
    mismatched = sorted(
        key for key in shared if baseline[key] != ledger[key]
    )
    equal = not baseline_only and not ledger_only and not mismatched
    return {
        "checked": True,
        "equal": equal,
        "shared_keys": len(shared),
        "baseline_only_keys": baseline_only,
        "ledger_only_keys": ledger_only,
        "mismatched_keys": [
            {
                "key": key,
                "baseline": baseline[key],
                "ledger": ledger[key],
            }
            for key in mismatched
        ],
        "ignored_prefixes": list(IGNORED_SET_PREFIXES),
        "note": (
            "Only shared EA inputs were compared. Tester model, dates, symbol, "
            "deposit/leverage, spread, commissions, swaps, delay and history "
            "coverage must still be checked from Strategy Tester evidence."
        ),
    }


def event_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    return dict(sorted(Counter(row["Event"] for row in rows).items()))


def compare_csv_rows(
    baseline_rows: list[dict[str, str]],
    ledger_rows: list[dict[str, str]],
) -> dict[str, Any]:
    differences: list[dict[str, Any]] = []
    differing_row_count = 0
    first_difference: dict[str, Any] | None = None
    common_length = min(len(baseline_rows), len(ledger_rows))

    for index in range(common_length):
        left = baseline_rows[index]
        right = ledger_rows[index]
        field_differences = [
            {
                "column": column,
                "baseline": left[column],
                "ledger": right[column],
            }
            for column in COMPARE_COLUMNS
            if left[column] != right[column]
        ]
        if field_differences:
            differing_row_count += 1
            if first_difference is None:
                first_difference = {
                    "row_number": index + 2,
                    "sequence_index": index + 1,
                    "baseline_event": left["Event"],
                    "ledger_event": right["Event"],
                    "field_differences": field_differences,
                }
            if len(differences) < 50:
                differences.append({
                    "row_number": index + 2,
                    "baseline_event": left["Event"],
                    "ledger_event": right["Event"],
                    "field_differences": field_differences,
                })

    if len(baseline_rows) != len(ledger_rows):
        if first_difference is None:
            first_difference = {
                "row_number": common_length + 2,
                "sequence_index": common_length + 1,
                "baseline_event": (
                    baseline_rows[common_length]["Event"]
                    if common_length < len(baseline_rows) else None
                ),
                "ledger_event": (
                    ledger_rows[common_length]["Event"]
                    if common_length < len(ledger_rows) else None
                ),
                "field_differences": [{"column": "__ROW_COUNT__",
                                       "baseline": len(baseline_rows),
                                       "ledger": len(ledger_rows)}],
            }

    equal = len(baseline_rows) == len(ledger_rows) and differing_row_count == 0
    return {
        "equal": equal,
        "baseline_rows": len(baseline_rows),
        "ledger_rows": len(ledger_rows),
        "differing_rows_in_common_range": differing_row_count,
        "first_difference": first_difference,
        "differences_truncated_to_50": differences,
    }


def compare_runs(
    baseline_csv: str | Path,
    ledger_csv: str | Path,
    baseline_set: str | Path | None = None,
    ledger_set: str | Path | None = None,
) -> dict[str, Any]:
    baseline_rows, baseline_symbol = read_legacy_csv(baseline_csv)
    ledger_rows, ledger_symbol = read_legacy_csv(ledger_csv)
    if baseline_symbol != ledger_symbol:
        raise InputError(
            f"Symbol mismatch: baseline={baseline_symbol!r}, ledger={ledger_symbol!r}"
        )

    settings = compare_set_files(baseline_set, ledger_set)
    csv_result = compare_csv_rows(baseline_rows, ledger_rows)
    baseline_versions = sorted({row["EA_Version"] for row in baseline_rows})
    ledger_versions = sorted({row["EA_Version"] for row in ledger_rows})

    if not csv_result["equal"]:
        status = "FAIL_EVENT_STREAM_MISMATCH"
    elif settings["checked"] and not settings["equal"]:
        status = "FAIL_SHARED_EA_INPUT_MISMATCH"
    elif settings["checked"]:
        status = "PASS_SHARED_EA_INPUTS_AND_EVENT_STREAM_ONLY"
    else:
        status = "CSV_STREAM_MATCH_SETTINGS_UNVERIFIED"

    baseline_events = event_counts(baseline_rows)
    ledger_events = event_counts(ledger_rows)
    trade_counts = {
        "baseline": {
            event: baseline_events.get(event, 0) for event in sorted(TRADE_EVENTS)
        },
        "ledger": {
            event: ledger_events.get(event, 0) for event in sorted(TRADE_EVENTS)
        },
    }
    return {
        "status": status,
        "csv_equal_ignoring_ea_version": csv_result["equal"],
        "symbol": baseline_symbol,
        "baseline_csv": str(baseline_csv),
        "ledger_legacy_csv": str(ledger_csv),
        "baseline_ea_versions": baseline_versions,
        "ledger_ea_versions": ledger_versions,
        "settings": settings,
        "csv_comparison": csv_result,
        "baseline_event_counts": baseline_events,
        "ledger_event_counts": ledger_events,
        "trade_event_counts": trade_counts,
        "scope_note": (
            "This compares the shared legacy event stream, not the 28-column "
            "v2 ledger. A passing result does not verify tester dates/model, "
            "broker history, financial report equality, source/EX5 hashes, "
            "or profitability. Archive those separately before accepting Replay A/B."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare C2 baseline vs Ledger-v2 shared legacy event CSVs."
    )
    parser.add_argument("baseline_csv", help="C2 baseline legacy event CSV")
    parser.add_argument("ledger_csv", help="Ledger-v2 legacy event CSV (11 columns)")
    parser.add_argument("--baseline-set", default=None, help="Baseline MT5 .set file")
    parser.add_argument("--ledger-set", default=None, help="Ledger-v2 MT5 .set file")
    parser.add_argument("--output-json", default=None, help="Optional JSON report path")
    args = parser.parse_args()

    try:
        report = compare_runs(
            args.baseline_csv,
            args.ledger_csv,
            args.baseline_set,
            args.ledger_set,
        )
    except InputError as exc:
        print(json.dumps({"status": "INPUT_ERROR", "error": str(exc)}, indent=2))
        return 3

    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output_json:
        try:
            output_path = Path(args.output_json)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"Cannot write JSON report: {exc}", file=sys.stderr)
            return 3

    if report["status"] == "FAIL_EVENT_STREAM_MISMATCH":
        return 2
    if report["status"] == "FAIL_SHARED_EA_INPUT_MISMATCH":
        return 2
    if report["status"] == "CSV_STREAM_MATCH_SETTINGS_UNVERIFIED":
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
