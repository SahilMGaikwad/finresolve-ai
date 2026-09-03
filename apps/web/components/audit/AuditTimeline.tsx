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
        padding: "0.85rem 1.25rem",
        borderBottom: "1px solid var(--border-subtle)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <div>
          <span className="heading-editorial" style={{ fontSize: "12px", color: "var(--text-primary)" }}>
            CRYPTOGRAPHIC EVENT SEQUENCE
          </span>
          <span className="mono" style={{ fontSize: "11px", color: "var(--text-muted)", marginLeft: "0.5rem" }}>
            ({events.length} BLOCKS)
          </span>
        </div>
        <div className="mono" style={{ fontSize: "10.5px", color: "var(--text-dim)" }}>
          EVENT N ↓ HASH EVENT N-1 ↓ HASH EVENT N-2
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
              <th>TIMESTAMP</th>
              <th>ACTOR</th>
              <th>ROLE</th>
              <th>OPERATION</th>
              <th>CASE</th>
              <th>RESULT</th>
              <th>SHA-256 HASH POINTER</th>
            </tr>
          </thead>
          <tbody>
            {events.map((evt, idx) => (
              <tr key={evt.event_id || idx}>
                <td className="mono" style={{ fontSize: "11px", color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                  {formatDateTime(evt.timestamp)}
                </td>
                <td className="mono" style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                  {evt.actor}
                </td>
                <td style={{ fontSize: "11.5px", color: "var(--text-secondary)" }}>
                  {evt.actor_role}
                </td>
                <td style={{ fontWeight: 700, color: "var(--text-primary)", fontSize: "12px" }}>
                  {evt.operation}
                </td>
                <td className="mono" style={{ fontSize: "11.5px", color: "var(--color-brand)" }}>
                  {evt.case_id || "—"}
                </td>
                <td>
                  <span style={{
                    fontSize: "10.5px",
                    fontWeight: 700,
                    color: evt.result === "SUCCESS" ? "var(--status-reconciled)" : "var(--color-brand)",
                  }}>
                    ● {evt.result}
                  </span>
                </td>
                <td className="mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                  {evt.event_hash ? (
                    <span title={evt.event_hash} style={{ cursor: "help" }}>
                      {evt.event_hash.slice(0, 16)}...
                    </span>
                  ) : "GENESIS_ROOT"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
