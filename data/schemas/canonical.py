"""
FinResolve AI — Canonical Normalised Record Schema

The common internal representation after normalisation.
All source-specific records are converted to this form.
Includes provenance metadata.
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from data.schemas.enums import RecordType
from data.schemas.money import Money
from data.schemas.provenance import Provenance


class CanonicalRecord(BaseModel):
    """
    Canonical normalised record.

    This is the internal representation used by matching, evidence
    collection, and all downstream services. It provides a uniform
    view regardless of the source system.
    """

    canonical_id: UUID = Field(default_factory=uuid4, description="Internal canonical ID")
    record_type: RecordType = Field(description="Type of the original record")
    source_record: dict[str, Any] = Field(
        description="Full normalised record data as a dict"
    )
    amount: Money = Field(description="Primary amount (normalised to minor units)")
    merchant_id: str = Field(description="Merchant identifier")
    timestamp: datetime = Field(description="Primary timestamp (normalised to UTC)")
    reference_ids: dict[str, str] = Field(
        default_factory=dict,
        description="Map of reference type to ID (e.g., {'payment_id': 'pay_xxx', 'order_id': 'ord_yyy'})",
    )
    provenance: Provenance = Field(description="Ingestion and normalisation provenance")
    content_hash: str = Field(
        default="",
        description="Deterministic hash of (source_system, source_record_id, schema_version) "
                    "for idempotent ingestion",
    )

    model_config = {"from_attributes": True}
