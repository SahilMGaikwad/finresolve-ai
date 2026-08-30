"""
FinResolve AI — Generator Configuration

Typed configuration for the synthetic data generator.
Supports deterministic hashing for manifest reproducibility.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from data.schemas.enums import CaseDifficulty, Currency


@dataclass(frozen=True)
class GeneratorConfig:
    """
    Configuration for synthetic dataset generation.

    All parameters affecting output are captured here so that
    the configuration hash uniquely identifies the dataset shape.
    """

    # ---- Core ----
    seed: int = 42
    num_cases: int = 1000
    corruption_rate: float = 0.08  # fraction of cases with corruption (0.0–1.0)
    difficulty: str = "mixed"  # "easy", "medium", "hard", "mixed"

    # ---- Merchants ----
    merchant_count: int = 10

    # ---- Amounts (in paise) ----
    min_amount_minor: int = 10000       # ₹100
    max_amount_minor: int = 10000000    # ₹100,000

    # ---- Currency ----
    currency: str = "INR"

    # ---- Date range ----
    start_date: str = "2026-01-01"
    end_date: str = "2026-06-30"

    # ---- Record generation ----
    refund_probability: float = 0.15    # fraction of cases with refunds
    payout_probability: float = 0.30    # fraction of cases that generate payouts

    # ---- Fee rates (basis points) ----
    platform_fee_bps: int = 200         # 2.00%
    gst_on_fee_bps: int = 1800          # 18% GST on the platform fee

    # ---- Output ----
    output_dir: str = "data/generated"

    # ---- Versions ----
    generator_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    dataset_version: str = "1.0.0"

    @property
    def currency_enum(self) -> Currency:
        """Convert string currency to enum."""
        return Currency(self.currency)

    @property
    def difficulty_enum(self) -> CaseDifficulty | None:
        """Convert string difficulty to enum, None for 'mixed'."""
        if self.difficulty == "mixed":
            return None
        return CaseDifficulty(self.difficulty)

    @property
    def output_path(self) -> Path:
        """Full output path including seed subdirectory."""
        return Path(self.output_dir) / f"seed_{self.seed}"

    def configuration_hash(self) -> str:
        """
        Compute a SHA-256 hash of all generation-affecting parameters.

        This hash uniquely identifies the dataset configuration.
        Two configs with the same hash will produce identical datasets.
        """
        # Exclude output_dir from hash — it doesn't affect data content
        hashable = {
            "seed": self.seed,
            "num_cases": self.num_cases,
            "corruption_rate": self.corruption_rate,
            "difficulty": self.difficulty,
            "merchant_count": self.merchant_count,
            "min_amount_minor": self.min_amount_minor,
            "max_amount_minor": self.max_amount_minor,
            "currency": self.currency,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "refund_probability": self.refund_probability,
            "payout_probability": self.payout_probability,
            "platform_fee_bps": self.platform_fee_bps,
            "gst_on_fee_bps": self.gst_on_fee_bps,
            "generator_version": self.generator_version,
            "schema_version": self.schema_version,
        }
        serialised = json.dumps(hashable, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialised.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        """Serialise all configuration for the manifest."""
        return {
            "seed": self.seed,
            "num_cases": self.num_cases,
            "corruption_rate": self.corruption_rate,
            "difficulty": self.difficulty,
            "merchant_count": self.merchant_count,
            "min_amount_minor": self.min_amount_minor,
            "max_amount_minor": self.max_amount_minor,
            "currency": self.currency,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "refund_probability": self.refund_probability,
            "payout_probability": self.payout_probability,
            "platform_fee_bps": self.platform_fee_bps,
            "gst_on_fee_bps": self.gst_on_fee_bps,
            "output_dir": self.output_dir,
            "generator_version": self.generator_version,
            "schema_version": self.schema_version,
            "dataset_version": self.dataset_version,
        }
