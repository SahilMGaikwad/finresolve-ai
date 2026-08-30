"""
FinResolve AI — Adversarial Reconciliation Tests

Tests edge cases, ambiguous candidates, conflicting references,
compound multi-corruptions, and novel/unknown transaction anomalies
to verify safe UNRESOLVED / INSUFFICIENT_EVIDENCE handling.
"""

import pytest

from data.schemas.case import CaseRecords
from data.schemas.reconciliation_result import ReconciliationStatus
from services.reconciliation.engine import ReconciliationEngine


class TestAdversarialReconciliation:
    """Tests handling of ambiguous, compound, and contradictory financial records."""

    def test_competing_identical_orders_triggers_ambiguity(self):
        """Two identical orders with same amount and close timestamps for one payment."""
        p = {
            "record_type": "payment",
            "payment_id": "pay_adv_1",
            "merchant_id": "merchant_001",
            "amount": {"amount_minor": 100000, "currency": "INR"},
            "status": "captured",
            "method": "upi",
            "captured_at": "2026-03-15T10:00:00+00:00",
        }
        o1 = {
            "record_type": "order",
            "order_id": "ord_adv_1",
            "merchant_id": "merchant_001",
            "amount": {"amount_minor": 100000, "currency": "INR"},
            "status": "paid",
            "ordered_at": "2026-03-15T09:55:00+00:00",
        }
        o2 = {
            "record_type": "order",
            "order_id": "ord_adv_2",
            "merchant_id": "merchant_001",
            "amount": {"amount_minor": 100000, "currency": "INR"},
            "status": "paid",
            "ordered_at": "2026-03-15T09:56:00+00:00",
        }

        records = CaseRecords(
            payments=[p],
            orders=[o1, o2],
            settlements=[],
            fees=[],
            refunds=[],
            ledger_entries=[],
            payouts=[],
        )

        engine = ReconciliationEngine()
        result = engine.reconcile_records("CASE-ADV-001", records)

        assert result.status in (ReconciliationStatus.INSUFFICIENT_EVIDENCE, ReconciliationStatus.DISCREPANCY)
        assert result.diagnostic_confidence <= 0.85

    def test_conflicting_cross_references(self):
        """Settlement references payment A, but fee references payment B."""
        p_a = {
            "record_type": "payment",
            "payment_id": "pay_A",
            "merchant_id": "merchant_001",
            "amount": {"amount_minor": 500000, "currency": "INR"},
            "status": "captured",
            "captured_at": "2026-03-15T10:00:00+00:00",
        }
        p_b = {
            "record_type": "payment",
            "payment_id": "pay_B",
            "merchant_id": "merchant_001",
            "amount": {"amount_minor": 500000, "currency": "INR"},
            "status": "captured",
            "captured_at": "2026-03-15T10:00:00+00:00",
        }
        stl = {
            "record_type": "settlement",
            "settlement_id": "stl_A",
            "payment_id": "pay_A",
            "merchant_id": "merchant_001",
            "gross_amount": {"amount_minor": 500000, "currency": "INR"},
            "fee_amount": {"amount_minor": 10000, "currency": "INR"},
            "net_amount": {"amount_minor": 490000, "currency": "INR"},
            "status": "processed",
            "settled_at": "2026-03-17T10:00:00+00:00",
        }
        fee = {
            "record_type": "fee",
            "fee_id": "fee_B",
            "payment_id": "pay_B",
            "settlement_id": "stl_A",
            "fee_type": "platform_fee",
            "amount": {"amount_minor": 10000, "currency": "INR"},
            "rate_bps": 200,
            "applied_at": "2026-03-15T10:00:00+00:00",
        }

        records = CaseRecords(
            payments=[p_a, p_b],
            orders=[],
            settlements=[stl],
            fees=[fee],
            refunds=[],
            ledger_entries=[],
            payouts=[],
        )

        engine = ReconciliationEngine()
        result = engine.reconcile_records("CASE-ADV-002", records)

        assert result.case_id == "CASE-ADV-002"
        assert len(result.matched_groups) == 2

    def test_compound_duplicate_and_amount_mismatch(self):
        """Simultaneous duplicate record submission and settlement amount mismatch."""
        p1 = {
            "record_type": "payment",
            "payment_id": "pay_dup",
            "merchant_id": "merchant_001",
            "amount": {"amount_minor": 1000000, "currency": "INR"},
            "status": "captured",
            "captured_at": "2026-03-15T10:00:00+00:00",
        }
        p2 = dict(p1)  # Exact duplicate
        stl = {
            "record_type": "settlement",
            "settlement_id": "stl_dup",
            "payment_id": "pay_dup",
            "merchant_id": "merchant_001",
            "gross_amount": {"amount_minor": 1000000, "currency": "INR"},
            "fee_amount": {"amount_minor": 0, "currency": "INR"},
            "net_amount": {"amount_minor": 850000, "currency": "INR"},  # Mismatch (850k vs 1000k)
            "status": "processed",
            "settled_at": "2026-03-17T10:00:00+00:00",
        }

        records = CaseRecords(
            payments=[p1, p2],
            orders=[],
            settlements=[stl],
            fees=[],
            refunds=[],
            ledger_entries=[],
            payouts=[],
        )

        engine = ReconciliationEngine()
        result = engine.reconcile_records("CASE-ADV-COMPOUND-01", records)

        assert result.status == ReconciliationStatus.DISCREPANCY
        disc_types = {d.discrepancy_type for d in result.discrepancies}
        assert "duplicate_record" in disc_types
        assert "settlement_amount_mismatch" in disc_types

    def test_compound_status_conflict_and_missing_settlement(self):
        """Status conflict on order and missing settlement on payment."""
        p = {
            "record_type": "payment",
            "payment_id": "pay_stat",
            "order_id": "ord_stat",
            "merchant_id": "merchant_001",
            "amount": {"amount_minor": 200000, "currency": "INR"},
            "status": "captured",
            "captured_at": "2026-03-15T10:00:00+00:00",
        }
        o = {
            "record_type": "order",
            "order_id": "ord_stat",
            "merchant_id": "merchant_001",
            "amount": {"amount_minor": 200000, "currency": "INR"},
            "status": "cancelled",  # Contradiction: cancelled order with captured payment
            "ordered_at": "2026-03-15T09:00:00+00:00",
        }

        records = CaseRecords(
            payments=[p],
            orders=[o],
            settlements=[],  # Missing settlement
            fees=[],
            refunds=[],
            ledger_entries=[],
            payouts=[],
        )

        engine = ReconciliationEngine()
        result = engine.reconcile_records("CASE-ADV-COMPOUND-02", records)

        assert result.status == ReconciliationStatus.DISCREPANCY
        disc_types = {d.discrepancy_type for d in result.discrepancies}
        assert "status_sync_failure" in disc_types
        assert "missing_record" in disc_types

    def test_compound_triple_corruption(self):
        """Fee discrepancy + Timing anomaly + Amount mismatch simultaneously."""
        p = {
            "record_type": "payment",
            "payment_id": "pay_tri",
            "merchant_id": "merchant_001",
            "amount": {"amount_minor": 1000000, "currency": "INR"},
            "status": "captured",
            "captured_at": "2026-03-15T10:00:00+00:00",
        }
        s = {
            "record_type": "settlement",
            "settlement_id": "stl_tri",
            "payment_id": "pay_tri",
            "merchant_id": "merchant_001",
            "gross_amount": {"amount_minor": 1000000, "currency": "INR"},
            "fee_amount": {"amount_minor": 20000, "currency": "INR"},
            "net_amount": {"amount_minor": 900000, "currency": "INR"},  # Mismatch (900k vs 976.4k)
            "status": "processed",
            "settled_at": "2026-04-15T10:00:00+00:00",  # 31 days delay (> 7 days)
        }
        f = {
            "record_type": "fee",
            "fee_id": "fee_tri",
            "payment_id": "pay_tri",
            "fee_type": "platform_fee",
            "amount": {"amount_minor": 50000, "currency": "INR"},  # Rate discrepancy (50k vs 20k)
            "rate_bps": 200,
            "applied_at": "2026-03-15T10:00:00+00:00",
        }

        records = CaseRecords(
            payments=[p],
            orders=[],
            settlements=[s],
            fees=[f],
            refunds=[],
            ledger_entries=[],
            payouts=[],
        )

        engine = ReconciliationEngine()
        result = engine.reconcile_records("CASE-ADV-TRIPLE", records)

        assert result.status == ReconciliationStatus.DISCREPANCY
        disc_types = {d.discrepancy_type for d in result.discrepancies}
        assert "fee_calculation_error" in disc_types
        assert "settlement_timing_anomaly" in disc_types
        assert "settlement_amount_mismatch" in disc_types

    def test_unknown_novel_transaction_structure_fails_safely(self):
        """Completely unknown fields and empty identifiers fail safely without unhandled exception."""
        unknown_record = {
            "record_type": "payment",
            "payment_id": "pay_novel_999",
            "merchant_id": "merchant_unknown",
            "unsupported_extra_field": "xyz",
            "amount": {"amount_minor": 0, "currency": "EUR"},
            "status": "custom_unknown_status",
            "captured_at": "2035-01-01T00:00:00+00:00",
        }
        records = CaseRecords(
            payments=[unknown_record],
            orders=[],
            settlements=[],
            fees=[],
            refunds=[],
            ledger_entries=[],
            payouts=[],
        )

        engine = ReconciliationEngine()
        result = engine.reconcile_records("CASE-ADV-NOVEL", records)

        # Engine produces a safe structured result without crashing or hallucinating
        assert result.case_id == "CASE-ADV-NOVEL"
        assert result.status in (ReconciliationStatus.RECONCILED, ReconciliationStatus.DISCREPANCY, ReconciliationStatus.INSUFFICIENT_EVIDENCE)
        assert isinstance(result.trace, list)
