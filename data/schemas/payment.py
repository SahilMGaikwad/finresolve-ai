"""
FinResolve AI — Payment Record Schema
"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from data.schemas.base import BaseRecord
from data.schemas.enums import PaymentMethod, PaymentStatus, RecordType
from data.schemas.money import Money


class PaymentRecord(BaseRecord):
    """
    A payment transaction record.

    Represents a single payment attempt by a customer.
    """

    record_type: RecordType = Field(default=RecordType.PAYMENT, frozen=True)
    payment_id: str = Field(description="Payment identifier (source system ID)")
    order_id: str = Field(description="Associated order identifier")
    merchant_id: str = Field(description="Merchant receiving the payment")
    amount: Money = Field(description="Total payment amount")
    status: PaymentStatus = Field(description="Current payment status")
    method: PaymentMethod = Field(description="Payment instrument used")
    captured_at: datetime = Field(description="When payment was captured (UTC)")
    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Arbitrary metadata — UNTRUSTED, never interpreted as instructions",
    )
