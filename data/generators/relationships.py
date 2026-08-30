"""
FinResolve AI — Relationship Builder

Ensures referential integrity across all records within a case.
Constructs consistent payment → order → settlement → fee → ledger chains.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from data.generators.config import GeneratorConfig
from data.generators.merchants import MerchantProfile
from data.schemas.enums import (
    Currency,
    FeeType,
    LedgerEntryType,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    PayoutStatus,
    RecordType,
    RefundStatus,
    SettlementStatus,
)
from data.schemas.money import Money


def _random_datetime(
    rng: random.Random,
    start: datetime,
    end: datetime,
) -> datetime:
    """Generate a random datetime between start and end (UTC)."""
    delta = end - start
    random_seconds = rng.randint(0, max(1, int(delta.total_seconds())))
    return start + timedelta(seconds=random_seconds)


def _deterministic_hex(rng: random.Random, length: int = 16) -> str:
    """Generate deterministic hex string from the seeded RNG."""
    return f"{rng.getrandbits(length * 4):0{length}x}"


def build_clean_case_records(
    case_index: int,
    merchant: MerchantProfile,
    config: GeneratorConfig,
    rng: random.Random,
) -> dict:
    """
    Build a complete set of clean, internally consistent records for one case.

    Returns a dict of serialised record lists keyed by record type.
    All amounts use integer minor units. All relationships are valid.

    The chain is:
        order → payment → fee(s) → settlement → ledger_entries
        (optionally: → refund)
    """
    currency = config.currency_enum
    start_dt = datetime.fromisoformat(config.start_date).replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(config.end_date).replace(tzinfo=timezone.utc)

    # ---- IDs ----
    case_id = f"CASE-{case_index + 1:06d}"
    order_id = f"ord_{_deterministic_hex(rng)}"
    payment_id = f"pay_{_deterministic_hex(rng)}"
    settlement_id = f"stl_{_deterministic_hex(rng)}"

    # ---- Amount ----
    amount_minor = rng.randint(merchant.typical_min_amount, merchant.typical_max_amount)
    payment_amount = Money.from_minor(amount_minor, currency)

    # ---- Timestamps ----
    order_time = _random_datetime(rng, start_dt, end_dt - timedelta(days=14))
    payment_time = order_time + timedelta(minutes=rng.randint(1, 60))
    settlement_time = payment_time + timedelta(days=merchant.settlement_delay_days)

    # ---- Fees (integer arithmetic only) ----
    platform_fee = payment_amount.multiply_bps(merchant.platform_fee_bps)
    gst_on_fee = platform_fee.multiply_bps(merchant.gst_on_fee_bps)
    total_fee = platform_fee + gst_on_fee
    net_settlement = payment_amount - total_fee

    # ---- Payment method ----
    method = rng.choice(list(PaymentMethod))
    items_count = rng.randint(1, 5)

    # ---- Build records ----

    order_record = {
        "record_type": RecordType.ORDER.value,
        "order_id": order_id,
        "merchant_id": merchant.merchant_id,
        "amount": payment_amount.model_dump(),
        "status": OrderStatus.PAID.value,
        "items_count": items_count,
        "ordered_at": order_time.isoformat(),
    }

    payment_record = {
        "record_type": RecordType.PAYMENT.value,
        "payment_id": payment_id,
        "order_id": order_id,
        "merchant_id": merchant.merchant_id,
        "amount": payment_amount.model_dump(),
        "status": PaymentStatus.CAPTURED.value,
        "method": method.value,
        "captured_at": payment_time.isoformat(),
        "metadata": {
            "source": "synthetic_generator",
            "case_id": case_id,
        },
    }

    platform_fee_id = f"fee_{_deterministic_hex(rng)}"
    gst_fee_id = f"fee_{_deterministic_hex(rng)}"

    platform_fee_record = {
        "record_type": RecordType.FEE.value,
        "fee_id": platform_fee_id,
        "payment_id": payment_id,
        "settlement_id": settlement_id,
        "fee_type": FeeType.PLATFORM_FEE.value,
        "amount": platform_fee.model_dump(),
        "rate_bps": merchant.platform_fee_bps,
        "applied_at": payment_time.isoformat(),
    }

    gst_fee_record = {
        "record_type": RecordType.FEE.value,
        "fee_id": gst_fee_id,
        "payment_id": payment_id,
        "settlement_id": settlement_id,
        "fee_type": FeeType.GST.value,
        "amount": gst_on_fee.model_dump(),
        "rate_bps": merchant.gst_on_fee_bps,
        "applied_at": payment_time.isoformat(),
    }

    settlement_record = {
        "record_type": RecordType.SETTLEMENT.value,
        "settlement_id": settlement_id,
        "payment_id": payment_id,
        "merchant_id": merchant.merchant_id,
        "gross_amount": payment_amount.model_dump(),
        "fee_amount": total_fee.model_dump(),
        "net_amount": net_settlement.model_dump(),
        "status": SettlementStatus.PROCESSED.value,
        "settled_at": settlement_time.isoformat(),
        "utr": f"UTR{rng.randint(100000000000, 999999999999)}",
    }

    # ---- Ledger entries ----
    # Payment credit
    ledger_balance = payment_amount
    payment_ledger = {
        "record_type": RecordType.LEDGER_ENTRY.value,
        "entry_id": f"le_{_deterministic_hex(rng)}",
        "reference_id": payment_id,
        "reference_type": RecordType.PAYMENT.value,
        "merchant_id": merchant.merchant_id,
        "debit": Money.zero(currency).model_dump(),
        "credit": payment_amount.model_dump(),
        "balance_after": ledger_balance.model_dump(),
        "entry_type": LedgerEntryType.CREDIT.value,
        "posted_at": payment_time.isoformat(),
    }

    # Fee debit
    ledger_balance = ledger_balance - total_fee
    fee_ledger = {
        "record_type": RecordType.LEDGER_ENTRY.value,
        "entry_id": f"le_{_deterministic_hex(rng)}",
        "reference_id": settlement_id,
        "reference_type": RecordType.SETTLEMENT.value,
        "merchant_id": merchant.merchant_id,
        "debit": total_fee.model_dump(),
        "credit": Money.zero(currency).model_dump(),
        "balance_after": ledger_balance.model_dump(),
        "entry_type": LedgerEntryType.DEBIT.value,
        "posted_at": settlement_time.isoformat(),
    }

    # Settlement debit (money leaving the pool to merchant's bank)
    ledger_balance = ledger_balance - net_settlement
    settlement_ledger = {
        "record_type": RecordType.LEDGER_ENTRY.value,
        "entry_id": f"le_{_deterministic_hex(rng)}",
        "reference_id": settlement_id,
        "reference_type": RecordType.SETTLEMENT.value,
        "merchant_id": merchant.merchant_id,
        "debit": net_settlement.model_dump(),
        "credit": Money.zero(currency).model_dump(),
        "balance_after": ledger_balance.model_dump(),
        "entry_type": LedgerEntryType.DEBIT.value,
        "posted_at": settlement_time.isoformat(),
    }

    records = {
        "payments": [payment_record],
        "orders": [order_record],
        "settlements": [settlement_record],
        "fees": [platform_fee_record, gst_fee_record],
        "ledger_entries": [payment_ledger, fee_ledger, settlement_ledger],
        "refunds": [],
        "payouts": [],
    }

    # ---- Optional refund ----
    if rng.random() < config.refund_probability:
        refund_fraction_bps = rng.randint(2000, 10000)  # 20%–100% refund
        refund_amount = payment_amount.multiply_bps(refund_fraction_bps)
        refund_id = f"rfnd_{_deterministic_hex(rng)}"
        refund_time = payment_time + timedelta(days=rng.randint(1, 10))
        refund_processed = refund_time + timedelta(hours=rng.randint(1, 48))

        is_full = refund_fraction_bps == 10000
        payment_status = PaymentStatus.REFUNDED if is_full else PaymentStatus.PARTIALLY_REFUNDED
        order_status = OrderStatus.REFUNDED if is_full else OrderStatus.PARTIALLY_REFUNDED

        # Update payment and order status
        payment_record["status"] = payment_status.value
        order_record["status"] = order_status.value

        refund_record = {
            "record_type": RecordType.REFUND.value,
            "refund_id": refund_id,
            "payment_id": payment_id,
            "amount": refund_amount.model_dump(),
            "reason": rng.choice([
                "customer_request", "product_defective",
                "order_cancelled", "duplicate_payment",
            ]),
            "status": RefundStatus.PROCESSED.value,
            "initiated_at": refund_time.isoformat(),
            "processed_at": refund_processed.isoformat(),
        }
        records["refunds"].append(refund_record)

        # Refund ledger entry
        ledger_balance_after_refund = Money.from_minor(
            -refund_amount.amount_minor, currency
        )
        refund_ledger = {
            "record_type": RecordType.LEDGER_ENTRY.value,
            "entry_id": f"le_{_deterministic_hex(rng)}",
            "reference_id": refund_id,
            "reference_type": RecordType.REFUND.value,
            "merchant_id": merchant.merchant_id,
            "debit": refund_amount.model_dump(),
            "credit": Money.zero(currency).model_dump(),
            "balance_after": ledger_balance_after_refund.model_dump(),
            "entry_type": LedgerEntryType.REVERSAL.value,
            "posted_at": refund_processed.isoformat(),
        }
        records["ledger_entries"].append(refund_ledger)

    # Store internal IDs for corruption engine to reference
    _internal = {
        "case_id": case_id,
        "payment_id": payment_id,
        "order_id": order_id,
        "settlement_id": settlement_id,
        "merchant": merchant,
        "payment_amount": payment_amount,
        "total_fee": total_fee,
        "net_settlement": net_settlement,
    }

    return {"records": records, "_internal": _internal}
