"""
FinResolve AI — Matching Service

Deterministic multi-signal matching for financial records.
"""

from services.matching.matcher import MatcherConfig, RecordMatcher, evaluate_pair
from services.matching.signals import (
    evaluate_amount_signal,
    evaluate_currency_signal,
    evaluate_merchant_signal,
    evaluate_reference_signal,
    evaluate_timestamp_proximity_signal,
)

__all__ = [
    "MatcherConfig",
    "RecordMatcher",
    "evaluate_amount_signal",
    "evaluate_currency_signal",
    "evaluate_merchant_signal",
    "evaluate_pair",
    "evaluate_reference_signal",
    "evaluate_timestamp_proximity_signal",
]
