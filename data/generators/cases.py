"""
FinResolve AI — Case Generator

Orchestrates generation of individual reconciliation cases.
Each case is a self-contained unit with ground truth and observed data.
"""

from __future__ import annotations

import copy
import random

from data.generators.config import GeneratorConfig
from data.generators.corruptions import apply_corruptions
from data.generators.ground_truth import build_expected_outcome
from data.generators.merchants import MerchantProfile
from data.generators.relationships import build_clean_case_records
from data.schemas.case import CaseRecords, ExpectedOutcome, ReconciliationCase
from data.schemas.corruption import CorruptionLabel
from data.schemas.enums import CaseDifficulty


def _select_difficulty(config: GeneratorConfig, rng: random.Random) -> CaseDifficulty:
    """Select a difficulty level for a case."""
    if config.difficulty_enum is not None:
        return config.difficulty_enum

    # Mixed: weighted distribution
    roll = rng.random()
    if roll < 0.40:
        return CaseDifficulty.EASY
    elif roll < 0.75:
        return CaseDifficulty.MEDIUM
    else:
        return CaseDifficulty.HARD


def generate_case(
    case_index: int,
    merchant: MerchantProfile,
    config: GeneratorConfig,
    rng: random.Random,
) -> ReconciliationCase:
    """
    Generate a single reconciliation case.

    Steps:
    1. Build clean, consistent records (ground truth)
    2. Deep-copy to create observed records
    3. Decide whether to corrupt (based on corruption_rate)
    4. If corrupting: apply corruptions to observed only
    5. Build expected outcome from corruption labels

    Args:
        case_index: Sequential case index (for case_id generation).
        merchant: Merchant profile for this case.
        config: Generator configuration.
        rng: Seeded Random instance.

    Returns:
        A complete ReconciliationCase.
    """
    # Step 1: Build clean records
    result = build_clean_case_records(case_index, merchant, config, rng)
    clean_records = result["records"]
    internal = result["_internal"]
    case_id = internal["case_id"]

    # Step 2: Deep-copy for observed
    observed_records = copy.deepcopy(clean_records)

    # Step 3: Decide whether to corrupt
    difficulty = _select_difficulty(config, rng)
    corruptions: list[CorruptionLabel] = []

    should_corrupt = rng.random() < config.corruption_rate
    if should_corrupt:
        # Step 4: Apply corruptions to observed only
        corruptions = apply_corruptions(observed_records, internal, difficulty, rng)

    # Step 5: Build expected outcome
    expected_outcome = build_expected_outcome(corruptions, difficulty)

    return ReconciliationCase(
        case_id=case_id,
        merchant_id=merchant.merchant_id,
        ground_truth=CaseRecords(**clean_records),
        observed=CaseRecords(**observed_records),
        corruptions=corruptions,
        difficulty=difficulty,
        expected_outcome=expected_outcome,
        metadata={
            "merchant_name": merchant.name,
            "merchant_category": merchant.category,
            "generator_version": config.generator_version,
        },
    )
