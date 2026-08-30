"""
FinResolve AI — Deterministic Reconciliation Engine

The primary orchestrator that coordinates matching, rule execution, evidence collection,
graph building, and diagnosis without an LLM or access to ground truth.
"""

from __future__ import annotations

import logging
from typing import Any

from data.schemas.case import CaseRecords, ReconciliationCase
from data.schemas.discrepancy import Discrepancy, RootCauseHypothesis
from data.schemas.enums import RecordType
from data.schemas.matching import MatchGroup, MatchState
from data.schemas.reconciliation_result import (
    ReconciliationResult,
    ReconciliationStatus,
)
from services.diagnosis.diagnoser import DeterministicDiagnoser
from services.evidence.collector import EvidenceCollector
from services.evidence.graph import EvidenceGraphBuilder
from services.matching.matcher import MatcherConfig, RecordMatcher
from services.reconciliation.rules import (
    AmountReconciliationRule,
    FeeAnalysisRule,
    LedgerDoubleEntryRule,
    RuleResult,
    StatusConsistencyRule,
    TemporalConsistencyRule,
)
from services.reconciliation.trace import TraceRecorder

logger = logging.getLogger("finresolve.reconciliation.engine")


class ReconciliationEngine:
    """
    Deterministic Financial Reconciliation Engine.
    Operates strictly on observed records.
    """

    def __init__(self, matcher_config: MatcherConfig | None = None):
        self.matcher = RecordMatcher(matcher_config)
        self.rules = [
            AmountReconciliationRule(),
            FeeAnalysisRule(),
            TemporalConsistencyRule(),
            StatusConsistencyRule(),
            LedgerDoubleEntryRule(),
        ]
        self.diagnoser = DeterministicDiagnoser()
        self.graph_builder = EvidenceGraphBuilder()

    def reconcile_case(self, case: ReconciliationCase) -> ReconciliationResult:
        """
        Reconcile a case by evaluating only its observed records.

        IMPORTANT: This method strictly accesses case.observed and case.case_id.
        It NEVER touches case.ground_truth or case.corruptions.
        """
        return self.reconcile_records(case_id=case.case_id, records=case.observed)

    def reconcile_records(
        self,
        case_id: str,
        records: CaseRecords,
    ) -> ReconciliationResult:
        """
        Core reconciliation pipeline executing across observed records.
        """
        trace = TraceRecorder()

        # Step 1: Build local records lookup
        records_lookup: dict[str, dict[str, Any]] = {
            "_all_payments": list(records.payments),
            "_all_orders": list(records.orders),
            "_all_settlements": list(records.settlements),
            "_all_fees": list(records.fees),
            "_all_refunds": list(records.refunds),
            "_all_ledger_entries": list(records.ledger_entries),
            "_all_payouts": list(records.payouts),
        }
        for p in records.payments:
            if p.get("payment_id"):
                records_lookup[p["payment_id"]] = p
        for o in records.orders:
            if o.get("order_id"):
                records_lookup[o["order_id"]] = o
        for s in records.settlements:
            if s.get("settlement_id"):
                records_lookup[s["settlement_id"]] = s
        for f in records.fees:
            if f.get("fee_id"):
                records_lookup[f["fee_id"]] = f
        for r in records.refunds:
            if r.get("refund_id"):
                records_lookup[r["refund_id"]] = r
        for le in records.ledger_entries:
            if le.get("entry_id"):
                records_lookup[le["entry_id"]] = le
        for po in records.payouts:
            if po.get("payout_id"):
                records_lookup[po["payout_id"]] = po

        trace.record_step(
            phase="ingestion",
            description=f"Loaded {len(records_lookup)} observed records into reconciliation working memory",
            inputs={"record_counts": {
                "payments": len(records.payments),
                "orders": len(records.orders),
                "settlements": len(records.settlements),
                "fees": len(records.fees),
                "refunds": len(records.refunds),
                "ledger_entries": len(records.ledger_entries),
            }},
            outcome="Ready for record matching",
        )

        # Step 2: Execute Multi-Signal Matching
        groups, unmatched = self.matcher.match_records(records)

        trace.record_step(
            phase="matching",
            description="Formed match groups using explainable multi-signal scoring",
            inputs={"group_count": len(groups), "unmatched_counts": {k: len(v) for k, v in unmatched.items()}},
            outcome=f"Formed {len(groups)} match groups with state: {[g.match_state.value for g in groups]}",
        )

        # Step 3: Evaluate Reconciliation Rules
        rule_results: list[RuleResult] = []
        for group in groups:
            for rule in self.rules:
                res = rule.evaluate(group, records_lookup)
                rule_results.append(res)
                
                trace.record_step(
                    phase=rule.category,
                    description=f"Evaluated {rule.rule_id} ({rule.category}) on payment {group.payment_id}",
                    inputs={"payment_id": group.payment_id, "settlement_ids": group.settlement_ids},
                    calculation=str(res.difference) if res.difference else None,
                    outcome="PASSED" if res.passed else f"FAILED: {res.explanation}",
                )

        # Step 4: Collect Evidence
        collector = EvidenceCollector()
        evidence_list = collector.collect_from_rule_results(rule_results)

        trace.record_step(
            phase="evidence_collection",
            description=f"Aggregated {len(evidence_list)} structured evidence items from rule failures",
            outcome=f"Collected {len(evidence_list)} evidence observations",
        )

        # Step 5: Build Evidence Graph
        evidence_graph = self.graph_builder.build_graph(records, groups, evidence_list)

        trace.record_step(
            phase="graph_construction",
            description=f"Built Evidence Graph with {len(evidence_graph.nodes)} nodes and {len(evidence_graph.edges)} edges",
            outcome="Graph structure generated",
        )

        # Step 6: Diagnose Root-Causes
        discrepancies = self.diagnoser.diagnose_case(
            case_id=case_id,
            groups=groups,
            unmatched_records=unmatched,
            rule_results=rule_results,
            evidence_list=evidence_list,
            records_lookup=records_lookup,
        )

        all_hypotheses: list[RootCauseHypothesis] = []
        for d in discrepancies:
            all_hypotheses.extend(d.candidate_hypotheses)

        trace.record_step(
            phase="diagnosis",
            description=f"Derived {len(discrepancies)} discrepancies and {len(all_hypotheses)} root-cause hypotheses",
            outcome=f"Discrepancies: {[d.discrepancy_type for d in discrepancies]}",
        )

        # Step 7: Determine Final Status and Confidence
        status = ReconciliationStatus.RECONCILED
        matching_conf = 1.0
        diagnostic_conf = 1.0

        if groups:
            matching_conf = min(g.confidence for g in groups)

        if any(g.match_state == MatchState.AMBIGUOUS for g in groups):
            status = ReconciliationStatus.INSUFFICIENT_EVIDENCE
            diagnostic_conf = 0.5
        elif any(g.match_state == MatchState.CONFLICT for g in groups):
            status = ReconciliationStatus.UNRESOLVED
            diagnostic_conf = 0.6
        elif discrepancies:
            status = ReconciliationStatus.DISCREPANCY
            diagnostic_conf = max((h.plausibility_score for h in all_hypotheses), default=0.85)
        else:
            status = ReconciliationStatus.RECONCILED
            diagnostic_conf = 1.0

        trace.record_step(
            phase="conclusion",
            description=f"Reconciliation concluded with status {status.value.upper()}",
            outcome=f"Status: {status.value}, Matching Confidence: {matching_conf:.2f}, Diagnostic Confidence: {diagnostic_conf:.2f}",
        )

        return ReconciliationResult(
            case_id=case_id,
            status=status,
            matched_groups=groups,
            unmatched_records=unmatched,
            discrepancies=discrepancies,
            evidence=evidence_list,
            evidence_graph=evidence_graph,
            hypotheses=all_hypotheses,
            trace=trace.get_trace(),
            matching_confidence=round(matching_conf, 4),
            diagnostic_confidence=round(diagnostic_conf, 4),
        )
