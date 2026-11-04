"""Point-in-time candidate contract and interval purge utilities.

Research-only utilities. They do not train a trading model or create labels.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CandidateSample:
    candidate_id: str
    group_id: str
    decision_seq: int
    feature_available_seq: tuple[int, ...]
    label_start_seq: int
    label_end_seq: int


@dataclass(frozen=True)
class PurgeResult:
    kept: tuple[CandidateSample, ...]
    removed_reasons: dict[str, str]


def validate_candidate(sample: CandidateSample) -> None:
    if not sample.candidate_id.strip():
        raise ValueError("candidate_id must be non-empty.")
    if not sample.group_id.strip():
        raise ValueError("group_id must be non-empty.")
    if sample.decision_seq < 0:
        raise ValueError("decision_seq must be non-negative.")
    if sample.label_start_seq < sample.decision_seq:
        raise ValueError("label interval cannot start before candidate decision.")
    if sample.label_end_seq < sample.label_start_seq:
        raise ValueError("label_end_seq must be >= label_start_seq.")
    for index, available_seq in enumerate(sample.feature_available_seq):
        if available_seq > sample.decision_seq:
            raise ValueError(
                f"Feature {index} is available at sequence {available_seq}, "
                f"after decision sequence {sample.decision_seq}."
            )


def validate_unique_candidates(samples: Iterable[CandidateSample]) -> None:
    seen: set[str] = set()
    for sample in samples:
        validate_candidate(sample)
        if sample.candidate_id in seen:
            raise ValueError(f"Duplicate candidate_id: {sample.candidate_id}")
        seen.add(sample.candidate_id)


def _overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    """Closed-interval overlap."""
    return a_start <= b_end and b_start <= a_end


def purge_training_candidates(
    train: Iterable[CandidateSample],
    test: Iterable[CandidateSample],
    *,
    embargo_bars: int = 0,
    group_aware: bool = True,
) -> PurgeResult:
    """Remove train candidates that leak into test label intervals.

    Purging checks label-interval overlap, then optionally removes any training
    sample from a Range/Cycle group present in test. Embargo excludes training
    candidates immediately after the latest test label end.

    This is a transparent primitive, not a complete CPCV implementation.
    Fold construction, feature-window overlap and chronology remain caller duties.
    """
    train_items = tuple(train)
    test_items = tuple(test)
    validate_unique_candidates(train_items)
    validate_unique_candidates(test_items)
    cross_split_ids = {x.candidate_id for x in train_items} & {x.candidate_id for x in test_items}
    if cross_split_ids:
        raise ValueError(f"Candidate IDs appear in both train and test: {sorted(cross_split_ids)}")

    if embargo_bars < 0:
        raise ValueError("embargo_bars must be non-negative.")
    if not test_items:
        return PurgeResult(kept=train_items, removed_reasons={})

    test_intervals = tuple((x.label_start_seq, x.label_end_seq) for x in test_items)
    test_groups = {x.group_id for x in test_items}
    latest_test_end = max(x.label_end_seq for x in test_items)

    kept: list[CandidateSample] = []
    removed: dict[str, str] = {}
    for item in train_items:
        if group_aware and item.group_id in test_groups:
            removed[item.candidate_id] = "GROUP_OVERLAP"
            continue

        if any(
            _overlap(item.label_start_seq, item.label_end_seq, start, end)
            for start, end in test_intervals
        ):
            removed[item.candidate_id] = "LABEL_INTERVAL_OVERLAP"
            continue

        if (
            embargo_bars > 0
            and latest_test_end < item.decision_seq <= latest_test_end + embargo_bars
        ):
            removed[item.candidate_id] = "EMBARGO"
            continue

        kept.append(item)

    return PurgeResult(kept=tuple(kept), removed_reasons=removed)
