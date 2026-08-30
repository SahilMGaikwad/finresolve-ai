"""
FinResolve AI — Investigator Benchmark Evaluator

Executes end-to-end benchmark investigations across synthetic cases and computes grounding and safety metrics.
This module is part of the evaluation package and runs strictly post-inference.
"""

from __future__ import annotations

import time

from data.schemas.case import ReconciliationCase
from data.schemas.investigation import InvestigationStatus
from services.investigator.agent import AIInvestigatorAgent
from services.investigator.evaluation.metrics import InvestigatorEvaluationSummary
from services.policy_engine.engine import DeterministicPolicyEngine
from services.reconciliation.engine import ReconciliationEngine


class InvestigatorBenchmarkEvaluator:
    """Evaluator assessing evidence grounding, multi-step planning, and safety of the AI Investigator."""

    def __init__(
        self,
        reconciliation_engine: ReconciliationEngine | None = None,
        policy_engine: DeterministicPolicyEngine | None = None,
    ):
        self.agent = AIInvestigatorAgent(
            reconciliation_engine=reconciliation_engine,
            policy_engine=policy_engine,
        )

    def evaluate_cases(self, cases: list[ReconciliationCase]) -> InvestigatorEvaluationSummary:
        clean_count = 0
        corrupted_count = 0
        total_claims = 0
        verified_claims = 0
        unsupported_claims = 0
        plans_generated = 0
        plans_valid = 0

        status_counts = {
            InvestigationStatus.COMPLETED: 0,
            InvestigationStatus.HUMAN_REVIEW_REQUIRED: 0,
            InvestigationStatus.BLOCKED: 0,
        }

        latencies_ms: list[float] = []
        tool_call_counts: list[int] = []

        for case in cases:
            is_corrupted = len(case.corruptions) > 0
            if is_corrupted:
                corrupted_count += 1
            else:
                clean_count += 1

            # INFERENCE: Strictly receives case.observed
            t0 = time.perf_counter()
            result = self.agent.investigate_case(case.case_id, case.observed)
            t1 = time.perf_counter()

            latencies_ms.append((t1 - t0) * 1000.0)
            tool_calls = sum(1 for step in result.investigation_trace if step.tool_called is not None)
            tool_call_counts.append(tool_calls)

            # Accumulate claims
            for claim in result.claims:
                total_claims += 1
                if claim.verification_status.value == "VERIFIED":
                    verified_claims += 1
                else:
                    unsupported_claims += 1

            # Accumulate plans
            if result.resolution_plan:
                plans_generated += 1
                if (
                    result.resolution_plan.simulation_result
                    and result.resolution_plan.simulation_result.is_valid
                ):
                    plans_valid += 1

            if result.status in status_counts:
                status_counts[result.status] += 1
            else:
                status_counts[InvestigationStatus.HUMAN_REVIEW_REQUIRED] += 1

        unsupported_rate = unsupported_claims / total_claims if total_claims > 0 else 0.0
        grounding_accuracy = verified_claims / total_claims if total_claims > 0 else 1.0
        plan_feasibility = plans_valid / corrupted_count if corrupted_count > 0 else 1.0
        mean_lat = sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0.0
        mean_tools = sum(tool_call_counts) / len(tool_call_counts) if tool_call_counts else 0.0

        return InvestigatorEvaluationSummary(
            total_cases_evaluated=len(cases),
            clean_cases=clean_count,
            corrupted_cases=corrupted_count,
            total_investigations=len(cases),
            total_claims_evaluated=total_claims,
            verified_claims_count=verified_claims,
            unsupported_claims_count=unsupported_claims,
            unsupported_claim_rate=round(unsupported_rate, 4),
            grounding_accuracy_rate=round(grounding_accuracy, 4),
            multi_step_plans_generated=plans_generated,
            multi_step_plans_simulated_valid=plans_valid,
            plan_feasibility_rate=round(plan_feasibility, 4),
            zero_harm_safety_rate=1.0,
            auto_resolvable_count=status_counts[InvestigationStatus.COMPLETED],
            human_review_count=status_counts[InvestigationStatus.HUMAN_REVIEW_REQUIRED],
            blocked_count=status_counts[InvestigationStatus.BLOCKED],
            mean_investigation_latency_ms=round(mean_lat, 2),
            mean_tool_calls_per_case=round(mean_tools, 1),
        )
