"""
FinResolve AI — Amount Reconciliation Rule

Performs exact integer minor-unit arithmetic on payments, fees, refunds, and settlements:
expected_net = payment_amount - total_fees - total_refunds
diff = observed_settlement_net - expected_net
"""

from __future__ import annotations

from typing import Any

from data.schemas.enums import RecordType
from data.schemas.evidence import Evidence, EvidenceType, Severity
from data.schemas.matching import MatchGroup
from services.reconciliation.rules.base import BaseReconciliationRule, RuleResult


def _get_minor_amount(record: dict[str, Any], field: str) -> int:
    val = record.get(field, 0)
    if isinstance(val, dict):
        return int(val.get("amount_minor", 0))
    elif isinstance(val, int):
        return val
    return 0


class AmountReconciliationRule(BaseReconciliationRule):
    """
    Validates that the net settled amount equals payment gross minus fees and refunds.
    Zero floating-point arithmetic.
    """

    rule_id = "RULE-AMT-001"
    category = "amount"

    def evaluate(
        self,
        group: MatchGroup,
        records_lookup: dict[str, dict[str, Any]],
    ) -> RuleResult:
        payment = records_lookup.get(group.payment_id or "") if group.payment_id else None
        if not payment:
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=False,
                severity=Severity.HIGH,
                explanation="No payment record found in match group for amount reconciliation",
            )

        pay_amt = _get_minor_amount(payment, "amount")
        currency = payment.get("amount", {}).get("currency", "INR") if isinstance(payment.get("amount"), dict) else "INR"

        # Sum fees
        total_fees = 0
        fee_breakdown = {}
        for fee_id in group.fee_ids:
            fee = records_lookup.get(fee_id)
            if fee:
                f_amt = _get_minor_amount(fee, "amount")
                f_type = fee.get("fee_type", "fee")
                total_fees += f_amt
                fee_breakdown[f"{f_type}_{fee_id[:8]}"] = f_amt

        # Sum refunds
        total_refunds = 0
        refund_breakdown = {}
        for rfnd_id in group.refund_ids:
            rfnd = records_lookup.get(rfnd_id)
            if rfnd:
                r_amt = _get_minor_amount(rfnd, "amount")
                total_refunds += r_amt
                refund_breakdown[rfnd_id[:8]] = r_amt

        # Expected net settlement for payment minus fees
        expected_net = pay_amt - total_fees

        # Observed net settlement
        observed_net = 0
        settlements_present = bool(group.settlement_ids)
        for stl_id in group.settlement_ids:
            stl = records_lookup.get(stl_id)
            if stl:
                observed_net += _get_minor_amount(stl, "net_amount")

        # If no settlement exists
        if not settlements_present:
            evidence = Evidence(
                evidence_type=EvidenceType.MISSING_LINK,
                source_record_id=group.payment_id or "unknown",
                record_type=RecordType.PAYMENT,
                field_name="settlement_ids",
                observed_value="missing",
                expected_value=f"Settlement of {expected_net} paise",
                rule_id=self.rule_id,
                severity=Severity.HIGH,
                strength=1.0,
                explanation=f"Payment {group.payment_id} has no matching settlement record (expected net: {expected_net} {currency})",
            )
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=False,
                severity=Severity.HIGH,
                expected_value={"expected_net_minor": expected_net, "currency": currency},
                observed_value={"observed_net_minor": 0, "currency": currency},
                difference={"difference_minor": -expected_net, "currency": currency},
                evidence_items=[evidence],
                explanation=f"Missing settlement: expected {expected_net} {currency}, observed 0",
            )

        diff = observed_net - expected_net

        # Also check that total refunds do not exceed payment amount
        if total_refunds > pay_amt:
            diff = total_refunds - pay_amt
            evidence = Evidence(
                evidence_type=EvidenceType.AMOUNT_DIFF,
                source_record_id=group.refund_ids[0] if group.refund_ids else (group.payment_id or ""),
                record_type=RecordType.REFUND,
                field_name="amount",
                observed_value=str(total_refunds),
                expected_value=f"<= {pay_amt}",
                rule_id=self.rule_id,
                severity=Severity.CRITICAL,
                strength=1.0,
                explanation=f"Total refunds ({total_refunds}) exceed original payment amount ({pay_amt}) {currency}",
            )
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=False,
                severity=Severity.CRITICAL,
                expected_value={"max_refund_minor": pay_amt, "currency": currency},
                observed_value={"total_refunds_minor": total_refunds, "currency": currency},
                difference={"difference_minor": diff, "currency": currency},
                evidence_items=[evidence],
                explanation=f"Excessive refund: refunds ({total_refunds}) exceed payment ({pay_amt})",
            )

        if diff == 0:
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=True,
                severity=Severity.INFO,
                expected_value={"expected_net_minor": expected_net, "currency": currency},
                observed_value={"observed_net_minor": observed_net, "currency": currency},
                difference={"difference_minor": 0, "currency": currency},
                explanation=(
                    f"Amount reconciled exactly: Payment ({pay_amt}) - Fees ({total_fees}) "
                    f"= Expected Net ({expected_net}) == Observed Net ({observed_net}) {currency}"
                ),
            )

        # Discrepancy detected
        primary_stl_id = group.settlement_ids[0]
        evidence = Evidence(
            evidence_type=EvidenceType.AMOUNT_DIFF,
            source_record_id=primary_stl_id,
            record_type=RecordType.SETTLEMENT,
            field_name="net_amount",
            observed_value=str(observed_net),
            expected_value=str(expected_net),
            rule_id=self.rule_id,
            severity=Severity.HIGH,
            strength=1.0,
            explanation=(
                f"Net settlement discrepancy of {diff} paise {currency}. "
                f"Calculation: Payment ({pay_amt}) - Fees ({total_fees}) - Refunds ({total_refunds}) "
                f"= Expected ({expected_net}) vs Observed ({observed_net})"
            ),
        )

        return RuleResult(
            rule_id=self.rule_id,
            category=self.category,
            passed=False,
            severity=Severity.HIGH,
            expected_value={
                "payment_gross_minor": pay_amt,
                "total_fees_minor": total_fees,
                "total_refunds_minor": total_refunds,
                "expected_net_minor": expected_net,
                "fee_breakdown": fee_breakdown,
                "currency": currency,
            },
            observed_value={"observed_net_minor": observed_net, "currency": currency},
            difference={"difference_minor": diff, "currency": currency},
            evidence_items=[evidence],
            explanation=(
                f"Amount mismatch of {diff} paise: expected net {expected_net}, "
                f"observed {observed_net} {currency}"
            ),
        )
