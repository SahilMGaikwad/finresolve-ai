"""
FinResolve AI — Resolution, Simulation, and Policy Schemas

Data models for counterfactual simulation, financial delta accounting,
candidate resolution actions, policy decisions, and resolution proposals.
All monetary calculations operate in exact integer minor units (paise).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from data.schemas.case import CaseRecords
from data.schemas.enums import RecordType
from data.schemas.money import Currency
from data.schemas.reconciliation_result import TraceStep


class ResolutionActionType(str, Enum):
    """Types of counterfactual corrective actions."""
    FEE_ADJUSTMENT = "fee_adjustment"                       # Recalculate or refund incorrect fee
    SETTLEMENT_ADJUSTMENT = "settlement_adjustment"         # Adjust settlement net or post split completion
    REFUND_CORRECTION = "refund_correction"                 # Correct refund amount or status
    MISSING_RECORD_RECONSTRUCTION = "missing_record_recon"  # Propose synthetic entry for missing record
    REFERENCE_CORRECTION = "reference_correction"           # Fix broken foreign reference
    STATUS_CORRECTION = "status_correction"                 # Synchronize contradictory status states
    LEDGER_CORRECTION = "ledger_correction"                 # Post compensating double-entry ledger entry


class ResolutionAction(BaseModel):
    """A specific proposed corrective action to be simulated."""
    action_type: ResolutionActionType
    target_record_id: str
    target_record_type: RecordType
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific parameters (e.g. adjusted_amount_minor, corrected_reference_id)",
    )
    justification: str = Field(description="Explanation of why this action is hypothesized to resolve the discrepancy")

    model_config = {"from_attributes": True}


class FinancialDelta(BaseModel):
    """
    Exact integer minor unit movements across all stakeholder balance accounts.
    Enforces the fundamental zero-sum conservation law:
    merchant_delta + fee_delta + tax_delta + customer_delta == 0
    """
    merchant_balance_delta_minor: int = 0   # Change to merchant account balance (paise)
    fee_balance_delta_minor: int = 0        # Change to platform fee account (paise)
    tax_balance_delta_minor: int = 0        # Change to GST tax liability account (paise)
    customer_balance_delta_minor: int = 0   # Change to customer account / refund (paise)
    currency: Currency = Currency.INR

    @property
    def net_system_delta_minor(self) -> int:
        """Conservation law check: Net system funds must sum to 0 in a closed financial system."""
        return (
            self.merchant_balance_delta_minor
            + self.fee_balance_delta_minor
            + self.tax_balance_delta_minor
            + self.customer_balance_delta_minor
        )

    @property
    def is_balanced(self) -> bool:
        """Returns True if the delta conserves total monetary balance."""
        return self.net_system_delta_minor == 0

    @property
    def absolute_adjustment_value_minor(self) -> int:
        """Returns the maximum absolute balance movement across stakeholders."""
        return max(
            abs(self.merchant_balance_delta_minor),
            abs(self.fee_balance_delta_minor),
            abs(self.tax_balance_delta_minor),
            abs(self.customer_balance_delta_minor),
        )


class CounterfactualState(BaseModel):
    """
    An isolated, in-memory deep clone of observed records representing the projected state.
    Ensures zero in-place mutation of the source records.
    """
    case_id: str
    projected_records: CaseRecords
    mutated_record_ids: list[str] = Field(default_factory=list)
    reconstructed_record_ids: list[str] = Field(default_factory=list)
    virtual_ledger_entries: list[dict[str, Any]] = Field(default_factory=list)


class SimulationResult(BaseModel):
    """
    The output of running closed-loop deterministic reconciliation on a CounterfactualState.
    """
    simulation_id: str = Field(default_factory=lambda: f"sim_{uuid4().hex[:12]}")
    is_valid: bool = Field(description="True if projected state resolves discrepancy with zero residual errors")
    monetary_balance_verified: bool = Field(description="True if all amounts balance exactly in minor units")
    ledger_balance_verified: bool = Field(description="True if double-entry debit/credit consistency is maintained")
    temporal_consistency_verified: bool = Field(description="True if lifecycle sequence is valid")
    status_consistency_verified: bool = Field(description="True if cross-entity statuses are harmonious")
    relationship_integrity_verified: bool = Field(description="True if all foreign references resolve")
    residual_discrepancies: list[str] = Field(
        default_factory=list,
        description="Any remaining or newly introduced discrepancy types",
    )
    financial_delta: FinancialDelta
    trace: list[TraceStep] = Field(default_factory=list)
    explanation: str

    model_config = {"from_attributes": True}


class RiskLevel(str, Enum):
    """Risk severity classification for proposed resolutions."""
    LOW = "LOW"             # Standard low-value fee/reference adjustment (<= ₹5,000, high confidence)
    MEDIUM = "MEDIUM"       # Moderate adjustment value (₹5,000 - ₹50,000)
    HIGH = "HIGH"           # High monetary value (> ₹50,000) or complex multi-record alteration
    CRITICAL = "CRITICAL"   # Direct ledger manual adjustment, deletion, or elevated uncertainty


class PolicyDecisionType(str, Enum):
    """Deterministic policy decision outcome."""
    AUTO_RESOLVABLE = "AUTO_RESOLVABLE"   # Fully validated, low-risk, eligible for automated processing
    HUMAN_REVIEW = "HUMAN_REVIEW"         # Valid simulation but requires human financial analyst approval
    BLOCKED = "BLOCKED"                   # Violates financial invariants or policy safety bounds
    NO_SAFE_ACTION = "NO_SAFE_ACTION"     # Insufficient or contradictory evidence to construct safe action


class PolicyRuleEvaluation(BaseModel):
    """Evaluation result for an individual deterministic policy rule."""
    rule_id: str
    rule_name: str
    passed: bool
    observed_value: Any
    threshold_value: Any
    reason: str


class PolicyDecision(BaseModel):
    """The complete decision produced by the Deterministic Policy Engine."""
    decision: PolicyDecisionType
    risk_level: RiskLevel
    risk_factors: list[str] = Field(default_factory=list)
    rule_evaluations: list[PolicyRuleEvaluation] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    approval_requirement: Literal["NONE", "SINGLE_APPROVER", "DUAL_APPROVER"] = "SINGLE_APPROVER"

    model_config = {"from_attributes": True}


class ResolutionProposal(BaseModel):
    """
    The primary end-to-end resolution artifact combining diagnosis, action,
    counterfactual simulation, risk assessment, policy decision, and audit metadata.
    """
    proposal_id: str = Field(default_factory=lambda: f"prop_{uuid4().hex[:12]}")
    case_id: str
    discrepancy_id: str
    action: ResolutionAction
    affected_records: list[str]
    before_state: dict[str, Any]
    proposed_change: dict[str, Any]
    projected_state: dict[str, Any]
    financial_delta: FinancialDelta
    evidence_refs: list[str]
    simulation_result: SimulationResult
    policy_decision: PolicyDecision
    idempotency_key: str
    audit_reference: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"from_attributes": True}
