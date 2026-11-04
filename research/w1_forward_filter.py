"""Causal forward filtering for a finite-state HMM.

Research-only utility. It deliberately computes filtered probabilities
P(S_t | X_1:t), not smoothed posteriors P(S_t | X_1:T).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FilterResult:
    probabilities: np.ndarray
    log_alpha: np.ndarray
    log_likelihood: float


def _logsumexp(values: np.ndarray, axis: int) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    maximum = np.max(values, axis=axis, keepdims=True)
    finite = np.isfinite(maximum)
    safe_maximum = np.where(finite, maximum, 0.0)
    with np.errstate(invalid="ignore"):
        shifted_values = values - safe_maximum
    shifted_values = np.where(np.broadcast_to(finite, values.shape), shifted_values, -np.inf)
    total = np.sum(np.exp(shifted_values), axis=axis, keepdims=True)
    with np.errstate(divide="ignore"):
        result = safe_maximum + np.log(total)
    result = np.where(finite, result, -np.inf)
    return np.squeeze(result, axis=axis)


def _probability_vector(values: np.ndarray, name: str, size: int) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    if vector.shape != (size,):
        raise ValueError(f"{name} must have shape ({size},), got {vector.shape}.")
    if not np.all(np.isfinite(vector)) or np.any(vector < 0.0):
        raise ValueError(f"{name} must contain finite non-negative values.")
    with np.errstate(over="ignore", invalid="ignore"):
        total = float(vector.sum())
    if not np.isfinite(total) or total <= 0.0:
        raise ValueError(f"{name} must have finite positive total mass.")
    return vector / total


def forward_filter(
    log_emission: np.ndarray,
    transition_matrix: np.ndarray,
    initial_state_prob: np.ndarray,
) -> FilterResult:
    """Compute normalized filtered state probabilities.

    Args:
        log_emission:
            Array [T, K], where log_emission[t, j] is log p(x_t | S_t=j).
            Emissions must already be computed using parameters frozen before
            the evaluated sequence. No future observation may enter a row.
        transition_matrix:
            Row-stochastic [K, K] matrix A[i, j] = P(S_t=j | S_(t-1)=i).
        initial_state_prob:
            Prior state distribution for the FIRST observation in this input
            segment. For a continuation after a previous filtered posterior
            alpha_prev, pass alpha_prev @ transition_matrix.

    Returns:
        FilterResult with probabilities [T, K], normalized log-alpha [T, K],
        and the sequence log likelihood under the supplied frozen parameters.

    This function does not fit HMM parameters, scale features, select states,
    or infer regime names. Those operations must be train-fold-only.
    """
    emissions = np.asarray(log_emission, dtype=float)
    transition = np.asarray(transition_matrix, dtype=float)

    if emissions.ndim != 2 or emissions.shape[0] < 1 or emissions.shape[1] < 1:
        raise ValueError("log_emission must be a non-empty [time, states] matrix.")
    if np.any(np.isnan(emissions)) or np.any(np.isposinf(emissions)):
        raise ValueError("log_emission may contain finite values or -inf, not NaN/+inf.")

    time_steps, states = emissions.shape
    if transition.shape != (states, states):
        raise ValueError(
            f"transition_matrix must have shape ({states}, {states}), got {transition.shape}."
        )
    if not np.all(np.isfinite(transition)) or np.any(transition < 0.0):
        raise ValueError("transition_matrix must be finite and non-negative.")
    row_sums = transition.sum(axis=1)
    if not np.allclose(row_sums, 1.0, rtol=1e-8, atol=1e-10):
        raise ValueError("Each transition_matrix row must sum to 1.")

    initial = _probability_vector(initial_state_prob, "initial_state_prob", states)
    with np.errstate(divide="ignore"):
        log_transition = np.log(transition)
        log_initial = np.log(initial)

    log_alpha = np.empty((time_steps, states), dtype=float)
    total_log_likelihood = 0.0

    unnormalized = log_initial + emissions[0]
    scale = float(_logsumexp(unnormalized, axis=0))
    if not np.isfinite(scale):
        raise ValueError("The first observation has zero probability under all states.")
    log_alpha[0] = unnormalized - scale
    total_log_likelihood += scale

    for t in range(1, time_steps):
        # Predict: P(S_t | X_1:t-1) = alpha_(t-1) @ A.
        predicted_log_prob = _logsumexp(
            log_alpha[t - 1][:, None] + log_transition,
            axis=0,
        )
        # Update with only the current observation x_t.
        unnormalized = predicted_log_prob + emissions[t]
        scale = float(_logsumexp(unnormalized, axis=0))
        if not np.isfinite(scale):
            raise ValueError(f"Observation at sequence index {t} has zero probability under all states.")
        log_alpha[t] = unnormalized - scale
        total_log_likelihood += scale

    probabilities = np.exp(log_alpha)
    return FilterResult(
        probabilities=probabilities,
        log_alpha=log_alpha,
        log_likelihood=float(total_log_likelihood),
    )
