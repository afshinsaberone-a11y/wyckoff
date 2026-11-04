# AGENT_02 — BOOT-002 Run Bundle Validator

This research-only validator checks the evidence manifests for the four A/B/C/D MT5 runs.

## Expected variants

- A: H1STRUCT Audit v1.083 / Lookback 5
- B: MultiAudit v1.084 / Lookback 5
- C: MultiAudit v1.084 / Lookback 10
- D: MultiAudit v1.084 / Lookback 20

## What it verifies

- Exact Expert name, source path, property version, EA_VERSION and Lookback for each role.
- Successful compile result and SHA-256 identity for source/executable artifacts.
- Expected SET identity and all-other-inputs-match assertion.
- Common frozen test window, broker, symbol, timeframe, model, deposit, leverage and execution-cost assumptions.
- Presence and hashes of HTML, Journal and Events CSV outputs.
- Journal/CSV identity checks and required acceptance flags.
- Same MetaEditor build across runs; distinct A/B EX5 files; identical MultiAudit EX5 for B/C/D.
- Exactly one complete run for each A/B/C/D role.

This validates submitted evidence only. It does **not** compile MQL5, launch Strategy Tester, parse raw HTML/Journal/CSV content, or infer missing hashes. Values must be copied from actual MT5 outputs.

## Run

```bash
python -m unittest discover -s research -p "test_boot002_bundle_validator.py" -v
```
