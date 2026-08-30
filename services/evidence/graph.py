"""
FinResolve AI — Evidence Graph Builder

Constructs a lightweight in-memory evidence graph from observed records,
matched groups, and rule results.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from data.schemas.case import CaseRecords
from data.schemas.evidence import (
    Evidence,
    EvidenceGraphModel,
    GraphEdge,
    GraphEdgeType,
    GraphNode,
    GraphNodeType,
)
from data.schemas.matching import MatchGroup
from services.reconciliation.rules.base import RuleResult


class EvidenceGraphBuilder:
    """
    Constructs an explainable directed graph connecting entities, financial events,
    and mechanical support/conflict edges.
    """

    def build_graph(
        self,
        records: CaseRecords,
        groups: list[MatchGroup],
        evidence_items: list[Evidence],
    ) -> EvidenceGraphModel:
        """
        Build an EvidenceGraphModel from observed records and reconciliation findings.
        """
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        # 1. Populate Nodes from records
        for payment in records.payments:
            pid = payment.get("payment_id", "")
            if pid:
                node_id = f"payment:{pid}"
                nodes[node_id] = GraphNode(
                    node_id=node_id,
                    node_type=GraphNodeType.PAYMENT,
                    label=f"Payment {pid[:10]}",
                    attributes={"amount": payment.get("amount"), "status": payment.get("status")},
                )

        for order in records.orders:
            oid = order.get("order_id", "")
            if oid:
                node_id = f"order:{oid}"
                nodes[node_id] = GraphNode(
                    node_id=node_id,
                    node_type=GraphNodeType.ORDER,
                    label=f"Order {oid[:10]}",
                    attributes={"amount": order.get("amount"), "status": order.get("status")},
                )

        for settlement in records.settlements:
            sid = settlement.get("settlement_id", "")
            if sid:
                node_id = f"settlement:{sid}"
                nodes[node_id] = GraphNode(
                    node_id=node_id,
                    node_type=GraphNodeType.SETTLEMENT,
                    label=f"Settlement {sid[:10]}",
                    attributes={"net_amount": settlement.get("net_amount"), "status": settlement.get("status")},
                )

        for fee in records.fees:
            fid = fee.get("fee_id", "")
            if fid:
                node_id = f"fee:{fid}"
                nodes[node_id] = GraphNode(
                    node_id=node_id,
                    node_type=GraphNodeType.FEE,
                    label=f"Fee {fee.get('fee_type', '')}",
                    attributes={"amount": fee.get("amount"), "rate_bps": fee.get("rate_bps")},
                )

        for refund in records.refunds:
            rid = refund.get("refund_id", "")
            if rid:
                node_id = f"refund:{rid}"
                nodes[node_id] = GraphNode(
                    node_id=node_id,
                    node_type=GraphNodeType.REFUND,
                    label=f"Refund {rid[:10]}",
                    attributes={"amount": refund.get("amount"), "status": refund.get("status")},
                )

        for entry in records.ledger_entries:
            eid = entry.get("entry_id", "")
            if eid:
                node_id = f"ledger_entry:{eid}"
                nodes[node_id] = GraphNode(
                    node_id=node_id,
                    node_type=GraphNodeType.LEDGER_ENTRY,
                    label=f"Ledger {entry.get('entry_type', '')}",
                    attributes={"debit": entry.get("debit"), "credit": entry.get("credit")},
                )

        # 2. Add structural relationship edges from records
        for payment in records.payments:
            pid = payment.get("payment_id")
            oid = payment.get("order_id")
            if pid and oid and f"payment:{pid}" in nodes and f"order:{oid}" in nodes:
                edges.append(
                    GraphEdge(
                        source_node_id=f"payment:{pid}",
                        target_node_id=f"order:{oid}",
                        edge_type=GraphEdgeType.PAYS_FOR,
                    )
                )

        for settlement in records.settlements:
            sid = settlement.get("settlement_id")
            pid = settlement.get("payment_id")
            if sid and pid and f"settlement:{sid}" in nodes and f"payment:{pid}" in nodes:
                edges.append(
                    GraphEdge(
                        source_node_id=f"settlement:{sid}",
                        target_node_id=f"payment:{pid}",
                        edge_type=GraphEdgeType.SETTLES,
                    )
                )

        for fee in records.fees:
            fid = fee.get("fee_id")
            pid = fee.get("payment_id")
            sid = fee.get("settlement_id")
            if fid and pid and f"fee:{fid}" in nodes and f"payment:{pid}" in nodes:
                edges.append(
                    GraphEdge(
                        source_node_id=f"fee:{fid}",
                        target_node_id=f"payment:{pid}",
                        edge_type=GraphEdgeType.CHARGES,
                    )
                )
            if fid and sid and f"fee:{fid}" in nodes and f"settlement:{sid}" in nodes:
                edges.append(
                    GraphEdge(
                        source_node_id=f"fee:{fid}",
                        target_node_id=f"settlement:{sid}",
                        edge_type=GraphEdgeType.CHARGES,
                    )
                )

        for refund in records.refunds:
            rid = refund.get("refund_id")
            pid = refund.get("payment_id")
            if rid and pid and f"refund:{rid}" in nodes and f"payment:{pid}" in nodes:
                edges.append(
                    GraphEdge(
                        source_node_id=f"refund:{rid}",
                        target_node_id=f"payment:{pid}",
                        edge_type=GraphEdgeType.REFUNDS,
                    )
                )

        for entry in records.ledger_entries:
            eid = entry.get("entry_id")
            ref_id = entry.get("reference_id")
            ref_type = entry.get("reference_type")
            target_node = f"{ref_type}:{ref_id}" if ref_type and ref_id else None
            if eid and target_node and f"ledger_entry:{eid}" in nodes and target_node in nodes:
                edges.append(
                    GraphEdge(
                        source_node_id=f"ledger_entry:{eid}",
                        target_node_id=target_node,
                        edge_type=GraphEdgeType.POSTS_TO,
                    )
                )

        # 3. Add Conflict and Support Edges based on Evidence
        for ev in evidence_items:
            src_node = f"{ev.record_type.value}:{ev.source_record_id}"
            if src_node in nodes:
                # If there's an expected or referenced entity, add conflict edge
                edges.append(
                    GraphEdge(
                        source_node_id=src_node,
                        target_node_id=src_node,  # self-referencing conflict attribute or specific link
                        edge_type=GraphEdgeType.CONFLICTS_WITH,
                        attributes={"evidence_id": str(ev.evidence_id), "reason": ev.explanation},
                    )
                )

        return EvidenceGraphModel(nodes=list(nodes.values()), edges=edges)
