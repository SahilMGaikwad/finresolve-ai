"""
FinResolve AI — Shared Enumerations

All enumeration types used across the data model.
Centralised here to avoid circular imports and ensure consistency.
"""

from enum import Enum, unique


# ---- Record Types ----

@unique
class RecordType(str, Enum):
    """Types of financial records processed by the system."""
    PAYMENT = "payment"
    ORDER = "order"
    SETTLEMENT = "settlement"
    REFUND = "refund"
    FEE = "fee"
    LEDGER_ENTRY = "ledger_entry"
    PAYOUT = "payout"


# ---- Currency ----

@unique
class Currency(str, Enum):
    """Supported currencies. Values are ISO 4217 codes."""
    INR = "INR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


# Minor-unit multipliers for each currency (how many minor units per major unit)
CURRENCY_MINOR_UNITS: dict[Currency, int] = {
    Currency.INR: 100,   # 1 INR = 100 paise
    Currency.USD: 100,   # 1 USD = 100 cents
    Currency.EUR: 100,   # 1 EUR = 100 cents
    Currency.GBP: 100,   # 1 GBP = 100 pence
}


# ---- Payment ----

@unique
class PaymentStatus(str, Enum):
    """Payment lifecycle states."""
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


@unique
class PaymentMethod(str, Enum):
    """Payment instrument types."""
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"
    BANK_TRANSFER = "bank_transfer"


# ---- Order ----

@unique
class OrderStatus(str, Enum):
    """Order lifecycle states."""
    CREATED = "created"
    PAID = "paid"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    PARTIALLY_REFUNDED = "partially_refunded"
    REFUNDED = "refunded"


# ---- Settlement ----

@unique
class SettlementStatus(str, Enum):
    """Settlement lifecycle states."""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


# ---- Refund ----

@unique
class RefundStatus(str, Enum):
    """Refund lifecycle states."""
    INITIATED = "initiated"
    PROCESSED = "processed"
    FAILED = "failed"


# ---- Fee ----

@unique
class FeeType(str, Enum):
    """Types of fees applied to transactions."""
    PLATFORM_FEE = "platform_fee"
    PAYMENT_GATEWAY_FEE = "payment_gateway_fee"
    GST = "gst"
    SETTLEMENT_FEE = "settlement_fee"


# ---- Ledger ----

@unique
class LedgerEntryType(str, Enum):
    """Types of ledger entries."""
    CREDIT = "credit"
    DEBIT = "debit"
    REVERSAL = "reversal"
    ADJUSTMENT = "adjustment"


# ---- Payout ----

@unique
class PayoutStatus(str, Enum):
    """Payout lifecycle states."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    REVERSED = "reversed"


# ---- Validation ----

@unique
class ValidationStatus(str, Enum):
    """Outcome of record validation at ingestion."""
    ACCEPTED = "accepted"       # Valid, proceed to normalization
    QUARANTINED = "quarantined" # Parseable but suspect, needs review
    INVALID = "invalid"         # Unparseable or missing required fields


# ---- Corruption ----

@unique
class CorruptionType(str, Enum):
    """Types of corruption injected into synthetic data."""
    AMOUNT_MISMATCH = "amount_mismatch"
    MISSING_RECORD = "missing_record"
    DUPLICATE_RECORD = "duplicate_record"
    FEE_DISCREPANCY = "fee_discrepancy"
    TIMING_MISMATCH = "timing_mismatch"
    STATUS_INCONSISTENCY = "status_inconsistency"
    PARTIAL_SETTLEMENT = "partial_settlement"
    INCORRECT_REFERENCE = "incorrect_reference"


# ---- Case Difficulty ----

@unique
class CaseDifficulty(str, Enum):
    """Difficulty levels for reconciliation cases."""
    EASY = "easy"       # Single clear discrepancy, deterministic match
    MEDIUM = "medium"   # May have multiple related discrepancies
    HARD = "hard"       # Compound discrepancies, ambiguous resolution
