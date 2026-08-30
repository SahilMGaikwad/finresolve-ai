"use client";

import { useState } from "react";
import { AccessibleGraphList } from "./AccessibleGraphList";
import { formatINR } from "@/lib/formatters";

interface EvidenceGraphCanvasProps {
  graphData: {
    nodes: any[];
    edges: any[];
  };
}

export function EvidenceGraphCanvas({ graphData }: EvidenceGraphCanvasProps) {
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [isTableView, setIsTableView] = useState(false);

  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];

  // Organized layered layout
  const nodePositions = nodes.map((node, i) => {
    const total = nodes.length || 1;
    const angle = (i / total) * 2 * Math.PI - Math.PI / 2;
    const rx = 230;
    const ry = 150;
    const cx = 330 + rx * Math.cos(angle);
    const cy = 210 + ry * Math.sin(angle);
    return { ...node, x: cx, y: cy };
  });

  const nodeMap = new Map(nodePositions.map((n) => [n.node_id, n]));

  const getNodeColor = (type: string) => {
    switch (type) {
      case "payment": return "#315cf5";
      case "settlement": return "#14b8a6";
      case "fee": return "#d97706";
      case "refund": return "#dc2626";
      case "ledger_entry": return "#4f46e5";
      default: return "#64748b";
    }
  };

  return (
    <div className="surface" style={{ padding: "1.25rem 1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div>
          <span style={{ fontSize: "16px", fontWeight: 700, color: "#111827" }}>
            Deterministic Evidence Graph
          </span>
          <span style={{ fontSize: "13px", color: "var(--text-muted)", marginLeft: "0.5rem" }}>
            ({nodes.length} entities, {edges.length} relationships)
          </span>
        </div>
        <button
          onClick={() => setIsTableView(!isTableView)}
          className="btn-secondary"
          style={{ fontSize: "13px", padding: "0.3rem 0.75rem" }}
        >
          {isTableView ? "Canvas Mode" : "Table Mode"}
        </button>
      </div>

      {isTableView ? (
        <AccessibleGraphList nodes={nodes} edges={edges} />
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 290px", gap: "1rem" }}>
          {/* SVG Canvas */}
          <div style={{
            backgroundColor: "#f8fafc",
            borderRadius: "8px",
            border: "1px solid var(--border-subtle)",
            overflow: "hidden",
            display: "flex",
            justifyContent: "center",
          }}>
            <svg width="660" height="420" viewBox="0 0 660 420" style={{ maxWidth: "100%", height: "auto" }}>
              <defs>
                <marker
                  id="arrow-verified"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="5"
                  markerHeight="5"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
                </marker>
                <marker
                  id="arrow-conflict"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="5"
                  markerHeight="5"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626" />
                </marker>
              </defs>

              {/* Edges */}
              {edges.map((edge, i) => {
                const srcId = edge.source_node_id || edge.source_id;
                const tgtId = edge.target_node_id || edge.target_id;
                const src = nodeMap.get(srcId);
                const tgt = nodeMap.get(tgtId);
                if (!src || !tgt) return null;

                const isConflict = edge.edge_type === "CONFLICTS_WITH";
                const isSelf = srcId === tgtId;

                if (isSelf) {
                  return (
                    <path
                      key={i}
                      d={`M ${src.x} ${src.y - 10} C ${src.x - 25} ${src.y - 35}, ${src.x + 25} ${src.y - 35}, ${src.x} ${src.y - 10}`}
                      fill="none"
                      stroke="#dc2626"
                      strokeWidth="1.5"
                      strokeDasharray="3 3"
                    />
                  );
                }

                return (
                  <g key={i}>
                    <line
                      x1={src.x}
                      y1={src.y}
                      x2={tgt.x}
                      y2={tgt.y}
                      stroke={isConflict ? "#dc2626" : "#cbd5e1"}
                      strokeWidth={isConflict ? 1.75 : 1.2}
                      strokeDasharray={isConflict ? "4 3" : "none"}
                      markerEnd={isConflict ? "url(#arrow-conflict)" : "url(#arrow-verified)"}
                    />
                    <text
                      x={(src.x + tgt.x) / 2}
                      y={(src.y + tgt.y) / 2 - 4}
                      fill={isConflict ? "#dc2626" : "#64748b"}
                      fontSize="9"
                      fontWeight="600"
                      fontFamily="var(--font-mono)"
                      textAnchor="middle"
                    >
                      {edge.edge_type}
                    </text>
                  </g>
                );
              })}

              {/* Nodes with Hover Scale */}
              {nodePositions.map((node) => {
                const isSelected = selectedNode?.node_id === node.node_id;
                const color = getNodeColor(node.node_type);

                return (
                  <g
                    key={node.node_id}
                    onClick={() => setSelectedNode(node)}
                    style={{ cursor: "pointer", transition: "transform 0.15s ease" }}
                  >
                    {isSelected && (
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r="17"
                        fill="none"
                        stroke="#315cf5"
                        strokeWidth="2"
                        strokeDasharray="3 2"
                      />
                    )}
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r="11"
                      fill="#ffffff"
                      stroke={color}
                      strokeWidth="2.5"
                    />
                    <text
                      x={node.x}
                      y={node.y + 22}
                      fill="#111827"
                      fontSize="10"
                      fontWeight="600"
                      fontFamily="var(--font-mono)"
                      textAnchor="middle"
                    >
                      {node.label || node.node_id}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Node Inspector Panel */}
          <div style={{
            background: "#f8fafc",
            borderRadius: "8px",
            border: "1px solid var(--border-subtle)",
            padding: "1rem",
            display: "flex",
            flexDirection: "column",
          }}>
            <div style={{
              fontSize: "12px",
              fontWeight: 700,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.04em",
              marginBottom: "0.75rem",
              borderBottom: "1px solid var(--border-subtle)",
              paddingBottom: "0.4rem",
            }}>
              Node Properties
            </div>

            {selectedNode ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <div>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Record ID</div>
                  <div className="mono" style={{ fontSize: "13px", fontWeight: 600, color: "#111827", wordBreak: "break-all" }}>
                    {selectedNode.node_id}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Type</div>
                  <span className="badge badge-info" style={{ marginTop: "0.2rem", textTransform: "capitalize" }}>
                    {selectedNode.node_type}
                  </span>
                </div>

                {selectedNode.attributes?.amount && (
                  <div>
                    <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Amount</div>
                    <div className="tabular-num" style={{ fontSize: "16px", fontWeight: 700, color: "#059669" }}>
                      {formatINR(selectedNode.attributes.amount.amount_minor || selectedNode.attributes.amount)}
                    </div>
                  </div>
                )}

                {selectedNode.attributes?.net_amount && (
                  <div>
                    <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Net Settled</div>
                    <div className="tabular-num" style={{ fontSize: "16px", fontWeight: 700, color: "#315cf5" }}>
                      {formatINR(selectedNode.attributes.net_amount.amount_minor || selectedNode.attributes.net_amount)}
                    </div>
                  </div>
                )}

                <div>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Payload Fields</div>
                  <pre className="mono" style={{
                    fontSize: "12px",
                    background: "#ffffff",
                    padding: "0.6rem",
                    borderRadius: "6px",
                    border: "1px solid var(--border-subtle)",
                    overflowX: "auto",
                    color: "var(--text-secondary)",
                  }}>
                    {JSON.stringify(selectedNode.attributes || {}, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: "center", padding: "3rem 0.5rem", color: "var(--text-muted)", fontSize: "13.5px" }}>
                Select any entity node on the canvas to inspect payload attributes.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
