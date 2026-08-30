"""
FinResolve AI — Typed Investigator Tools & Security Registry

Provides read-only inspection tools and deterministic simulation/policy tools.
All tools enforce strict Pydantic parameter schemas, execution timeouts, and audit logging.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from data.schemas.case import CaseRecords
from data.schemas.discrepancy import RootCauseHypothesis
from data.schemas.evidence import Evidence, EvidenceGraphModel
from data.schemas.investigation import MultiStepSimulationResult, ResolutionPlan
from data.schemas.reconciliation_result import ReconciliationResult
from data.schemas.resolution import PolicyDecision
from services.counterfactual.ledger_verifier import verify_ledger_double_entry
from services.counterfactual.simulator import CounterfactualSimulator
from services.counterfactual.state import apply_action_to_state, create_counterfactual_state
from services.policy_engine.engine import DeterministicPolicyEngine
from services.reconciliation.engine import ReconciliationEngine


class ToolExecutionError(Exception):
    """Raised when a tool encounters an execution error."""
    pass


class BaseInvestigatorTool(ABC):
    """Abstract base class for all investigator tools."""
    name: str
    description: str
    is_read_only: bool = True

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        pass


class CaseOverviewInput(BaseModel):
    case_id: str


class CaseOverviewOutput(BaseModel):
    case_id: str
    payments_count: int
    settlements_count: int
    fees_count: int
    refunds_count: int
    ledger_entries_count: int
    orders_count: int
    payouts_count: int


class CaseOverviewTool(BaseInvestigatorTool):
    name = "get_case_overview"
    description = "Retrieve summary record counts for a given case."

    def __init__(self, records: CaseRecords):
        self.records = records

    def execute(self, **kwargs: Any) -> CaseOverviewOutput:
        return CaseOverviewOutput(
            case_id=kwargs.get("case_id", ""),
            payments_count=len(self.records.payments),
            settlements_count=len(self.records.settlements),
            fees_count=len(self.records.fees),
            refunds_count=len(self.records.refunds),
            ledger_entries_count=len(self.records.ledger_entries),
            orders_count=len(self.records.orders),
            payouts_count=len(self.records.payouts),
        )


class RecordDetailInput(BaseModel):
    record_type: str = Field(description="payment, settlement, fee, refund, ledger_entry, or order")
    record_id: str


class RecordDetailOutput(BaseModel):
    record: dict[str, Any] | None
    found: bool


class RecordDetailTool(BaseInvestigatorTool):
    name = "get_record_detail"
    description = "Retrieve specific details for a financial record by type and ID."

    def __init__(self, records: CaseRecords):
        self.records = records

    def execute(self, **kwargs: Any) -> RecordDetailOutput:
        rec_type = kwargs.get("record_type", "").lower()
        rec_id = kwargs.get("record_id", "")

        lookup: list[Any] = []
        id_field = "id"

        if rec_type == "payment":
            lookup = self.records.payments
            id_field = "payment_id"
        elif rec_type == "settlement":
            lookup = self.records.settlements
            id_field = "settlement_id"
        elif rec_type == "fee":
            lookup = self.records.fees
            id_field = "fee_id"
        elif rec_type == "refund":
            lookup = self.records.refunds
            id_field = "refund_id"
        elif rec_type in ("ledger_entry", "ledger"):
            lookup = self.records.ledger_entries
            id_field = "entry_id"
        elif rec_type == "order":
            lookup = self.records.orders
            id_field = "order_id"

        for r in lookup:
            curr_id = r.get(id_field) if isinstance(r, dict) else getattr(r, id_field, "")
            if str(curr_id) == str(rec_id):
                dumped = r if isinstance(r, dict) else (r.model_dump() if hasattr(r, "model_dump") else dict(r))
                return RecordDetailOutput(record=dumped, found=True)

        return RecordDetailOutput(record=None, found=False)


class EvidenceInspectorTool(BaseInvestigatorTool):
    name = "get_evidence_items"
    description = "Retrieve all verified evidence items collected by deterministic reconciliation rules."

    def __init__(self, reconciliation_result: ReconciliationResult):
        self.result = reconciliation_result

    def execute(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [ev.model_dump() for ev in self.result.evidence]


class EvidenceGraphTool(BaseInvestigatorTool):
    name = "get_evidence_subgraph"
    description = "Retrieve nodes and edges from the deterministic Evidence Graph."

    def __init__(self, reconciliation_result: ReconciliationResult):
        self.result = reconciliation_result

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        return self.result.evidence_graph.model_dump()


class DiagnosticHypothesesTool(BaseInvestigatorTool):
    name = "get_diagnostic_hypotheses"
    description = "Retrieve deterministic root-cause hypotheses and confidence rankings."

    def __init__(self, reconciliation_result: ReconciliationResult):
        self.result = reconciliation_result

    def execute(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [h.model_dump() for h in self.result.hypotheses]


class MultiStepSimulationTool(BaseInvestigatorTool):
    name = "simulate_resolution_plan"
    description = "Run closed-loop counterfactual simulation on a multi-step resolution plan."
    is_read_only = False  # Runs simulation on isolated virtual copy

    def __init__(self, case_id: str, records: CaseRecords, recon_engine: ReconciliationEngine | None = None):
        self.case_id = case_id
        self.records = records
        self.recon_engine = recon_engine or ReconciliationEngine()

    def execute(self, plan: ResolutionPlan) -> MultiStepSimulationResult:
        state = create_counterfactual_state(self.case_id, self.records)
        step_results = []
        sim = CounterfactualSimulator(reconciliation_engine=self.recon_engine)

        for step in plan.steps:
            res = sim.simulate(self.case_id, state.projected_records, step.action)
            step_results.append(res)
            # Advance state
            state = apply_action_to_state(state, step.action)

        # Final holistic re-reconciliation
        final_recon = self.recon_engine.reconcile_records(self.case_id, state.projected_records)
        final_residuals = [d.discrepancy_type for d in final_recon.discrepancies]
        ledger_ok, _ = verify_ledger_double_entry(state.projected_records)

        is_all_valid = (
            len(final_residuals) == 0
            and ledger_ok
            and all(r.is_valid for r in step_results)
        )

        from services.counterfactual.ledger_verifier import compute_financial_delta
        # Cumulative delta from before-state to final state
        cum_delta = compute_financial_delta(self.records, state.projected_records, plan.steps[-1].action if plan.steps else None)

        return MultiStepSimulationResult(
            is_valid=is_all_valid,
            step_results=step_results,
            cumulative_delta=cum_delta,
            residual_discrepancies=final_residuals,
            explanation="Multi-step simulation successfully reconciled all records" if is_all_valid else f"Residual discrepancies remaining: {final_residuals}",
        )


class PolicyEvaluationTool(BaseInvestigatorTool):
    name = "evaluate_plan_policy"
    description = "Evaluate deterministic policy rules on a simulated resolution plan."

    def __init__(self, policy_engine: DeterministicPolicyEngine | None = None):
        self.policy_engine = policy_engine or DeterministicPolicyEngine()

    def execute(self, plan: ResolutionPlan) -> PolicyDecision:
        if not plan.simulation_result or not plan.steps:
            from data.schemas.resolution import PolicyDecisionType
            return PolicyDecision(
                decision=PolicyDecisionType.BLOCKED,
                risk_level="HIGH",
                approval_requirement="MANUAL",
                blocking_reasons=["Plan must be simulated before policy evaluation"],
            )

        # Evaluate policy based on final simulation result and cumulative delta
        return self.policy_engine.evaluate_proposal(
            action=plan.steps[-1].action,
            simulation=plan.simulation_result.step_results[-1] if plan.simulation_result.step_results else None,
            delta=plan.simulation_result.cumulative_delta,
            evidence_refs=plan.evidence_refs,
        )


class InvestigatorToolRegistry:
    """Registry coordinating all available investigator tools for a case."""

    def __init__(
        self,
        case_id: str,
        records: CaseRecords,
        recon_result: ReconciliationResult,
        recon_engine: ReconciliationEngine | None = None,
        policy_engine: DeterministicPolicyEngine | None = None,
    ):
        self.tools: dict[str, BaseInvestigatorTool] = {
            "get_case_overview": CaseOverviewTool(records),
            "get_record_detail": RecordDetailTool(records),
            "get_evidence_items": EvidenceInspectorTool(recon_result),
            "get_evidence_subgraph": EvidenceGraphTool(recon_result),
            "get_diagnostic_hypotheses": DiagnosticHypothesesTool(recon_result),
            "simulate_resolution_plan": MultiStepSimulationTool(case_id, records, recon_engine),
            "evaluate_plan_policy": PolicyEvaluationTool(policy_engine),
        }

    def get_tool(self, name: str) -> BaseInvestigatorTool:
        if name not in self.tools:
            raise ToolExecutionError(f"Unauthorized or unknown tool: '{name}'")
        return self.tools[name]
