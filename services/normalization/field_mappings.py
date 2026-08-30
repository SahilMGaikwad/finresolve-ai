"""
FinResolve AI — Field Mappings

Defines how source-system-specific field names map to the canonical schema.
Pluggable per source system.
"""

from __future__ import annotations

from typing import Any

from data.schemas.enums import RecordType

# ---- Source-system-specific field mappings ----
#
# Each mapping is: {source_field_name: canonical_field_name}
# Only fields that differ from canonical names need to be listed.

_RAZORPAY_PAYMENT_MAPPING: dict[str, str] = {
    "id": "payment_id",
    "amount": "amount",          # Razorpay returns amounts in paise (already minor units)
    "currency": "currency",
    "method": "method",
    "status": "status",
    "order_id": "order_id",
    "created_at": "captured_at",
    "notes": "metadata",
}

_RAZORPAY_ORDER_MAPPING: dict[str, str] = {
    "id": "order_id",
    "amount": "amount",
    "currency": "currency",
    "status": "status",
    "created_at": "ordered_at",
}

_RAZORPAY_SETTLEMENT_MAPPING: dict[str, str] = {
    "id": "settlement_id",
    "amount": "net_amount",
    "status": "status",
    "created_at": "settled_at",
    "utr": "utr",
}

# Combined mapping registry
SOURCE_FIELD_MAPPINGS: dict[str, dict[str, dict[str, str]]] = {
    "razorpay": {
        RecordType.PAYMENT.value: _RAZORPAY_PAYMENT_MAPPING,
        RecordType.ORDER.value: _RAZORPAY_ORDER_MAPPING,
        RecordType.SETTLEMENT.value: _RAZORPAY_SETTLEMENT_MAPPING,
    },
    # Synthetic records already use canonical names
    "synthetic": {},
}


def get_field_mapping(
    source_system: str,
    record_type: str,
) -> dict[str, str]:
    """
    Get the field mapping for a specific source system and record type.

    Args:
        source_system: Source system identifier.
        record_type: Record type string.

    Returns:
        Dict mapping source field names to canonical field names.
        Empty dict if no mapping is needed (fields already canonical).
    """
    system_mappings = SOURCE_FIELD_MAPPINGS.get(source_system, {})
    return system_mappings.get(record_type, {})


def apply_field_mapping(
    raw_data: dict[str, Any],
    mapping: dict[str, str],
) -> dict[str, Any]:
    """
    Apply a field mapping to a raw data dict.

    Renames keys according to the mapping. Keys not in the mapping
    are passed through unchanged.

    Args:
        raw_data: Raw record dict.
        mapping: Field name mapping (source → canonical).

    Returns:
        New dict with renamed fields.
    """
    if not mapping:
        return dict(raw_data)  # shallow copy, no renaming needed

    result = {}
    for key, value in raw_data.items():
        canonical_key = mapping.get(key, key)
        result[canonical_key] = value
    return result
