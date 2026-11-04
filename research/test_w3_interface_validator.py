from __future__ import annotations

import unittest

from w3_interface_validator import InterfaceRejected, validate_hmm_payload


def valid_payload():
    return {
        "schema_version": "W3_HMM_ML_INTERFACE_V1",
        "run_id": "RUN-001",
        "candidate_id": "RUN-001:R3:C2:A1:E4",
        "decision_seq": 500,
        "as_of_seq": 500,
        "available_at_seq": 500,
        "time_basis": "BROKER_SERVER_RAW_SEQUENCE",
        "hmm_model_version": "hmm-k3-fold2-v1",
        "fold_id": "fold-2",
        "state_mapping_version": "map-fold2-v1",
        "filtered_probabilities": [0.15, 0.7, 0.15],
        "posterior_entropy": 0.82,
        "data_version": "xau-h1-v0",
    }


class HybridInterfaceTests(unittest.TestCase):
    def test_accepts_valid_causal_probability_payload(self):
        validate_hmm_payload(valid_payload(), expected_states=3)

    def test_rejects_missing_probability_vector(self):
        payload = valid_payload()
        del payload["filtered_probabilities"]
        with self.assertRaises(InterfaceRejected):
            validate_hmm_payload(payload, expected_states=3)

    def test_rejects_probabilities_that_do_not_sum_to_one(self):
        payload = valid_payload()
        payload["filtered_probabilities"] = [0.2, 0.2, 0.2]
        with self.assertRaises(InterfaceRejected):
            validate_hmm_payload(payload, expected_states=3)

    def test_rejects_future_available_regime_probability(self):
        payload = valid_payload()
        payload["available_at_seq"] = payload["decision_seq"] + 1
        with self.assertRaises(InterfaceRejected):
            validate_hmm_payload(payload, expected_states=3)

    def test_rejects_stale_regime_probability(self):
        payload = valid_payload()
        payload["as_of_seq"] = 490
        payload["available_at_seq"] = 490
        with self.assertRaises(InterfaceRejected):
            validate_hmm_payload(payload, expected_states=3, max_staleness_bars=1)

    def test_rejects_unexpected_payload_fields(self):
        payload = valid_payload()
        payload["unversioned_extra"] = "must not pass schema additionalProperties=false"
        with self.assertRaises(InterfaceRejected):
            validate_hmm_payload(payload, expected_states=3)

    def test_rejects_expected_state_count_below_schema_minimum(self):
        with self.assertRaises(InterfaceRejected):
            validate_hmm_payload(valid_payload(), expected_states=1)

    def test_rejects_invalid_staleness_configuration(self):
        with self.assertRaises(InterfaceRejected):
            validate_hmm_payload(valid_payload(), expected_states=3, max_staleness_bars=-1)

    def test_rejects_invalid_probability_tolerance(self):
        with self.assertRaises(InterfaceRejected):
            validate_hmm_payload(valid_payload(), expected_states=3, probability_tolerance=float("nan"))

    def test_validates_optional_timestamp_field_types(self):
        payload = valid_payload()
        payload["observed_at_server"] = 123
        with self.assertRaises(InterfaceRejected):
            validate_hmm_payload(payload, expected_states=3)

    def test_allows_schema_optional_timestamp_fields(self):
        payload = valid_payload()
        payload["source_bar_open_server"] = None
        payload["observed_at_server"] = "2026-11-04T12:00:00"
        validate_hmm_payload(payload, expected_states=3)

    def test_rejects_wrong_state_dimension(self):
        payload = valid_payload()
        payload["filtered_probabilities"] = [0.4, 0.6]
        with self.assertRaises(InterfaceRejected):
            validate_hmm_payload(payload, expected_states=3)


if __name__ == "__main__":
    unittest.main()
