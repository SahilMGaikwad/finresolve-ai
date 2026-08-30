"""
FinResolve AI — Matching Data Schemas

Defines models and enums for deterministic, multi-signal record matching.
"""

from __future__ import annotations

from enum import Enum, unique
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from data.schemas.enums import RecordType


@unique
class MatchState(str, Enum):
    """The classification of a record's matching certainty."""
    MATCHED = "matched"               # High-confidence deterministic or multi-signal match
    PROBABLE_MATCH = "probable_match" # Strong signal match, but below full confidence threshold
    AMBIGUOUS = "ambiguous"           # Multiple competing candidates with similar strength
    UNMATCHED = "unmatched"           # No candidate found meeting minimal criteria
    CONFLICT = "conflict"             # Candidate exists but exhibits mutually contradictory signals


class MatchSignal(BaseModel):
    """
    A single explainable signal contributing to a record match.
    """

    name: str = Field(description="Name of the signal (e.g. 'exact_reference', 'amount_match')")
    weight: float = Field(ge=0.0, le=1.0, description="Configured weight for this signal")
    raw_score: float = Field(ge=-1.0, le=1.0, description="Raw normalized score (-1.0 to 1.0)")
    weighted_score: float = Field(ge=-1.0, le=1.0, description="raw_score * weight")
    explanation: str = Field(description="Human-readable explanation of why this signal scored as it did")

    model_config = {"from_attributes": True}


class MatchCandidate(BaseModel):
    """
    A candidate record evaluated for matching against a primary record.
    """

    target_record_id: str = Field(description="ID of the candidate record")
    target_record_type: RecordType = Field(description="Record type of the candidate")
    aggregate_score: float = Field(ge=-1.0, le=1.0, description="Sum of weighted scores")
    signals: list[MatchSignal] = Field(default_factory=list, description="Breakdown of individual signals")
    state: MatchState = Field(description="Determined matching state")

    model_config = {"from_attributes": True}


class MatchGroup(BaseModel):
    """
    A coherent group of matched financial records representing a transaction lifecycle.
    """

    group_id: UUID = Field(default_factory=uuid4, description="Unique group identifier")
    payment_id: str | None = Field(default=None, description="Primary payment ID if matched")
    order_id: str | None = Field(default=None, description="Primary order ID if matched")
    settlement_ids: list[str] = Field(default_factory=list, description="Matched settlement IDs")
    fee_ids: list[str] = Field(default_factory=list, description="Matched fee IDs")
    refund_ids: list[str] = Field(default_factory=list, description="Matched refund IDs")
    ledger_entry_ids: list[str] = Field(default_factory=list, description="Matched ledger entry IDs")
    payout_ids: list[str] = Field(default_factory=list, description="Matched payout IDs")
    
    # Matching diagnostic metadata
    match_state: MatchState = Field(default=MatchState.MATCHED, description="Overall group match state")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Aggregate match confidence")
    candidate_evaluations: list[MatchCandidate] = Field(
        default_factory=list,
        description="Evaluations of candidates considered during group formation"
    )

    model_config = {"from_attributes": True}
