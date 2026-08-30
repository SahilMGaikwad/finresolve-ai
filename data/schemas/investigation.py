"""
FinResolve AI — Investigation Schemas

Data models for evidence-grounded AI investigations, factual claim validation,
multi-step resolution planning, and human review handoff packages.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from data.schemas.resolution import FinancialDelta, PolicyDecision, ResolutionAction, SimulationResult


class InvestigationStatus(str, Enum):
    """Lifecycle status of an investigation."""
    CREATED = "CREATED"
    INVESTIGATING = "INVESTIGATING"
    EVIDENCE_COLLECTED = "EVIDENCE_COLLECTED"
    DIAGNOSIS_SYNTHESIZED = "DIAGNOSIS_SYNTHESIZED"
    PLANNING = "PLANNING"
    SIMULATING = "SIMULATING"
    POLICY_REVIEW = "POLICY_REVIEW"
    CLAIM_VALIDATION = "CLAIM_VALIDATION"
    COMPLETED = "COMPLETED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class ClaimVerificationStatus(str, Enum):
    """Status of an AI-generated factual claim evaluated against the evidence graph."""
    VERIFIED = "VERIFIED"           # Claim matches observable records and evidence items
    UNSUPPORTED = "UNSUPPORTED"     # Claim references unverified records or ungrounded facts
    CONTRADICTED = "CONTRADICTED"   # Claim directly contradicts observable financial records


class FactualClaim(BaseModel):
    """A specific factual statement extracted from the AI's investigation summary."""
    claim_id: str = Field(default_factory=lambda: f"clm_{uuid4().hex[:10]}")
    claim_text: str = Field(description="The natural language claim made by the investigator")
    claimed_entity_id: str = Field(description="The primary record or case ID cited")
    claimed_field: str = Field(description="The specific attribute or metric referenced")
    claimed_value: Any = Field(description="The value asserted in the claim")
    evidence_ids: list[str] = Field(
        default_factory=list,
        description="List of supporting evidence IDs cited in the claim",
    )
    verification_status: ClaimVerificationStatus = ClaimVerificationStatus.UNSUPPORTED
    verification_reason: str = "Pending verification"

    model_config = {"from_attributes": True}


class PlanStep(BaseModel):
    """An individual sequential step in a multi-step resolution plan."""
    step_number: int
    action: ResolutionAction
    rationale: str
    expected_intermediate_effect: str

    model_config = {"from_attributes": True}


class MultiStepSimulationResult(BaseModel):
    """The outcome of sequentially simulating all steps in a ResolutionPlan."""
    is_valid: bool
    step_results: list[SimulationResult] = Field(default_factory=list)
    cumulative_delta: FinancialDelta
    residual_discrepancies: list[str] = Field(default_factory=list)
    explanation: str

    model_config = {"from_attributes": True}


class ResolutionPlan(BaseModel):
    """A multi-step composite resolution plan designed to resolve compound discrepancies."""
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid4().hex[:10]}")
    case_id: str
    steps: list[PlanStep] = Field(default_factory=list)
    overall_strategy: str
    evidence_refs: list[str] = Field(default_factory=list)
    simulation_result: MultiStepSimulationResult | None = None
    financial_delta: FinancialDelta | None = None
    policy_decision: PolicyDecision | None = None

    model_config = {"from_attributes": True}


class HumanReviewPackage(BaseModel):
    """Structured handoff package generated when automated resolution is blocked or requires human review."""
    case_id: str
    discrepancies_summary: list[str]
    verified_evidence_summary: list[str]
    failed_simulations_summary: list[str]
    key_ambiguities: list[str]
    recommended_analyst_actions: list[str]
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"

    model_config = {"from_attributes": True}


class AgentTraceStep(BaseModel):
    """An observable step in the AI investigator's reasoning and tool execution trace."""
    step_number: int
    state: InvestigationStatus
    action_taken: str
    tool_called: str | None = None
    tool_output_summary: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationResult(BaseModel):
    """The comprehensive structured output of an AI financial investigation."""
    investigation_id: str = Field(default_factory=lambda: f"inv_{uuid4().hex[:12]}")
    case_id: str
    status: InvestigationStatus
    summary: str
    symptoms_identified: list[str] = Field(default_factory=list)
    root_cause_explanation: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    claims: list[FactualClaim] = Field(default_factory=list)
    unsupported_claims_count: int = 0
    resolution_plan: ResolutionPlan | None = None
    human_review_package: HumanReviewPackage | None = None
    investigation_trace: list[AgentTraceStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"from_attributes": True}
