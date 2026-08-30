"""
FinResolve AI — Deterministic Policy Rules

Defines explicit, deterministic rules evaluated on simulated resolution proposals.
No LLM or heuristic involvement: every rule produces explainable pass/fail decisions.
"""

from __future__ import annotations

from typing import Any

from data.schemas.resolution import (
    FinancialDelta,
    PolicyRuleEvaluation,
    ResolutionAction,
    ResolutionActionType,
    RiskLevel,
    SimulationResult,
)


class PolicyRule:
    """Base class for deterministic policy rules."""
    rule_id: str
    rule_name: str
    description: str

    def evaluate(
        self,
        action: ResolutionAction,
        simulation: SimulationResult,
        delta: FinancialDelta,
        risk: RiskLevel,
        evidence_refs: list[str],
        max_auto_amount_minor: int,
        auto_resolve_enabled: bool,
    ) -> PolicyRuleEvaluation:
        raise NotImplementedError


class SimulationValidityRule(PolicyRule):
    """POL-001: Verifies that the counterfactual simulation succeeded with 0 residual errors."""
    rule_id = "POL-001"
    rule_name = "SimulationValidity"
    description = "Action must successfully pass closed-loop reconciliation simulation."

    def evaluate(
        self,
        action: ResolutionAction,
        simulation: SimulationResult,
        delta: FinancialDelta,
        risk: RiskLevel,
        evidence_refs: list[str],
        max_auto_amount_minor: int,
        auto_resolve_enabled: bool,
    ) -> PolicyRuleEvaluation:
        passed = simulation.is_valid and len(simulation.residual_discrepancies) == 0
        return PolicyRuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=passed,
            observed_value={"is_valid": simulation.is_valid, "residuals": simulation.residual_discrepancies},
            threshold_value={"is_valid": True, "residuals": 0},
            reason="Simulation succeeded with zero residual errors" if passed else "Simulation failed or left residual errors",
        )


class EvidenceSufficiencyRule(PolicyRule):
    r"""POL-002: Verifies that the action is grounded in $\ge 1$ supporting evidence item."""
    rule_id = "POL-002"
    rule_name = "EvidenceSufficiency"
    description = "Proposal must cite verifiable evidence items."

    def evaluate(
        self,
        action: ResolutionAction,
        simulation: SimulationResult,
        delta: FinancialDelta,
        risk: RiskLevel,
        evidence_refs: list[str],
        max_auto_amount_minor: int,
        auto_resolve_enabled: bool,
    ) -> PolicyRuleEvaluation:
        passed = len(evidence_refs) > 0
        return PolicyRuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=passed,
            observed_value=len(evidence_refs),
            threshold_value=">= 1 evidence ref",
            reason=f"Action backed by {len(evidence_refs)} evidence item(s)" if passed else "No supporting evidence provided",
        )


class MonetaryThresholdRule(PolicyRule):
    """POL-003: Verifies whether the transaction adjustment value is within auto-resolve threshold."""
    rule_id = "POL-003"
    rule_name = "MonetaryThreshold"
    description = "Autonomous actions must not exceed configured value threshold (paise)."

    def evaluate(
        self,
        action: ResolutionAction,
        simulation: SimulationResult,
        delta: FinancialDelta,
        risk: RiskLevel,
        evidence_refs: list[str],
        max_auto_amount_minor: int,
        auto_resolve_enabled: bool,
    ) -> PolicyRuleEvaluation:
        abs_value = delta.absolute_adjustment_value_minor
        passed = abs_value <= max_auto_amount_minor
        return PolicyRuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=passed,
            observed_value=abs_value,
            threshold_value=max_auto_amount_minor,
            reason=(
                f"Adjustment value ({abs_value} paise) within auto threshold ({max_auto_amount_minor} paise)"
                if passed else
                f"Adjustment value ({abs_value} paise) exceeds auto threshold ({max_auto_amount_minor} paise) -> requires human review"
            ),
        )


class RiskClassificationRule(PolicyRule):
    """POL-004: Evaluates risk tier and blocks high-risk unvetted modifications."""
    rule_id = "POL-004"
    rule_name = "RiskClassification"
    description = "High or Critical risk proposals require human financial analyst review."

    def evaluate(
        self,
        action: ResolutionAction,
        simulation: SimulationResult,
        delta: FinancialDelta,
        risk: RiskLevel,
        evidence_refs: list[str],
        max_auto_amount_minor: int,
        auto_resolve_enabled: bool,
    ) -> PolicyRuleEvaluation:
        is_low_risk = risk in (RiskLevel.LOW, RiskLevel.MEDIUM)
        return PolicyRuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=is_low_risk,
            observed_value=risk.value,
            threshold_value="LOW or MEDIUM",
            reason=f"Risk classified as {risk.value}",
        )


class MasterAutoResolveSwitchRule(PolicyRule):
    """POL-005: Enforces the master safety configuration flag."""
    rule_id = "POL-005"
    rule_name = "MasterAutoResolveSwitch"
    description = "Auto-resolution must be explicitly enabled in configuration."

    def evaluate(
        self,
        action: ResolutionAction,
        simulation: SimulationResult,
        delta: FinancialDelta,
        risk: RiskLevel,
        evidence_refs: list[str],
        max_auto_amount_minor: int,
        auto_resolve_enabled: bool,
    ) -> PolicyRuleEvaluation:
        return PolicyRuleEvaluation(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=auto_resolve_enabled,
            observed_value=auto_resolve_enabled,
            threshold_value=True,
            reason="Auto-resolve master switch is enabled" if auto_resolve_enabled else "Auto-resolve master switch is disabled (default safe mode)",
        )
