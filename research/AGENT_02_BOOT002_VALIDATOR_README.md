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


## Validate the four completed manifests

After placing one completed JSON manifest for each role in a folder:

```powershell
python research/validate_boot002_bundle.py `
  --run-a runs/BOOT-002/run_A/run_manifest.json `
  --run-b runs/BOOT-002/run_B/run_manifest.json `
  --run-c runs/BOOT-002/run_C/run_manifest.json `
  --run-d runs/BOOT-002/run_D/run_manifest.json `
  --output-json runs/BOOT-002/comparison/bundle_validation.json
```

Exit code 0 means the submitted manifests pass the evidence/identity checks. Exit code 2 means at least one manifest is incomplete or inconsistent; exit code 3 means the output result could not be written. This does not mean MT5 ran successfully unless the manifests contain actual source/build/HTML/Journal/CSV evidence with matching hashes.
