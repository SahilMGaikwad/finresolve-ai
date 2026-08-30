"use client";

import { InvestigationResult } from "@/lib/api";
import { formatDateTime } from "@/lib/formatters";
import { DiscrepancyBadge } from "../cases/DiscrepancyBadge";

interface InvestigationPanelProps {
  investigation: InvestigationResult | null;
  isLoading: boolean;
  onTriggerInvestigation: () => void;
}

export function InvestigationPanel({
  investigation,
  isLoading,
  onTriggerInvestigation,
}: InvestigationPanelProps) {
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      {/* Header & Trigger */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#fff" }}>
            AI Financial Investigator Console
          </h3>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            Evidence-grounded reasoning, diagnostic hypotheses, and factual claim verification.
          </p>
        </div>
        <button
          onClick={onTriggerInvestigation}
          disabled={isLoading}
          className="btn-primary"
          style={{ padding: "0.6rem 1.25rem" }}
        >
          {isLoading ? "Running Investigation..." : "⚡ Run AI Investigation"}
        </button>
      </div>

      {isLoading && (
        <div style={{
          padding: "2rem",
          textAlign: "center",
          backgroundColor: "var(--bg-secondary)",
          borderRadius: "8px",
          border: "1px solid var(--border-subtle)",
        }}>
          <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>⏳</div>
          <div style={{ fontWeight: 600, color: "#fff" }}>Investigating Observable Records & Evidence...</div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
            Executing tool pipeline: overview → evidence → diagnosis → simulation → policy → claim validator
          </div>
        </div>
      )}

      {investigation && !isLoading && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Summary Box */}
          <div style={{
            backgroundColor: "var(--bg-secondary)",
            padding: "1.25rem",
            borderRadius: "8px",
            border: "1px solid var(--border-subtle)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                Investigation Summary
              </span>
              <DiscrepancyBadge status={investigation.status} />
            </div>
            <p style={{ fontSize: "0.9rem", color: "#fff", lineHeight: 1.6 }}>
              {investigation.summary}
            </p>
            <div style={{ marginTop: "0.75rem", fontSize: "0.85rem", color: "var(--text-accent)" }}>
              <strong>Root Cause:</strong> {investigation.root_cause_explanation}
            </div>
          </div>

          {/* Factual Claims Grounding Table */}
          <div>
            <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "#fff", marginBottom: "0.5rem" }}>
              Verified Factual Statements ({investigation.claims?.length || 0})
            </h4>
            <div style={{ overflowX: "auto" }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Claim Statement</th>
                    <th>Entity Cited</th>
                    <th>Field</th>
                    <th>Value</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {investigation.claims?.map((c) => {
                    const isVerified = c.verification_status === "VERIFIED";
                    return (
                      <tr key={c.claim_id}>
                        <td>{c.claim_text}</td>
                        <td className="mono" style={{ color: "var(--text-accent)" }}>{c.claimed_entity_id}</td>
                        <td className="mono">{c.claimed_field}</td>
                        <td className="mono" style={{ color: "#fff" }}>{String(c.claimed_value)}</td>
                        <td>
                          <span className={isVerified ? "badge badge-reconciled" : "badge badge-discrepancy"}>
                            {isVerified ? "VERIFIED" : c.verification_status}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                  {(!investigation.claims || investigation.claims.length === 0) && (
                    <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)" }}>No factual claims evaluated</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Trace Steps Accordion */}
          {investigation.investigation_trace && investigation.investigation_trace.length > 0 && (
            <div>
              <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "#fff", marginBottom: "0.5rem" }}>
                Agent Execution Trace
              </h4>
              <div style={{
                backgroundColor: "var(--bg-secondary)",
                borderRadius: "8px",
                border: "1px solid var(--border-subtle)",
                padding: "0.75rem 1rem",
                display: "flex",
                flexDirection: "column",
                gap: "0.5rem",
              }}>
                {investigation.investigation_trace.map((step) => (
                  <div
                    key={`step-${step.step_number}`}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      fontSize: "0.8rem",
                      padding: "0.35rem 0",
                      borderBottom: "1px solid rgba(255,255,255,0.05)",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <span className="mono" style={{ color: "var(--text-muted)" }}>#{step.step_number}</span>
                      <span style={{ fontWeight: 600, color: "#fff" }}>{step.action_taken}</span>
                    </div>
                    {step.tool_called && (
                      <span className="badge badge-info mono" style={{ fontSize: "0.7rem" }}>
                        {step.tool_called}()
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
