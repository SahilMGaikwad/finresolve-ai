"""
FinResolve AI — AI Financial Investigator Agent

Coordinates the full investigation lifecycle:
Tool execution -> Multi-step planning -> Closed-loop simulation -> Policy gating -> Claim validation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from data.schemas.case import CaseRecords
from data.schemas.investigation import (
    HumanReviewPackage,
    InvestigationResult,
    InvestigationStatus,
)
from data.schemas.resolution import PolicyDecisionType
from services.investigator.fallback import DeterministicInvestigatorFallback
from services.investigator.planner import MultiStepResolutionPlanner
from services.investigator.provider import LLMProvider, MockDeterministicLLMProvider
from services.investigator.state_machine import InvestigationStateMachine
from services.investigator.tools import InvestigatorToolRegistry
from services.investigator.validator import ClaimValidator
from services.policy_engine.engine import DeterministicPolicyEngine
from services.reconciliation.engine import ReconciliationEngine

logger = logging.getLogger("finresolve.investigator")


class AIInvestigatorAgent:
    """
    Evidence-grounded AI Financial Investigator Agent.
    """

    def __init__(
        self,
        reconciliation_engine: ReconciliationEngine | None = None,
        policy_engine: DeterministicPolicyEngine | None = None,
        llm_provider: LLMProvider | None = None,
    ):
        self.recon_engine = reconciliation_engine or ReconciliationEngine()
        self.policy_engine = policy_engine or DeterministicPolicyEngine()
        self.llm_provider = llm_provider or MockDeterministicLLMProvider()
        self.planner = MultiStepResolutionPlanner()
        self.fallback = DeterministicInvestigatorFallback()

    def investigate_case(
        self,
        case_id: str,
        records: CaseRecords,
        enable_fallback: bool = True,
    ) -> InvestigationResult:
        """
        Execute full evidence-grounded investigation of a case.
        """
        sm = InvestigationStateMachine(case_id=case_id)
        investigation_id = f"inv_{uuid4().hex[:12]}"

        try:
            # 1. State: CREATED -> INVESTIGATING
            sm.transition_to(InvestigationStatus.INVESTIGATING, "Initiating case inspection and reconciliation")

            # 2. Run deterministic reconciliation (Evidence collection)
            recon_result = self.recon_engine.reconcile_records(case_id, records)
            tool_registry = InvestigatorToolRegistry(
                case_id=case_id,
                records=records,
                recon_result=recon_result,
                recon_engine=self.recon_engine,
                policy_engine=self.policy_engine,
            )

            # Record evidence tool calls in trace
            sm.record_tool_call("get_case_overview")
            overview = tool_registry.get_tool("get_case_overview").execute(case_id=case_id)

            sm.record_tool_call("get_evidence_items")
            evidence_items = tool_registry.get_tool("get_evidence_items").execute()

            sm.transition_to(
                InvestigationStatus.EVIDENCE_COLLECTED,
                f"Collected {len(evidence_items)} verified evidence items",
                tool_called="get_evidence_items",
                tool_output_summary=f"Found {len(evidence_items)} items across {overview.payments_count} payments",
            )

            # 3. State: EVIDENCE_COLLECTED -> DIAGNOSIS_SYNTHESIZED
            sm.record_tool_call("get_diagnostic_hypotheses")
            hypotheses = tool_registry.get_tool("get_diagnostic_hypotheses").execute()

            sm.transition_to(
                InvestigationStatus.DIAGNOSIS_SYNTHESIZED,
                f"Synthesized {len(hypotheses)} root-cause hypotheses",
                tool_called="get_diagnostic_hypotheses",
                tool_output_summary=f"Primary cause: {hypotheses[0]['cause_type'] if hypotheses else 'None'}",
            )

            # 4. Multi-Step Resolution Planning & Simulation
            plan = None
            if recon_result.discrepancies:
                sm.transition_to(InvestigationStatus.PLANNING, "Generating composite multi-step resolution plan")
                plan = self.planner.generate_plan(case_id, records, recon_result)

                if plan and plan.steps:
                    # Run simulation
                    sm.transition_to(InvestigationStatus.SIMULATING, f"Simulating {len(plan.steps)}-step resolution plan")
                    sm.record_tool_call("simulate_resolution_plan")
                    sim_result = tool_registry.get_tool("simulate_resolution_plan").execute(plan)
                    plan.simulation_result = sim_result
                    plan.financial_delta = sim_result.cumulative_delta

                    # Evaluate policy
                    sm.transition_to(InvestigationStatus.POLICY_REVIEW, "Evaluating deterministic policy gating on plan")
                    sm.record_tool_call("evaluate_plan_policy")
                    policy_decision = tool_registry.get_tool("evaluate_plan_policy").execute(plan)
                    plan.policy_decision = policy_decision
                else:
                    sm.transition_to(InvestigationStatus.CLAIM_VALIDATION, "No safe action candidates; proceeding to claim validation")
            else:
                sm.transition_to(InvestigationStatus.CLAIM_VALIDATION, "No discrepancies; proceeding to claim validation")

            # 5. LLM Synthesis & Claim Validation
            if isinstance(self.llm_provider, MockDeterministicLLMProvider):
                synthesis = self.llm_provider.synthesize_investigation(case_id, records, recon_result)
            else:
                # Fallback to structured generation
                synthesis = self.fallback.synthesize(case_id, records, recon_result, plan)

            # Validate Claims
            validator = ClaimValidator(records, recon_result)
            validated_claims, unsupported_count = validator.validate_all(synthesis.claims)

            # Determine Final Status
            if plan and plan.policy_decision:
                if plan.policy_decision.decision == PolicyDecisionType.AUTO_RESOLVABLE and unsupported_count == 0:
                    final_status = InvestigationStatus.COMPLETED
                elif plan.policy_decision.decision == PolicyDecisionType.BLOCKED:
                    final_status = InvestigationStatus.BLOCKED
                else:
                    final_status = InvestigationStatus.HUMAN_REVIEW_REQUIRED
            elif recon_result.discrepancies:
                final_status = InvestigationStatus.HUMAN_REVIEW_REQUIRED
            else:
                final_status = InvestigationStatus.COMPLETED

            # Build Human Review Package if not completed
            human_pkg = None
            if final_status in (InvestigationStatus.HUMAN_REVIEW_REQUIRED, InvestigationStatus.BLOCKED):
                human_pkg = HumanReviewPackage(
                    case_id=case_id,
                    discrepancies_summary=[d.discrepancy_type for d in recon_result.discrepancies],
                    verified_evidence_summary=[f"Evidence {ev.evidence_id}: {ev.explanation}" for ev in recon_result.evidence[:5]],
                    failed_simulations_summary=[plan.simulation_result.explanation] if plan and plan.simulation_result and not plan.simulation_result.is_valid else [],
                    key_ambiguities=[h.description for h in recon_result.hypotheses[1:]],
                    recommended_analyst_actions=[
                        "Inspect underlying merchant processing contract",
                        "Verify bank settlement UTR reference",
                        "Authorize human resolution review",
                    ],
                    priority="HIGH" if len(recon_result.discrepancies) > 1 else "MEDIUM",
                )

            sm.transition_to(final_status, f"Investigation concluded with status {final_status.value}")

            return InvestigationResult(
                investigation_id=investigation_id,
                case_id=case_id,
                status=final_status,
                summary=synthesis.summary,
                symptoms_identified=synthesis.symptoms,
                root_cause_explanation=synthesis.root_cause_explanation,
                supporting_evidence_ids=[str(ev.evidence_id) for ev in recon_result.evidence],
                claims=validated_claims,
                unsupported_claims_count=unsupported_count,
                resolution_plan=plan,
                human_review_package=human_pkg,
                investigation_trace=sm.trace,
                created_at=datetime.now(timezone.utc),
            )

        except Exception as exc:
            logger.error("Investigation failed for case %s: %s", case_id, exc, exc_info=True)
            if enable_fallback:
                logger.info("Engaging deterministic fallback for case %s", case_id)
                recon_res = self.recon_engine.reconcile_records(case_id, records)
                return self.fallback.synthesize(case_id, records, recon_res, reason=str(exc))
            raise
