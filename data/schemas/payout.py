"""
FinResolve AI — Payout Record Schema
"""

from datetime import datetime

from pydantic import Field

from data.schemas.base import BaseRecord
from data.schemas.enums import PayoutStatus, RecordType
from data.schemas.money import Money


class PayoutRecord(BaseRecord):
    """
    A payout record.

    Represents a batch transfer from the payment gateway to the merchant's
    bank account, aggregating one or more settlements.
    """

    record_type: RecordType = Field(default=RecordType.PAYOUT, frozen=True)
    payout_id: str = Field(description="Payout identifier")
    merchant_id: str = Field(description="Merchant receiving the payout")
    amount: Money = Field(description="Total payout amount")
    settlement_ids: list[str] = Field(
        default_factory=list,
        description="List of settlement IDs included in this payout",
    )
    status: PayoutStatus = Field(description="Payout processing status")
    initiated_at: datetime = Field(description="When payout was initiated (UTC)")
    completed_at: datetime | None = Field(
        default=None, description="When payout was completed (UTC)"
    )
    utr: str = Field(default="", description="Unique Transaction Reference")
