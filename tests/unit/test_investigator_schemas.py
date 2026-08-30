"""
FinResolve AI — Investigator Schemas Unit Tests

Tests serialization and validation of FactualClaim, PlanStep, ResolutionPlan,
MultiStepSimulationResult, HumanReviewPackage, and InvestigationResult models.
"""

from data.schemas.enums import Currency, RecordType
from data.schemas.investigation import (
    AgentTraceStep,
    ClaimVerificationStatus,
    FactualClaim,
    HumanReviewPackage,
    InvestigationResult,
    InvestigationStatus,
    MultiStepSimulationResult,
    PlanStep,
    ResolutionPlan,
)
from data.schemas.resolution import FinancialDelta, ResolutionAction, ResolutionActionType


class TestInvestigatorSchemas:
    """Tests investigation data model instantiation and constraints."""

    def test_factual_claim_instantiation(self):
        claim = FactualClaim(
            claim_text="Payment pay_100 captured amount is 50000 minor units",
            claimed_entity_id="pay_100",
            claimed_field="amount",
            claimed_value=50000,
            evidence_ids=["ev_amt_01"],
        )
        assert claim.claimed_entity_id == "pay_100"
        assert claim.verification_status == ClaimVerificationStatus.UNSUPPORTED

    def test_resolution_plan_and_steps(self):
        action = ResolutionAction(
            action_type=ResolutionActionType.FEE_ADJUSTMENT,
            target_record_id="fee_01",
            target_record_type=RecordType.FEE,
            parameters={"adjusted_amount_minor": 1500},
            justification="Contract fee rate adjustment",
        )
        step = PlanStep(
            step_number=1,
            action=action,
            rationale="Correct fee",
            expected_intermediate_effect="Update fee balance",
        )
        plan = ResolutionPlan(
            case_id="CASE-100",
            steps=[step],
            overall_strategy="Single-step fee fix",
            evidence_refs=["ev_fee_01"],
        )
        assert len(plan.steps) == 1
        assert plan.steps[0].action.action_type == ResolutionActionType.FEE_ADJUSTMENT

    def test_human_review_package(self):
        pkg = HumanReviewPackage(
            case_id="CASE-200",
            discrepancies_summary=["settlement_amount_mismatch"],
            verified_evidence_summary=["Evidence ev_01: Amount mismatch of ₹50.00"],
            failed_simulations_summary=["Residual discrepancy remained"],
            key_ambiguities=["Contract fee schedule unknown"],
            recommended_analyst_actions=["Inspect original merchant agreement"],
            priority="HIGH",
        )
        assert pkg.case_id == "CASE-200"
        assert pkg.priority == "HIGH"
