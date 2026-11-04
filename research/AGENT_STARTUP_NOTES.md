# W2 branch startup

This branch contains the first point-in-time Candidate validator:
- `research/w2_candidate_validator.py`
- `research/test_w2_candidate_validator.py`
- `docs/W2_ML_CANDIDATE_SCORING_STARTER_FA.md`

Run locally:
```bash
python -m unittest discover -s research -p "test_w2_candidate_validator.py" -v
```

Acceptance focus: no feature may become available after decision time; duplicate Candidate IDs across train/test are rejected; overlapping label intervals, same Range groups and embargo windows are purged.

Research-only: this does not train a model or fabricate real candidates/outcomes.
