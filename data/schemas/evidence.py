"""
FinResolve AI — Evidence & Evidence Graph Schemas

Defines models for structured evidence items, severity ratings,
and the lightweight in-memory evidence graph.
"""

from __future__ import annotations

from enum import Enum, unique
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from data.schemas.enums import RecordType


@unique
class Severity(str, Enum):
    """Severity classification for rules, evidence, and discrepancies."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@unique
class EvidenceType(str, Enum):
    """Categorization of evidence observations."""
    AMOUNT_DIFF = "amount_diff"
    MISSING_LINK = "missing_link"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    STATUS_CONFLICT = "status_conflict"
    FEE_MISMATCH = "fee_mismatch"
    DUPLICATE_ENTRY = "duplicate_entry"
    LEDGER_IMBALANCE = "ledger_imbalance"
    REFERENCE_MISMATCH = "reference_mismatch"


class Evidence(BaseModel):
    """
    A single piece of mechanical evidence supporting or contradicting a discrepancy.
    """

    evidence_id: UUID = Field(default_factory=uuid4, description="Unique evidence ID")
    evidence_type: EvidenceType = Field(description="Classification of this evidence")
    source_record_id: str = Field(description="ID of the record providing this evidence")
    record_type: RecordType = Field(description="Type of the source record")
    field_name: str = Field(description="Target field inspected")
    observed_value: Any = Field(description="Actual value observed in the record")
    expected_value: Any | None = Field(default=None, description="Expected value if determinable")
    rule_id: str = Field(description="ID of the rule that generated this evidence")
    severity: Severity = Field(default=Severity.MEDIUM, description="Evidence severity level")
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence/strength of evidence")
    explanation: str = Field(description="Human-readable explanation of the evidence")

    model_config = {"from_attributes": True}


@unique
class GraphNodeType(str, Enum):
    """Types of nodes in the evidence graph."""
    CUSTOMER = "customer"
    ORDER = "order"
    PAYMENT = "payment"
    SETTLEMENT = "settlement"
    REFUND = "refund"
    FEE = "fee"
    LEDGER_ENTRY = "ledger_entry"
    PAYOUT = "payout"


@unique
class GraphEdgeType(str, Enum):
    """Types of directed relationships between evidence graph nodes."""
    BELONGS_TO = "BELONGS_TO"
    PAYS_FOR = "PAYS_FOR"
    SETTLES = "SETTLES"
    REFUNDS = "REFUNDS"
    CHARGES = "CHARGES"
    POSTS_TO = "POSTS_TO"
    REFERENCES = "REFERENCES"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    SUPPORTS = "SUPPORTS"


class GraphNode(BaseModel):
    """A node in the evidence graph representing an entity or record."""
    node_id: str = Field(description="Unique node identifier (e.g. 'payment:pay_123')")
    node_type: GraphNodeType = Field(description="Type of entity")
    label: str = Field(description="Short human-readable label")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Metadata & financial attributes")


class GraphEdge(BaseModel):
    """A directed edge in the evidence graph."""
    edge_id: UUID = Field(default_factory=uuid4, description="Unique edge identifier")
    source_node_id: str = Field(description="Origin node ID")
    target_node_id: str = Field(description="Target node ID")
    edge_type: GraphEdgeType = Field(description="Relationship type")
    weight: float = Field(default=1.0, description="Strength of the link")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Optional metadata or evidence references")


class EvidenceGraphModel(BaseModel):
    """Serialized representation of an evidence graph."""
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
