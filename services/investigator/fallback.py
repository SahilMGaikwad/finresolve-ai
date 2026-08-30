"""
FinResolve AI — Deterministic Investigator Fallback

Provides pure deterministic synthesis when an LLM provider is offline, unavailable, or encounters an error.
Ensures FinResolve AI never has a single point of failure in AI models.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from data.schemas.case import CaseRecords
from data.schemas.investigation import (
    HumanReviewPackage,
    InvestigationResult,
    InvestigationStatus,
    ResolutionPlan,
)
from data.schemas.reconciliation_result import ReconciliationResult


class DeterministicInvestigatorFallback:
    """
    Synthesizes rule-based investigation findings directly from Phase 3 diagnostic outputs.
    """

    def synthesize(
        self,
        case_id: str,
        records: CaseRecords,
        recon_result: ReconciliationResult,
        plan: ResolutionPlan | None = None,
        reason: str = "Fallback mode: Deterministic engine",
    ) -> InvestigationResult:
        symptoms = [d.discrepancy_type for d in recon_result.discrepancies]

        summary = (
            f"Deterministic investigation for case {case_id}. "
            f"Reconciliation concluded with status {recon_result.status.value.upper()}. "
            f"Total discrepancies: {len(symptoms)}."
        )

        explanation = (
            f"Diagnosed {len(recon_result.hypotheses)} root-cause hypotheses based on deterministic rules. "
            + (recon_result.hypotheses[0].description if recon_result.hypotheses else "No discrepancies detected.")
        )

        evidence_ids = [str(ev.evidence_id) for ev in recon_result.evidence]

        # Determine human review package if needed
        human_pkg = None
        status = InvestigationStatus.COMPLETED

        if recon_result.discrepancies or (plan and plan.policy_decision and plan.policy_decision.decision.value != "AUTO_RESOLVABLE"):
            status = InvestigationStatus.HUMAN_REVIEW_REQUIRED
            human_pkg = HumanReviewPackage(
                case_id=case_id,
                discrepancies_summary=symptoms,
                verified_evidence_summary=[f"Evidence {ev.evidence_id}: {ev.explanation}" for ev in recon_result.evidence[:5]],
                failed_simulations_summary=[plan.simulation_result.explanation] if plan and plan.simulation_result and not plan.simulation_result.is_valid else [],
                key_ambiguities=[h.description for h in recon_result.hypotheses[1:]],
                recommended_analyst_actions=[
                    "Verify original merchant settlement contract",
                    "Inspect banking UTR ledger confirmation",
                    "Review multi-entity cross-references",
                ],
                priority="HIGH" if len(symptoms) > 1 else "MEDIUM",
            )

        return InvestigationResult(
            investigation_id=f"inv_{uuid4().hex[:12]}",
            case_id=case_id,
            status=status,
            summary=summary,
            symptoms_identified=symptoms,
            root_cause_explanation=explanation,
            supporting_evidence_ids=evidence_ids,
            claims=[],
            unsupported_claims_count=0,
            resolution_plan=plan,
            human_review_package=human_pkg,
            investigation_trace=[],
            created_at=datetime.now(timezone.utc),
        )
