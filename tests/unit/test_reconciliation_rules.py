"""
FinResolve AI — Reconciliation Rules Unit Tests

Tests Amount, Fee, Temporal, Status, and Ledger reconciliation rules with exact arithmetic trails,
including edge cases (zero amounts, one-paise diff, split settlements, boundary delays).
"""

import pytest

from data.schemas.evidence import Severity
from data.schemas.matching import MatchGroup, MatchState
from services.reconciliation.rules import (
    AmountReconciliationRule,
    FeeAnalysisRule,
    LedgerDoubleEntryRule,
    StatusConsistencyRule,
    TemporalConsistencyRule,
)


@pytest.fixture
def clean_records():
    p = {
        "record_type": "payment",
        "payment_id": "pay_100",
        "order_id": "ord_100",
        "merchant_id": "merchant_001",
        "amount": {"amount_minor": 1000000, "currency": "INR"},
        "status": "captured",
        "method": "upi",
        "captured_at": "2026-03-15T10:00:00+00:00",
    }
    s = {
        "record_type": "settlement",
        "settlement_id": "stl_100",
        "payment_id": "pay_100",
        "merchant_id": "merchant_001",
        "gross_amount": {"amount_minor": 1000000, "currency": "INR"},
        "fee_amount": {"amount_minor": 23600, "currency": "INR"},
        "net_amount": {"amount_minor": 976400, "currency": "INR"},
        "status": "processed",
        "settled_at": "2026-03-18T10:00:00+00:00",
    }
    f1 = {
        "record_type": "fee",
        "fee_id": "fee_platform",
        "payment_id": "pay_100",
        "settlement_id": "stl_100",
        "fee_type": "platform_fee",
        "amount": {"amount_minor": 20000, "currency": "INR"},
        "rate_bps": 200,
        "applied_at": "2026-03-15T10:00:00+00:00",
    }
    f2 = {
        "record_type": "fee",
        "fee_id": "fee_gst",
        "payment_id": "pay_100",
        "settlement_id": "stl_100",
        "fee_type": "gst",
        "amount": {"amount_minor": 3600, "currency": "INR"},
        "rate_bps": 1800,
        "applied_at": "2026-03-15T10:00:00+00:00",
    }
    le1 = {
        "record_type": "ledger_entry",
        "entry_id": "le_1",
        "reference_id": "pay_100",
        "merchant_id": "merchant_001",
        "debit": {"amount_minor": 0, "currency": "INR"},
        "credit": {"amount_minor": 1000000, "currency": "INR"},
        "entry_type": "credit",
    }
    return {
        "pay_100": p,
        "stl_100": s,
        "fee_platform": f1,
        "fee_gst": f2,
        "le_1": le1,
    }


@pytest.fixture
def clean_group():
    return MatchGroup(
        payment_id="pay_100",
        order_id="ord_100",
        settlement_ids=["stl_100"],
        fee_ids=["fee_platform", "fee_gst"],
        refund_ids=[],
        ledger_entry_ids=["le_1"],
        match_state=MatchState.MATCHED,
    )


