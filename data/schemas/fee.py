"""
FinResolve AI — Fee Record Schema
"""

from datetime import datetime

from pydantic import Field

from data.schemas.base import BaseRecord
from data.schemas.enums import FeeType, RecordType
from data.schemas.money import Money


class FeeRecord(BaseRecord):
    """
    A fee record.

    Represents a fee charged on a transaction. Fee rates are expressed
    in basis points (bps) to avoid floating-point arithmetic.

    1 bps = 0.01%, so 200 bps = 2.00%.
    """

    record_type: RecordType = Field(default=RecordType.FEE, frozen=True)
    fee_id: str = Field(description="Fee identifier")
    payment_id: str = Field(description="Payment this fee is charged on")
    settlement_id: str = Field(default="", description="Settlement this fee is deducted from")
    fee_type: FeeType = Field(description="Type of fee")
    amount: Money = Field(description="Fee amount in minor units")
    rate_bps: int = Field(
        ge=0,
        description="Fee rate in basis points (1 bps = 0.01%). 0 for flat fees.",
    )
    applied_at: datetime = Field(description="When the fee was applied (UTC)")
