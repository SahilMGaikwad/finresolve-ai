"""
FinResolve AI — Deterministic Policy Engine

Evaluates simulation results and proposed actions against safety invariants,
monetary limits, risk classifications, and evidence requirements.
Determines whether an action is AUTO_RESOLVABLE, requires HUMAN_REVIEW, is BLOCKED, or NO_SAFE_ACTION.
"""

from __future__ import annotations

from typing import Any

from data.schemas.resolution import (
    FinancialDelta,
    PolicyDecision,
    PolicyDecisionType,
    PolicyRuleEvaluation,
    ResolutionAction,
    ResolutionActionType,
    RiskLevel,
    SimulationResult,
)
from services.policy_engine.rules import (
    EvidenceSufficiencyRule,
    MasterAutoResolveSwitchRule,
    MonetaryThresholdRule,
    PolicyRule,
    RiskClassificationRule,
    SimulationValidityRule,
)


class DeterministicPolicyEngine:
    """
    Evaluates resolution actions using strict, explainable deterministic policy rules.
    """

    def __init__(
        self,
        max_auto_resolve_amount_minor: int = 500_000,  # 500,000 paise = ₹5,000
        auto_resolve_enabled: bool = False,            # Default to human review safe mode
    ):
        self.max_auto_amount_minor = max_auto_resolve_amount_minor
        self.auto_resolve_enabled = auto_resolve_enabled
        self.rules: list[PolicyRule] = [
            SimulationValidityRule(),
            EvidenceSufficiencyRule(),
            MonetaryThresholdRule(),
            RiskClassificationRule(),
            MasterAutoResolveSwitchRule(),
        ]

    def classify_risk(
        self,
        action: ResolutionAction,
        simulation: SimulationResult,
        delta: FinancialDelta,
        evidence_refs: list[str],
    ) -> tuple[RiskLevel, list[str]]:
        """Compute deterministic risk tier and factors."""
        factors: list[str] = []
        abs_value = delta.absolute_adjustment_value_minor

        # Value thresholds (paise)
        if abs_value > 5_000_000:  # > ₹50,000
            factors.append(f"High monetary adjustment value: {abs_value} paise")
        elif abs_value > 500_000:  # > ₹5,000
            factors.append(f"Moderate monetary adjustment value: {abs_value} paise")

        # Action type risk
        if action.action_type == ResolutionActionType.LEDGER_CORRECTION:
            factors.append("Direct ledger compensating entry")
        elif action.action_type == ResolutionActionType.MISSING_RECORD_RECONSTRUCTION:
            factors.append("Synthetic record reconstruction")

        # Evidence strength
        if len(evidence_refs) < 2:
            factors.append("Single evidence point grounding")

        # Determine level
        if any("High monetary" in f or "Direct ledger" in f for f in factors):
            return RiskLevel.HIGH, factors
        elif any("Moderate monetary" in f or "Synthetic record" in f for f in factors):
            return RiskLevel.MEDIUM, factors
        return RiskLevel.LOW, factors

    def evaluate_proposal(
        self,
        action: ResolutionAction,
        simulation: SimulationResult,
        delta: FinancialDelta,
        evidence_refs: list[str],
    ) -> PolicyDecision:
        """
        Evaluate all policy rules on a simulated resolution proposal.
        """
        risk_level, risk_factors = self.classify_risk(action, simulation, delta, evidence_refs)

        evaluations: list[PolicyRuleEvaluation] = []
        for rule in self.rules:
            res = rule.evaluate(
                action=action,
                simulation=simulation,
                delta=delta,
                risk=risk_level,
                evidence_refs=evidence_refs,
                max_auto_amount_minor=self.max_auto_amount_minor,
                auto_resolve_enabled=self.auto_resolve_enabled,
            )
            evaluations.append(res)

        eval_map = {e.rule_id: e for e in evaluations}
        blocking_reasons: list[str] = []

        # 1. Critical Hard Blockers
        if not eval_map["POL-001"].passed:
            blocking_reasons.append("Simulation failed to clear discrepancies or maintain financial invariants")
            return PolicyDecision(
                decision=PolicyDecisionType.BLOCKED,
                risk_level=risk_level,
                risk_factors=risk_factors,
                rule_evaluations=evaluations,
                blocking_reasons=blocking_reasons,
                approval_requirement="SINGLE_APPROVER",
            )

        if not eval_map["POL-002"].passed:
            blocking_reasons.append("No supporting diagnostic evidence provided")
            return PolicyDecision(
                decision=PolicyDecisionType.NO_SAFE_ACTION,
                risk_level=risk_level,
                risk_factors=risk_factors,
                rule_evaluations=evaluations,
                blocking_reasons=blocking_reasons,
                approval_requirement="SINGLE_APPROVER",
            )

        # 2. Check if Auto-Resolvable conditions are met
        is_auto_eligible = (
            eval_map["POL-001"].passed
            and eval_map["POL-002"].passed
            and eval_map["POL-003"].passed
            and eval_map["POL-004"].passed
            and eval_map["POL-005"].passed
        )

        if is_auto_eligible:
            return PolicyDecision(
                decision=PolicyDecisionType.AUTO_RESOLVABLE,
                risk_level=risk_level,
                risk_factors=risk_factors,
                rule_evaluations=evaluations,
                blocking_reasons=[],
                approval_requirement="NONE",
            )

        # 3. Otherwise, Valid Proposal Routed to Human Review
        approval_req = "DUAL_APPROVER" if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL) else "SINGLE_APPROVER"
        return PolicyDecision(
            decision=PolicyDecisionType.HUMAN_REVIEW,
            risk_level=risk_level,
            risk_factors=risk_factors,
            rule_evaluations=evaluations,
            blocking_reasons=[],
            approval_requirement=approval_req,
        )
