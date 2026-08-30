"""
FinResolve AI — Diagnosis Engine Unit Tests

Tests mechanical root-cause hypothesis generation and candidate ranking.
"""

from data.schemas.evidence import Evidence, EvidenceType, Severity
from data.schemas.matching import MatchGroup
from services.diagnosis.diagnoser import DeterministicDiagnoser
from services.reconciliation.rules.base import RuleResult


def test_diagnose_amount_mismatch():
    diagnoser = DeterministicDiagnoser()
    group = MatchGroup(payment_id="pay_1", settlement_ids=["stl_1"])
    rule_res = RuleResult(
        rule_id="RULE-AMT-001",
        category="amount",
        passed=False,
        severity=Severity.HIGH,
        difference={"difference_minor": -5000, "currency": "INR"},
        explanation="Amount mismatch",
    )
    records_lookup = {
        "pay_1": {"payment_id": "pay_1", "amount": {"amount_minor": 100000}},
        "stl_1": {"settlement_id": "stl_1", "gross_amount": {"amount_minor": 100000}, "net_amount": {"amount_minor": 95000}},
    }

    discrepancies = diagnoser.diagnose_case(
        case_id="CASE-001",
        groups=[group],
        unmatched_records={},
        rule_results=[rule_res],
        evidence_list=[],
        records_lookup=records_lookup,
    )

    assert len(discrepancies) == 1
    d = discrepancies[0]
    assert d.discrepancy_type == "settlement_amount_mismatch"
    assert len(d.candidate_hypotheses) >= 1
    assert d.candidate_hypotheses[0].is_primary is True
    assert d.candidate_hypotheses[0].cause_type == "incorrect_settlement_calculation"


def test_diagnose_broken_reference():
    diagnoser = DeterministicDiagnoser()
    records_lookup = {
        "stl_invalid": {"settlement_id": "stl_invalid", "payment_id": "pay_non_existent"},
    }

    discrepancies = diagnoser.diagnose_case(
        case_id="CASE-002",
        groups=[],
        unmatched_records={"settlements": ["stl_invalid"]},
        rule_results=[],
        evidence_list=[],
        records_lookup=records_lookup,
    )

    assert len(discrepancies) == 1
    d = discrepancies[0]
    assert d.discrepancy_type == "broken_reference"
    assert d.candidate_hypotheses[0].cause_type == "reference_id_error"
