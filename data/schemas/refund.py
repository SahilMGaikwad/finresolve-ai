"""
FinResolve AI — Refund Record Schema
"""

from datetime import datetime

from pydantic import Field

from data.schemas.base import BaseRecord
from data.schemas.enums import RecordType, RefundStatus
from data.schemas.money import Money


class RefundRecord(BaseRecord):
    """
    A refund record.

    Represents a full or partial refund of a payment.
    """

    record_type: RecordType = Field(default=RecordType.REFUND, frozen=True)
    refund_id: str = Field(description="Refund identifier")
    payment_id: str = Field(description="Payment being refunded")
    amount: Money = Field(description="Refund amount (must be <= original payment)")
    reason: str = Field(default="", description="Reason for refund")
    status: RefundStatus = Field(description="Refund processing status")
    initiated_at: datetime = Field(description="When refund was initiated (UTC)")
    processed_at: datetime | None = Field(
        default=None, description="When refund was processed (UTC), None if pending"
    )
