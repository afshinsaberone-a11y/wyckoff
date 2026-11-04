"""Fail-closed validator for chronological financial ML fold manifests.

This validates experiment metadata only. It does not build folds or train models.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


_REQUIRED = {
    "fold_id",
    "train_start_seq",
    "train_end_seq",
    "validation_start_seq",
    "validation_end_seq",
    "test_start_seq",
    "test_end_seq",
    "label_horizon_bars",
    "purge_rule",
    "embargo_bars",
    "group_policy",
    "scaler_fit_scope",
    "model_fit_scope",
    "threshold_selection_scope",
}


class FoldManifestRejected(ValueError):
    """Raised when a fold manifest violates the frozen governance contract."""


def _strict_non_negative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise FoldManifestRejected(f"{name} must be a non-negative integer.")
    return value


def _non_empty_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FoldManifestRejected(f"{name} must be a non-empty string.")
    return value


def validate_fold_manifest(manifest: Mapping[str, Any]) -> None:
    """Validate split chronology and prevent test-informed fit/threshold choices.

    Sequence indices must use one frozen, monotonically increasing bar/sequence
    basis for all windows. Label-interval purging and group-aware splitting are
    required by policy, but the actual candidate-level purge is performed by a
    separate data-splitting stage (for example W2's purge primitive).
    """
    if not isinstance(manifest, Mapping):
        raise FoldManifestRejected("manifest must be a mapping.")

    missing = _REQUIRED - set(manifest.keys())
    if missing:
        raise FoldManifestRejected(f"Missing required fields: {sorted(missing)}")

    _non_empty_text(manifest["fold_id"], "fold_id")
    for key in (
        "train_start_seq", "train_end_seq",
        "validation_start_seq", "validation_end_seq",
        "test_start_seq", "test_end_seq",
        "embargo_bars",
    ):
        _strict_non_negative_int(manifest[key], key)

    horizon = _strict_non_negative_int(manifest["label_horizon_bars"], "label_horizon_bars")
    if horizon < 1:
        raise FoldManifestRejected("label_horizon_bars must be at least 1.")

    windows = (
        ("train", manifest["train_start_seq"], manifest["train_end_seq"]),
        ("validation", manifest["validation_start_seq"], manifest["validation_end_seq"]),
        ("test", manifest["test_start_seq"], manifest["test_end_seq"]),
    )
    for name, start, end in windows:
        if start > end:
            raise FoldManifestRejected(f"{name} window start must be <= end.")

    if not manifest["train_end_seq"] < manifest["validation_start_seq"]:
        raise FoldManifestRejected("Train and Validation windows must be strictly chronological and non-overlapping.")
    if not manifest["validation_end_seq"] < manifest["test_start_seq"]:
        raise FoldManifestRejected("Validation and Test windows must be strictly chronological and non-overlapping.")

    purge_rule = _non_empty_text(manifest["purge_rule"], "purge_rule")
    if purge_rule != "LABEL_INTERVAL_OVERLAP":
        raise FoldManifestRejected("purge_rule must be LABEL_INTERVAL_OVERLAP.")

    _non_empty_text(manifest["group_policy"], "group_policy")
    for key in ("scaler_fit_scope", "model_fit_scope"):
        if manifest[key] != "TRAIN_ONLY":
            raise FoldManifestRejected(f"{key} must be TRAIN_ONLY.")
    if manifest["threshold_selection_scope"] != "VALIDATION_ONLY":
        raise FoldManifestRejected("threshold_selection_scope must be VALIDATION_ONLY.")
