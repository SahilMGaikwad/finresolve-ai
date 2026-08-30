"""
FinResolve AI — Discrepancy & Hypothesis Schemas

Defines structured models for detected financial discrepancies
and mechanically supported root-cause hypotheses.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from data.schemas.evidence import Severity


class RootCauseHypothesis(BaseModel):
    """
    A mechanically derived candidate explanation for a discrepancy.
    Must specify explicit supporting and contradicting evidence IDs.
    """

    hypothesis_id: UUID = Field(default_factory=uuid4, description="Unique hypothesis ID")
    cause_type: str = Field(description="Structured cause key (e.g. 'incorrect_settlement_calculation')")
    title: str = Field(description="Short title of the hypothesis")
    description: str = Field(description="Detailed explanation of the mechanical rationale")
    supporting_evidence_ids: list[UUID] = Field(
        default_factory=list, description="IDs of evidence that support this hypothesis"
    )
    contradicting_evidence_ids: list[UUID] = Field(
        default_factory=list, description="IDs of evidence that contradict this hypothesis"
    )
    plausibility_score: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Score based on supporting vs contradicting evidence"
    )
    is_primary: bool = Field(
        default=False, description="Whether this is the most plausible primary hypothesis"
    )

    model_config = {"from_attributes": True}


class Discrepancy(BaseModel):
    """
    A detected inconsistency between related financial records.
    Backed by rule results, evidence references, and candidate hypotheses.
    """

    discrepancy_id: UUID = Field(default_factory=uuid4, description="Unique discrepancy ID")
    case_id: str = Field(description="Associated reconciliation case ID")
    discrepancy_type: str = Field(description="Standardized discrepancy type code")
    title: str = Field(description="Summary title")
    severity: Severity = Field(default=Severity.MEDIUM, description="Discrepancy severity level")
    affected_record_ids: list[str] = Field(
        default_factory=list, description="IDs of records directly involved in the discrepancy"
    )
    evidence_ids: list[UUID] = Field(
        default_factory=list, description="List of evidence IDs demonstrating the discrepancy"
    )
    candidate_hypotheses: list[RootCauseHypothesis] = Field(
        default_factory=list, description="Mechanically generated candidate causes"
    )
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in the discrepancy's existence"
    )
    is_resolved: bool = Field(
        default=False, description="Whether this discrepancy was resolved by compensating records (e.g. fees/refunds)"
    )
    resolution_notes: str | None = Field(
        default=None, description="Explanation if resolved mechanically by compensating entries"
    )

    model_config = {"from_attributes": True}
