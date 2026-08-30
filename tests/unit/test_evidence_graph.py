"""
FinResolve AI — Evidence Graph Unit Tests

Tests construction of graph nodes and relationship/conflict edges.
"""

from data.schemas.case import CaseRecords
from data.schemas.evidence import Evidence, EvidenceType, GraphNodeType, Severity
from data.schemas.matching import MatchGroup
from services.evidence.collector import EvidenceCollector
from services.evidence.graph import EvidenceGraphBuilder


def test_evidence_collector_deduplication():
    collector = EvidenceCollector()
    ev1 = Evidence(
        evidence_type=EvidenceType.AMOUNT_DIFF,
        source_record_id="stl_1",
        record_type="settlement",
        field_name="net_amount",
        observed_value="1000",
        rule_id="RULE-AMT-001",
        severity=Severity.HIGH,
        explanation="Diff 1",
    )
    ev2 = Evidence(
        evidence_type=EvidenceType.AMOUNT_DIFF,
        source_record_id="stl_1",
        record_type="settlement",
        field_name="net_amount",
        observed_value="1000",
        rule_id="RULE-AMT-001",
        severity=Severity.HIGH,
        explanation="Diff 1 copy",
    )
    collector.add_evidence(ev1)
    collector.add_evidence(ev2)
    assert len(collector.get_all()) == 1


def test_evidence_graph_construction():
    records = CaseRecords(
        payments=[{"payment_id": "pay_1", "order_id": "ord_1", "amount": {"amount_minor": 100, "currency": "INR"}}],
        orders=[{"order_id": "ord_1", "amount": {"amount_minor": 100, "currency": "INR"}}],
        settlements=[{"settlement_id": "stl_1", "payment_id": "pay_1", "net_amount": {"amount_minor": 98, "currency": "INR"}}],
        fees=[],
        refunds=[],
        ledger_entries=[],
        payouts=[],
    )
    groups = [MatchGroup(payment_id="pay_1", order_id="ord_1", settlement_ids=["stl_1"])]
    evidence = [
        Evidence(
            evidence_type=EvidenceType.AMOUNT_DIFF,
            source_record_id="stl_1",
            record_type="settlement",
            field_name="net_amount",
            observed_value="98",
            rule_id="RULE-AMT-001",
            severity=Severity.HIGH,
            explanation="Diff",
        )
    ]

    builder = EvidenceGraphBuilder()
    graph = builder.build_graph(records, groups, evidence)

    assert len(graph.nodes) == 3
    node_types = {n.node_type for n in graph.nodes}
    assert GraphNodeType.PAYMENT in node_types
    assert GraphNodeType.ORDER in node_types
    assert GraphNodeType.SETTLEMENT in node_types

    edge_types = {e.edge_type.value for e in graph.edges}
    assert "PAYS_FOR" in edge_types
    assert "SETTLES" in edge_types
    assert "CONFLICTS_WITH" in edge_types
