"""
FinResolve AI — Adversarial Counterfactual Tests

Tests resilience against invalid simulations, missing evidence,
unauthorized approvals, and invalid ledger mutations.
"""

import pytest
from fastapi.testclient import TestClient

from apps.api.config import Settings
from apps.api.main import create_app
from data.schemas.enums import RecordType
from data.schemas.resolution import (
    FinancialDelta,
    PolicyDecisionType,
    ResolutionAction,
    ResolutionActionType,
    SimulationResult,
)
from data.schemas.case import CaseRecords
from services.counterfactual.approval import ApprovalWorkflowManager
from services.counterfactual.ledger_verifier import verify_ledger_double_entry
from services.policy_engine.engine import DeterministicPolicyEngine
from services.security.auth import AuthenticatedUser, Role


@pytest.fixture
def client():
    settings = Settings(app_env="test", debug=False)
    app = create_app(settings)
    return TestClient(app)


class TestAdversarialCounterfactual:
    """Adversarial security and invariant tests for counterfactual engine."""

    def test_missing_evidence_results_in_no_safe_action(self):
        engine = DeterministicPolicyEngine()
        action = ResolutionAction(
            action_type=ResolutionActionType.FEE_ADJUSTMENT,
            target_record_id="fee_99",
            target_record_type=RecordType.FEE,
            parameters={"adjusted_amount_minor": 100},
            justification="Unbacked action",
        )
        sim = SimulationResult(
            is_valid=True,
            monetary_balance_verified=True,
            ledger_balance_verified=True,
            temporal_consistency_verified=True,
            status_consistency_verified=True,
            relationship_integrity_verified=True,
            residual_discrepancies=[],
            financial_delta=FinancialDelta(),
            explanation="Technically valid math",
        )

        # Empty evidence refs MUST trigger NO_SAFE_ACTION
        decision = engine.evaluate_proposal(action, sim, sim.financial_delta, evidence_refs=[])
        assert decision.decision == PolicyDecisionType.NO_SAFE_ACTION

    def test_invalid_ledger_double_entry_fails_verification(self):
        # Malicious record with both debit and credit
        invalid_entry = {
            "record_type": "ledger_entry",
            "entry_id": "le_bad_01",
            "debit": {"amount_minor": 5000, "currency": "INR"},
            "credit": {"amount_minor": 5000, "currency": "INR"},
        }
        records = CaseRecords(ledger_entries=[invalid_entry])
        ok, err = verify_ledger_double_entry(records)
        assert ok is False
        assert "cannot have both" in err

    def test_viewer_role_cannot_approve_resolution(self):
        workflow = ApprovalWorkflowManager()
        proposer = AuthenticatedUser(user_id="u_analyst", username="analyst", role=Role.ANALYST)
        viewer = AuthenticatedUser(user_id="u_viewer", username="viewer", role=Role.VIEWER)

        workflow.submit_for_review("prop_200", proposer)

        with pytest.raises(PermissionError, match="not authorized to approve"):
            workflow.approve_proposal("prop_200", viewer)

    def test_api_propose_endpoint_rejects_sql_injection_case_id(self, client):
        res = client.post(
            "/cases/CASE-01'; DROP TABLE cases; --/propose-resolutions",
            json={"payments": []},
        )
        assert res.status_code in (400, 422, 500)
