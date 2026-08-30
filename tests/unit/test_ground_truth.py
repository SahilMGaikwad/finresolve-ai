"""
FinResolve AI — Ground Truth Tests

Verifies that corrupted cases can be identified from ground truth,
and that ground truth labels are consistent with corruptions applied.
"""

import pytest

from data.generators.config import GeneratorConfig
from data.generators.generate import generate_dataset


class TestGroundTruth:
    """Ground truth labels match corruption state."""

    @pytest.fixture
    def dataset_with_corruptions(self):
        config = GeneratorConfig(seed=42, num_cases=50, corruption_rate=0.5)
        cases, _ = generate_dataset(config)
        return cases

    @pytest.fixture
    def clean_dataset(self):
        config = GeneratorConfig(seed=42, num_cases=20, corruption_rate=0.0)
        cases, _ = generate_dataset(config)
        return cases

    def test_corrupted_cases_have_discrepancy_flag(self, dataset_with_corruptions):
        for case in dataset_with_corruptions:
            if case.corruptions:
                assert case.expected_outcome.has_discrepancy is True, (
                    f"Case {case.case_id} has corruptions but has_discrepancy is False"
                )

    def test_clean_cases_have_no_discrepancy_flag(self, dataset_with_corruptions):
        for case in dataset_with_corruptions:
            if not case.corruptions:
                assert case.expected_outcome.has_discrepancy is False, (
                    f"Case {case.case_id} has no corruptions but has_discrepancy is True"
                )

    def test_all_clean_cases_clean(self, clean_dataset):
        for case in clean_dataset:
            assert case.expected_outcome.has_discrepancy is False
            assert case.expected_outcome.discrepancy_type is None
            assert case.expected_outcome.root_cause is None

    def test_corrupted_cases_have_discrepancy_type(self, dataset_with_corruptions):
        for case in dataset_with_corruptions:
            if case.corruptions:
                assert case.expected_outcome.discrepancy_type is not None
                assert case.expected_outcome.root_cause is not None

    def test_ground_truth_not_leaked_to_observed(self, dataset_with_corruptions):
        """Observed data must not contain ground-truth labels."""
        for case in dataset_with_corruptions:
            if case.corruptions:
                # Ground truth and observed should differ
                gt_payments = case.ground_truth.payments
                obs_payments = case.observed.payments
                # At the very least, for corrupted cases that touch
                # non-payment fields, payments may be the same.
                # But the overall observed bundle should differ from ground truth.
                gt_dict = case.ground_truth.model_dump()
                obs_dict = case.observed.model_dump()
                assert gt_dict != obs_dict, (
                    f"Case {case.case_id} has corruptions but "
                    "ground_truth == observed"
                )

    def test_correct_resolution_has_actions(self, dataset_with_corruptions):
        for case in dataset_with_corruptions:
            if case.corruptions:
                resolution = case.expected_outcome.correct_resolution
                assert resolution is not None
                assert "actions" in resolution
                assert len(resolution["actions"]) > 0

    def test_resolution_references_corruption_types(self, dataset_with_corruptions):
        """Resolution actions should reference the corruption types that caused them."""
        for case in dataset_with_corruptions:
            if case.corruptions:
                resolution = case.expected_outcome.correct_resolution
                corruption_types = {c.corruption_type.value for c in case.corruptions}
                action_types = {a["corruption_type"] for a in resolution["actions"]}
                assert action_types == corruption_types, (
                    f"Case {case.case_id}: action types {action_types} "
                    f"don't match corruption types {corruption_types}"
                )
