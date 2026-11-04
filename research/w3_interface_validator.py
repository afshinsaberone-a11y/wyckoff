"""Fail-closed validator for the W3 HMM-to-ML interface."""
from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any


REQUIRED = {
    "schema_version",
    "run_id",
    "candidate_id",
    "decision_seq",
    "as_of_seq",
    "available_at_seq",
    "time_basis",
    "hmm_model_version",
    "fold_id",
    "state_mapping_version",
    "filtered_probabilities",
    "posterior_entropy",
    "data_version",
}


class InterfaceRejected(ValueError):
    """Raised when a regime payload must not reach the ML scorer."""


def validate_hmm_payload(
    payload: Mapping[str, Any],
    *,
    expected_states: int,
    max_staleness_bars: int = 1,
    probability_tolerance: float = 1e-6,
) -> None:
    """Validate a causal, fresh, normalized HMM probability vector.

    An invalid payload is rejected; caller must fail closed and must not
    silently fall back to stale/smoothed values or bypass W0 risk controls.
    """
    if not isinstance(payload, Mapping):
        raise InterfaceRejected("Payload must be a mapping.")
    missing = REQUIRED - set(payload.keys())
    if missing:
        raise InterfaceRejected(f"Missing required fields: {sorted(missing)}")
    if payload["schema_version"] != "W3_HMM_ML_INTERFACE_V1":
        raise InterfaceRejected("Unsupported schema_version.")
    if payload["time_basis"] != "BROKER_SERVER_RAW_SEQUENCE":
        raise InterfaceRejected("Unsupported time_basis.")
    for key in ("run_id", "candidate_id", "hmm_model_version", "fold_id", "state_mapping_version", "data_version"):
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise InterfaceRejected(f"{key} must be a non-empty string.")

    seq_keys = ("decision_seq", "as_of_seq", "available_at_seq")
    for key in seq_keys:
        if isinstance(payload[key], bool) or not isinstance(payload[key], int) or payload[key] < 0:
            raise InterfaceRejected(f"{key} must be a non-negative integer.")
    if payload["as_of_seq"] > payload["available_at_seq"]:
        raise InterfaceRejected("HMM output is marked available before its source sequence.")
    if payload["available_at_seq"] > payload["decision_seq"]:
        raise InterfaceRejected("HMM output contains information available after the ML decision.")
    if payload["decision_seq"] - payload["as_of_seq"] > max_staleness_bars:
        raise InterfaceRejected("HMM probability vector is stale at the candidate decision.")

    probabilities = payload["filtered_probabilities"]
    if not isinstance(probabilities, (list, tuple)) or len(probabilities) != expected_states:
        raise InterfaceRejected("filtered_probabilities has the wrong number of states.")
    if any(
        isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(float(p))
        or float(p) < 0.0 or float(p) > 1.0
        for p in probabilities
    ):
        raise InterfaceRejected("Each state probability must be finite and in [0, 1].")
    if abs(sum(float(p) for p in probabilities) - 1.0) > probability_tolerance:
        raise InterfaceRejected("filtered_probabilities must sum to 1.")

    entropy = payload["posterior_entropy"]
    if isinstance(entropy, bool) or not isinstance(entropy, (int, float)) or not math.isfinite(float(entropy)) or entropy < 0:
        raise InterfaceRejected("posterior_entropy must be finite and non-negative.")
