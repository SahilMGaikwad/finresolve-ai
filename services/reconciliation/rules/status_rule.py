"""
FinResolve AI — Status Consistency Rule

Detects contradictory lifecycle states across matched records.
"""

from __future__ import annotations

from typing import Any

from data.schemas.enums import (
    OrderStatus,
    PaymentStatus,
    RecordType,
    RefundStatus,
    SettlementStatus,
)
from data.schemas.evidence import Evidence, EvidenceType, Severity
from data.schemas.matching import MatchGroup
from services.reconciliation.rules.base import BaseReconciliationRule, RuleResult


class StatusConsistencyRule(BaseReconciliationRule):
    """
    Validates cross-entity status logic (e.g. failed payment cannot have processed settlement).
    """

    rule_id = "RULE-STAT-001"
    category = "status"

    def evaluate(
        self,
        group: MatchGroup,
        records_lookup: dict[str, dict[str, Any]],
    ) -> RuleResult:
        payment = records_lookup.get(group.payment_id or "") if group.payment_id else None
        evidence_items: list[Evidence] = []

        if not payment:
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=True,
                severity=Severity.INFO,
                explanation="No payment record present for status check",
            )

        pay_status = payment.get("status")

        # 1. Failed payment vs Processed Settlement
        for stl_id in group.settlement_ids:
            stl = records_lookup.get(stl_id)
            if not stl:
                continue

            stl_status = stl.get("status")
            if pay_status == PaymentStatus.FAILED.value and stl_status == SettlementStatus.PROCESSED.value:
                evidence = Evidence(
                    evidence_type=EvidenceType.STATUS_CONFLICT,
                    source_record_id=group.payment_id or "unknown",
                    record_type=RecordType.PAYMENT,
                    field_name="status",
                    observed_value=f"Payment={pay_status}, Settlement={stl_status}",
                    expected_value="Payment must be 'captured' if settlement is 'processed'",
                    rule_id=self.rule_id,
                    severity=Severity.CRITICAL,
                    strength=1.0,
                    explanation=f"Payment {group.payment_id} marked 'failed' but has processed settlement {stl_id}",
                )
                evidence_items.append(evidence)

        # 2. Refund processed vs Payment status
        for rfnd_id in group.refund_ids:
            rfnd = records_lookup.get(rfnd_id)
            if not rfnd:
                continue

            rfnd_status = rfnd.get("status")
            if rfnd_status == RefundStatus.PROCESSED.value:
                if pay_status not in (PaymentStatus.REFUNDED.value, PaymentStatus.PARTIALLY_REFUNDED.value, PaymentStatus.CAPTURED.value):
                    evidence = Evidence(
                        evidence_type=EvidenceType.STATUS_CONFLICT,
                        source_record_id=rfnd_id,
                        record_type=RecordType.REFUND,
                        field_name="status",
                        observed_value=f"Refund={rfnd_status}, Payment={pay_status}",
                        expected_value="Payment should reflect refund status",
                        rule_id=self.rule_id,
                        severity=Severity.HIGH,
                        strength=0.9,
                        explanation=f"Refund {rfnd_id} is processed but payment {group.payment_id} is in status '{pay_status}'",
                    )
                    evidence_items.append(evidence)

        # 3. Order status vs Payment status
        if group.order_id:
            order = records_lookup.get(group.order_id)
            if order:
                ord_status = order.get("status")
                if ord_status == OrderStatus.CANCELLED.value and pay_status == PaymentStatus.CAPTURED.value:
                    evidence = Evidence(
                        evidence_type=EvidenceType.STATUS_CONFLICT,
                        source_record_id=group.order_id,
                        record_type=RecordType.ORDER,
                        field_name="status",
                        observed_value=f"Order={ord_status}, Payment={pay_status}",
                        expected_value="Cancelled order should not have captured unrefunded payment",
                        rule_id=self.rule_id,
                        severity=Severity.HIGH,
                        strength=0.9,
                        explanation=f"Order {group.order_id} is marked cancelled, but payment {group.payment_id} is captured",
                    )
                    evidence_items.append(evidence)

        if not evidence_items:
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=True,
                severity=Severity.INFO,
                explanation="All record statuses are logically consistent across matched entities",
            )

        return RuleResult(
            rule_id=self.rule_id,
            category=self.category,
            passed=False,
            severity=Severity.HIGH,
            evidence_items=evidence_items,
            explanation=f"Detected {len(evidence_items)} status consistency violations",
        )
