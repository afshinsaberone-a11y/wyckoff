from __future__ import annotations

import unittest

from ohlcv_quality import validate_ohlcv_rows


def row(timestamp, **overrides):
    result = {
        "timestamp": timestamp,
        "open": "2300.00",
        "high": "2301.00",
        "low": "2299.00",
        "close": "2300.50",
        "tick_volume": "120",
        "spread_points": "25",
    }
    result.update(overrides)
    return result


class OHLCVQualityTests(unittest.TestCase):
    def test_accepts_clean_server_time_rows(self):
        summary = validate_ohlcv_rows([
            row("2026.01.05 10:00"),
            row("2026.01.05 10:01"),
        ])
        self.assertTrue(summary.structurally_valid)
        self.assertEqual(summary.rows_read, 2)
        self.assertEqual(summary.first_server_time, "2026-01-05 10:00:00")

    def test_detects_ohlc_corruption(self):
        summary = validate_ohlcv_rows([
            row("2026.01.05 10:00", high="2298.00"),
        ])
        self.assertEqual(summary.invalid_ohlc_rows, 1)
        self.assertFalse(summary.structurally_valid)

    def test_detects_duplicate_timestamp(self):
        summary = validate_ohlcv_rows([
            row("2026.01.05 10:00"),
            row("2026.01.05 10:00"),
        ])
        self.assertEqual(summary.duplicate_timestamps, 1)
        self.assertFalse(summary.structurally_valid)

    def test_detects_non_monotonic_timestamp(self):
        summary = validate_ohlcv_rows([
            row("2026.01.05 10:02"),
            row("2026.01.05 10:01"),
        ])
        self.assertEqual(summary.non_monotonic_rows, 1)
        self.assertFalse(summary.structurally_valid)

    def test_reports_gap_without_calling_it_corruption(self):
        summary = validate_ohlcv_rows([
            row("2026.01.05 10:00"),
            row("2026.01.05 10:05"),
        ])
        self.assertEqual(summary.gap_intervals, 1)
        self.assertEqual(summary.estimated_missing_intervals, 4)
        self.assertTrue(summary.structurally_valid)

    def test_counts_zero_tick_volume(self):
        summary = validate_ohlcv_rows([
            row("2026.01.05 10:00", tick_volume="0"),
        ])
        self.assertEqual(summary.zero_tick_volume_rows, 1)
        self.assertTrue(summary.structurally_valid)

    def test_rejects_negative_or_fractional_tick_volume(self):
        summary = validate_ohlcv_rows([
            row("2026.01.05 10:00", tick_volume="-1"),
            row("2026.01.05 10:01", tick_volume="1.5"),
        ])
        self.assertEqual(summary.invalid_tick_volume_rows, 2)
        self.assertFalse(summary.structurally_valid)

    def test_counts_zero_and_missing_spread_separately(self):
        summary = validate_ohlcv_rows([
            row("2026.01.05 10:00", spread_points="0"),
            row("2026.01.05 10:01", spread_points=""),
        ])
        self.assertEqual(summary.zero_spread_rows, 1)
        self.assertEqual(summary.missing_spread_rows, 1)
        self.assertTrue(summary.structurally_valid)

    def test_rejects_negative_spread(self):
        summary = validate_ohlcv_rows([
            row("2026.01.05 10:00", spread_points="-1"),
        ])
        self.assertEqual(summary.invalid_spread_rows, 1)
        self.assertFalse(summary.structurally_valid)

    def test_counts_malformed_timestamps(self):
        summary = validate_ohlcv_rows([
            row("not-a-time"),
        ])
        self.assertEqual(summary.invalid_timestamp_rows, 1)
        self.assertFalse(summary.structurally_valid)

    def test_rejects_empty_input_as_not_structurally_valid(self):
        summary = validate_ohlcv_rows([])
        self.assertFalse(summary.structurally_valid)
        self.assertEqual(summary.rows_read, 0)

    def test_rejects_invalid_timeframe(self):
        with self.assertRaises(ValueError):
            validate_ohlcv_rows([], timeframe_seconds=True)


if __name__ == "__main__":
    unittest.main()
