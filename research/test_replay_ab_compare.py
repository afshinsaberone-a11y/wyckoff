from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from replay_ab_compare import (
    CSV_COLUMNS,
    InputError,
    compare_csv_rows,
    compare_runs,
    compare_set_files,
    read_legacy_csv,
)


def make_row(
    event: str = "RANGE_FOUND",
    version: str = "1.08-C2",
    **overrides: str,
) -> dict[str, str]:
    row = {
        "ServerTime": "2026.11.04 10:00:00",
        "EA_Version": version,
        "Symbol": "XAUUSD",
        "InitialBalance": "1000.00",
        "SetupID": "1",
        "Direction": "BUY",
        "Event": event,
        "Details": "widthATR=2.5",
        "RangeHigh": "4100.00",
        "RangeLow": "4050.00",
        "PositionID": "0",
    }
    row.update(overrides)
    return row


class ReplayABComparatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.base_csv = self.root / "base.csv"
        self.ledger_csv = self.root / "ledger.csv"
        self.base_set = self.root / "base.set"
        self.ledger_set = self.root / "ledger.set"

    def tearDown(self):
        self.temp.cleanup()

    def write_csv(self, path: Path, rows, header=CSV_COLUMNS):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)

    def test_csv_stream_matches_when_only_ea_version_differs(self):
        self.write_csv(self.base_csv, [make_row(), make_row("ORDER_OPENED")])
        self.write_csv(
            self.ledger_csv,
            [
                make_row(version="1.083-LEDGER"),
                make_row("ORDER_OPENED", version="1.083-LEDGER"),
            ],
        )
        base_rows, _ = read_legacy_csv(self.base_csv)
        ledger_rows, _ = read_legacy_csv(self.ledger_csv)
        report = compare_csv_rows(base_rows, ledger_rows)
        self.assertTrue(report["equal"])
        self.assertIsNone(report["first_difference"])

    def test_first_row_difference_is_reported_with_column_values(self):
        self.write_csv(self.base_csv, [make_row()])
        self.write_csv(self.ledger_csv, [make_row(Details="widthATR=2.6")])
        base_rows, _ = read_legacy_csv(self.base_csv)
        ledger_rows, _ = read_legacy_csv(self.ledger_csv)
        report = compare_csv_rows(base_rows, ledger_rows)
        self.assertFalse(report["equal"])
        self.assertEqual(report["first_difference"]["row_number"], 2)
        self.assertEqual(
            report["first_difference"]["field_differences"][0]["column"],
            "Details",
        )

    def test_row_order_is_significant(self):
        self.write_csv(self.base_csv, [make_row("SPRING_CONFIRMED"), make_row("TEST_CONFIRMED")])
        self.write_csv(self.ledger_csv, [make_row("TEST_CONFIRMED"), make_row("SPRING_CONFIRMED")])
        base_rows, _ = read_legacy_csv(self.base_csv)
        ledger_rows, _ = read_legacy_csv(self.ledger_csv)
        self.assertFalse(compare_csv_rows(base_rows, ledger_rows)["equal"])

    def test_row_count_difference_is_reported(self):
        self.write_csv(self.base_csv, [make_row(), make_row("ORDER_OPENED")])
        self.write_csv(self.ledger_csv, [make_row()])
        base_rows, _ = read_legacy_csv(self.base_csv)
        ledger_rows, _ = read_legacy_csv(self.ledger_csv)
        report = compare_csv_rows(base_rows, ledger_rows)
        self.assertFalse(report["equal"])
        self.assertEqual(
            report["first_difference"]["field_differences"][0]["column"],
            "__ROW_COUNT__",
        )

    def test_schema_order_is_strict(self):
        reversed_header = list(reversed(CSV_COLUMNS))
        self.write_csv(self.base_csv, [make_row()], header=reversed_header)
        with self.assertRaises(InputError):
            read_legacy_csv(self.base_csv)

    def test_header_only_csv_is_rejected(self):
        self.write_csv(self.base_csv, [])
        with self.assertRaises(InputError):
            read_legacy_csv(self.base_csv)

    def test_set_files_ignore_ledger_only_inputs_and_normalize_values(self):
        self.base_set.write_text(
            "InpRiskPercent=0.50\nInpUseFilter=true\nInpEntryTF=5\n",
            encoding="utf-8",
        )
        self.ledger_set.write_text(
            "InpRiskPercent=0.5||0.1||0.1||1.0||N\n"
            "InpUseFilter=TRUE\nInpEntryTF=5\n"
            "InpLedgerRunID=WM20261104A002\n",
            encoding="utf-8",
        )
        report = compare_set_files(self.base_set, self.ledger_set)
        self.assertTrue(report["equal"])
        self.assertEqual(report["shared_keys"], 3)
        self.assertEqual(report["baseline_only_keys"], [])
        self.assertEqual(report["ledger_only_keys"], [])

    def test_shared_input_mismatch_is_detected(self):
        self.base_set.write_text("InpRiskPercent=0.50\n", encoding="utf-8")
        self.ledger_set.write_text("InpRiskPercent=0.75\n", encoding="utf-8")
        report = compare_set_files(self.base_set, self.ledger_set)
        self.assertFalse(report["equal"])
        self.assertEqual(report["mismatched_keys"][0]["key"], "InpRiskPercent")

    def test_missing_shared_input_is_detected(self):
        self.base_set.write_text("InpRiskPercent=0.5\nInpRewardRisk=2\n", encoding="utf-8")
        self.ledger_set.write_text("InpRiskPercent=0.5\n", encoding="utf-8")
        report = compare_set_files(self.base_set, self.ledger_set)
        self.assertFalse(report["equal"])
        self.assertEqual(report["baseline_only_keys"], ["InpRewardRisk"])

    def test_matching_csv_without_set_files_is_not_full_ab_pass(self):
        self.write_csv(self.base_csv, [make_row()])
        self.write_csv(self.ledger_csv, [make_row(version="1.083-LEDGER")])
        report = compare_runs(self.base_csv, self.ledger_csv)
        self.assertEqual(report["status"], "CSV_STREAM_MATCH_SETTINGS_UNVERIFIED")

    def test_matching_csv_and_shared_set_files_pass_limited_gate(self):
        self.write_csv(self.base_csv, [make_row(), make_row("ORDER_OPENED")])
        self.write_csv(
            self.ledger_csv,
            [
                make_row(version="1.083-LEDGER"),
                make_row("ORDER_OPENED", version="1.083-LEDGER"),
            ],
        )
        self.base_set.write_text("InpRiskPercent=0.5\n", encoding="utf-8")
        self.ledger_set.write_text(
            "InpRiskPercent=0.50\nInpLedgerRunID=WM20261104A002\n",
            encoding="utf-8",
        )
        report = compare_runs(
            self.base_csv, self.ledger_csv, self.base_set, self.ledger_set
        )
        self.assertEqual(
            report["status"],
            "PASS_SHARED_EA_INPUTS_AND_EVENT_STREAM_ONLY",
        )

    def test_only_one_set_file_is_rejected(self):
        with self.assertRaises(InputError):
            compare_set_files(self.base_set, None)

    def test_duplicate_set_key_is_rejected(self):
        self.base_set.write_text("InpRiskPercent=0.5\nInpRiskPercent=0.6\n", encoding="utf-8")
        self.ledger_set.write_text("InpRiskPercent=0.5\n", encoding="utf-8")
        with self.assertRaises(InputError):
            compare_set_files(self.base_set, self.ledger_set)

    def test_symbol_mismatch_is_rejected(self):
        self.write_csv(self.base_csv, [make_row()])
        self.write_csv(self.ledger_csv, [make_row(Symbol="EURUSD")])
        with self.assertRaises(InputError):
            compare_runs(self.base_csv, self.ledger_csv)


if __name__ == "__main__":
    unittest.main(verbosity=2)
