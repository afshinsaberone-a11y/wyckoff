from __future__ import annotations

import unittest

from w2_candidate_validator import (
    CandidateSample,
    purge_training_candidates,
    validate_candidate,
    validate_unique_candidates,
)


def sample(candidate_id, group, decision, available, label_start, label_end):
    return CandidateSample(
        candidate_id=candidate_id,
        group_id=group,
        decision_seq=decision,
        feature_available_seq=tuple(available),
        label_start_seq=label_start,
        label_end_seq=label_end,
    )


class CandidateValidatorTests(unittest.TestCase):
    def test_accepts_point_in_time_features(self):
        validate_candidate(sample("c1", "r1", 10, [7, 10], 11, 15))

    def test_rejects_feature_available_after_decision(self):
        with self.assertRaises(ValueError):
            validate_candidate(sample("c1", "r1", 10, [7, 11], 11, 15))

    def test_rejects_duplicate_candidate_id(self):
        rows = [
            sample("c1", "r1", 10, [8], 11, 15),
            sample("c1", "r2", 20, [19], 21, 25),
        ]
        with self.assertRaises(ValueError):
            validate_unique_candidates(rows)

    def test_rejects_same_candidate_in_train_and_test(self):
        train = [sample("c1", "r1", 10, [9], 11, 15)]
        test = [sample("c1", "r1", 10, [9], 11, 15)]
        with self.assertRaises(ValueError):
            purge_training_candidates(train, test)

    def test_purges_overlapping_label_intervals(self):
        train = [
            sample("tr_before", "r1", 5, [4], 6, 9),
            sample("tr_overlap", "r2", 12, [11], 13, 18),
        ]
        test = [sample("te", "r3", 14, [13], 15, 20)]
        result = purge_training_candidates(train, test, group_aware=False)
        self.assertEqual([x.candidate_id for x in result.kept], ["tr_before"])
        self.assertEqual(result.removed_reasons["tr_overlap"], "LABEL_INTERVAL_OVERLAP")

    def test_purges_same_group_and_embargo(self):
        train = [
            sample("same_group", "r_test", 5, [4], 6, 7),
            sample("embargoed", "r_other", 25, [24], 26, 30),
            sample("kept", "r_far", 40, [39], 41, 45),
        ]
        test = [sample("te", "r_test", 10, [9], 11, 20)]
        result = purge_training_candidates(train, test, embargo_bars=10)
        self.assertEqual([x.candidate_id for x in result.kept], ["kept"])
        self.assertEqual(result.removed_reasons["same_group"], "GROUP_OVERLAP")
        self.assertEqual(result.removed_reasons["embargoed"], "EMBARGO")


if __name__ == "__main__":
    unittest.main()
