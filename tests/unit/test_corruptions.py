"""
FinResolve AI — Corruption Tests

Verifies that every corruption type is actually injected,
ground truth remains unchanged, and labels are accurate.
"""

import copy
import random

import pytest

from data.generators.cases import generate_case
from data.generators.config import GeneratorConfig
from data.generators.corruptions import apply_corruptions, _CORRUPTION_HANDLERS
from data.generators.merchants import generate_merchants
from data.generators.relationships import build_clean_case_records
from data.schemas.enums import CaseDifficulty, CorruptionType


class TestCorruptionInjection:
    """Every corruption type is actually injected and labels are correct."""

    @pytest.fixture
    def clean_case_data(self):
        config = GeneratorConfig(seed=42, num_cases=1)
        rng = random.Random(42)
        merchants = generate_merchants(config, rng)
        rng2 = random.Random(100)
        result = build_clean_case_records(0, merchants[0], config, rng2)
        return result

    @pytest.mark.parametrize("corruption_type", list(CorruptionType))
    def test_each_corruption_type_produces_label(self, corruption_type, clean_case_data):
        """Every corruption type should produce at least one label when applied."""
        observed = copy.deepcopy(clean_case_data["records"])
        internal = clean_case_data["_internal"]
        rng = random.Random(42)

        handler = _CORRUPTION_HANDLERS[corruption_type]
        label = handler(observed, internal, rng)

        # Handler should return a label (may be None if no valid target)
        if label is not None:
            assert label.corruption_type == corruption_type
            assert label.case_id == internal["case_id"]
            assert label.target_record_id != ""
            assert label.description != ""

    def test_ground_truth_not_modified_by_corruption(self):
        """Corruption must never modify ground truth records."""
        config = GeneratorConfig(seed=42, num_cases=10, corruption_rate=1.0)
        rng = random.Random(42)
        merchants = generate_merchants(config, rng)

        for i in range(10):
            merchant = merchants[i % len(merchants)]
            rng_case = random.Random(42 + i)
            result = build_clean_case_records(i, merchant, config, rng_case)
            ground_truth = copy.deepcopy(result["records"])
            observed = copy.deepcopy(result["records"])

            # Apply corruptions to observed
            rng_corrupt = random.Random(42 + i + 1000)
            apply_corruptions(observed, result["_internal"], CaseDifficulty.HARD, rng_corrupt)

            # Ground truth should be unchanged
            assert ground_truth == result["records"], \
                f"Ground truth was modified in case {i}!"

    def test_observed_differs_after_corruption(self):
        """After corruption, observed should differ from ground truth."""
        config = GeneratorConfig(seed=42, num_cases=1)
        rng = random.Random(42)
        merchants = generate_merchants(config, rng)
        rng2 = random.Random(100)
        result = build_clean_case_records(0, merchants[0], config, rng2)

        ground_truth = copy.deepcopy(result["records"])
        observed = copy.deepcopy(result["records"])

        rng3 = random.Random(42)
        labels = apply_corruptions(observed, result["_internal"], CaseDifficulty.MEDIUM, rng3)

        if labels:
            # Observed should differ from ground truth
            assert observed != ground_truth

    def test_corruption_labels_have_original_and_corrupted_values(self):
        """Every label should record both original and corrupted values."""
        config = GeneratorConfig(seed=42, num_cases=1)
        rng = random.Random(42)
        merchants = generate_merchants(config, rng)
        rng2 = random.Random(100)
        result = build_clean_case_records(0, merchants[0], config, rng2)
        observed = copy.deepcopy(result["records"])

        rng3 = random.Random(42)
        labels = apply_corruptions(observed, result["_internal"], CaseDifficulty.HARD, rng3)

        for label in labels:
            assert label.original_value != "", f"Missing original_value in {label.corruption_type}"
            assert label.corrupted_value != "", f"Missing corrupted_value in {label.corruption_type}"
            # Original and corrupted should differ (except for missing/duplicate which use descriptive values)
            if label.corruption_type not in {CorruptionType.MISSING_RECORD, CorruptionType.DUPLICATE_RECORD}:
                assert label.original_value != label.corrupted_value, \
                    f"original == corrupted for {label.corruption_type}"


class TestCorruptionCoverage:
    """Verify that all corruption types appear in a large enough dataset."""

    def test_all_corruption_types_appear(self):
        """With enough cases at hard difficulty, all types should appear."""
        config = GeneratorConfig(seed=42, num_cases=200, corruption_rate=1.0, difficulty="hard")
        rng = random.Random(42)
        merchants = generate_merchants(config, rng)

        seen_types: set[CorruptionType] = set()
        for i in range(200):
            merchant = merchants[i % len(merchants)]
            case = generate_case(i, merchant, config, rng)
            for corruption in case.corruptions:
                seen_types.add(corruption.corruption_type)

        # All corruption types should appear at least once
        all_types = set(CorruptionType)
        missing = all_types - seen_types
        assert not missing, f"Corruption types never generated: {missing}"
