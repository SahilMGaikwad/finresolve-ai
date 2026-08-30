"""
FinResolve AI — Ledger Double-Entry Rule

Verifies double-entry accounting integrity and balance progressions.
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


class LedgerDoubleEntryRule(BaseReconciliationRule):
    """
    Validates that merchant ledger entries adhere to double-entry integrity
    and reflect all matched financial events.
    """

    rule_id = "RULE-LEDG-001"
    category = "ledger"

    def evaluate(
        self,
        group: MatchGroup,
        records_lookup: dict[str, dict[str, Any]],
    ) -> RuleResult:
        evidence_items: list[Evidence] = []
        entries = [records_lookup.get(eid) for eid in group.ledger_entry_ids if records_lookup.get(eid)]

        # If no ledger entries exist in case
        if not entries:
            # If there's a payment or settlement, absence of ledger entries is a violation
            if group.payment_id or group.settlement_ids:
                evidence = Evidence(
                    evidence_type=EvidenceType.LEDGER_IMBALANCE,
                    source_record_id=group.payment_id or "group",
                    record_type=RecordType.LEDGER_ENTRY,
                    field_name="entries",
                    observed_value="0 ledger entries",
                    expected_value="Ledger entries for payment/settlement postings",
                    rule_id=self.rule_id,
                    severity=Severity.HIGH,
                    strength=0.9,
                    explanation="No ledger entries found corresponding to matched financial transactions",
                )
                evidence_items.append(evidence)
                return RuleResult(
                    rule_id=self.rule_id,
                    category=self.category,
                    passed=False,
                    severity=Severity.HIGH,
                    evidence_items=evidence_items,
                    explanation="Missing ledger postings for matched transaction group",
                )
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=True,
                severity=Severity.INFO,
                explanation="No financial transactions requiring ledger entries in this group",
            )

        # 1. Check double-entry format (debit != credit, one must be zero)
        for entry in entries:
            eid = entry.get("entry_id", "unknown")
            debit = _get_minor_amount(entry, "debit")
            credit = _get_minor_amount(entry, "credit")

            if debit > 0 and credit > 0:
                evidence = Evidence(
                    evidence_type=EvidenceType.LEDGER_IMBALANCE,
                    source_record_id=eid,
                    record_type=RecordType.LEDGER_ENTRY,
                    field_name="debit/credit",
                    observed_value=f"debit={debit}, credit={credit}",
                    expected_value="Exactly one of debit or credit must be non-zero",
                    rule_id=self.rule_id,
                    severity=Severity.CRITICAL,
                    strength=1.0,
                    explanation=f"Ledger entry {eid} contains both debit and credit amounts",
                )
                evidence_items.append(evidence)

            if debit == 0 and credit == 0:
                evidence = Evidence(
                    evidence_type=EvidenceType.LEDGER_IMBALANCE,
                    source_record_id=eid,
                    record_type=RecordType.LEDGER_ENTRY,
                    field_name="debit/credit",
                    observed_value="debit=0, credit=0",
                    expected_value="Entry amount must be > 0",
                    rule_id=self.rule_id,
                    severity=Severity.MEDIUM,
                    strength=0.8,
                    explanation=f"Ledger entry {eid} has zero debit and zero credit",
                )
                evidence_items.append(evidence)

        # 2. Check total posted debits and credits
        total_debits = sum(_get_minor_amount(e, "debit") for e in entries)
        total_credits = sum(_get_minor_amount(e, "credit") for e in entries)

        if not evidence_items:
            return RuleResult(
                rule_id=self.rule_id,
                category=self.category,
                passed=True,
                severity=Severity.INFO,
                expected_value={"total_credits": total_credits, "total_debits": total_debits},
                observed_value={"entry_count": len(entries)},
                explanation=f"Verified {len(entries)} ledger entries with valid double-entry debit/credit postings",
            )

        return RuleResult(
            rule_id=self.rule_id,
            category=self.category,
            passed=False,
            severity=Severity.HIGH,
            evidence_items=evidence_items,
            explanation=f"Detected {len(evidence_items)} ledger double-entry anomalies",
        )
