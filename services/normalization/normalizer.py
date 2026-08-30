"""
FinResolve AI — Record Normalizer

Converts validated source records into canonical form:
- Currency amounts → integer minor units
- Timestamps → UTC
- Field names → canonical names
- Provenance attached

The normalizer is deterministic: same input always produces
the same canonical output.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from data.schemas.canonical import CanonicalRecord
from data.schemas.enums import Currency, RecordType
from data.schemas.money import Money
from data.schemas.provenance import Provenance
from services.ingestion.errors import NormalizationError
from services.normalization.field_mappings import apply_field_mapping, get_field_mapping

logger = logging.getLogger("finresolve.normalization")

# ---- Amount normalization ----

# Fields that contain monetary amounts (as Money dicts)
_AMOUNT_FIELDS = {
    "amount", "gross_amount", "fee_amount", "net_amount",
    "debit", "credit", "balance_after",
}

# Primary amount field per record type
_PRIMARY_AMOUNT_FIELD: dict[str, str] = {
    RecordType.PAYMENT.value: "amount",
    RecordType.ORDER.value: "amount",
    RecordType.SETTLEMENT.value: "net_amount",
    RecordType.REFUND.value: "amount",
    RecordType.FEE.value: "amount",
    RecordType.LEDGER_ENTRY.value: "credit",  # Use credit as primary; debit may be zero
    RecordType.PAYOUT.value: "amount",
}

# Primary timestamp field per record type
_PRIMARY_TIMESTAMP_FIELD: dict[str, str] = {
    RecordType.PAYMENT.value: "captured_at",
    RecordType.ORDER.value: "ordered_at",
    RecordType.SETTLEMENT.value: "settled_at",
    RecordType.REFUND.value: "initiated_at",
    RecordType.FEE.value: "applied_at",
    RecordType.LEDGER_ENTRY.value: "posted_at",
    RecordType.PAYOUT.value: "initiated_at",
}

# Reference ID fields per record type
_REFERENCE_ID_FIELDS: dict[str, list[str]] = {
    RecordType.PAYMENT.value: ["payment_id", "order_id"],
    RecordType.ORDER.value: ["order_id"],
    RecordType.SETTLEMENT.value: ["settlement_id", "payment_id"],
    RecordType.REFUND.value: ["refund_id", "payment_id"],
    RecordType.FEE.value: ["fee_id", "payment_id", "settlement_id"],
    RecordType.LEDGER_ENTRY.value: ["entry_id", "reference_id"],
    RecordType.PAYOUT.value: ["payout_id"],
}


def _normalize_timestamp(value: Any) -> datetime:
    """
    Normalize a timestamp to UTC datetime.

    Handles:
    - ISO 8601 strings (with or without timezone)
    - datetime objects
    - Unix timestamps (int/float)

    Raises:
        NormalizationError: If the value cannot be parsed as a timestamp.
    """
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc)
        except (OSError, ValueError, OverflowError):
            pass

    raise NormalizationError(
        f"Cannot parse timestamp: {value!r}",
        field="timestamp",
        original_value=value,
        target_type="datetime",
    )


def _extract_amount(record_data: dict, record_type: str) -> Money:
    """Extract the primary amount from a record."""
    field_name = _PRIMARY_AMOUNT_FIELD.get(record_type, "amount")
    amount_data = record_data.get(field_name)

    if amount_data is None:
        raise NormalizationError(
            f"Missing amount field: {field_name}",
            field=field_name,
            original_value=None,
            target_type="Money",
        )

    if isinstance(amount_data, dict):
        # Already a Money dict
        currency_str = amount_data.get("currency", "INR")
        amount_minor = amount_data.get("amount_minor", 0)
        if isinstance(amount_minor, float):
            raise NormalizationError(
                "Float detected in monetary amount — refusing to normalize",
                field=field_name,
                original_value=amount_minor,
                target_type="int",
            )
        return Money(amount_minor=int(amount_minor), currency=Currency(currency_str))

    raise NormalizationError(
        f"Unexpected amount format: {type(amount_data).__name__}",
        field=field_name,
        original_value=amount_data,
        target_type="Money",
    )


def _extract_timestamp(record_data: dict, record_type: str) -> datetime:
    """Extract and normalize the primary timestamp from a record."""
    field_name = _PRIMARY_TIMESTAMP_FIELD.get(record_type, "created_at")
    ts_value = record_data.get(field_name)

    if ts_value is None:
        raise NormalizationError(
            f"Missing timestamp field: {field_name}",
            field=field_name,
            original_value=None,
            target_type="datetime",
        )

    return _normalize_timestamp(ts_value)


def _extract_reference_ids(record_data: dict, record_type: str) -> dict[str, str]:
    """Extract all reference IDs from a record."""
    fields = _REFERENCE_ID_FIELDS.get(record_type, [])
    refs = {}
    for field_name in fields:
        value = record_data.get(field_name)
        if value is not None and str(value).strip():
            refs[field_name] = str(value)
    return refs


def _extract_merchant_id(record_data: dict) -> str:
    """Extract merchant_id from a record, defaulting to 'unknown'."""
    return str(record_data.get("merchant_id", "unknown"))


def normalize_record(
    record_data: dict[str, Any],
    source_system: str = "synthetic",
    provenance: Provenance | None = None,
) -> CanonicalRecord:
    """
    Normalize a validated record to canonical form.

    Steps:
    1. Apply source-system field mappings.
    2. Extract and normalize primary amount (integer minor units).
    3. Extract and normalize primary timestamp (UTC).
    4. Extract reference IDs.
    5. Attach provenance.

    Args:
        record_data: Validated record as a dict.
        source_system: Source system identifier (for field mapping).
        provenance: Pre-computed provenance (from ingestor).

    Returns:
        CanonicalRecord.

    Raises:
        NormalizationError: If normalization fails.
    """
    record_type = record_data.get("record_type", "")

    # Step 1: Apply field mapping
    mapping = get_field_mapping(source_system, record_type)
    mapped_data = apply_field_mapping(record_data, mapping)

    # Step 2: Extract amount
    amount = _extract_amount(mapped_data, record_type)

    # Step 3: Extract timestamp
    timestamp = _extract_timestamp(mapped_data, record_type)

    # Step 4: Extract reference IDs
    reference_ids = _extract_reference_ids(mapped_data, record_type)

    # Step 5: Build canonical record
    if provenance is None:
        provenance = Provenance(
            source_system=source_system,
            source_record_id=next(iter(reference_ids.values()), str(uuid4())),
        )

    # Compute content hash for idempotency
    import hashlib
    hash_key = f"{source_system}:{provenance.source_record_id}:{provenance.schema_version}"
    content_hash = hashlib.sha256(hash_key.encode("utf-8")).hexdigest()

    return CanonicalRecord(
        record_type=RecordType(record_type),
        source_record=mapped_data,
        amount=amount,
        merchant_id=_extract_merchant_id(mapped_data),
        timestamp=timestamp,
        reference_ids=reference_ids,
        provenance=provenance,
        content_hash=content_hash,
    )
