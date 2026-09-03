"use client";

import { useState } from "react";
import { formatINR } from "@/lib/formatters";

interface EvidenceGraphCanvasProps {
  graphData?: {
    nodes: any[];
    edges: any[];
  };
  graph?: {
    nodes: any[];
    edges: any[];
  };
}

export function EvidenceGraphCanvas({ graphData, graph }: EvidenceGraphCanvasProps) {
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [isTableView, setIsTableView] = useState(false);

  const activeGraph = graphData || graph || { nodes: [], edges: [] };
  const nodes = activeGraph.nodes || [];
  const edges = activeGraph.edges || [];

  // Organized layered layout
  const nodePositions = nodes.map((node, i) => {
    const total = nodes.length || 1;
    const angle = (i / total) * 2 * Math.PI - Math.PI / 2;
    const rx = 230;
    const ry = 135;
    const cx = 330 + rx * Math.cos(angle);
    const cy = 195 + ry * Math.sin(angle);
    return { ...node, x: cx, y: cy };
  });

  const nodeMap = new Map(nodePositions.map((n) => [n.node_id, n]));

  const getNodeColor = (type: string) => {
    switch (type) {
      case "payment": return "var(--text-primary)";
      case "settlement": return "var(--color-brand)";
      case "fee": return "var(--status-review)";
      case "refund": return "var(--status-discrepancy)";
      case "ledger_entry": return "var(--text-secondary)";
      default: return "var(--text-muted)";
    }
  };

  return (
    <div style={{
      backgroundColor: "var(--bg-surface)",
      border: "1px solid var(--border-subtle)",
      padding: "1.75rem",
      display: "flex",
      flexDirection: "column",
      gap: "1.25rem",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <div style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.1em" }}>
            GROUND-TRUTH ISOLATION
          </div>
          <h2 className="heading-editorial title-large" style={{ marginTop: "2px" }}>
            EVIDENCE GRAPH
          </h2>
          <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
            {nodes.length} OBSERVABLE ENTITIES • {edges.length} CAUSAL RELATIONSHIPS
          </div>
        </div>

        <button
          onClick={() => setIsTableView(!isTableView)}
          className="btn btn-secondary btn-sm"
        >
          {isTableView ? "CANVAS MODE" : "TABLE MODE"}
        </button>
      </div>

      {isTableView ? (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>NODE ID</th>
                <th>TYPE</th>
                <th>LABEL</th>
                <th>ATTRIBUTES</th>
              </tr>
            </thead>
            <tbody>
              {nodes.map((node) => (
                <tr key={node.node_id}>
                  <td className="mono" style={{ fontWeight: 700, color: "var(--text-primary)" }}>{node.node_id}</td>
                  <td>
                    <span className="mono" style={{ fontSize: "10.5px", textTransform: "uppercase" }}>
                      {node.node_type}
                    </span>
                  </td>
                  <td style={{ color: "var(--text-secondary)" }}>{node.label}</td>
                  <td className="mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                    {JSON.stringify(node.attributes || {})}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: "1.25rem" }}>
          {/* SVG Canvas */}
          <div style={{
            backgroundColor: "var(--bg-canvas)",
            border: "1px solid var(--border-subtle)",
            overflow: "hidden",
            display: "flex",
            justifyContent: "center",
          }}>
            <svg width="660" height="390" viewBox="0 0 660 390" style={{ maxWidth: "100%", height: "auto" }}>
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
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--border-strong)" />
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
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--color-brand)" />
                </marker>
              </defs>

              {/* Render Connecting Edges */}
              {edges.map((edge, idx) => {
                const source = nodeMap.get(edge.source_node_id);
                const target = nodeMap.get(edge.target_node_id);
                if (!source || !target) return null;
                const isConflict = edge.edge_type === "CONFLICTS_WITH";
                return (
                  <g key={edge.edge_id || idx}>
                    <line
                      x1={source.x}
                      y1={source.y}
                      x2={target.x}
                      y2={target.y}
                      stroke={isConflict ? "var(--color-brand)" : "var(--border-subtle)"}
                      strokeWidth={isConflict ? "1.5" : "1"}
                      strokeDasharray={isConflict ? "3,3" : undefined}
                      markerEnd={isConflict ? "url(#arrow-conflict)" : "url(#arrow-verified)"}
                    />
                    <text
                      x={(source.x + target.x) / 2}
                      y={(source.y + target.y) / 2 - 4}
                      fill="var(--text-dim)"
                      fontSize="9"
                      fontFamily="var(--font-mono)"
                      textAnchor="middle"
                    >
                      {edge.edge_type}
                    </text>
                  </g>
                );
              })}

              {/* Render Entity Nodes */}
              {nodePositions.map((node) => {
                const isSelected = selectedNode?.node_id === node.node_id;
                const color = getNodeColor(node.node_type);
                return (
                  <g
                    key={node.node_id}
                    onClick={() => setSelectedNode(node)}
                    style={{ cursor: "pointer" }}
                  >
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r="15"
                      fill="var(--bg-surface-secondary)"
                      stroke={isSelected ? "var(--color-brand)" : "var(--border-medium)"}
                      strokeWidth={isSelected ? "2" : "1"}
                    />
                    <text
                      x={node.x}
                      y={node.y + 3}
                      fill={color}
                      fontSize="8.5"
                      fontWeight="700"
                      fontFamily="var(--font-mono)"
                      textAnchor="middle"
                    >
                      {node.node_type?.slice(0, 3).toUpperCase()}
                    </text>
                    <text
                      x={node.x}
                      y={node.y + 25}
                      fill="var(--text-primary)"
                      fontSize="9.5"
                      fontWeight="600"
                      textAnchor="middle"
                    >
                      {node.label || node.node_id.slice(0, 12)}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Node Inspector Sidebar */}
          <div style={{
            backgroundColor: "var(--bg-surface-secondary)",
            border: "1px solid var(--border-subtle)",
            padding: "1.25rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem",
          }}>
            <div style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              ENTITY ATTRIBUTES
            </div>
            {selectedNode ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                <div>
                  <div style={{ fontSize: "9.5px", color: "var(--text-muted)", textTransform: "uppercase" }}>Node Identifier</div>
                  <div className="mono" style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-primary)", wordBreak: "break-all", marginTop: "2px" }}>
                    {selectedNode.node_id}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: "9.5px", color: "var(--text-muted)", textTransform: "uppercase" }}>Type</div>
                  <div className="mono" style={{ fontSize: "11px", color: "var(--color-brand)", fontWeight: 700, marginTop: "2px" }}>
                    {selectedNode.node_type?.toUpperCase()}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: "9.5px", color: "var(--text-muted)", textTransform: "uppercase" }}>Raw Attributes</div>
                  <pre style={{
                    marginTop: "4px",
                    backgroundColor: "var(--bg-canvas)",
                    padding: "0.6rem",
                    fontSize: "10px",
                    fontFamily: "var(--font-mono)",
                    color: "var(--text-secondary)",
                    overflowX: "auto",
                    border: "1px solid var(--border-hairline)",
                  }}>
                    {JSON.stringify(selectedNode.attributes || {}, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div style={{ color: "var(--text-muted)", fontSize: "11.5px", marginTop: "1rem", textAlign: "center" }}>
                Select any entity node to inspect ground-truth attributes and causal relationships.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
