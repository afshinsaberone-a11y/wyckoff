from __future__ import annotations

import unittest

from migrate_legacy_event_csv import normalize_row


class LegacyEventMigrationTests(unittest.TestCase):
    def setUp(self):
        self.source_path = "events/example.csv"
        self.source_sha = "a" * 64

    def row(self, **overrides):
        data = {
            "ServerTime": "2026.04.24 18:55:00",
            "EA_Version": "1.08-C2-TIMING-SB050-T030",
            "Symbol": "XAUUSD",
            "InitialBalance": "10000.00",
            "SetupID": "54",
            "Direction": "BUY",
            "Event": "M5_BUY_RECOVERY_CONFIRMED",
            "Details": "close=4729.35; clearedRetestHigh=0",
            "RangeHigh": "4833.09",
            "RangeLow": "4664.18",
            "PositionID": "12345",
        }
        data.update(overrides)
        return data

    def test_legacy_setup_maps_to_range_not_candidate(self):
        item = normalize_row(self.row(), 7, self.source_path, self.source_sha)
        self.assertEqual(
            item["range_id"],
            "LEGACY_RANGE:1.08-C2-TIMING-SB050-T030:XAUUSD:54",
        )
        self.assertEqual(item["group_id"], item["range_id"])
        self.assertEqual(item["legacy_setup_id"], "54")
        self.assertEqual(item["range_identity_basis"], "LEGACY_SETUP_COUNTER_RANGE_LEVEL")
        self.assertEqual(item["candidate_id"], "")
        self.assertEqual(item["cycle_id"], "")
        self.assertEqual(item["attempt_id"], "")

    def test_zero_setup_does_not_create_range(self):
        item = normalize_row(self.row(SetupID="0", Event="EA_INIT"), 2, self.source_path, self.source_sha)
        self.assertEqual(item["range_id"], "")
        self.assertEqual(item["group_id"], "")
        self.assertEqual(item["candidate_id"], "")

    def test_timestamp_is_not_fabricated_as_utc(self):
        item = normalize_row(self.row(), 7, self.source_path, self.source_sha)
        self.assertEqual(item["server_time_raw"], "2026.04.24 18:55:00")
        self.assertEqual(item["server_timezone"], "UNKNOWN")
        self.assertEqual(item["event_time_utc"], "")
        self.assertEqual(item["available_at_utc"], "")
        self.assertEqual(item["decision_time_utc"], "")

    def test_stable_event_id_and_distinct_duplicate_rows(self):
        row = self.row()
        first = normalize_row(row, 7, self.source_path, self.source_sha)
        repeated = normalize_row(row, 7, self.source_path, self.source_sha)
        next_row = normalize_row(row, 8, self.source_path, self.source_sha)
        self.assertEqual(first["event_id"], repeated["event_id"])
        self.assertNotEqual(first["event_id"], next_row["event_id"])

    def test_position_id_is_not_promoted_to_trade_id(self):
        item = normalize_row(self.row(PositionID="98765"), 7, self.source_path, self.source_sha)
        self.assertEqual(item["legacy_position_id"], "98765")
        self.assertEqual(item["trade_id"], "")


if __name__ == "__main__":
    unittest.main()
