"use client";

import { useState } from "react";
import { AccessibleGraphList } from "./AccessibleGraphList";

interface EvidenceGraphCanvasProps {
  graphData: {
    nodes: any[];
    edges: any[];
  };
}

export function EvidenceGraphCanvas({ graphData }: EvidenceGraphCanvasProps) {
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [isAccessibleView, setIsAccessibleView] = useState(false);

  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];

  // Layout node positions in concentric/grid slots
  const nodePositions = nodes.map((node, i) => {
    const total = nodes.length || 1;
    const angle = (i / total) * 2 * Math.PI - Math.PI / 2;
    const radius = 180;
    const cx = 350 + radius * Math.cos(angle);
    const cy = 240 + radius * Math.sin(angle);
    return { ...node, x: cx, y: cy };
  });

  const nodeMap = new Map(nodePositions.map((n) => [n.node_id, n]));

  return (
    <div className="card" style={{ padding: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div>
          <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "#fff" }}>
            Deterministic Evidence Graph
          </h3>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            Visualizing verified entity references, double-entry postings, and discrepancy edges.
          </p>
        </div>
        <button
          onClick={() => setIsAccessibleView(!isAccessibleView)}
          className="btn-secondary"
          style={{ fontSize: "0.75rem", padding: "0.35rem 0.75rem" }}
        >
          {isAccessibleView ? "Visual Canvas View" : "Accessible Table View"}
        </button>
      </div>

      {isAccessibleView ? (
        <AccessibleGraphList nodes={nodes} edges={edges} />
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: "1.5rem" }}>
          {/* SVG Canvas */}
          <div style={{
            backgroundColor: "var(--bg-secondary)",
            borderRadius: "8px",
            border: "1px solid var(--border-subtle)",
            overflow: "hidden",
            display: "flex",
            justifyContent: "center",
          }}>
            <svg width="700" height="480" viewBox="0 0 700 480" style={{ maxWidth: "100%", height: "auto" }}>
              {/* Edges */}
              {edges.map((edge, i) => {
                const src = nodeMap.get(edge.source_id);
                const tgt = nodeMap.get(edge.target_id);
                if (!src || !tgt) return null;

                const isDiscrepancy = edge.edge_type === "CONFLICTS_WITH" || edge.edge_type === "VIOLATES";
                const strokeColor = isDiscrepancy ? "#ef4444" : "#38bdf8";

                return (
                  <g key={`edge-${i}`}>
                    <line
                      x1={src.x}
                      y1={src.y}
                      x2={tgt.x}
                      y2={tgt.y}
                      stroke={strokeColor}
                      strokeWidth={isDiscrepancy ? 2.5 : 1.5}
                      strokeDasharray={isDiscrepancy ? "4 4" : undefined}
                      opacity={0.7}
                    />
                    <text
                      x={(src.x + tgt.x) / 2}
                      y={(src.y + tgt.y) / 2 - 4}
                      fill="var(--text-muted)"
                      fontSize="9"
                      fontFamily="var(--font-mono)"
                      textAnchor="middle"
                    >
                      {edge.edge_type}
                    </text>
                  </g>
                );
              })}

              {/* Nodes */}
              {nodePositions.map((node) => {
                const isSelected = selectedNode?.node_id === node.node_id;
                let fill = "#1e293b";
                let stroke = "#38bdf8";

                if (node.node_type === "payment") { stroke = "#10b981"; fill = "rgba(16, 185, 129, 0.2)"; }
                if (node.node_type === "settlement") { stroke = "#3b82f6"; fill = "rgba(59, 130, 246, 0.2)"; }
                if (node.node_type === "fee") { stroke = "#f59e0b"; fill = "rgba(245, 158, 11, 0.2)"; }
                if (node.node_type === "ledger_entry") { stroke = "#6366f1"; fill = "rgba(99, 102, 241, 0.2)"; }

                return (
                  <g
                    key={node.node_id}
                    onClick={() => setSelectedNode(node)}
                    style={{ cursor: "pointer" }}
                  >
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={isSelected ? 26 : 22}
                      fill={fill}
                      stroke={isSelected ? "#fff" : stroke}
                      strokeWidth={isSelected ? 3 : 2}
                    />
                    <text
                      x={node.x}
                      y={node.y + 4}
                      fill="#fff"
                      fontSize="10"
                      fontWeight="600"
                      fontFamily="var(--font-mono)"
                      textAnchor="middle"
                    >
                      {node.node_type?.slice(0, 3).toUpperCase()}
                    </text>
                    <text
                      x={node.x}
                      y={node.y + 36}
                      fill="var(--text-secondary)"
                      fontSize="9"
                      fontFamily="var(--font-mono)"
                      textAnchor="middle"
                    >
                      {node.node_id?.length > 14 ? `${node.node_id.slice(0, 12)}...` : node.node_id}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Node Inspector Drawer */}
          <div style={{
            backgroundColor: "var(--bg-secondary)",
            borderRadius: "8px",
            border: "1px solid var(--border-subtle)",
            padding: "1rem",
            display: "flex",
            flexDirection: "column",
          }}>
            <h4 style={{ fontSize: "0.85rem", fontWeight: 600, color: "#fff", marginBottom: "0.75rem" }}>
              Node Inspector
            </h4>
            {selectedNode ? (
              <div style={{ fontSize: "0.8rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <div>
                  <span style={{ color: "var(--text-muted)" }}>Entity ID:</span>
                  <div className="mono" style={{ color: "var(--text-accent)", wordBreak: "break-all" }}>
                    {selectedNode.node_id}
                  </div>
                </div>
                <div>
                  <span style={{ color: "var(--text-muted)" }}>Type:</span>
                  <div style={{ fontWeight: 600, color: "#fff" }}>
                    {selectedNode.node_type?.toUpperCase()}
                  </div>
                </div>
                <div>
                  <span style={{ color: "var(--text-muted)" }}>Connected Edges:</span>
                  <div className="mono" style={{ color: "#fff" }}>
                    {edges.filter((e) => e.source_id === selectedNode.node_id || e.target_id === selectedNode.node_id).length} edges
                  </div>
                </div>
              </div>
            ) : (
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Click any graph node to inspect entity references and relation paths.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
