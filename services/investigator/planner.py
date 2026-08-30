"""
FinResolve AI — Multi-Step Resolution Planner

Constructs composite, sequential resolution plans for compound financial discrepancies.
Combines multiple candidate actions (e.g. reference correction -> fee adjustment -> settlement adjustment).
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from data.schemas.case import CaseRecords
from data.schemas.investigation import PlanStep, ResolutionPlan
from data.schemas.reconciliation_result import ReconciliationResult
from services.counterfactual.generator import CandidateActionGenerator


class MultiStepResolutionPlanner:
    """
    Synthesizes atomic candidate actions into coherent, multi-step resolution plans.
    """

    def __init__(self):
        self.generator = CandidateActionGenerator()

    def generate_plan(
        self,
        case_id: str,
        records: CaseRecords,
        recon_result: ReconciliationResult,
    ) -> ResolutionPlan | None:
        """
        Generate a multi-step resolution plan ordered logically:
        1. Reference & Identity Corrections
        2. Fee & Tax Recalculations
        3. Missing Record Reconstructions / Split Tranches
        4. Settlement Balance Adjustments
        5. Duplicate Compensations
        """
        candidate_actions = self.generator.generate_candidate_actions(
            case_id=case_id,
            records=records,
            discrepancies=recon_result.discrepancies,
            hypotheses=recon_result.hypotheses,
        )
        if not candidate_actions:
            return None

        # Sort actions into dependency execution order
        action_priority = {
            "reference_correction": 1,
            "status_correction": 2,
            "fee_adjustment": 3,
            "missing_record_recon": 4,
            "settlement_adjustment": 5,
            "ledger_correction": 6,
        }

        sorted_actions = sorted(
            candidate_actions,
            key=lambda a: action_priority.get(a.action_type.value, 99),
        )

        steps: list[PlanStep] = []
        evidence_refs: set[str] = set()

        for idx, action in enumerate(sorted_actions, start=1):
            step = PlanStep(
                step_number=idx,
                action=action,
                rationale=action.justification,
                expected_intermediate_effect=f"Apply {action.action_type.value} on record {action.target_record_id}",
            )
            steps.append(step)

        # Collect evidence references from reconciliation result
        for ev in recon_result.evidence:
            evidence_refs.add(str(ev.evidence_id))

        strategy_desc = (
            f"Sequential resolution plan containing {len(steps)} steps: "
            + " -> ".join(s.action.action_type.value for s in steps)
        )

        return ResolutionPlan(
            plan_id=f"plan_{uuid4().hex[:10]}",
            case_id=case_id,
            steps=steps,
            overall_strategy=strategy_desc,
            evidence_refs=list(evidence_refs),
        )
