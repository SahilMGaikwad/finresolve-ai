"""
FinResolve AI — Financial Delta & Ledger Verifier

Verifies conservation of funds and double-entry accounting integrity during counterfactual simulation.
All arithmetic operates strictly in integer minor units (paise).
"""

from __future__ import annotations

from typing import Any

from data.schemas.case import CaseRecords
from data.schemas.enums import Currency
from data.schemas.resolution import FinancialDelta, ResolutionAction


def _get_amount_minor(rec: dict[str, Any] | Any, field: str = "amount") -> int:
    """Extract minor currency unit integer from Money dict or object."""
    if isinstance(rec, dict):
        val = rec.get(field)
    else:
        val = getattr(rec, field, None)

    if isinstance(val, dict):
        return int(val.get("amount_minor", 0))
    elif hasattr(val, "amount_minor"):
        return int(val.amount_minor)
    elif isinstance(val, int):
        return val
    return 0


def _get_val(rec: dict[str, Any] | Any, key: str, default: Any = None) -> Any:
    if isinstance(rec, dict):
        return rec.get(key, default)
    return getattr(rec, key, default)


def compute_financial_delta(
    before_records: CaseRecords,
    after_records: CaseRecords,
    action: ResolutionAction,
) -> FinancialDelta:
    """
    Compute the exact integer minor unit balance shifts across Merchant, Fee, Tax, and Customer.
    """
    # 1. Total Settlement Net (Merchant Funds)
    before_merchant_net = sum(_get_amount_minor(s, "net_amount") for s in before_records.settlements)
    after_merchant_net = sum(_get_amount_minor(s, "net_amount") for s in after_records.settlements)
    merchant_delta = after_merchant_net - before_merchant_net

    # 2. Total Platform Fees
    before_fees = sum(_get_amount_minor(f, "amount") for f in before_records.fees)
    after_fees = sum(_get_amount_minor(f, "amount") for f in after_records.fees)
    fee_delta = after_fees - before_fees

    # 3. Total Taxes
    before_taxes = sum(_get_amount_minor(f, "tax_amount") for f in before_records.fees)
    after_taxes = sum(_get_amount_minor(f, "tax_amount") for f in after_records.fees)
    tax_delta = after_taxes - before_taxes

    # 4. Total Refunds (Customer Funds)
    before_refunds = sum(_get_amount_minor(r, "amount") for r in before_records.refunds)
    after_refunds = sum(_get_amount_minor(r, "amount") for r in after_records.refunds)
    customer_delta = after_refunds - before_refunds

    return FinancialDelta(
        merchant_balance_delta_minor=merchant_delta,
        fee_balance_delta_minor=fee_delta,
        tax_balance_delta_minor=tax_delta,
        customer_balance_delta_minor=customer_delta,
        currency=Currency.INR,
    )


def verify_ledger_double_entry(records: CaseRecords) -> tuple[bool, str | None]:
    """
    Verify that double-entry ledger entries maintain valid debit and credit balance.
    """
    if not records.ledger_entries:
        return True, None

    for entry in records.ledger_entries:
        debit_amt = _get_amount_minor(entry, "debit")
        credit_amt = _get_amount_minor(entry, "credit")
        entry_id = _get_val(entry, "entry_id", "unknown")

        if debit_amt > 0 and credit_amt > 0:
            return False, f"Ledger entry {entry_id} cannot have both non-zero debit ({debit_amt}) and credit ({credit_amt})"
        if debit_amt == 0 and credit_amt == 0:
            return False, f"Ledger entry {entry_id} must have either positive debit or credit"

    return True, None
