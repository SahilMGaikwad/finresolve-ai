"""
FinResolve AI — Temporal Consistency Rule

Validates event lifecycle ordering and settlement delay bounds:
order_time <= payment_time <= settlement_time
payment_time <= refund_time
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from data.schemas.enums import RecordType
from data.schemas.evidence import Evidence, EvidenceType, Severity
from data.schemas.matching import MatchGroup
from services.reconciliation.rules.base import BaseReconciliationRule, RuleResult


def _parse_utc_timestamp(record: dict[str, Any], field: str) -> datetime | None:
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


class TemporalConsistencyRule(BaseReconciliationRule):
    """
    Validates logical event sequence and flags temporal anomalies.
    """

    rule_id = "RULE-TIME-001"
    category = "temporal"

    def __init__(self, max_settlement_delay_days: int = 7):
        self.max_settlement_delay_days = max_settlement_delay_days

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
                explanation="No payment record present for temporal sequence check",
            )

        pay_time = _parse_utc_timestamp(payment, "captured_at")
        if not pay_time:
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=True,
                severity=Severity.INFO,
                explanation="Payment record missing timestamp",
            )

        # 1. Check Order sequence (Order <= Payment)
        if group.order_id:
            order = records_lookup.get(group.order_id)
            if order:
                ord_time = _parse_utc_timestamp(order, "ordered_at")
                if ord_time and ord_time > pay_time + timedelta(minutes=5):
                    evidence = Evidence(
                        evidence_type=EvidenceType.TEMPORAL_ANOMALY,
                        source_record_id=group.order_id,
                        record_type=RecordType.ORDER,
                        field_name="ordered_at",
                        observed_value=ord_time.isoformat(),
                        expected_value=f"<= {pay_time.isoformat()}",
                        rule_id=self.rule_id,
                        severity=Severity.MEDIUM,
                        strength=0.9,
                        explanation=f"Order timestamp ({ord_time.isoformat()}) is after payment capture ({pay_time.isoformat()})",
                    )
                    evidence_items.append(evidence)

        # 2. Check Settlement sequence (Payment <= Settlement <= Payment + max_delay)
        for stl_id in group.settlement_ids:
            stl = records_lookup.get(stl_id)
            if not stl:
                continue

            stl_time = _parse_utc_timestamp(stl, "settled_at")
            if not stl_time:
                continue

            if stl_time < pay_time:
                evidence = Evidence(
                    evidence_type=EvidenceType.TEMPORAL_ANOMALY,
                    source_record_id=stl_id,
                    record_type=RecordType.SETTLEMENT,
                    field_name="settled_at",
                    observed_value=stl_time.isoformat(),
                    expected_value=f">= {pay_time.isoformat()}",
                    rule_id=self.rule_id,
                    severity=Severity.HIGH,
                    strength=1.0,
                    explanation=f"Settlement occurred ({stl_time.isoformat()}) before payment capture ({pay_time.isoformat()})",
                )
                evidence_items.append(evidence)
            else:
                delay = (stl_time - pay_time).total_seconds() / 86400.0
                if delay > self.max_settlement_delay_days:
                    evidence = Evidence(
                        evidence_type=EvidenceType.TEMPORAL_ANOMALY,
                        source_record_id=stl_id,
                        record_type=RecordType.SETTLEMENT,
                        field_name="settled_at",
                        observed_value=stl_time.isoformat(),
                        expected_value=f"<= {self.max_settlement_delay_days} days delay",
                        rule_id=self.rule_id,
                        severity=Severity.MEDIUM,
                        strength=0.85,
                        explanation=f"Settlement delay of {delay:.1f} days exceeds configured window of {self.max_settlement_delay_days} days",
                    )
                    evidence_items.append(evidence)

        # 3. Check Refund sequence (Payment <= Refund)
        for rfnd_id in group.refund_ids:
            rfnd = records_lookup.get(rfnd_id)
            if not rfnd:
                continue

            rfnd_time = _parse_utc_timestamp(rfnd, "initiated_at")
            if rfnd_time and rfnd_time < pay_time:
                evidence = Evidence(
                    evidence_type=EvidenceType.TEMPORAL_ANOMALY,
                    source_record_id=rfnd_id,
                    record_type=RecordType.REFUND,
                    field_name="initiated_at",
                    observed_value=rfnd_time.isoformat(),
                    expected_value=f">= {pay_time.isoformat()}",
                    rule_id=self.rule_id,
                    severity=Severity.HIGH,
                    strength=1.0,
                    explanation=f"Refund initiated ({rfnd_time.isoformat()}) before payment was captured ({pay_time.isoformat()})",
                )
                evidence_items.append(evidence)

        if not evidence_items:
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=True,
                severity=Severity.INFO,
                explanation="All event timestamps follow logical chronological lifecycle ordering",
            )

        return RuleResult(
            rule_id=self.rule_id,
            category=self.category,
            passed=False,
            severity=Severity.MEDIUM,
            evidence_items=evidence_items,
            explanation=f"Detected {len(evidence_items)} temporal sequencing anomalies",
        )
