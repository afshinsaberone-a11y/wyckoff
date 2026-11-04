# W3 branch startup

This branch contains the first fail-closed HMM-to-ML interface:
- `contracts/W3_HMM_ML_INTERFACE_V1.schema.json`
- `research/w3_interface_validator.py`
- `research/test_w3_interface_validator.py`
- `docs/W3_HYBRID_INTEGRATION_STARTER_FA.md`

Run locally:
```bash
python -m unittest discover -s research -p "test_w3_interface_validator.py" -v
python -m json.tool contracts/W3_HMM_ML_INTERFACE_V1.schema.json > /dev/null
```

Acceptance focus: probability dimensions and sum, causal availability sequence, freshness, fold/model identity, and fail-closed rejection.

Research-only: no EA integration or risk-control override.
