"""
FinResolve AI — Ingestion Pipeline

Processes raw financial records through validation, deduplication,
and provenance assignment. Designed for idempotent operation.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from data.schemas.enums import ValidationStatus
from data.schemas.provenance import Provenance
from services.ingestion.errors import DuplicateRecordError
from services.ingestion.validator import ValidationResult, validate_record

logger = logging.getLogger("finresolve.ingestion")


@dataclass
class IngestionResult:
    """
    Result of ingesting a single record.

    Attributes:
        status: Validation status (ACCEPTED, QUARANTINED, INVALID).
        provenance: Provenance metadata (if accepted/quarantined).
        content_hash: Idempotency hash for deduplication.
        validation_result: Detailed validation result.
        is_duplicate: Whether this record was already ingested.
        error: Error details if ingestion failed.
    """

    status: ValidationStatus
    provenance: Provenance | None = None
    content_hash: str = ""
    validation_result: ValidationResult | None = None
    is_duplicate: bool = False
    error: dict[str, Any] | None = None


def compute_content_hash(
    source_system: str,
    source_record_id: str,
    schema_version: str,
) -> str:
    """
    Compute a deterministic content hash for idempotent ingestion.

    The hash uniquely identifies a record based on its source identity,
    not its content. This ensures that re-ingesting the same source record
    does not create a duplicate canonical record.

    Args:
        source_system: Originating system identifier.
        source_record_id: Original record ID in the source system.
        schema_version: Schema version used for validation.

    Returns:
        SHA-256 hex digest.
    """
    key = f"{source_system}:{source_record_id}:{schema_version}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


class Ingestor:
    """
    Stateful ingestion pipeline.

    Tracks ingested content hashes to enforce idempotency within
    an ingestion session. In production, this would check against
    the database; here we use an in-memory set.
    """

    def __init__(
        self,
        source_system: str = "synthetic",
        schema_version: str = "1.0.0",
        normalization_version: str = "1.0.0",
    ):
        self.source_system = source_system
        self.schema_version = schema_version
        self.normalization_version = normalization_version
        self.batch_id: UUID = uuid4()
        self._ingested_hashes: dict[str, str] = {}  # hash → canonical_id

    def ingest(
        self,
        raw_data: dict[str, Any],
        source_record_id: str | None = None,
    ) -> IngestionResult:
        """
        Ingest a single raw record.

        Steps:
        1. Validate the record.
        2. Compute content hash.
        3. Check for duplicates (idempotency).
        4. Assign provenance metadata.

        Args:
            raw_data: Raw record dict.
            source_record_id: Original ID in the source system.
                              If None, attempts to extract from the record.

        Returns:
            IngestionResult with status and provenance.
        """
        # Step 1: Validate
        validation_result = validate_record(raw_data)

        if validation_result.status == ValidationStatus.INVALID:
            logger.warning(f"Record rejected: {validation_result.errors}")
            return IngestionResult(
                status=ValidationStatus.INVALID,
                validation_result=validation_result,
                error=validation_result.errors[0] if validation_result.errors else None,
            )

        # Step 2: Extract source_record_id if not provided
        if source_record_id is None:
            source_record_id = self._extract_source_id(raw_data)

        # Step 3: Compute content hash for idempotency
        content_hash = compute_content_hash(
            self.source_system,
            source_record_id,
            self.schema_version,
        )

        # Step 4: Duplicate check
        if content_hash in self._ingested_hashes:
            existing_id = self._ingested_hashes[content_hash]
            logger.info(f"Duplicate detected: {source_record_id} (hash={content_hash[:12]}...)")
            return IngestionResult(
                status=validation_result.status,
                content_hash=content_hash,
                validation_result=validation_result,
                is_duplicate=True,
                error=DuplicateRecordError(
                    f"Record {source_record_id} already ingested",
                    content_hash=content_hash,
                    existing_canonical_id=existing_id,
                ).to_dict(),
            )

        # Step 5: Assign provenance
        canonical_id = str(uuid4())
        provenance = Provenance(
            source_system=self.source_system,
            source_record_id=source_record_id,
            ingestion_batch_id=self.batch_id,
            schema_version=self.schema_version,
            normalization_version=self.normalization_version,
            ingestion_timestamp=datetime.now(timezone.utc),
            validation_status=validation_result.status,
        )

        # Track for idempotency
        self._ingested_hashes[content_hash] = canonical_id

        logger.debug(f"Ingested: {source_record_id} → {canonical_id} ({validation_result.status.value})")

        return IngestionResult(
            status=validation_result.status,
            provenance=provenance,
            content_hash=content_hash,
            validation_result=validation_result,
        )

    def _extract_source_id(self, raw_data: dict[str, Any]) -> str:
        """Extract the source record ID from raw data."""
        # Try common ID fields in order of specificity
        for id_field in [
            "payment_id", "order_id", "settlement_id", "refund_id",
            "fee_id", "entry_id", "payout_id", "record_id",
        ]:
            if id_field in raw_data:
                return str(raw_data[id_field])

        # Fallback: generate a hash of the data content
        import json
        serialised = json.dumps(raw_data, sort_keys=True, default=str)
        return hashlib.sha256(serialised.encode("utf-8")).hexdigest()[:32]

    @property
    def ingested_count(self) -> int:
        """Number of unique records ingested in this session."""
        return len(self._ingested_hashes)

    def reset(self) -> None:
        """Reset the ingestor state for a new session."""
        self._ingested_hashes.clear()
        self.batch_id = uuid4()
