"""
FinResolve AI — Reconciliation Case Schema

The fundamental evaluation unit. Groups related financial records
with separated ground truth and observed (potentially corrupted) data.
"""

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from data.schemas.corruption import CorruptionLabel
from data.schemas.enums import CaseDifficulty


class CaseRecords(BaseModel):
    """
    A bundle of related financial records for a single reconciliation case.

    Records are stored as dicts (serialised Pydantic models) to allow
    heterogeneous record types in the same container.
    """

    payments: list[dict[str, Any]] = Field(default_factory=list)
    orders: list[dict[str, Any]] = Field(default_factory=list)
    settlements: list[dict[str, Any]] = Field(default_factory=list)
    refunds: list[dict[str, Any]] = Field(default_factory=list)
    fees: list[dict[str, Any]] = Field(default_factory=list)
    ledger_entries: list[dict[str, Any]] = Field(default_factory=list)
    payouts: list[dict[str, Any]] = Field(default_factory=list)


class ExpectedOutcome(BaseModel):
    """
    Ground-truth expected outcome for a reconciliation case.

    This is what a perfect system should conclude.
    """

    has_discrepancy: bool = Field(description="Whether this case has a true discrepancy")
    discrepancy_type: str | None = Field(
        default=None, description="Ground-truth discrepancy type (if any)"
    )
    root_cause: str | None = Field(
        default=None, description="Ground-truth root cause (if any)"
    )
    correct_resolution: dict[str, Any] | None = Field(
        default=None, description="The correct resolution action (if any)"
    )
    should_escalate: bool = Field(
        default=False,
        description="Whether this case should be escalated to human review "
                    "(e.g., ambiguous or multi-cause)",
    )


class ReconciliationCase(BaseModel):
    """
    A single reconciliation case — the fundamental evaluation unit.

    Contains:
    - ground_truth: Clean, correct records (never modified by corruption)
    - observed: Potentially corrupted records (what the system sees)
    - corruptions: Labels describing what was changed
    - expected_outcome: What a correct system should conclude
    """

    case_id: str = Field(description="Unique case identifier (e.g., 'CASE-000001')")
    merchant_id: str = Field(description="Merchant this case belongs to")
    ground_truth: CaseRecords = Field(
        description="Clean, correct records — never modified"
    )
    observed: CaseRecords = Field(
        description="Records as the system sees them — potentially corrupted"
    )
    corruptions: list[CorruptionLabel] = Field(
        default_factory=list,
        description="Labels for all corruptions applied to observed data",
    )
    difficulty: CaseDifficulty = Field(description="Case difficulty level")
    expected_outcome: ExpectedOutcome = Field(
        description="Ground-truth expected outcome"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional case metadata",
    )

    model_config = {"from_attributes": True}
