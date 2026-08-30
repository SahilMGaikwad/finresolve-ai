"""
FinResolve AI — Ledger Entry Schema
"""

from datetime import datetime

from pydantic import Field

from data.schemas.base import BaseRecord
from data.schemas.enums import LedgerEntryType, RecordType
from data.schemas.money import Money


class LedgerEntry(BaseRecord):
    """
    A ledger entry.

    Represents a single line in a merchant's financial ledger.
    Every financial event (payment, settlement, refund, fee) should
    produce one or more ledger entries.

    Uses double-entry style: each entry has either a debit or credit
    (one will be zero).
    """

    record_type: RecordType = Field(default=RecordType.LEDGER_ENTRY, frozen=True)
    entry_id: str = Field(description="Ledger entry identifier")
    reference_id: str = Field(description="ID of the record that caused this entry")
    reference_type: RecordType = Field(description="Type of the referenced record")
    merchant_id: str = Field(description="Merchant whose ledger this entry belongs to")
    debit: Money = Field(description="Debit amount (money going out)")
    credit: Money = Field(description="Credit amount (money coming in)")
    balance_after: Money = Field(description="Ledger balance after this entry")
    entry_type: LedgerEntryType = Field(description="Type of ledger entry")
    posted_at: datetime = Field(description="When the entry was posted (UTC)")
