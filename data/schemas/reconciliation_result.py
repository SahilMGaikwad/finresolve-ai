"""
FinResolve AI — Reconciliation Result & Audit Trace Schemas

Defines the final top-level outcome of running deterministic reconciliation
on a case, including machine-readable audit trails.
"""

from __future__ import annotations

from enum import Enum, unique
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from data.schemas.discrepancy import Discrepancy, RootCauseHypothesis
from data.schemas.evidence import Evidence, EvidenceGraphModel
from data.schemas.matching import MatchGroup


@unique
class ReconciliationStatus(str, Enum):
    """The overarching outcome status of a reconciliation case."""
    RECONCILED = "reconciled"                               # All records match and balance exactly
    RECONCILED_WITH_VARIANCE = "reconciled_with_variance"   # Reconciled within allowable tolerances/compensated
    DISCREPANCY = "discrepancy"                             # One or more clear discrepancies detected
    UNRESOLVED = "unresolved"                               # Discrepancy present but conflicting/unclear root cause
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"         # Key records missing or ambiguous candidates preventing resolution


class TraceStep(BaseModel):
    """
    A single step in the deterministic, observable reconciliation reasoning trace.
    Contains observable inputs, rule applications, calculations, and outcomes.
    """

    step_number: int = Field(description="Sequential step index")
    phase: str = Field(description="Pipeline phase (e.g. 'matching', 'amount_rule', 'fee_rule', 'diagnosis')")
    description: str = Field(description="Human-readable description of the operation performed")
    inputs: dict[str, Any] = Field(default_factory=dict, description="Observable records/values inspected")
    calculation: str | None = Field(default=None, description="Exact arithmetic or logic trail if applicable")
    outcome: str = Field(description="Step result or observation")

    model_config = {"from_attributes": True}


class ReconciliationResult(BaseModel):
    """
    The complete outcome of deterministic reconciliation for a case.
    """

    case_id: str = Field(description="Reconciliation case identifier")
    status: ReconciliationStatus = Field(description="Final reconciliation status")
    matched_groups: list[MatchGroup] = Field(
        default_factory=list, description="Groups of matched records"
    )
    unmatched_records: dict[str, list[str]] = Field(
        default_factory=dict, description="IDs of records that could not be matched"
    )
    discrepancies: list[Discrepancy] = Field(
        default_factory=list, description="Detected discrepancies"
    )
    evidence: list[Evidence] = Field(
        default_factory=list, description="All collected evidence items"
    )
    evidence_graph: EvidenceGraphModel = Field(
        default_factory=EvidenceGraphModel, description="Lightweight graph representation"
    )
    hypotheses: list[RootCauseHypothesis] = Field(
        default_factory=list, description="Generated root-cause hypotheses across all discrepancies"
    )
    trace: list[TraceStep] = Field(
        default_factory=list, description="Step-by-step observable audit trail"
    )
    
    # Separated confidence scores
    matching_confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in record groupings"
    )
    diagnostic_confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in root-cause determination"
    )

    model_config = {"from_attributes": True}
