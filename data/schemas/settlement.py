"""
FinResolve AI — Settlement Record Schema
"""

from datetime import datetime

from pydantic import Field

from data.schemas.base import BaseRecord
from data.schemas.enums import RecordType, SettlementStatus
from data.schemas.money import Money


class SettlementRecord(BaseRecord):
    """
    A settlement record.

    Represents the transfer of funds from payment gateway to merchant,
    after fees have been deducted.

    Invariant (for clean data):
        net_amount = gross_amount - fee_amount
    """

    record_type: RecordType = Field(default=RecordType.SETTLEMENT, frozen=True)
    settlement_id: str = Field(description="Settlement identifier")
    payment_id: str = Field(description="Associated payment identifier")
    merchant_id: str = Field(description="Merchant receiving the settlement")
    gross_amount: Money = Field(description="Total amount before fee deduction")
    fee_amount: Money = Field(description="Total fees deducted")
    net_amount: Money = Field(description="Amount actually settled to merchant")
    status: SettlementStatus = Field(description="Settlement status")
    settled_at: datetime = Field(description="When settlement was processed (UTC)")
    utr: str = Field(default="", description="Unique Transaction Reference for bank transfer")
