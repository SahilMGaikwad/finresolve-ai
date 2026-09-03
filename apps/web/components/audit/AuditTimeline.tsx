"use client";

import { AuditEvent } from "@/lib/api";
import { formatDateTime } from "@/lib/formatters";

interface AuditTimelineProps {
  events: AuditEvent[];
  isTamperFree?: boolean;
}

export function AuditTimeline({ events, isTamperFree = true }: AuditTimelineProps) {
  return (
    <div className="table-container">
      <div style={{
        padding: "0.85rem 1rem",
        borderBottom: "1px solid var(--border-subtle)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <div>
          <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
            Cryptographic Event Chain
          </span>
          <span style={{ fontSize: "12px", color: "var(--text-muted)", marginLeft: "0.5rem" }}>
            ({events.length} chained blocks)
          </span>
        </div>
        <div style={{ fontSize: "11px", color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
          Event N ↓ hash Event N-1 ↓ hash Event N-2
        </div>
      </div>

      {events.length === 0 ? (
        <div style={{ padding: "3rem 1rem", textAlign: "center", color: "var(--text-muted)", fontSize: "12.5px" }}>
          No audit entries recorded in memory.
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Actor</th>
              <th>Role</th>
              <th>Operation</th>
              <th>Case ID</th>
              <th>Result</th>
              <th>SHA-256 Hash Pointer</th>
            </tr>
          </thead>
          <tbody>
            {events.map((evt, idx) => (
              <tr key={evt.event_id || idx}>
                <td className="mono" style={{ fontSize: "11.5px", color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                  {formatDateTime(evt.timestamp)}
                </td>
                <td className="mono" style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                  {evt.actor}
                </td>
                <td style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                  {evt.actor_role}
                </td>
                <td style={{ fontWeight: 600, color: "var(--text-primary)", fontSize: "12px" }}>
                  {evt.operation}
                </td>
                <td className="mono" style={{ fontSize: "12px", color: "var(--color-indigo)" }}>
                  {evt.case_id || "—"}
                </td>
                <td>
                  <span className={`badge badge-${evt.result === "SUCCESS" ? "reconciled" : "blocked"}`} style={{ fontSize: "10px" }}>
                    {evt.result}
                  </span>
                </td>
                <td className="mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                  {evt.event_hash ? (
                    <span title={evt.event_hash} style={{ cursor: "help" }}>
                      {evt.event_hash.slice(0, 16)}...
                    </span>
                  ) : "GENESIS"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
