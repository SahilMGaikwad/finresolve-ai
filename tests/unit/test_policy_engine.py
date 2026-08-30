"""
FinResolve AI — Deterministic Policy Engine Unit Tests

Tests policy rules POL-001 through POL-005, value limit gating, risk tiers, and approval workflows.
"""

import pytest

from data.schemas.enums import RecordType
from data.schemas.resolution import (
    FinancialDelta,
    PolicyDecisionType,
    ResolutionAction,
    ResolutionActionType,
    RiskLevel,
    SimulationResult,
)
from services.counterfactual.approval import ApprovalStatus, ApprovalWorkflowManager
from services.policy_engine.engine import DeterministicPolicyEngine
from services.security.auth import AuthenticatedUser, Role


class TestPolicyEngineDecisions:
    """Tests deterministic policy evaluation."""

    def test_auto_resolvable_when_enabled(self):
        engine = DeterministicPolicyEngine(max_auto_resolve_amount_minor=500_000, auto_resolve_enabled=True)
        action = ResolutionAction(
            action_type=ResolutionActionType.FEE_ADJUSTMENT,
            target_record_id="fee_01",
            target_record_type=RecordType.FEE,
            parameters={"adjusted_amount_minor": 1000},
            justification="Low risk fee adjustment",
        )
        sim = SimulationResult(
            is_valid=True,
            monetary_balance_verified=True,
            ledger_balance_verified=True,
            temporal_consistency_verified=True,
            status_consistency_verified=True,
            relationship_integrity_verified=True,
            residual_discrepancies=[],
            financial_delta=FinancialDelta(merchant_balance_delta_minor=1000, fee_balance_delta_minor=-1000),
            explanation="Valid simulation",
        )

        decision = engine.evaluate_proposal(action, sim, sim.financial_delta, evidence_refs=["ev_1", "ev_2"])
        assert decision.decision == PolicyDecisionType.AUTO_RESOLVABLE
        assert decision.approval_requirement == "NONE"

    def test_human_review_when_auto_disabled(self):
        engine = DeterministicPolicyEngine(max_auto_resolve_amount_minor=500_000, auto_resolve_enabled=False)
        action = ResolutionAction(
            action_type=ResolutionActionType.SETTLEMENT_ADJUSTMENT,
            target_record_id="stl_01",
            target_record_type=RecordType.SETTLEMENT,
            parameters={"adjusted_net_amount_minor": 50000},
            justification="Settlement net adjustment",
        )
        sim = SimulationResult(
            is_valid=True,
            monetary_balance_verified=True,
            ledger_balance_verified=True,
            temporal_consistency_verified=True,
            status_consistency_verified=True,
            relationship_integrity_verified=True,
            residual_discrepancies=[],
            financial_delta=FinancialDelta(merchant_balance_delta_minor=5000),
            explanation="Valid simulation",
        )

        decision = engine.evaluate_proposal(action, sim, sim.financial_delta, evidence_refs=["ev_1", "ev_2"])
        assert decision.decision == PolicyDecisionType.HUMAN_REVIEW
        assert decision.approval_requirement == "SINGLE_APPROVER"

    def test_blocked_when_simulation_fails(self):
        engine = DeterministicPolicyEngine()
        action = ResolutionAction(
            action_type=ResolutionActionType.SETTLEMENT_ADJUSTMENT,
            target_record_id="stl_01",
            target_record_type=RecordType.SETTLEMENT,
            parameters={},
            justification="Failed action",
        )
        sim = SimulationResult(
            is_valid=False,
            monetary_balance_verified=False,
            ledger_balance_verified=True,
            temporal_consistency_verified=True,
            status_consistency_verified=True,
            relationship_integrity_verified=True,
            residual_discrepancies=["settlement_amount_mismatch"],
            financial_delta=FinancialDelta(),
            explanation="Simulation failed",
        )

        decision = engine.evaluate_proposal(action, sim, sim.financial_delta, evidence_refs=["ev_1"])
        assert decision.decision == PolicyDecisionType.BLOCKED
        assert len(decision.blocking_reasons) > 0


class TestApprovalWorkflow:
    """Tests separation of duties in approval workflow."""

    def test_separation_of_duties_enforced(self):
        workflow = ApprovalWorkflowManager()
        proposer = AuthenticatedUser(user_id="analyst_01", username="analyst", role=Role.ANALYST)
        approver = AuthenticatedUser(user_id="approver_01", username="approver", role=Role.APPROVER)

        # Propose
        rec = workflow.submit_for_review("prop_100", proposer)
        assert rec.status == ApprovalStatus.PENDING

        # Proposer CANNOT approve own proposal
        with pytest.raises(PermissionError, match="Separation of duties"):
            workflow.approve_proposal("prop_100", proposer)

        # Authorized approver approves
        approved_rec = workflow.approve_proposal("prop_100", approver, comments="Looks accurate")
        assert approved_rec.status == ApprovalStatus.APPROVED
        assert approved_rec.approver_id == "approver_01"
