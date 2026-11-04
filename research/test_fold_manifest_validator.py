from __future__ import annotations

import unittest

from fold_manifest_validator import FoldManifestRejected, validate_fold_manifest


def valid_fold():
    return {
        "fold_id": "WF-001",
        "train_start_seq": 0,
        "train_end_seq": 999,
        "validation_start_seq": 1012,
        "validation_end_seq": 1249,
        "test_start_seq": 1262,
        "test_end_seq": 1499,
        "label_horizon_bars": 12,
        "purge_rule": "LABEL_INTERVAL_OVERLAP",
        "embargo_bars": 12,
        "group_policy": "RANGE_GROUPED",
        "scaler_fit_scope": "TRAIN_ONLY",
        "model_fit_scope": "TRAIN_ONLY",
        "threshold_selection_scope": "VALIDATION_ONLY",
    }


class FoldManifestTests(unittest.TestCase):
    def test_accepts_chronological_frozen_fold(self):
        validate_fold_manifest(valid_fold())

    def test_rejects_train_validation_overlap(self):
        fold = valid_fold()
        fold["validation_start_seq"] = fold["train_end_seq"]
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_validation_test_overlap(self):
        fold = valid_fold()
        fold["test_start_seq"] = fold["validation_end_seq"]
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_reversed_window(self):
        fold = valid_fold()
        fold["train_start_seq"] = 1000
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_boolean_sequence(self):
        fold = valid_fold()
        fold["test_start_seq"] = True
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_negative_embargo(self):
        fold = valid_fold()
        fold["embargo_bars"] = -1
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_zero_label_horizon(self):
        fold = valid_fold()
        fold["label_horizon_bars"] = 0
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_row_count_purge_instead_of_label_interval_purge(self):
        fold = valid_fold()
        fold["purge_rule"] = "FIXED_ROW_GAP"
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_scaler_fit_outside_train(self):
        fold = valid_fold()
        fold["scaler_fit_scope"] = "TRAIN_AND_TEST"
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_model_fit_outside_train(self):
        fold = valid_fold()
        fold["model_fit_scope"] = "ALL_DATA"
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_threshold_tuning_on_test(self):
        fold = valid_fold()
        fold["threshold_selection_scope"] = "TEST_ONLY"
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_missing_group_policy(self):
        fold = valid_fold()
        fold["group_policy"] = " "
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)

    def test_rejects_missing_required_field(self):
        fold = valid_fold()
        del fold["label_horizon_bars"]
        with self.assertRaises(FoldManifestRejected):
            validate_fold_manifest(fold)


if __name__ == "__main__":
    unittest.main()
