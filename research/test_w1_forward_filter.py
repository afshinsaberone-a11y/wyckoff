from __future__ import annotations

import unittest

import numpy as np

from w1_forward_filter import forward_filter


class ForwardFilterTests(unittest.TestCase):
    def setUp(self):
        self.transition = np.array([[0.92, 0.08], [0.15, 0.85]], dtype=float)
        self.initial = np.array([0.6, 0.4], dtype=float)
        self.emission = np.log(
            np.array([
                [0.8, 0.2],
                [0.7, 0.3],
                [0.2, 0.8],
                [0.1, 0.9],
            ], dtype=float)
        )

    def test_probabilities_are_normalized(self):
        result = forward_filter(self.emission, self.transition, self.initial)
        np.testing.assert_allclose(result.probabilities.sum(axis=1), 1.0, atol=1e-12)
        self.assertTrue(np.all(result.probabilities >= 0.0))
        self.assertTrue(np.isfinite(result.log_likelihood))

    def test_future_observations_do_not_change_past_filtered_values(self):
        original = forward_filter(self.emission, self.transition, self.initial)
        changed = self.emission.copy()
        changed[3] = np.log(np.array([1e-7, 1.0 - 1e-7]))
        revised = forward_filter(changed, self.transition, self.initial)
        np.testing.assert_allclose(
            original.probabilities[:3],
            revised.probabilities[:3],
            atol=1e-12,
        )

    def test_continuation_uses_propagated_last_posterior(self):
        full = forward_filter(self.emission, self.transition, self.initial)
        first = forward_filter(self.emission[:2], self.transition, self.initial)
        next_prior = first.probabilities[-1] @ self.transition
        second = forward_filter(self.emission[2:], self.transition, next_prior)
        np.testing.assert_allclose(
            np.vstack([first.probabilities, second.probabilities]),
            full.probabilities,
            atol=1e-12,
        )

    def test_rejects_non_stochastic_transition_matrix(self):
        invalid = np.array([[0.9, 0.2], [0.1, 0.9]], dtype=float)
        with self.assertRaises(ValueError):
            forward_filter(self.emission, invalid, self.initial)

    def test_rejects_shape_mismatch(self):
        with self.assertRaises(ValueError):
            forward_filter(self.emission, np.eye(3), self.initial)

    def test_rejects_zero_initial_mass(self):
        with self.assertRaises(ValueError):
            forward_filter(self.emission, self.transition, np.array([0.0, 0.0]))


if __name__ == "__main__":
    unittest.main()
