"""
FinResolve AI — Corruption Label Schema

Records exactly what corruption was applied to a case's observed data,
enabling ground-truth evaluation.
"""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from data.schemas.enums import CorruptionType, RecordType


class CorruptionLabel(BaseModel):
    """
    A label describing a single corruption applied to a case.

    Captures the full details of what was changed, enabling
    exact evaluation of whether the system detected and
    correctly diagnosed the corruption.
    """

    corruption_id: UUID = Field(default_factory=uuid4, description="Unique corruption identifier")
    case_id: str = Field(description="Case this corruption belongs to")
    corruption_type: CorruptionType = Field(description="Type of corruption applied")
    target_record_type: RecordType = Field(description="Record type that was corrupted")
    target_record_id: str = Field(description="ID of the record that was corrupted")
    target_field: str = Field(description="Field name that was modified")
    original_value: str = Field(description="Original (correct) value before corruption")
    corrupted_value: str = Field(description="Value after corruption was applied")
    description: str = Field(description="Human-readable description of what this corruption simulates")

    model_config = {"from_attributes": True}
