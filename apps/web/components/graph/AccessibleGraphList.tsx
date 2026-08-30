"use client";

interface AccessibleGraphListProps {
  nodes: any[];
  edges: any[];
}

export function AccessibleGraphList({ nodes, edges }: AccessibleGraphListProps) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table className="data-table">
        <thead>
          <tr>
            <th>Source Entity</th>
            <th>Relationship Type</th>
            <th>Target Entity</th>
            <th>Edge Status</th>
          </tr>
        </thead>
        <tbody>
          {edges.map((edge, idx) => {
            const isDiscrepancy = edge.edge_type === "CONFLICTS_WITH" || edge.edge_type === "VIOLATES";
            return (
              <tr key={`acc-edge-${idx}`}>
                <td className="mono">{edge.source_id}</td>
                <td style={{ fontWeight: 600, color: isDiscrepancy ? "var(--status-discrepancy)" : "var(--text-accent)" }}>
                  {edge.edge_type}
                </td>
                <td className="mono">{edge.target_id}</td>
                <td>
                  <span className={isDiscrepancy ? "badge badge-discrepancy" : "badge badge-reconciled"}>
                    {isDiscrepancy ? "Discrepancy" : "Verified"}
                  </span>
                </td>
              </tr>
            );
          })}
          {edges.length === 0 && (
            <tr><td colSpan={4} style={{ textAlign: "center", color: "var(--text-muted)" }}>No graph edges found</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
