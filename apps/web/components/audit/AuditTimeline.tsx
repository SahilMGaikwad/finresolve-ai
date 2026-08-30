"use client";

import { AuditEvent } from "@/lib/api";
import { formatDateTime } from "@/lib/formatters";

interface AuditTimelineProps {
  events: AuditEvent[];
  isTamperFree?: boolean;
}

export function AuditTimeline({ events, isTamperFree = true }: AuditTimelineProps) {
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#fff" }}>
            Cryptographic Audit Timeline
          </h3>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            Immutable SHA-256 cryptographic chain of all financial actions, simulations, and approvals.
          </p>
        </div>
        <span className={isTamperFree ? "badge badge-reconciled" : "badge badge-discrepancy"}>
          {isTamperFree ? "✓ SHA-256 CHAIN VERIFIED" : "⚠️ CHAIN COMPROMISED"}
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {events.map((evt) => (
          <div
            key={evt.event_id}
            style={{
              backgroundColor: "var(--bg-secondary)",
              padding: "1rem",
              borderRadius: "6px",
              border: "1px solid var(--border-subtle)",
              display: "flex",
              flexDirection: "column",
              gap: "0.35rem",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span className="mono" style={{ color: "var(--text-accent)", fontSize: "0.75rem" }}>
                  {evt.event_id}
                </span>
                <span style={{ fontWeight: 600, color: "#fff", fontSize: "0.85rem" }}>
                  {evt.operation}
                </span>
              </div>
              <span className="mono" style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                {formatDateTime(evt.timestamp)}
              </span>
            </div>

            <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              Actor: <span style={{ color: "#fff" }}>{evt.actor}</span> ({evt.actor_role}) | Result:{" "}
              <span style={{ fontWeight: 600, color: evt.result === "SUCCESS" ? "var(--status-reconciled)" : "var(--status-discrepancy)" }}>
                {evt.result}
              </span>
            </div>

            {evt.reason && (
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontStyle: "italic" }}>
                {evt.reason}
              </div>
            )}

            <div className="mono" style={{ fontSize: "0.65rem", color: "var(--text-muted)", marginTop: "0.25rem", wordBreak: "break-all" }}>
              Hash: {evt.event_hash ? evt.event_hash.slice(0, 32) : "GENESIS"}...
            </div>
          </div>
        ))}

        {events.length === 0 && (
          <p style={{ textAlign: "center", color: "var(--text-muted)", padding: "1.5rem" }}>
            No audit events recorded yet.
          </p>
        )}
      </div>
    </div>
  );
}
