"""
FinResolve AI — Resolution Orchestrator

End-to-end orchestration:
ReconciliationResult → Candidate Generation → Counterfactual Simulation → Policy Evaluation → ResolutionProposal
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from data.schemas.case import CaseRecords
from data.schemas.reconciliation_result import ReconciliationResult
from data.schemas.resolution import ResolutionProposal
from services.audit.logger import global_audit_logger
from services.counterfactual.generator import CandidateActionGenerator
from services.counterfactual.ledger_verifier import _get_amount_minor
from services.counterfactual.simulator import CounterfactualSimulator
from services.policy_engine.engine import DeterministicPolicyEngine


class ResolutionOrchestrator:
    """
    Orchestrates candidate resolution generation, simulation, and policy evaluation.
    """

    def __init__(
        self,
        candidate_generator: CandidateActionGenerator | None = None,
        simulator: CounterfactualSimulator | None = None,
        policy_engine: DeterministicPolicyEngine | None = None,
    ):
        self.generator = candidate_generator or CandidateActionGenerator()
        self.simulator = simulator or CounterfactualSimulator()
        self.policy_engine = policy_engine or DeterministicPolicyEngine()

    def generate_proposals(
        self,
        case_id: str,
        observed_records: CaseRecords,
        reconciliation_result: ReconciliationResult,
    ) -> list[ResolutionProposal]:
        """
        Generate, simulate, and evaluate resolution proposals for all discrepancies in a case.
        """
        proposals: list[ResolutionProposal] = []

        if not reconciliation_result.discrepancies:
            return proposals

        # 1. Generate candidate actions
        candidate_actions = self.generator.generate_candidate_actions(
            case_id=case_id,
            records=observed_records,
            discrepancies=reconciliation_result.discrepancies,
        )

        for action in candidate_actions:
            # Map evidence references
            evidence_refs = [
                str(d.evidence_ids[0]) for d in reconciliation_result.discrepancies if d.evidence_ids
            ] if reconciliation_result.discrepancies else []

            # 2. Run closed-loop counterfactual simulation
            sim_result = self.simulator.simulate(
                case_id=case_id,
                observed_records=observed_records,
                action=action,
                evidence_refs=evidence_refs,
            )

            # 3. Evaluate deterministic policy rules
            policy_decision = self.policy_engine.evaluate_proposal(
                action=action,
                simulation=sim_result,
                delta=sim_result.financial_delta,
                evidence_refs=evidence_refs,
            )

            # 4. Generate deterministic idempotency key
            key_raw = f"{case_id}:{action.action_type.value}:{action.target_record_id}:{json.dumps(action.parameters, sort_keys=True)}"
            idempotency_key = hashlib.sha256(key_raw.encode("utf-8")).hexdigest()

            # 5. Extract state snapshots
            before_snapshot = {
                "payments_count": len(observed_records.payments),
                "settlements_count": len(observed_records.settlements),
                "fees_count": len(observed_records.fees),
                "settlement_net_total": sum(_get_amount_minor(s, "net_amount") for s in observed_records.settlements),
            }

            proposal = ResolutionProposal(
                case_id=case_id,
                discrepancy_id=str(reconciliation_result.discrepancies[0].discrepancy_id),
                action=action,
                affected_records=[action.target_record_id],
                before_state=before_snapshot,
                proposed_change=action.parameters,
                projected_state={"is_simulated_valid": sim_result.is_valid},
                financial_delta=sim_result.financial_delta,
                evidence_refs=evidence_refs,
                simulation_result=sim_result,
                policy_decision=policy_decision,
                idempotency_key=idempotency_key,
                audit_reference=f"sim_{idempotency_key[:10]}",
            )

            proposals.append(proposal)

            # 6. Audit log event
            global_audit_logger.record_event(
                actor="system",
                actor_role="SERVICE",
                operation="PROPOSAL_GENERATED",
                result="SUCCESS" if sim_result.is_valid else "FAILURE",
                case_id=case_id,
                reason=f"Generated proposal {proposal.proposal_id} with decision {policy_decision.decision.value}",
                evidence_refs=evidence_refs,
                policy_decision={"decision": policy_decision.decision.value, "risk": policy_decision.risk_level.value},
            )

        return proposals
