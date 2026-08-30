"use client";

import { AuditEvent } from "@/lib/api";
import { formatDateTime } from "@/lib/formatters";

interface AuditTimelineProps {
  events: AuditEvent[];
  isTamperFree?: boolean;
}

export function AuditTimeline({ events, isTamperFree = true }: AuditTimelineProps) {
  return (
    <div className="surface" style={{ overflow: "hidden" }}>
      <div style={{
        padding: "1rem 1.25rem",
        borderBottom: "1px solid var(--border-subtle)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <div>
          <span style={{ fontSize: "16px", fontWeight: 700, color: "#111827" }}>
            Chronological Audit Ledger
          </span>
          <span style={{ fontSize: "13px", color: "var(--text-muted)", marginLeft: "0.5rem" }}>
            ({events.length} cryptographic events)
          </span>
        </div>
        <span className={`badge badge-${isTamperFree ? "reconciled" : "blocked"}`}>
          {isTamperFree ? "SHA-256 Hash Chain Verified" : "Chain Tampering Detected"}
        </span>
      </div>

      {events.length === 0 ? (
        <div style={{ padding: "3rem 1rem", textAlign: "center", color: "var(--text-muted)", fontSize: "14px" }}>
          No audit entries recorded in memory.
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Actor</th>
                <th>Role</th>
                <th>Operation</th>
                <th>Case ID</th>
                <th>Result</th>
                <th>Request ID</th>
                <th>Block Hash</th>
              </tr>
            </thead>
            <tbody>
              {events.map((evt, idx) => (
                <tr key={evt.event_id || idx}>
                  <td className="mono" style={{ fontSize: "12.5px", color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                    {formatDateTime(evt.timestamp)}
                  </td>
                  <td className="mono" style={{ fontWeight: 600, color: "#111827" }}>
                    {evt.actor}
                  </td>
                  <td style={{ fontSize: "13px" }}>
                    {evt.actor_role}
                  </td>
                  <td style={{ fontWeight: 600, color: "#111827" }}>
                    {evt.operation}
                  </td>
                  <td className="mono" style={{ fontSize: "13px", color: "#315cf5" }}>
                    {evt.case_id || "—"}
                  </td>
                  <td>
                    <span className={`badge badge-${evt.result === "SUCCESS" ? "reconciled" : "blocked"}`}>
                      {evt.result}
                    </span>
                  </td>
                  <td className="mono" style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {evt.request_id || "—"}
                  </td>
                  <td className="mono" style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {evt.event_hash ? `${evt.event_hash.slice(0, 12)}...` : "sha256"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
