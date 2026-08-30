"""
FinResolve AI — Generator Determinism Tests

Verifies that the generator produces deterministic, reproducible output.
"""

import json
import random

import pytest

from data.generators.cases import generate_case
from data.generators.config import GeneratorConfig
from data.generators.generate import generate_dataset
from data.generators.merchants import generate_merchants


class TestGeneratorDeterminism:
    """Same seed → same output, different seed → different output."""

    def test_same_seed_same_merchants(self):
        config = GeneratorConfig(seed=42, merchant_count=5)
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        merchants1 = generate_merchants(config, rng1)
        merchants2 = generate_merchants(config, rng2)
        assert len(merchants1) == len(merchants2)
        for m1, m2 in zip(merchants1, merchants2):
            assert m1.merchant_id == m2.merchant_id
            assert m1.name == m2.name
            assert m1.platform_fee_bps == m2.platform_fee_bps

    def test_different_seed_different_merchants(self):
        config1 = GeneratorConfig(seed=42, merchant_count=5)
        config2 = GeneratorConfig(seed=99, merchant_count=5)
        merchants1 = generate_merchants(config1, random.Random(42))
        merchants2 = generate_merchants(config2, random.Random(99))
        # At least one merchant should differ
        names1 = [m.name for m in merchants1]
        names2 = [m.name for m in merchants2]
        assert names1 != names2

    def test_same_seed_same_cases(self):
        config = GeneratorConfig(seed=42, num_cases=20, corruption_rate=0.3)
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        merchants = generate_merchants(config, random.Random(42))

        cases1 = [generate_case(i, merchants[i % len(merchants)], config, rng1) for i in range(20)]
        cases2 = [generate_case(i, merchants[i % len(merchants)], config, rng2) for i in range(20)]

        # Regenerate merchants with same seed for second run
        merchants2 = generate_merchants(config, random.Random(42))
        rng2b = random.Random(42)
        cases2b = [generate_case(i, merchants2[i % len(merchants2)], config, rng2b) for i in range(20)]

        for c1, c2 in zip(cases1, cases2b):
            assert c1.case_id == c2.case_id
            assert len(c1.corruptions) == len(c2.corruptions)
            assert c1.expected_outcome.has_discrepancy == c2.expected_outcome.has_discrepancy

    def test_different_seed_different_cases(self):
        config1 = GeneratorConfig(seed=42, num_cases=5, corruption_rate=0.5)
        config2 = GeneratorConfig(seed=99, num_cases=5, corruption_rate=0.5)
        merchants1 = generate_merchants(config1, random.Random(42))
        merchants2 = generate_merchants(config2, random.Random(99))

        rng1 = random.Random(42)
        rng2 = random.Random(99)
        cases1 = [generate_case(i, merchants1[i % len(merchants1)], config1, rng1) for i in range(5)]
        cases2 = [generate_case(i, merchants2[i % len(merchants2)], config2, rng2) for i in range(5)]

        # Payment amounts should differ between seeds
        amounts1 = [c.ground_truth.payments[0]["amount"]["amount_minor"] for c in cases1]
        amounts2 = [c.ground_truth.payments[0]["amount"]["amount_minor"] for c in cases2]
        assert amounts1 != amounts2


class TestGeneratorConfiguration:
    """Configuration changes affect expected dimensions."""

    def test_case_count_matches_config(self):
        config = GeneratorConfig(seed=42, num_cases=50, corruption_rate=0.0)
        cases, summary = generate_dataset(config)
        assert len(cases) == 50
        assert summary["case_count"] == 50

    def test_no_corruption_produces_clean_cases(self):
        config = GeneratorConfig(seed=42, num_cases=20, corruption_rate=0.0)
        cases, summary = generate_dataset(config)
        for case in cases:
            assert len(case.corruptions) == 0
            assert case.expected_outcome.has_discrepancy is False
        assert summary["corrupted_cases"] == 0

    def test_full_corruption_produces_corrupted_cases(self):
        config = GeneratorConfig(seed=42, num_cases=20, corruption_rate=1.0)
        cases, summary = generate_dataset(config)
        # All cases should have corruption
        for case in cases:
            assert len(case.corruptions) > 0
            assert case.expected_outcome.has_discrepancy is True
        assert summary["corrupted_cases"] == 20

    def test_merchant_count_matches_config(self):
        config = GeneratorConfig(seed=42, merchant_count=7)
        merchants = generate_merchants(config, random.Random(42))
        assert len(merchants) == 7

    def test_configuration_hash_deterministic(self):
        config1 = GeneratorConfig(seed=42, num_cases=100)
        config2 = GeneratorConfig(seed=42, num_cases=100)
        assert config1.configuration_hash() == config2.configuration_hash()

    def test_configuration_hash_changes_with_params(self):
        config1 = GeneratorConfig(seed=42, num_cases=100)
        config2 = GeneratorConfig(seed=42, num_cases=200)
        assert config1.configuration_hash() != config2.configuration_hash()

    def test_every_case_has_records(self):
        config = GeneratorConfig(seed=42, num_cases=10, corruption_rate=0.0)
        cases, _ = generate_dataset(config)
        for case in cases:
            assert len(case.ground_truth.payments) >= 1
            assert len(case.ground_truth.orders) >= 1
            assert len(case.ground_truth.settlements) >= 1
            assert len(case.ground_truth.fees) >= 1
            assert len(case.ground_truth.ledger_entries) >= 1
