"""
FinResolve AI — Ingestion Idempotency Tests

Verifies that re-ingesting the same record does not create duplicates.
"""

import pytest

from data.schemas.enums import ValidationStatus
from services.ingestion.ingestor import Ingestor, compute_content_hash


class TestIdempotency:
    """Same record twice → one canonical record."""

    def _valid_payment(self) -> dict:
        return {
            "record_type": "payment",
            "payment_id": "pay_idem_001",
            "order_id": "ord_idem_001",
            "merchant_id": "merchant_0001",
            "amount": {"amount_minor": 5000000, "currency": "INR"},
            "status": "captured",
            "method": "upi",
            "captured_at": "2026-03-15T14:30:00+05:30",
        }

    def test_first_ingestion_accepted(self):
        ingestor = Ingestor(source_system="test")
        result = ingestor.ingest(self._valid_payment(), source_record_id="pay_idem_001")
        assert result.status == ValidationStatus.ACCEPTED
        assert result.is_duplicate is False
        assert result.provenance is not None

    def test_second_ingestion_detected_as_duplicate(self):
        ingestor = Ingestor(source_system="test")
        payment = self._valid_payment()

        result1 = ingestor.ingest(payment, source_record_id="pay_idem_001")
        assert result1.is_duplicate is False

        result2 = ingestor.ingest(payment, source_record_id="pay_idem_001")
        assert result2.is_duplicate is True

    def test_duplicate_does_not_increase_count(self):
        ingestor = Ingestor(source_system="test")
        payment = self._valid_payment()

        ingestor.ingest(payment, source_record_id="pay_idem_001")
        assert ingestor.ingested_count == 1

        ingestor.ingest(payment, source_record_id="pay_idem_001")
        assert ingestor.ingested_count == 1  # still 1

    def test_different_records_both_ingested(self):
        ingestor = Ingestor(source_system="test")
        p1 = self._valid_payment()
        p2 = self._valid_payment()
        p2["payment_id"] = "pay_idem_002"

        ingestor.ingest(p1, source_record_id="pay_idem_001")
        ingestor.ingest(p2, source_record_id="pay_idem_002")
        assert ingestor.ingested_count == 2

    def test_different_source_system_not_duplicate(self):
        """Same record from different source systems should not be considered duplicate."""
        ingestor1 = Ingestor(source_system="system_a")
        ingestor2 = Ingestor(source_system="system_b")
        payment = self._valid_payment()

        result1 = ingestor1.ingest(payment, source_record_id="pay_idem_001")
        result2 = ingestor2.ingest(payment, source_record_id="pay_idem_001")

        # Different ingestors = different sessions, but verify hash differs
        hash_a = compute_content_hash("system_a", "pay_idem_001", "1.0.0")
        hash_b = compute_content_hash("system_b", "pay_idem_001", "1.0.0")
        assert hash_a != hash_b


class TestProvenance:
    """Provenance fields are populated correctly."""

    def _valid_payment(self) -> dict:
        return {
            "record_type": "payment",
            "payment_id": "pay_prov_001",
            "order_id": "ord_prov_001",
            "merchant_id": "merchant_0001",
            "amount": {"amount_minor": 5000000, "currency": "INR"},
            "status": "captured",
            "method": "upi",
            "captured_at": "2026-03-15T14:30:00+05:30",
        }

    def test_provenance_source_system(self):
        ingestor = Ingestor(source_system="razorpay_test")
        result = ingestor.ingest(self._valid_payment(), source_record_id="pay_prov_001")
        assert result.provenance.source_system == "razorpay_test"

    def test_provenance_source_record_id_preserved(self):
        ingestor = Ingestor(source_system="test")
        result = ingestor.ingest(self._valid_payment(), source_record_id="pay_prov_001")
        assert result.provenance.source_record_id == "pay_prov_001"

    def test_provenance_batch_id_consistent(self):
        ingestor = Ingestor(source_system="test")
        p1 = self._valid_payment()
        p2 = self._valid_payment()
        p2["payment_id"] = "pay_prov_002"

        r1 = ingestor.ingest(p1, source_record_id="pay_prov_001")
        r2 = ingestor.ingest(p2, source_record_id="pay_prov_002")

        assert r1.provenance.ingestion_batch_id == r2.provenance.ingestion_batch_id

    def test_provenance_schema_version(self):
        ingestor = Ingestor(source_system="test", schema_version="2.0.0")
        result = ingestor.ingest(self._valid_payment(), source_record_id="pay_prov_001")
        assert result.provenance.schema_version == "2.0.0"

    def test_provenance_validation_status(self):
        ingestor = Ingestor(source_system="test")
        result = ingestor.ingest(self._valid_payment(), source_record_id="pay_prov_001")
        assert result.provenance.validation_status == ValidationStatus.ACCEPTED

    def test_invalid_record_no_provenance(self):
        ingestor = Ingestor(source_system="test")
        result = ingestor.ingest({"bad": "data"})
        assert result.status == ValidationStatus.INVALID
        assert result.provenance is None

    def test_reset_clears_state(self):
        ingestor = Ingestor(source_system="test")
        ingestor.ingest(self._valid_payment(), source_record_id="pay_prov_001")
        old_batch = ingestor.batch_id
        assert ingestor.ingested_count == 1

        ingestor.reset()
        assert ingestor.ingested_count == 0
        assert ingestor.batch_id != old_batch


class TestContentHash:
    """Content hash is deterministic."""

    def test_same_inputs_same_hash(self):
        h1 = compute_content_hash("sys_a", "rec_001", "1.0.0")
        h2 = compute_content_hash("sys_a", "rec_001", "1.0.0")
        assert h1 == h2

    def test_different_system_different_hash(self):
        h1 = compute_content_hash("sys_a", "rec_001", "1.0.0")
        h2 = compute_content_hash("sys_b", "rec_001", "1.0.0")
        assert h1 != h2

    def test_different_record_different_hash(self):
        h1 = compute_content_hash("sys_a", "rec_001", "1.0.0")
        h2 = compute_content_hash("sys_a", "rec_002", "1.0.0")
        assert h1 != h2

    def test_hash_is_sha256_hex(self):
        h = compute_content_hash("sys", "rec", "1.0.0")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)
