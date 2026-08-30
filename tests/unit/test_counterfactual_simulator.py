"""
FinResolve AI — Counterfactual Simulator Unit Tests

Tests state cloning isolation, action mutation, and closed-loop simulation verification.
"""

import pytest

from data.schemas.case import CaseRecords
from data.schemas.enums import RecordType
from data.schemas.resolution import ResolutionAction, ResolutionActionType
from services.counterfactual.simulator import CounterfactualSimulator
from services.counterfactual.state import apply_action_to_state, create_counterfactual_state


class TestCounterfactualStateIsolation:
    """Tests that counterfactual state mutation does not affect source records."""

    def test_state_deep_clone_isolation(self):
        source_payment = {
            "record_type": "payment",
            "payment_id": "pay_test_01",
            "amount": {"amount_minor": 100000, "currency": "INR"},
            "status": "captured",
        }
        records = CaseRecords(payments=[source_payment])

        state = create_counterfactual_state("CASE-TEST-001", records)
        action = ResolutionAction(
            action_type=ResolutionActionType.STATUS_CORRECTION,
            target_record_id="pay_test_01",
            target_record_type=RecordType.PAYMENT,
            parameters={"corrected_status": "refunded"},
            justification="Test state mutation",
        )

        projected = apply_action_to_state(state, action)

        # Source record status remains untouched!
        assert records.payments[0]["status"] == "captured"
        # Projected record status is modified!
        assert projected.projected_records.payments[0]["status"] == "refunded"
        assert "pay_test_01" in projected.mutated_record_ids


class TestClosedLoopSimulation:
    """Tests closed-loop simulation on discrepancy cases."""

    def test_settlement_adjustment_simulation(self):
        payment = {
            "record_type": "payment",
            "payment_id": "pay_sim_01",
            "merchant_id": "m_01",
            "amount": {"amount_minor": 100000, "currency": "INR"},
            "status": "captured",
            "captured_at": "2026-03-15T10:00:00+00:00",
        }
        settlement = {
            "record_type": "settlement",
            "settlement_id": "stl_sim_01",
            "payment_id": "pay_sim_01",
            "merchant_id": "m_01",
            "gross_amount": {"amount_minor": 100000, "currency": "INR"},
            "fee_amount": {"amount_minor": 2000, "currency": "INR"},
            "net_amount": {"amount_minor": 80000, "currency": "INR"},  # Mismatch (should be 98000)
            "status": "processed",
            "settled_at": "2026-03-16T10:00:00+00:00",
        }
        fee = {
            "record_type": "fee",
            "fee_id": "fee_sim_01",
            "payment_id": "pay_sim_01",
            "settlement_id": "stl_sim_01",
            "fee_type": "platform_fee",
            "amount": {"amount_minor": 2000, "currency": "INR"},
            "rate_bps": 200,
            "applied_at": "2026-03-15T10:00:00+00:00",
        }
        records = CaseRecords(payments=[payment], settlements=[settlement], fees=[fee])

        action = ResolutionAction(
            action_type=ResolutionActionType.SETTLEMENT_ADJUSTMENT,
            target_record_id="stl_sim_01",
            target_record_type=RecordType.SETTLEMENT,
            parameters={
                "adjusted_gross_amount_minor": 100000,
                "adjusted_fee_amount_minor": 2000,
                "adjusted_net_amount_minor": 98000,
            },
            justification="Correct net amount to 98,000 paise",
        )

        simulator = CounterfactualSimulator()
        result = simulator.simulate("CASE-SIM-001", records, action)

        assert result.is_valid is True
        assert result.monetary_balance_verified is True
        assert len(result.residual_discrepancies) == 0
        assert result.financial_delta.merchant_balance_delta_minor == 18000
