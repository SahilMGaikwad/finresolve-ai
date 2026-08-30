"""
FinResolve AI — Explainable Matching Signals

Implements distinct, explainable signal evaluators that calculate match scores
between primary records (e.g. Payments) and candidate records (Settlements, Orders, etc.).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from data.schemas.enums import Currency, RecordType
from data.schemas.matching import MatchSignal


def evaluate_reference_signal(
    primary: dict[str, Any],
    candidate: dict[str, Any],
    weight: float = 0.40,
) -> MatchSignal:
    """
    Evaluates whether the candidate explicitly references the primary record ID,
    or vice versa.
    """
    p_type = primary.get("record_type")
    c_type = candidate.get("record_type")
    
    score = 0.0
    explanation = f"No explicit reference link between {p_type} and {c_type}"

    # Payment <-> Order
    if p_type == RecordType.PAYMENT.value and c_type == RecordType.ORDER.value:
        if primary.get("order_id") and primary.get("order_id") == candidate.get("order_id"):
            score = 1.0
            explanation = f"Payment explicitly references Order ID {candidate.get('order_id')}"
    elif p_type == RecordType.ORDER.value and c_type == RecordType.PAYMENT.value:
        if candidate.get("order_id") and candidate.get("order_id") == primary.get("order_id"):
            score = 1.0
            explanation = f"Payment explicitly references Order ID {primary.get('order_id')}"

    # Payment <-> Settlement
    elif p_type == RecordType.PAYMENT.value and c_type == RecordType.SETTLEMENT.value:
        if candidate.get("payment_id") and candidate.get("payment_id") == primary.get("payment_id"):
            score = 1.0
            explanation = f"Settlement explicitly references Payment ID {primary.get('payment_id')}"
        elif candidate.get("payment_id"):
            score = -1.0  # Explicit contradiction: belongs to a different payment
            explanation = f"Settlement references different Payment ID '{candidate.get('payment_id')}'"

    # Payment <-> Fee
    elif p_type == RecordType.PAYMENT.value and c_type == RecordType.FEE.value:
        if candidate.get("payment_id") and candidate.get("payment_id") == primary.get("payment_id"):
            score = 1.0
            explanation = f"Fee explicitly references Payment ID {primary.get('payment_id')}"
        elif candidate.get("payment_id"):
            score = -1.0
            explanation = f"Fee references different Payment ID '{candidate.get('payment_id')}'"

    # Payment <-> Refund
    elif p_type == RecordType.PAYMENT.value and c_type == RecordType.REFUND.value:
        if candidate.get("payment_id") and candidate.get("payment_id") == primary.get("payment_id"):
            score = 1.0
            explanation = f"Refund explicitly references Payment ID {primary.get('payment_id')}"
        elif candidate.get("payment_id"):
            score = -1.0
            explanation = f"Refund references different Payment ID '{candidate.get('payment_id')}'"

    # Payment / Settlement <-> Ledger Entry
    elif c_type == RecordType.LEDGER_ENTRY.value:
        ref_id = candidate.get("reference_id")
        if ref_id in (primary.get("payment_id"), primary.get("settlement_id"), primary.get("order_id"), primary.get("refund_id")):
            score = 1.0
            explanation = f"Ledger entry references {p_type} ID {ref_id}"

    return MatchSignal(
        name="reference_matching",
        weight=weight,
        raw_score=score,
        weighted_score=round(score * weight, 4),
        explanation=explanation,
    )


def _extract_amount_minor(record: dict[str, Any]) -> int | None:
    """Helper to extract the primary integer minor amount from various record shapes."""
    for field in ["amount", "gross_amount", "net_amount", "credit", "debit"]:
        val = record.get(field)
        if isinstance(val, dict) and "amount_minor" in val:
            return int(val["amount_minor"])
        elif isinstance(val, int):
            return val
    return None


def _extract_currency(record: dict[str, Any]) -> str | None:
    """Helper to extract currency string from record amounts."""
    for field in ["amount", "gross_amount", "net_amount", "credit", "debit"]:
        val = record.get(field)
        if isinstance(val, dict) and "currency" in val:
            curr = val["currency"]
            return curr.value if isinstance(curr, Currency) else str(curr)
    return None


def evaluate_amount_signal(
    primary: dict[str, Any],
    candidate: dict[str, Any],
    weight: float = 0.25,
) -> MatchSignal:
    """
    Evaluates amount compatibility between two records in integer minor units.
    """
    p_amt = _extract_amount_minor(primary)
    c_amt = _extract_amount_minor(candidate)

    if p_amt is None or c_amt is None:
        return MatchSignal(
            name="amount_compatibility",
            weight=weight,
            raw_score=0.0,
            weighted_score=0.0,
            explanation="One or both records lack an extractable amount",
        )

    # Exact amount match
    if p_amt == c_amt:
        return MatchSignal(
            name="amount_compatibility",
            weight=weight,
            raw_score=1.0,
            weighted_score=round(1.0 * weight, 4),
            explanation=f"Exact amount match ({p_amt} minor units)",
        )

    # Fee or Refund: allowed to be smaller than payment amount
    c_type = candidate.get("record_type")
    if c_type in (RecordType.FEE.value, RecordType.REFUND.value):
        if 0 < c_amt <= p_amt:
            return MatchSignal(
                name="amount_compatibility",
                weight=weight,
                raw_score=0.9,
                weighted_score=round(0.9 * weight, 4),
                explanation=f"{c_type.capitalize()} amount ({c_amt}) is within valid payment bounds ({p_amt})",
            )

    # Settlement: net amount is typically 90% - 100% of payment gross due to fees
    if c_type == RecordType.SETTLEMENT.value:
        if 0 < c_amt <= p_amt and (p_amt - c_amt) <= (p_amt * 0.15):
            return MatchSignal(
                name="amount_compatibility",
                weight=weight,
                raw_score=0.85,
                weighted_score=round(0.85 * weight, 4),
                explanation=f"Settlement net amount ({c_amt}) is consistent with payment gross ({p_amt}) less fees",
            )

    return MatchSignal(
        name="amount_compatibility",
        weight=weight,
        raw_score=0.0,
        weighted_score=0.0,
        explanation=f"Amount mismatch: primary={p_amt}, candidate={c_amt}",
    )


def evaluate_currency_signal(
    primary: dict[str, Any],
    candidate: dict[str, Any],
    weight: float = 0.10,
) -> MatchSignal:
    """
    Evaluates whether both records operate in the exact same ISO currency.
    """
    p_curr = _extract_currency(primary)
    c_curr = _extract_currency(candidate)

    if p_curr and c_curr and p_curr == c_curr:
        score = 1.0
        explanation = f"Currency matches exactly ({p_curr})"
    else:
        score = 0.0
        explanation = f"Currency mismatch or missing: primary={p_curr}, candidate={c_curr}"

    return MatchSignal(
        name="currency_match",
        weight=weight,
        raw_score=score,
        weighted_score=round(score * weight, 4),
        explanation=explanation,
    )


def _extract_timestamp(record: dict[str, Any]) -> datetime | None:
    """Helper to extract and parse primary timestamp as UTC datetime."""
    for field in ["captured_at", "ordered_at", "settled_at", "applied_at", "initiated_at", "posted_at", "created_at"]:
        val = record.get(field)
        if isinstance(val, datetime):
            return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
        elif isinstance(val, str):
            try:
                dt = datetime.fromisoformat(val)
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                pass
    return None


def evaluate_timestamp_proximity_signal(
    primary: dict[str, Any],
    candidate: dict[str, Any],
    weight: float = 0.15,
    max_window_days: int = 30,
) -> MatchSignal:
    """
    Evaluates temporal plausibility and proximity between two records.
    """
    p_time = _extract_timestamp(primary)
    c_time = _extract_timestamp(candidate)

    if not p_time or not c_time:
        return MatchSignal(
            name="timestamp_proximity",
            weight=weight,
            raw_score=0.5,
            weighted_score=round(0.5 * weight, 4),
            explanation="One or both records lack a valid timestamp; neutral score assigned",
        )

    delta = abs((c_time - p_time).total_seconds())
    delta_days = delta / 86400.0

    if delta_days <= 1.0:
        score = 1.0
        explanation = f"High temporal proximity (delta = {delta_days:.2f} days)"
    elif delta_days <= 7.0:
        score = 0.8
        explanation = f"Normal temporal window (delta = {delta_days:.2f} days)"
    elif delta_days <= max_window_days:
        # Linear decay between 7 and 30 days
        decay = (max_window_days - delta_days) / (max_window_days - 7.0)
        score = max(0.2, round(0.8 * decay, 2))
        explanation = f"Extended temporal window (delta = {delta_days:.2f} days, decay={score})"
    else:
        score = 0.0
        explanation = f"Exceeds maximum allowable temporal window ({delta_days:.1f} > {max_window_days} days)"

    return MatchSignal(
        name="timestamp_proximity",
        weight=weight,
        raw_score=score,
        weighted_score=round(score * weight, 4),
        explanation=explanation,
    )


def evaluate_merchant_signal(
    primary: dict[str, Any],
    candidate: dict[str, Any],
    weight: float = 0.10,
) -> MatchSignal:
    """
    Evaluates merchant identity consistency.
    """
    p_merch = primary.get("merchant_id")
    c_merch = candidate.get("merchant_id")

    if p_merch and c_merch and p_merch == c_merch:
        score = 1.0
        explanation = f"Merchant ID matches ({p_merch})"
    elif not p_merch or not c_merch:
        score = 0.5
        explanation = "Merchant ID absent in one or both records; neutral score"
    else:
        score = 0.0
        explanation = f"Merchant ID mismatch: primary={p_merch}, candidate={c_merch}"

    return MatchSignal(
        name="merchant_match",
        weight=weight,
        raw_score=score,
        weighted_score=round(score * weight, 4),
        explanation=explanation,
    )
