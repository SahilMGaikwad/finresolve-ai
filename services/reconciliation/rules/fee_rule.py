"""
FinResolve AI — Fee Analysis & Verification Rule

Re-verifies fee calculations using integer basis points math:
expected_fee = (base_amount * rate_bps + 5000) // 10000
"""

from __future__ import annotations

from typing import Any

from data.schemas.enums import FeeType, RecordType
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


class FeeAnalysisRule(BaseReconciliationRule):
    """
    Validates that recorded fee amounts match their stated basis-point rates.
    """

    rule_id = "RULE-FEE-001"
    category = "fee"

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
                passed=True,
                severity=Severity.INFO,
                explanation="No payment record found to calculate fee base on",
            )

        pay_amt = _get_minor_amount(payment, "amount")
        evidence_items: list[Evidence] = []
        platform_fee_minor = 0

        # Pass 1: Verify platform and standalone fees
        for fee_id in group.fee_ids:
            fee = records_lookup.get(fee_id)
            if not fee:
                continue

            fee_type = fee.get("fee_type")
            rate_bps = fee.get("rate_bps", 0)
            observed_fee = _get_minor_amount(fee, "amount")

            if fee_type == FeeType.PLATFORM_FEE.value:
                # Platform fee is based on payment amount
                expected_fee = (pay_amt * rate_bps + 5000) // 10000
                platform_fee_minor = expected_fee

                if observed_fee != expected_fee:
                    diff = observed_fee - expected_fee
                    evidence = Evidence(
                        evidence_type=EvidenceType.FEE_MISMATCH,
                        source_record_id=fee_id,
                        record_type=RecordType.FEE,
                        field_name="amount",
                        observed_value=str(observed_fee),
                        expected_value=str(expected_fee),
                        rule_id=self.rule_id,
                        severity=Severity.MEDIUM,
                        strength=1.0,
                        explanation=(
                            f"Platform fee calculation error: rate {rate_bps} bps on payment {pay_amt} "
                            f"yields {expected_fee} paise, but observed {observed_fee} paise (diff: {diff})"
                        ),
                    )
                    evidence_items.append(evidence)

            elif fee_type == FeeType.GST.value:
                # GST is calculated on platform fee (typically 1800 bps = 18%)
                if not platform_fee_minor:
                    for fid in group.fee_ids:
                        f_rec = records_lookup.get(fid, {})
                        if f_rec.get("fee_type") == FeeType.PLATFORM_FEE.value:
                            platform_fee_minor = _get_minor_amount(f_rec, "amount")
                            break
                base_for_gst = platform_fee_minor
                if base_for_gst > 0:
                    expected_gst = (base_for_gst * rate_bps + 5000) // 10000

                    if observed_fee != expected_gst:
                        diff = observed_fee - expected_gst
                        evidence = Evidence(
                            evidence_type=EvidenceType.FEE_MISMATCH,
                            source_record_id=fee_id,
                            record_type=RecordType.FEE,
                            field_name="amount",
                            observed_value=str(observed_fee),
                            expected_value=str(expected_gst),
                            rule_id=self.rule_id,
                            severity=Severity.MEDIUM,
                            strength=1.0,
                            explanation=(
                                f"GST fee calculation error: rate {rate_bps} bps on base fee {base_for_gst} "
                                f"yields {expected_gst} paise, but observed {observed_fee} paise (diff: {diff})"
                            ),
                        )
                        evidence_items.append(evidence)

        if not evidence_items:
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=True,
                severity=Severity.INFO,
                explanation=f"All {len(group.fee_ids)} fee calculations verified accurately against basis-point rates",
            )

        return RuleResult(
            rule_id=self.rule_id,
            category=self.category,
            passed=False,
            severity=Severity.MEDIUM,
            evidence_items=evidence_items,
            explanation=f"Detected {len(evidence_items)} fee calculation discrepancies",
        )
