"""Deterministic OHLCV/quote-quality checks for broker-exported bars.

Timestamps are kept in broker-server wall-clock form; this module never guesses
UTC offsets or treats session/weekend gaps as malformed OHLC data.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
import math
from typing import Any


_TIME_FORMATS = (
    "%Y.%m.%d %H:%M:%S",
    "%Y.%m.%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M",
)


def _parse_server_time(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a non-empty server-time string.")
    raw = value.strip()
    for fmt in _TIME_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unsupported server timestamp: {raw!r}")


def _number(row: Mapping[str, Any], key: str) -> float:
    value = row.get(key)
    if value is None or isinstance(value, bool):
        raise ValueError(f"{key} is missing or invalid.")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} is not numeric.") from exc
    if not math.isfinite(result):
        raise ValueError(f"{key} must be finite.")
    return result


@dataclass(frozen=True)
class QualitySummary:
    rows_read: int
    valid_timestamp_rows: int
    invalid_timestamp_rows: int
    invalid_ohlc_rows: int
    duplicate_timestamps: int
    non_monotonic_rows: int
    zero_tick_volume_rows: int
    invalid_tick_volume_rows: int
    missing_spread_rows: int
    zero_spread_rows: int
    invalid_spread_rows: int
    gap_intervals: int
    estimated_missing_intervals: int
    max_gap_seconds: int
    first_server_time: str | None
    last_server_time: str | None

    @property
    def structurally_valid(self) -> bool:
        return (
            self.rows_read > 0
            and self.invalid_timestamp_rows == 0
            and self.invalid_ohlc_rows == 0
            and self.duplicate_timestamps == 0
            and self.non_monotonic_rows == 0
            and self.invalid_tick_volume_rows == 0
            and self.invalid_spread_rows == 0
        )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["structurally_valid"] = self.structurally_valid
        return result


def validate_ohlcv_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    timeframe_seconds: int = 60,
) -> QualitySummary:
    """Validate canonical rows with timestamp/open/high/low/close/tick_volume.

    Optional spread_points is counted separately: missing or zero spread is a
    quality warning, not an OHLC corruption. A time gap is reported but not
    classified as invalid because session closures/weekends must be interpreted
    with the broker's trading calendar.
    """
    if isinstance(timeframe_seconds, bool) or not isinstance(timeframe_seconds, int) or timeframe_seconds <= 0:
        raise ValueError("timeframe_seconds must be a positive integer.")

    total = valid_ts = bad_ts = bad_ohlc = dupes = nonmono = 0
    zero_volume = bad_volume = missing_spread = zero_spread = bad_spread = 0
    gap_intervals = estimated_missing = max_gap = 0
    first_time: datetime | None = None
    last_time: datetime | None = None
    seen: set[datetime] = set()
    previous: datetime | None = None

    for row in rows:
        total += 1
        if not isinstance(row, Mapping):
            bad_ts += 1
            continue

        try:
            stamp = _parse_server_time(row.get("timestamp"))
        except ValueError:
            bad_ts += 1
            continue

        valid_ts += 1
        if first_time is None:
            first_time = stamp
        if stamp in seen:
            dupes += 1
        seen.add(stamp)

        if previous is not None:
            delta = int((stamp - previous).total_seconds())
            if delta <= 0:
                nonmono += 1
            elif delta > timeframe_seconds:
                gap_intervals += 1
                max_gap = max(max_gap, delta)
                estimated_missing += max(0, (delta // timeframe_seconds) - 1)
        previous = stamp
        last_time = stamp

        try:
            o = _number(row, "open")
            h = _number(row, "high")
            low = _number(row, "low")
            c = _number(row, "close")
            if min(o, h, low, c) <= 0 or h < max(o, c, low) or low > min(o, c, h):
                bad_ohlc += 1
        except ValueError:
            bad_ohlc += 1

        try:
            volume = _number(row, "tick_volume")
            if volume < 0 or not volume.is_integer():
                bad_volume += 1
            elif volume == 0:
                zero_volume += 1
        except ValueError:
            bad_volume += 1

        if "spread_points" not in row or row.get("spread_points") in (None, ""):
            missing_spread += 1
        else:
            try:
                spread = _number(row, "spread_points")
                if spread < 0 or not spread.is_integer():
                    bad_spread += 1
                elif spread == 0:
                    zero_spread += 1
            except ValueError:
                bad_spread += 1

    return QualitySummary(
        rows_read=total,
        valid_timestamp_rows=valid_ts,
        invalid_timestamp_rows=bad_ts,
        invalid_ohlc_rows=bad_ohlc,
        duplicate_timestamps=dupes,
        non_monotonic_rows=nonmono,
        zero_tick_volume_rows=zero_volume,
        invalid_tick_volume_rows=bad_volume,
        missing_spread_rows=missing_spread,
        zero_spread_rows=zero_spread,
        invalid_spread_rows=bad_spread,
        gap_intervals=gap_intervals,
        estimated_missing_intervals=estimated_missing,
        max_gap_seconds=max_gap,
        first_server_time=first_time.strftime("%Y-%m-%d %H:%M:%S") if first_time else None,
        last_server_time=last_time.strftime("%Y-%m-%d %H:%M:%S") if last_time else None,
    )
