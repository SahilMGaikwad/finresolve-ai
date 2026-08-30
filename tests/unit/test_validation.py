"""
FinResolve AI — Validation Tests

Tests that malformed records are rejected and valid records are accepted.
"""

import pytest

from data.schemas.enums import ValidationStatus
from services.ingestion.validator import validate_record


class TestValidation:
    """ACCEPTED / QUARANTINED / INVALID classification."""

    def _valid_payment(self) -> dict:
        return {
            "record_type": "payment",
            "payment_id": "pay_valid_001",
            "order_id": "ord_valid_001",
            "merchant_id": "merchant_0001",
            "amount": {"amount_minor": 5000000, "currency": "INR"},
            "status": "captured",
            "method": "upi",
            "captured_at": "2026-03-15T14:30:00+05:30",
        }

    def test_valid_record_accepted(self):
        result = validate_record(self._valid_payment())
        assert result.status == ValidationStatus.ACCEPTED
        assert result.record is not None
        assert len(result.errors) == 0

    def test_missing_record_type_invalid(self):
        data = {"payment_id": "pay_001", "amount": 5000}
        result = validate_record(data)
        assert result.status == ValidationStatus.INVALID

    def test_unknown_record_type_invalid(self):
        data = {"record_type": "alien_record", "id": "x"}
        result = validate_record(data)
        assert result.status == ValidationStatus.INVALID

    def test_not_a_dict_invalid(self):
        result = validate_record("this is not a dict")
        assert result.status == ValidationStatus.INVALID

    def test_missing_required_fields_invalid(self):
        data = {
            "record_type": "payment",
            "payment_id": "pay_001",
            # Missing: order_id, merchant_id, amount, status, method, captured_at
        }
        result = validate_record(data)
        assert result.status == ValidationStatus.INVALID
        assert len(result.errors) > 0

    def test_wrong_type_invalid(self):
        data = self._valid_payment()
        data["amount"] = "not_a_money_object"
        result = validate_record(data)
        assert result.status == ValidationStatus.INVALID

    def test_quarantined_large_amount(self):
        data = self._valid_payment()
        data["amount"] = {"amount_minor": 999_999_999, "currency": "INR"}  # > ₹10L
        result = validate_record(data)
        assert result.status == ValidationStatus.QUARANTINED
        assert len(result.warnings) > 0

    def test_valid_settlement_accepted(self):
        data = {
            "record_type": "settlement",
            "settlement_id": "stl_001",
            "payment_id": "pay_001",
            "merchant_id": "merchant_0001",
            "gross_amount": {"amount_minor": 5000000, "currency": "INR"},
            "fee_amount": {"amount_minor": 100000, "currency": "INR"},
            "net_amount": {"amount_minor": 4900000, "currency": "INR"},
            "status": "processed",
            "settled_at": "2026-03-18T10:00:00+00:00",
        }
        result = validate_record(data)
        assert result.status == ValidationStatus.ACCEPTED

    def test_valid_order_accepted(self):
        data = {
            "record_type": "order",
            "order_id": "ord_001",
            "merchant_id": "merchant_0001",
            "amount": {"amount_minor": 5000000, "currency": "INR"},
            "status": "paid",
            "items_count": 2,
            "ordered_at": "2026-03-15T14:00:00+00:00",
        }
        result = validate_record(data)
        assert result.status == ValidationStatus.ACCEPTED

    def test_errors_contain_structured_info(self):
        data = {"record_type": "payment"}  # Missing fields
        result = validate_record(data)
        assert result.status == ValidationStatus.INVALID
        assert len(result.errors) > 0
        error = result.errors[0]
        assert "error_type" in error
        assert "message" in error
