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
    const ry = 140;
    const cx = 330 + rx * Math.cos(angle);
    const cy = 200 + ry * Math.sin(angle);
    return { ...node, x: cx, y: cy };
  });

  const nodeMap = new Map(nodePositions.map((n) => [n.node_id, n]));

  const getNodeColor = (type: string) => {
    switch (type) {
      case "payment": return "var(--color-indigo)";
      case "settlement": return "var(--color-teal)";
      case "fee": return "var(--status-review)";
      case "refund": return "var(--status-discrepancy)";
      case "ledger_entry": return "var(--text-secondary)";
      default: return "var(--text-muted)";
    }
  };

  return (
    <div className="surface" style={{ padding: "1.25rem 1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div>
          <span style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)" }}>
            Deterministic Evidence Graph
          </span>
          <span style={{ fontSize: "12px", color: "var(--text-muted)", marginLeft: "0.5rem" }}>
            ({nodes.length} entities, {edges.length} relationships)
          </span>
        </div>
        <button
          onClick={() => setIsTableView(!isTableView)}
          className="btn btn-secondary btn-sm"
          style={{ fontSize: "11.5px" }}
        >
          {isTableView ? "Canvas Mode" : "Table Mode"}
        </button>
      </div>

      {isTableView ? (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Entity Node ID</th>
                <th>Type</th>
                <th>Label</th>
                <th>Key Attributes</th>
              </tr>
            </thead>
            <tbody>
              {nodes.map((node) => (
                <tr key={node.node_id}>
                  <td className="mono" style={{ fontWeight: 600, color: "var(--text-primary)" }}>{node.node_id}</td>
                  <td>
                    <span className="badge badge-neutral" style={{ fontSize: "10px", textTransform: "uppercase" }}>
                      {node.node_type}
                    </span>
                  </td>
                  <td style={{ color: "var(--text-secondary)" }}>{node.label}</td>
                  <td className="mono" style={{ fontSize: "11.5px", color: "var(--text-muted)" }}>
                    {JSON.stringify(node.attributes || {})}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: "1rem" }}>
          {/* SVG Canvas */}
          <div style={{
            backgroundColor: "var(--bg-canvas)",
            borderRadius: "6px",
            border: "1px solid var(--border-subtle)",
            overflow: "hidden",
            display: "flex",
            justifyContent: "center",
          }}>
            <svg width="660" height="400" viewBox="0 0 660 400" style={{ maxWidth: "100%", height: "auto" }}>
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
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--status-discrepancy)" />
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
                      stroke={isConflict ? "var(--status-discrepancy)" : "var(--border-medium)"}
                      strokeWidth={isConflict ? "2" : "1.2"}
                      strokeDasharray={isConflict ? "4,4" : undefined}
                      markerEnd={isConflict ? "url(#arrow-conflict)" : "url(#arrow-verified)"}
                    />
                    <text
                      x={(source.x + target.x) / 2}
                      y={(source.y + target.y) / 2 - 4}
                      fill="var(--text-muted)"
                      fontSize="9.5"
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
                      r="16"
                      fill="var(--bg-surface-secondary)"
                      stroke={isSelected ? "#ffffff" : color}
                      strokeWidth={isSelected ? "2.5" : "1.5"}
                    />
                    <text
                      x={node.x}
                      y={node.y + 3}
                      fill={color}
                      fontSize="9"
                      fontWeight="700"
                      fontFamily="var(--font-mono)"
                      textAnchor="middle"
                    >
                      {node.node_type?.slice(0, 3).toUpperCase()}
                    </text>
                    <text
                      x={node.x}
                      y={node.y + 26}
                      fill="var(--text-primary)"
                      fontSize="10"
                      fontWeight="500"
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
            borderRadius: "6px",
            border: "1px solid var(--border-subtle)",
            padding: "1rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.6rem",
          }}>
            <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
              Entity Inspector
            </div>
            {selectedNode ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <div>
                  <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>Node ID</div>
                  <div className="mono" style={{ fontSize: "11.5px", fontWeight: 600, color: "var(--text-primary)", wordBreak: "break-all" }}>
                    {selectedNode.node_id}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>Type</div>
                  <span className="badge badge-info" style={{ fontSize: "10px", textTransform: "uppercase", marginTop: "2px" }}>
                    {selectedNode.node_type}
                  </span>
                </div>
                <div>
                  <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>Attributes</div>
                  <pre style={{
                    marginTop: "4px",
                    backgroundColor: "var(--bg-canvas)",
                    padding: "0.5rem",
                    borderRadius: "4px",
                    fontSize: "10.5px",
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
                Click any node on the canvas to inspect entity attributes and relationship edges.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
