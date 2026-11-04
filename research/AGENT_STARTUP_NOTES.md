# W1 branch startup

This branch contains the first causal HMM filtering prototype:
- `research/w1_forward_filter.py`
- `research/test_w1_forward_filter.py`
- `docs/W1_HMM_REGIME_RESEARCH_STARTER_FA.md`

Run locally:
```bash
python -m pip install numpy
python -m unittest discover -s research -p "test_w1_forward_filter.py" -v
```

Acceptance focus: normalized filtered probabilities, invariance of past outputs to future observation changes, and correct continuation of the forward state across a train/test boundary.

Research-only: no XAUUSD fitting or trading claims.
