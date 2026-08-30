"""
FinResolve AI — Order Record Schema
"""

from datetime import datetime

from pydantic import Field

from data.schemas.base import BaseRecord
from data.schemas.enums import OrderStatus, RecordType
from data.schemas.money import Money


class OrderRecord(BaseRecord):
    """
    An order record.

    Represents a merchant order that may have one or more associated payments.
    """

    record_type: RecordType = Field(default=RecordType.ORDER, frozen=True)
    order_id: str = Field(description="Order identifier (source system ID)")
    merchant_id: str = Field(description="Merchant who created the order")
    amount: Money = Field(description="Total order amount")
    status: OrderStatus = Field(description="Current order status")
    items_count: int = Field(ge=1, description="Number of items in the order")
    ordered_at: datetime = Field(description="When the order was placed (UTC)")
