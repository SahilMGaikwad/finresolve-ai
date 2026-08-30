"""
FinResolve AI — Matching Engine Unit Tests

Tests multi-signal matching, 1:1, 1:N, N:1 relationships, and ambiguity detection.
"""

from datetime import datetime, timezone

import pytest

from data.schemas.case import CaseRecords
from data.schemas.enums import PaymentMethod, PaymentStatus, RecordType
from data.schemas.matching import MatchState
from data.schemas.money import Currency, Money
from services.matching.matcher import MatcherConfig, RecordMatcher, evaluate_pair
from services.matching.signals import (
    evaluate_amount_signal,
    evaluate_currency_signal,
    evaluate_merchant_signal,
    evaluate_reference_signal,
    evaluate_timestamp_proximity_signal,
)


def _payment_dict(
    payment_id="pay_001",
    order_id="ord_001",
    merchant_id="merchant_0001",
    amount_minor=500000,
    captured_at="2026-03-15T10:00:00+00:00",
) -> dict:
    return {
        "record_type": "payment",
        "payment_id": payment_id,
        "order_id": order_id,
        "merchant_id": merchant_id,
        "amount": {"amount_minor": amount_minor, "currency": "INR"},
        "status": "captured",
        "method": "upi",
        "captured_at": captured_at,
    }


def _settlement_dict(
    settlement_id="stl_001",
    payment_id="pay_001",
    merchant_id="merchant_0001",
    net_minor=488200,
    settled_at="2026-03-17T10:00:00+00:00",
) -> dict:
    return {
        "record_type": "settlement",
        "settlement_id": settlement_id,
        "payment_id": payment_id,
        "merchant_id": merchant_id,
        "gross_amount": {"amount_minor": 500000, "currency": "INR"},
        "fee_amount": {"amount_minor": 11800, "currency": "INR"},
        "net_amount": {"amount_minor": net_minor, "currency": "INR"},
        "status": "processed",
        "settled_at": settled_at,
    }


class TestMatchingSignals:
    """Individual explainable signal tests."""

    def test_reference_signal_match(self):
        p = _payment_dict()
        s = _settlement_dict()
        sig = evaluate_reference_signal(p, s, weight=0.40)
        assert sig.raw_score == 1.0
        assert sig.weighted_score == 0.40
        assert "explicitly references" in sig.explanation

    def test_reference_signal_mismatch(self):
        p = _payment_dict(payment_id="pay_001")
        s = _settlement_dict(payment_id="pay_999")
        sig = evaluate_reference_signal(p, s, weight=0.40)
        assert sig.raw_score == -1.0
        assert sig.weighted_score == -0.40

    def test_amount_signal_exact_match(self):
        p = _payment_dict(amount_minor=500000)
        o = {"record_type": "order", "order_id": "ord_001", "amount": {"amount_minor": 500000, "currency": "INR"}}
        sig = evaluate_amount_signal(p, o, weight=0.25)
        assert sig.raw_score == 1.0
        assert sig.weighted_score == 0.25

    def test_amount_signal_settlement_tolerance(self):
        p = _payment_dict(amount_minor=500000)
        s = _settlement_dict(net_minor=490000)
        sig = evaluate_amount_signal(p, s, weight=0.25)
        assert sig.raw_score > 0.8  # Consistent with fee reduction

    def test_currency_signal_match(self):
        p = _payment_dict()
        s = _settlement_dict()
        sig = evaluate_currency_signal(p, s, weight=0.10)
        assert sig.raw_score == 1.0
        assert sig.weighted_score == 0.10

    def test_currency_signal_mismatch(self):
        p = _payment_dict()
        s = _settlement_dict()
        s["gross_amount"]["currency"] = "USD"
        s["net_amount"]["currency"] = "USD"
        sig = evaluate_currency_signal(p, s, weight=0.10)
        assert sig.raw_score == 0.0

    def test_timestamp_proximity(self):
        p = _payment_dict(captured_at="2026-03-15T10:00:00+00:00")
        s = _settlement_dict(settled_at="2026-03-16T10:00:00+00:00")
        sig = evaluate_timestamp_proximity_signal(p, s, weight=0.15)
        assert sig.raw_score == 1.0


class TestRecordMatcher:
    """Full matcher group formation tests."""

    def test_clean_case_matching(self):
        p = _payment_dict()
        s = _settlement_dict()
        o = {"record_type": "order", "order_id": "ord_001", "merchant_id": "merchant_0001", "amount": {"amount_minor": 500000, "currency": "INR"}, "status": "paid", "ordered_at": "2026-03-15T09:50:00+00:00"}
        f1 = {"record_type": "fee", "fee_id": "fee_001", "payment_id": "pay_001", "fee_type": "platform_fee", "amount": {"amount_minor": 10000, "currency": "INR"}, "rate_bps": 200, "applied_at": "2026-03-15T10:00:00+00:00"}
        
        records = CaseRecords(
            payments=[p],
            orders=[o],
            settlements=[s],
            fees=[f1],
            refunds=[],
            ledger_entries=[],
            payouts=[],
        )

        matcher = RecordMatcher()
        groups, unmatched = matcher.match_records(records)

        assert len(groups) == 1
        group = groups[0]
        assert group.payment_id == "pay_001"
        assert group.order_id == "ord_001"
        assert "stl_001" in group.settlement_ids
        assert "fee_001" in group.fee_ids
        assert group.match_state == MatchState.MATCHED
        assert group.confidence >= 0.85
        assert len(unmatched["payments"]) == 0
        assert len(unmatched["orders"]) == 0
        assert len(unmatched["settlements"]) == 0

    def test_unmatched_settlement_with_invalid_ref(self):
        p = _payment_dict(payment_id="pay_001")
        s = _settlement_dict(settlement_id="stl_999", payment_id="pay_non_existent")

        records = CaseRecords(
            payments=[p],
            orders=[],
            settlements=[s],
            fees=[],
            refunds=[],
            ledger_entries=[],
            payouts=[],
        )

        matcher = RecordMatcher()
        groups, unmatched = matcher.match_records(records)

        assert len(groups) == 1
        assert "stl_999" not in groups[0].settlement_ids
        assert "stl_999" in unmatched["settlements"]