class TestAmountReconciliationRule:
    def test_clean_amount_passes(self, clean_group, clean_records):
        rule = AmountReconciliationRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True
        assert res.difference["difference_minor"] == 0
        assert len(res.evidence_items) == 0

    def test_one_paise_difference_detected(self, clean_group, clean_records):
        # 1 paise difference (976401 instead of 976400)
        clean_records["stl_100"]["net_amount"]["amount_minor"] = 976401
        rule = AmountReconciliationRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is False
        assert res.difference["difference_minor"] == 1
        assert len(res.evidence_items) == 1

    def test_zero_amount_payment_passes_if_zero_settlement(self, clean_group, clean_records):
        clean_records["pay_100"]["amount"]["amount_minor"] = 0
        clean_records["stl_100"]["gross_amount"]["amount_minor"] = 0
        clean_records["stl_100"]["fee_amount"]["amount_minor"] = 0
        clean_records["stl_100"]["net_amount"]["amount_minor"] = 0
        clean_group.fee_ids = []

        rule = AmountReconciliationRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True
        assert res.difference["difference_minor"] == 0

    def test_split_settlement_multiple_settlements(self, clean_group, clean_records):
        # Split settlement: Part 1 = 500,000, Part 2 = 476,400 (Total = 976,400)
        clean_records["stl_100"]["net_amount"]["amount_minor"] = 500000
        clean_records["stl_101"] = {
            "record_type": "settlement",
            "settlement_id": "stl_101",
            "payment_id": "pay_100",
            "gross_amount": {"amount_minor": 500000, "currency": "INR"},
            "fee_amount": {"amount_minor": 0, "currency": "INR"},
            "net_amount": {"amount_minor": 476400, "currency": "INR"},
            "status": "processed",
        }
        clean_group.settlement_ids = ["stl_100", "stl_101"]

        rule = AmountReconciliationRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True
        assert res.difference["difference_minor"] == 0

    def test_missing_settlement_fails(self, clean_group, clean_records):
        clean_group.settlement_ids = []
        rule = AmountReconciliationRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is False
        assert res.evidence_items[0].evidence_type.value == "missing_link"


class TestFeeAnalysisRule:
    def test_clean_fee_calculations(self, clean_group, clean_records):
        rule = FeeAnalysisRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True

    def test_zero_fee_rate(self, clean_group, clean_records):
        clean_records["fee_platform"]["rate_bps"] = 0
        clean_records["fee_platform"]["amount"]["amount_minor"] = 0
        clean_records["fee_gst"]["rate_bps"] = 0
        clean_records["fee_gst"]["amount"]["amount_minor"] = 0

        rule = FeeAnalysisRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True

    def test_fee_rate_discrepancy(self, clean_group, clean_records):
        clean_records["fee_platform"]["amount"]["amount_minor"] = 25000
        rule = FeeAnalysisRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is False
        assert len(res.evidence_items) == 1
        assert res.evidence_items[0].evidence_type.value == "fee_mismatch"


class TestTemporalConsistencyRule:
    def test_clean_temporal_order(self, clean_group, clean_records):
        rule = TemporalConsistencyRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True

    def test_same_timestamp_allowed(self, clean_group, clean_records):
        clean_records["stl_100"]["settled_at"] = clean_records["pay_100"]["captured_at"]
        rule = TemporalConsistencyRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True

    def test_missing_timestamp_handles_safely(self, clean_group, clean_records):
        clean_records["stl_100"]["settled_at"] = None
        rule = TemporalConsistencyRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True

    def test_settlement_delay_boundary_6_vs_8_days(self, clean_group, clean_records):
        rule = TemporalConsistencyRule(max_settlement_delay_days=7)

        # 6 days delay -> PASSED
        clean_records["stl_100"]["settled_at"] = "2026-03-21T10:00:00+00:00"
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True

        # 8 days delay -> FAILED
        clean_records["stl_100"]["settled_at"] = "2026-03-23T10:00:00+00:00"
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is False
        assert res.evidence_items[0].evidence_type.value == "temporal_anomaly"


class TestStatusConsistencyRule:
    def test_clean_status(self, clean_group, clean_records):
        rule = StatusConsistencyRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True

    def test_failed_payment_with_processed_settlement(self, clean_group, clean_records):
        clean_records["pay_100"]["status"] = "failed"
        rule = StatusConsistencyRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is False
        assert res.severity == Severity.HIGH
        assert res.evidence_items[0].evidence_type.value == "status_conflict"


class TestLedgerDoubleEntryRule:
    def test_clean_ledger_entry(self, clean_group, clean_records):
        rule = LedgerDoubleEntryRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is True

    def test_invalid_both_debit_and_credit(self, clean_group, clean_records):
        clean_records["le_1"]["debit"]["amount_minor"] = 50000
        rule = LedgerDoubleEntryRule()
        res = rule.evaluate(clean_group, clean_records)
        assert res.passed is False
        assert res.severity == Severity.HIGH
