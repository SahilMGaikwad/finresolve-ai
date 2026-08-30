"""
FinResolve AI — Structured Error Types

Typed error hierarchy for ingestion, validation, and normalization.
Each error type carries structured information for debugging and audit.
"""

from __future__ import annotations

from typing import Any


class IngestionError(Exception):
    """Base class for all ingestion-related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Serialise for structured logging and audit."""
        return {
            "error_type": type(self).__name__,
            "message": self.message,
            "details": self.details,
        }


class SchemaValidationError(IngestionError):
    """
    Record failed Pydantic schema validation.

    Missing required fields, wrong types, constraint violations.
    """

    def __init__(
        self,
        message: str,
        field_errors: list[dict[str, Any]] | None = None,
        record_type: str | None = None,
    ):
        super().__init__(message, {
            "field_errors": field_errors or [],
            "record_type": record_type,
        })
        self.field_errors = field_errors or []
        self.record_type = record_type


class NormalizationError(IngestionError):
    """
    Record could not be normalised to canonical form.

    Type coercion failure, unsupported currency, invalid timestamp format.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        original_value: Any = None,
        target_type: str | None = None,
    ):
        super().__init__(message, {
            "field": field,
            "original_value": str(original_value),
            "target_type": target_type,
        })
        self.field = field
        self.original_value = original_value
        self.target_type = target_type


class DuplicateRecordError(IngestionError):
    """
    Record with the same content hash already exists.

    Idempotency enforcement: same (source_system, source_record_id, schema_version)
    was already ingested.
    """

    def __init__(
        self,
        message: str,
        content_hash: str,
        existing_canonical_id: str | None = None,
    ):
        super().__init__(message, {
            "content_hash": content_hash,
            "existing_canonical_id": existing_canonical_id,
        })
        self.content_hash = content_hash
        self.existing_canonical_id = existing_canonical_id


class RelationshipError(IngestionError):
    """
    Record references a non-existent related record.

    Broken foreign key: e.g., settlement references a payment_id that
    does not exist in the ingested dataset.
    """

    def __init__(
        self,
        message: str,
        source_field: str,
        referenced_id: str,
        referenced_type: str | None = None,
    ):
        super().__init__(message, {
            "source_field": source_field,
            "referenced_id": referenced_id,
            "referenced_type": referenced_type,
        })
        self.source_field = source_field
        self.referenced_id = referenced_id
        self.referenced_type = referenced_type


class MalformedDataError(IngestionError):
    """
    Record is structurally unparseable.

    Not valid JSON, missing record_type discriminator, completely invalid format.
    """

    def __init__(self, message: str, raw_preview: str | None = None):
        super().__init__(message, {"raw_preview": raw_preview})
        self.raw_preview = raw_preview
