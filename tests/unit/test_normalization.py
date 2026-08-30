"""
FinResolve AI — Normalization Tests

Verifies that normalization produces correct canonical records.
"""

import pytest
from datetime import datetime, timezone, timedelta

from data.schemas.enums import Currency, RecordType
from services.normalization.normalizer import normalize_record, _normalize_timestamp
from services.normalization.field_mappings import apply_field_mapping
from services.ingestion.errors import NormalizationError


class TestTimestampNormalization:
    """All timestamps should be normalized to UTC."""

    def test_iso_string_with_utc(self):
        dt = _normalize_timestamp("2026-01-15T10:30:00+00:00")
        assert dt.tzinfo is not None
        assert dt.utcoffset() == timedelta(0)

    def test_iso_string_with_offset(self):
        dt = _normalize_timestamp("2026-01-15T16:00:00+05:30")
        assert dt.utcoffset() == timedelta(0)
        assert dt.hour == 10  # 16:00 IST = 10:30 UTC
        assert dt.minute == 30

    def test_iso_string_naive_assumed_utc(self):
        dt = _normalize_timestamp("2026-01-15T10:30:00")
        assert dt.tzinfo == timezone.utc

    def test_datetime_object(self):
        input_dt = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)
        result = _normalize_timestamp(input_dt)
        assert result == input_dt

    def test_unix_timestamp(self):
        # 2026-01-15T10:30:00 UTC as unix timestamp
        ts = 1768566600
        dt = _normalize_timestamp(ts)
        assert dt.tzinfo == timezone.utc

    def test_invalid_timestamp_raises(self):
        with pytest.raises(NormalizationError):
            _normalize_timestamp("not-a-date")

    def test_none_timestamp_raises(self):
        with pytest.raises(NormalizationError):
            _normalize_timestamp(None)


class TestRecordNormalization:
    """Validates full record normalization pipeline."""

    def _sample_payment(self) -> dict:
        return {
            "record_type": "payment",
            "payment_id": "pay_abc123",
            "order_id": "ord_def456",
            "merchant_id": "merchant_0001",
            "amount": {"amount_minor": 5000000, "currency": "INR"},
            "status": "captured",
            "method": "upi",
            "captured_at": "2026-03-15T14:30:00+05:30",
            "metadata": {"note": "test payment"},
        }

    def test_normalize_payment(self):
        record = self._sample_payment()
        canonical = normalize_record(record, source_system="synthetic")

        assert canonical.record_type == RecordType.PAYMENT
        assert canonical.amount.amount_minor == 5000000
        assert canonical.amount.currency == Currency.INR
        assert canonical.merchant_id == "merchant_0001"
        assert canonical.timestamp.tzinfo is not None
        assert "payment_id" in canonical.reference_ids
        assert canonical.reference_ids["payment_id"] == "pay_abc123"

    def test_normalize_preserves_source_record(self):
        record = self._sample_payment()
        canonical = normalize_record(record, source_system="synthetic")
        assert canonical.source_record["payment_id"] == "pay_abc123"

    def test_normalize_generates_content_hash(self):
        record = self._sample_payment()
        canonical = normalize_record(record, source_system="synthetic")
        assert canonical.content_hash != ""
        assert len(canonical.content_hash) == 64  # SHA-256 hex

    def test_same_record_same_hash(self):
        record = self._sample_payment()
        c1 = normalize_record(record, source_system="synthetic")
        c2 = normalize_record(record, source_system="synthetic")
        assert c1.content_hash == c2.content_hash

    def test_different_source_system_different_hash(self):
        record = self._sample_payment()
        c1 = normalize_record(record, source_system="synthetic")
        c2 = normalize_record(record, source_system="razorpay")
        assert c1.content_hash != c2.content_hash

    def test_normalize_settlement(self):
        record = {
            "record_type": "settlement",
            "settlement_id": "stl_xyz",
            "payment_id": "pay_abc",
            "merchant_id": "merchant_0001",
            "gross_amount": {"amount_minor": 5000000, "currency": "INR"},
            "fee_amount": {"amount_minor": 100000, "currency": "INR"},
            "net_amount": {"amount_minor": 4900000, "currency": "INR"},
            "status": "processed",
            "settled_at": "2026-03-18T10:00:00+00:00",
            "utr": "UTR123456789",
        }
        canonical = normalize_record(record, source_system="synthetic")
        assert canonical.record_type == RecordType.SETTLEMENT
        # Primary amount for settlement is net_amount
        assert canonical.amount.amount_minor == 4900000


class TestFieldMapping:
    """Source-specific field mappings produce canonical names."""

    def test_apply_empty_mapping(self):
        data = {"field_a": 1, "field_b": 2}
        result = apply_field_mapping(data, {})
        assert result == data

    def test_apply_mapping(self):
        data = {"id": "pay_123", "amount": 5000, "created_at": "2026-01-01"}
        mapping = {"id": "payment_id", "created_at": "captured_at"}
        result = apply_field_mapping(data, mapping)
        assert "payment_id" in result
        assert "captured_at" in result
        assert result["payment_id"] == "pay_123"
        assert result["amount"] == 5000  # unmapped field passes through

    def test_float_amount_rejected(self):
        """Normalizer must refuse float monetary amounts."""
        record = {
            "record_type": "payment",
            "payment_id": "pay_float",
            "order_id": "ord_float",
            "merchant_id": "merchant_0001",
            "amount": {"amount_minor": 500.50, "currency": "INR"},  # FLOAT!
            "status": "captured",
            "method": "upi",
            "captured_at": "2026-01-01T00:00:00+00:00",
        }
        with pytest.raises(NormalizationError, match="Float detected"):
            normalize_record(record, source_system="synthetic")
