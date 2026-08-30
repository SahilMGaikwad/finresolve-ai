"""
FinResolve AI — Property-Based Tests

Uses Hypothesis to verify invariants that must hold for
all generated data, not just specific examples.
"""

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from data.generators.config import GeneratorConfig
from data.generators.generate import generate_dataset


class TestPropertyBased:
    """Properties that must hold for all generated data."""

    @given(seed=st.integers(min_value=0, max_value=100000))
    @settings(max_examples=5, deadline=30000)
    def test_all_amounts_non_negative(self, seed):
        """For every clean payment: amount_minor >= 0."""
        config = GeneratorConfig(seed=seed, num_cases=10, corruption_rate=0.0)
        cases, _ = generate_dataset(config)

        for case in cases:
            for payment in case.ground_truth.payments:
                assert payment["amount"]["amount_minor"] >= 0, (
                    f"Negative amount in case {case.case_id}"
                )

    @given(seed=st.integers(min_value=0, max_value=100000))
    @settings(max_examples=5, deadline=30000)
    def test_all_case_ids_unique(self, seed):
        """For every generated case: case_id is unique."""
        config = GeneratorConfig(seed=seed, num_cases=50, corruption_rate=0.1)
        cases, _ = generate_dataset(config)

        case_ids = [c.case_id for c in cases]
        assert len(case_ids) == len(set(case_ids)), "Duplicate case_ids found"

    @given(seed=st.integers(min_value=0, max_value=100000))
    @settings(max_examples=5, deadline=30000)
    def test_referenced_ids_exist(self, seed):
        """For every valid relationship: referenced IDs exist."""
        config = GeneratorConfig(seed=seed, num_cases=10, corruption_rate=0.0)
        cases, _ = generate_dataset(config)

        for case in cases:
            payment_ids = {p["payment_id"] for p in case.ground_truth.payments}
            order_ids = {o["order_id"] for o in case.ground_truth.orders}

            for payment in case.ground_truth.payments:
                assert payment["order_id"] in order_ids
            for settlement in case.ground_truth.settlements:
                assert settlement["payment_id"] in payment_ids
            for fee in case.ground_truth.fees:
                assert fee["payment_id"] in payment_ids

    @given(seed=st.integers(min_value=0, max_value=100000))
    @settings(max_examples=3, deadline=60000)
    def test_deterministic_generation(self, seed):
        """same seed + same config = same dataset."""
        config = GeneratorConfig(seed=seed, num_cases=10, corruption_rate=0.2)

        cases1, summary1 = generate_dataset(config)
        cases2, summary2 = generate_dataset(config)

        assert summary1["case_count"] == summary2["case_count"]
        assert summary1["corrupted_cases"] == summary2["corrupted_cases"]
        assert summary1["record_counts"] == summary2["record_counts"]

        for c1, c2 in zip(cases1, cases2):
            assert c1.case_id == c2.case_id
            assert len(c1.corruptions) == len(c2.corruptions)

    @given(seed=st.integers(min_value=0, max_value=100000))
    @settings(max_examples=5, deadline=30000)
    def test_fee_amounts_non_negative(self, seed):
        """All fee amounts must be non-negative."""
        config = GeneratorConfig(seed=seed, num_cases=10, corruption_rate=0.0)
        cases, _ = generate_dataset(config)

        for case in cases:
            for fee in case.ground_truth.fees:
                assert fee["amount"]["amount_minor"] >= 0

    @given(seed=st.integers(min_value=0, max_value=100000))
    @settings(max_examples=5, deadline=30000)
    def test_settlement_net_not_greater_than_gross(self, seed):
        """Net settlement should not exceed gross settlement."""
        config = GeneratorConfig(seed=seed, num_cases=10, corruption_rate=0.0)
        cases, _ = generate_dataset(config)

        for case in cases:
            for settlement in case.ground_truth.settlements:
                gross = settlement["gross_amount"]["amount_minor"]
                net = settlement["net_amount"]["amount_minor"]
                assert net <= gross, (
                    f"Net ({net}) > Gross ({gross}) in case {case.case_id}"
                )
