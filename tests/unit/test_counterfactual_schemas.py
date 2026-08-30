"""
FinResolve AI — Counterfactual Schemas Unit Tests

Tests ResolutionAction, CounterfactualState, FinancialDelta,
SimulationResult, PolicyDecision, and ResolutionProposal models.
"""

import pytest

from data.schemas.case import CaseRecords
from data.schemas.enums import Currency, RecordType
from data.schemas.money import Money
from data.schemas.resolution import (
    CounterfactualState,
    FinancialDelta,
    PolicyDecision,
    PolicyDecisionType,
    PolicyRuleEvaluation,
    ResolutionAction,
    ResolutionActionType,
    ResolutionProposal,
    RiskLevel,
    SimulationResult,
)


class TestFinancialDelta:
    """Tests FinancialDelta minor-unit arithmetic and conservation laws."""

    def test_balanced_financial_delta(self):
        delta = FinancialDelta(
            merchant_balance_delta_minor=10000,
            fee_balance_delta_minor=-8000,
            tax_balance_delta_minor=-2000,
            customer_balance_delta_minor=0,
            currency=Currency.INR,
        )
        assert delta.net_system_delta_minor == 0
        assert delta.is_balanced is True
        assert delta.absolute_adjustment_value_minor == 10000

    def test_imbalanced_financial_delta(self):
        delta = FinancialDelta(
            merchant_balance_delta_minor=5000,
            fee_balance_delta_minor=0,
            tax_balance_delta_minor=0,
            customer_balance_delta_minor=0,
            currency=Currency.INR,
        )
        assert delta.net_system_delta_minor == 5000
        assert delta.is_balanced is False


class TestResolutionSchemas:
    """Tests ResolutionAction and SimulationResult serialization."""

    def test_resolution_action_instantiation(self):
        action = ResolutionAction(
            action_type=ResolutionActionType.FEE_ADJUSTMENT,
            target_record_id="fee_123",
            target_record_type=RecordType.FEE,
            parameters={"adjusted_amount_minor": 2000},
            justification="Fee recalculation to match schedule",
        )
        assert action.action_type == ResolutionActionType.FEE_ADJUSTMENT
        assert action.target_record_id == "fee_123"

    def test_simulation_result_model(self):
        delta = FinancialDelta(merchant_balance_delta_minor=0, fee_balance_delta_minor=0)
        sim = SimulationResult(
            is_valid=True,
            monetary_balance_verified=True,
            ledger_balance_verified=True,
            temporal_consistency_verified=True,
            status_consistency_verified=True,
            relationship_integrity_verified=True,
            residual_discrepancies=[],
            financial_delta=delta,
            explanation="Simulation passed all checks",
        )
        assert sim.is_valid is True
        assert len(sim.residual_discrepancies) == 0
