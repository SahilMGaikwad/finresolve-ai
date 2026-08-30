"""
FinResolve AI — Synthetic Merchant Generator

Generates deterministic synthetic merchant profiles.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from data.generators.config import GeneratorConfig


@dataclass(frozen=True)
class MerchantProfile:
    """
    A synthetic merchant profile.

    Contains merchant-specific parameters that influence
    transaction generation (fee rates, typical amounts, etc.).
    """

    merchant_id: str
    name: str
    category: str
    platform_fee_bps: int       # Merchant-specific fee rate (basis points)
    gst_on_fee_bps: int         # GST rate on fees (basis points)
    typical_min_amount: int     # Typical minimum transaction (paise)
    typical_max_amount: int     # Typical maximum transaction (paise)
    settlement_delay_days: int  # Typical days from payment to settlement


# Merchant business categories for realistic diversity
_CATEGORIES = [
    "e-commerce",
    "food_delivery",
    "saas",
    "travel",
    "education",
    "healthcare",
    "retail",
    "entertainment",
    "logistics",
    "fintech",
]

_NAME_PREFIXES = [
    "Nova", "Pixel", "Apex", "Synth", "Orbit",
    "Flux", "Bolt", "Crest", "Nimbus", "Zeta",
    "Prism", "Helix", "Quartz", "Pulse", "Vertex",
]

_NAME_SUFFIXES = [
    "Corp", "Labs", "Tech", "Solutions", "Systems",
    "Digital", "Works", "Hub", "Platform", "Services",
]


def generate_merchants(config: GeneratorConfig, rng: random.Random) -> list[MerchantProfile]:
    """
    Generate a list of synthetic merchant profiles.

    Deterministic for a given seed (via the provided rng instance).

    Args:
        config: Generator configuration.
        rng: Seeded Random instance for deterministic output.

    Returns:
        List of MerchantProfile instances.
    """
    merchants: list[MerchantProfile] = []

    for i in range(config.merchant_count):
        merchant_id = f"merchant_{i + 1:04d}"

        # Generate a synthetic but readable name
        prefix = rng.choice(_NAME_PREFIXES)
        suffix = rng.choice(_NAME_SUFFIXES)
        name = f"{prefix} {suffix}"

        category = _CATEGORIES[i % len(_CATEGORIES)]

        # Merchant-specific fee variation: ±50 bps around the base rate
        fee_variation = rng.randint(-50, 50)
        platform_fee_bps = max(50, config.platform_fee_bps + fee_variation)

        # Amount range variation per merchant
        amount_range = config.max_amount_minor - config.min_amount_minor
        typical_min = config.min_amount_minor + rng.randint(0, amount_range // 4)
        typical_max = config.min_amount_minor + rng.randint(amount_range // 2, amount_range)

        # Settlement delay: 1–7 days
        settlement_delay = rng.randint(1, 7)

        merchants.append(
            MerchantProfile(
                merchant_id=merchant_id,
                name=name,
                category=category,
                platform_fee_bps=platform_fee_bps,
                gst_on_fee_bps=config.gst_on_fee_bps,
                typical_min_amount=typical_min,
                typical_max_amount=typical_max,
                settlement_delay_days=settlement_delay,
            )
        )

    return merchants
