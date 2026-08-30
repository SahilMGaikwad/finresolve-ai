"""
FinResolve AI — Provenance Model

Tracks the origin and processing history of every normalised record.
Original source identifiers are never overwritten.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from data.schemas.enums import ValidationStatus


class Provenance(BaseModel):
    """
    Provenance metadata attached to every normalised record.

    Captures the full lineage: which source system produced it,
    how it was ingested, and what versions of the schema and
    normalisation logic were applied.
    """

    source_system: str = Field(
        description="Identifier for the originating system (e.g., 'razorpay', 'internal_ledger')"
    )
    source_record_id: str = Field(
        description="Original record ID in the source system. Never overwritten."
    )
    ingestion_batch_id: UUID = Field(
        default_factory=uuid4,
        description="Batch ID grouping records ingested together",
    )
    schema_version: str = Field(
        default="1.0.0",
        description="Version of the data schema used to validate this record",
    )
    normalization_version: str = Field(
        default="1.0.0",
        description="Version of the normalisation logic applied",
    )
    ingestion_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this record was ingested (UTC)",
    )
    validation_status: ValidationStatus = Field(
        default=ValidationStatus.ACCEPTED,
        description="Outcome of validation at ingestion",
    )

    model_config = {"from_attributes": True}
