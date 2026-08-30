"""
FinResolve AI — Record Validator

Validates raw record dicts against Pydantic schemas.
Classifies each record as ACCEPTED, QUARANTINED, or INVALID.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from data.schemas.enums import RecordType, ValidationStatus
from data.schemas.fee import FeeRecord
from data.schemas.ledger_entry import LedgerEntry
from data.schemas.order import OrderRecord
from data.schemas.payment import PaymentRecord
from data.schemas.payout import PayoutRecord
from data.schemas.refund import RefundRecord
from data.schemas.settlement import SettlementRecord
from services.ingestion.errors import MalformedDataError, SchemaValidationError

logger = logging.getLogger("finresolve.ingestion.validator")

# Map record types to their Pydantic model classes
_RECORD_TYPE_TO_MODEL: dict[str, type] = {
    RecordType.PAYMENT.value: PaymentRecord,
    RecordType.ORDER.value: OrderRecord,
    RecordType.SETTLEMENT.value: SettlementRecord,
    RecordType.REFUND.value: RefundRecord,
    RecordType.FEE.value: FeeRecord,
    RecordType.LEDGER_ENTRY.value: LedgerEntry,
    RecordType.PAYOUT.value: PayoutRecord,
}

# Fields that may indicate a quarantined (suspect but parseable) record
_QUARANTINE_INDICATORS = [
    # Suspiciously large amounts (> ₹10,00,000 = 10M paise)
    ("amount", lambda v: isinstance(v, dict) and v.get("amount_minor", 0) > 100_000_000),
    ("gross_amount", lambda v: isinstance(v, dict) and v.get("amount_minor", 0) > 100_000_000),
]


@dataclass
class ValidationResult:
    """
    Result of validating a single record.

    Attributes:
        status: ACCEPTED, QUARANTINED, or INVALID.
        record: The validated Pydantic model (if ACCEPTED or QUARANTINED).
        raw_data: Original raw data dict.
        errors: List of validation errors (if INVALID).
        warnings: List of quarantine reasons (if QUARANTINED).
    """

    status: ValidationStatus
    record: Any = None
    raw_data: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_record(raw_data: dict[str, Any]) -> ValidationResult:
    """
    Validate a raw record dict against its corresponding Pydantic schema.

    Steps:
    1. Check that raw_data is a dict with a valid record_type.
    2. Attempt Pydantic validation.
    3. Check quarantine indicators.
    4. Return ACCEPTED, QUARANTINED, or INVALID.

    Args:
        raw_data: Raw record as a dict.

    Returns:
        ValidationResult with status, validated record (if valid), and errors.
    """
    # Step 1: Basic structure check
    if not isinstance(raw_data, dict):
        return ValidationResult(
            status=ValidationStatus.INVALID,
            raw_data={},
            errors=[MalformedDataError(
                "Record is not a dict",
                raw_preview=str(raw_data)[:200],
            ).to_dict()],
        )

    record_type = raw_data.get("record_type")
    if record_type is None:
        return ValidationResult(
            status=ValidationStatus.INVALID,
            raw_data=raw_data,
            errors=[MalformedDataError(
                "Missing record_type field",
                raw_preview=str(raw_data)[:200],
            ).to_dict()],
        )

    model_class = _RECORD_TYPE_TO_MODEL.get(record_type)
    if model_class is None:
        return ValidationResult(
            status=ValidationStatus.INVALID,
            raw_data=raw_data,
            errors=[SchemaValidationError(
                f"Unknown record_type: {record_type}",
                record_type=record_type,
            ).to_dict()],
        )

    # Step 2: Pydantic validation
    try:
        record = model_class.model_validate(raw_data)
    except PydanticValidationError as e:
        field_errors = [
            {"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"], "type": err["type"]}
            for err in e.errors()
        ]
        return ValidationResult(
            status=ValidationStatus.INVALID,
            raw_data=raw_data,
            errors=[SchemaValidationError(
                f"Schema validation failed for {record_type}",
                field_errors=field_errors,
                record_type=record_type,
            ).to_dict()],
        )

    # Step 3: Quarantine checks
    warnings: list[str] = []
    for field_name, check_fn in _QUARANTINE_INDICATORS:
        value = raw_data.get(field_name)
        if value is not None and check_fn(value):
            warnings.append(f"Suspicious {field_name}: value may exceed normal range")

    if warnings:
        logger.warning(f"Record quarantined: {record_type} — {warnings}")
        return ValidationResult(
            status=ValidationStatus.QUARANTINED,
            record=record,
            raw_data=raw_data,
            warnings=warnings,
        )

    # Step 4: Accepted
    return ValidationResult(
        status=ValidationStatus.ACCEPTED,
        record=record,
        raw_data=raw_data,
    )
