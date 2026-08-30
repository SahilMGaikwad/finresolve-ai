"""
FinResolve AI — Multi-Step Planner Unit Tests

Tests composite sequential resolution planning and multi-step counterfactual simulation.
"""

import pytest

from data.schemas.case import CaseRecords
from data.schemas.enums import RecordType
from data.schemas.resolution import ResolutionAction, ResolutionActionType
from services.investigator.planner import MultiStepResolutionPlanner
from services.investigator.tools import MultiStepSimulationTool
from services.reconciliation.engine import ReconciliationEngine


class TestMultiStepPlanner:
    """Tests generation and simulation of multi-step resolution plans."""

    def test_multi_step_simulation_success(self):
        payment = {
            "record_type": "payment",
            "payment_id": "pay_plan_01",
            "merchant_id": "m_plan_01",
            "amount": {"amount_minor": 100000, "currency": "INR"},
            "status": "captured",
            "captured_at": "2026-03-15T10:00:00+00:00",
        }
        settlement = {
            "record_type": "settlement",
            "settlement_id": "stl_plan_01",
            "payment_id": "pay_plan_01",
            "merchant_id": "m_plan_01",
            "gross_amount": {"amount_minor": 100000, "currency": "INR"},
            "fee_amount": {"amount_minor": 2000, "currency": "INR"},
            "net_amount": {"amount_minor": 80000, "currency": "INR"},  # Mismatch (should be 98000)
            "status": "processed",
            "settled_at": "2026-03-16T10:00:00+00:00",
        }
        fee = {
            "record_type": "fee",
            "fee_id": "fee_plan_01",
            "payment_id": "pay_plan_01",
            "settlement_id": "stl_plan_01",
            "fee_type": "platform_fee",
            "amount": {"amount_minor": 2000, "currency": "INR"},
            "rate_bps": 200,
            "applied_at": "2026-03-15T10:00:00+00:00",
        }
        records = CaseRecords(payments=[payment], settlements=[settlement], fees=[fee])

        recon = ReconciliationEngine()
        res = recon.reconcile_records("CASE-PLAN-01", records)

        planner = MultiStepResolutionPlanner()
        plan = planner.generate_plan("CASE-PLAN-01", records, res)

        assert plan is not None
        assert len(plan.steps) >= 1

        tool = MultiStepSimulationTool("CASE-PLAN-01", records, recon)
        sim_result = tool.execute(plan)

        assert sim_result.is_valid is True
        assert len(sim_result.residual_discrepancies) == 0
        assert sim_result.cumulative_delta.merchant_balance_delta_minor == 18000
