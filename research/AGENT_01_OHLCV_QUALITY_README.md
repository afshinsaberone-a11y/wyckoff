# AGENT_01 OHLCV Data Quality Validator

This research-only helper validates normalized broker bar rows before resampling or feature construction.

Canonical row fields:
- `timestamp`: broker-server wall-clock timestamp; accepted formats are `YYYY.MM.DD HH:MM[:SS]` and ISO-like forms.
- `open`, `high`, `low`, `close`: positive finite numeric prices.
- `tick_volume`: non-negative integer count.
- `spread_points`: optional non-negative integer points.

The summary separates structural corruption from warnings:
- malformed timestamps, bad OHLC, duplicate/non-monotonic rows, invalid volume and invalid spread make `structurally_valid=false`;
- zero tick volume, zero/missing spread and time gaps are counted independently;
- gaps are not automatically considered bad because market sessions, holidays and weekends require broker-calendar interpretation.

The validator deliberately keeps broker-server time and does not guess UTC/DST offsets. It does not fill missing bars, repair quotes, infer ticks, or certify trading performance.

Run tests:
```bash
python -m unittest discover -s research -p "test_ohlcv_quality.py" -v
```
