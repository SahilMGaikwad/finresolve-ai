"""
FinResolve AI — Base Record Model

Shared base for all financial record schemas.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from data.schemas.enums import RecordType


class BaseRecord(BaseModel):
    """
    Base model for all financial records.

    Every record has a unique ID, a type discriminator, and timestamps.
    """

    record_id: UUID = Field(default_factory=uuid4, description="Unique record identifier")
    record_type: RecordType = Field(description="Type discriminator for this record")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the record was created (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the record was last updated (UTC)",
    )

    model_config = {"from_attributes": True}
