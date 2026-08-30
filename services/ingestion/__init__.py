"""
FinResolve AI — Ingestion Service

Processes raw financial records through validation, deduplication,
and provenance assignment.

Components:
- validator: Schema validation (ACCEPTED / QUARANTINED / INVALID)
- ingestor: Idempotent ingestion pipeline with provenance
- errors: Structured error types
"""

from services.ingestion.errors import (
    DuplicateRecordError,
    IngestionError,
    MalformedDataError,
    NormalizationError,
    RelationshipError,
    SchemaValidationError,
)
from services.ingestion.ingestor import IngestionResult, Ingestor, compute_content_hash
from services.ingestion.validator import ValidationResult, validate_record

__all__ = [
    "DuplicateRecordError",
    "IngestionError",
    "IngestionResult",
    "Ingestor",
    "MalformedDataError",
    "NormalizationError",
    "RelationshipError",
    "SchemaValidationError",
    "ValidationResult",
    "compute_content_hash",
    "validate_record",
]
