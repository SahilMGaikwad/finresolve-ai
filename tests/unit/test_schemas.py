"""
FinResolve AI — Schema Validation Tests

Tests that Pydantic schemas enforce required fields and types correctly.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import ValidationError as PydanticValidationError

from data.schemas.enums import (
    Currency, FeeType, LedgerEntryType, OrderStatus,
    PaymentMethod, PaymentStatus, RecordType, RefundStatus,
    SettlementStatus,
)
from data.schemas.money import Money
from data.schemas.payment import PaymentRecord
from data.schemas.order import OrderRecord
from data.schemas.settlement import SettlementRecord
from data.schemas.refund import RefundRecord
from data.schemas.fee import FeeRecord
from data.schemas.ledger_entry import LedgerEntry
from data.schemas.case import ReconciliationCase, CaseRecords, ExpectedOutcome
from data.schemas.corruption import CorruptionLabel
from data.schemas.enums import CaseDifficulty, CorruptionType


def _sample_money(amount: int = 50000) -> Money:
    return Money(amount_minor=amount, currency=Currency.INR)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TestPaymentSchema:
    def test_valid_payment(self):
        p = PaymentRecord(
            payment_id="pay_123",
            order_id="ord_456",
            merchant_id="merchant_001",
            amount=_sample_money(),
            status=PaymentStatus.CAPTURED,
            method=PaymentMethod.UPI,
            captured_at=_now(),
        )
        assert p.record_type == RecordType.PAYMENT
        assert p.payment_id == "pay_123"

    def test_missing_required_field(self):
        with pytest.raises(PydanticValidationError):
            PaymentRecord(
                payment_id="pay_123",
                # missing order_id, merchant_id, amount, status, method, captured_at
            )

    def test_metadata_is_dict(self):
        p = PaymentRecord(
            payment_id="pay_123",
            order_id="ord_456",
            merchant_id="merchant_001",
            amount=_sample_money(),
            status=PaymentStatus.CAPTURED,
            method=PaymentMethod.UPI,
            captured_at=_now(),
            metadata={"key": "value"},
        )
        assert p.metadata == {"key": "value"}


class TestOrderSchema:
    def test_valid_order(self):
        o = OrderRecord(
            order_id="ord_456",
            merchant_id="merchant_001",
            amount=_sample_money(),
            status=OrderStatus.PAID,
            items_count=3,
            ordered_at=_now(),
        )
        assert o.record_type == RecordType.ORDER
        assert o.items_count == 3

    def test_items_count_must_be_positive(self):
        with pytest.raises(PydanticValidationError):
            OrderRecord(
                order_id="ord_456",
                merchant_id="merchant_001",
                amount=_sample_money(),
                status=OrderStatus.PAID,
                items_count=0,  # Must be >= 1
                ordered_at=_now(),
            )


class TestSettlementSchema:
    def test_valid_settlement(self):
        s = SettlementRecord(
            settlement_id="stl_789",
            payment_id="pay_123",
            merchant_id="merchant_001",
            gross_amount=_sample_money(50000),
            fee_amount=_sample_money(1000),
            net_amount=_sample_money(49000),
            status=SettlementStatus.PROCESSED,
            settled_at=_now(),
        )
        assert s.record_type == RecordType.SETTLEMENT


class TestRefundSchema:
    def test_valid_refund(self):
        r = RefundRecord(
            refund_id="rfnd_001",
            payment_id="pay_123",
            amount=_sample_money(25000),
            status=RefundStatus.PROCESSED,
            initiated_at=_now(),
            processed_at=_now(),
        )
        assert r.record_type == RecordType.REFUND

    def test_processed_at_optional(self):
        r = RefundRecord(
            refund_id="rfnd_001",
            payment_id="pay_123",
            amount=_sample_money(25000),
            status=RefundStatus.INITIATED,
            initiated_at=_now(),
        )
        assert r.processed_at is None


class TestFeeSchema:
    def test_valid_fee(self):
        f = FeeRecord(
            fee_id="fee_001",
            payment_id="pay_123",
            fee_type=FeeType.PLATFORM_FEE,
            amount=_sample_money(1000),
            rate_bps=200,
            applied_at=_now(),
        )
        assert f.record_type == RecordType.FEE
        assert f.rate_bps == 200

    def test_rate_bps_non_negative(self):
        with pytest.raises(PydanticValidationError):
            FeeRecord(
                fee_id="fee_001",
                payment_id="pay_123",
                fee_type=FeeType.PLATFORM_FEE,
                amount=_sample_money(1000),
                rate_bps=-10,  # Must be >= 0
                applied_at=_now(),
            )


class TestLedgerEntrySchema:
    def test_valid_entry(self):
        le = LedgerEntry(
            entry_id="le_001",
            reference_id="pay_123",
            reference_type=RecordType.PAYMENT,
            merchant_id="merchant_001",
            debit=Money.zero(Currency.INR),
            credit=_sample_money(50000),
            balance_after=_sample_money(50000),
            entry_type=LedgerEntryType.CREDIT,
            posted_at=_now(),
        )
        assert le.record_type == RecordType.LEDGER_ENTRY


class TestCaseSchema:
    def test_valid_case(self):
        case = ReconciliationCase(
            case_id="CASE-000001",
            merchant_id="merchant_001",
            ground_truth=CaseRecords(),
            observed=CaseRecords(),
            difficulty=CaseDifficulty.EASY,
            expected_outcome=ExpectedOutcome(has_discrepancy=False),
        )
        assert case.case_id == "CASE-000001"
        assert case.expected_outcome.has_discrepancy is False

    def test_corruption_label(self):
        label = CorruptionLabel(
            case_id="CASE-000001",
            corruption_type=CorruptionType.AMOUNT_MISMATCH,
            target_record_type=RecordType.SETTLEMENT,
            target_record_id="stl_789",
            target_field="net_amount",
            original_value="49000",
            corrupted_value="47000",
            description="Settlement amount reduced",
        )
        assert label.corruption_type == CorruptionType.AMOUNT_MISMATCH
