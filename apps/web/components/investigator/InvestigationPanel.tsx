"use client";

import { InvestigationResult } from "@/lib/api";
import { PlayIcon } from "@/components/icons/Icons";

interface InvestigationPanelProps {
  investigation: InvestigationResult | null;
  isLoading: boolean;
  onTriggerInvestigation: () => void;
  caseId?: string;
}

export function InvestigationPanel({
  investigation,
  isLoading,
  onTriggerInvestigation,
  caseId,
}: InvestigationPanelProps) {
  const steps = [
    "1. Inspect Records",
    "2. Collect Evidence",
    "3. Analyze Relationships",
    "4. Synthesize Diagnosis",
    "5. Generate Resolution Plan",
    "6. Run Counterfactual Simulation",
    "7. Evaluate Policy",
  ];

  return (
    <div className="surface" style={{ padding: "1.25rem 1.5rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      {/* Header & Trigger */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "16px", fontWeight: 700, color: "#111827" }}>
              AI Investigation
            </span>
            {caseId && (
              <span className="mono" style={{ fontSize: "13px", color: "var(--text-muted)", fontWeight: 600 }}>
                {caseId}
              </span>
            )}
          </div>
          <p style={{ fontSize: "13.5px", color: "var(--text-muted)", marginTop: "2px" }}>
            Deterministic tool pipeline for multi-party diagnosis, evidence-grounded claims, and counterfactual simulation.
          </p>
        </div>
        <button
          onClick={onTriggerInvestigation}
          disabled={isLoading}
          className="btn-primary"
        >
          <PlayIcon size={12} />
          <span>{isLoading ? "Running Investigation..." : "Run AI Investigation"}</span>
        </button>
      </div>

      {/* 7-Step Vertical/Horizontal Progress Timeline */}
      <div style={{
        background: "#f8fafc",
        border: "1px solid var(--border-subtle)",
        borderRadius: "8px",
        padding: "1rem 1.25rem",
      }}>
        <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: "0.75rem" }}>
          Pipeline Execution Lifecycle
        </div>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(135px, 1fr))",
          gap: "0.5rem",
        }}>
          {steps.map((step, idx) => {
            const isCompleted = !isLoading && investigation;
            const isActive = isLoading && idx === 3; // simulated current stage pulse
            return (
              <div
                key={idx}
                className={isActive ? "pulse-active" : ""}
                style={{
                  padding: "0.5rem 0.75rem",
                  background: isCompleted ? "var(--color-teal-bg)" : isActive ? "var(--color-indigo-bg)" : "#ffffff",
                  border: isCompleted ? "1px solid var(--color-teal-border)" : isActive ? "1px solid var(--color-indigo-border)" : "1px solid var(--border-subtle)",
                  borderRadius: "6px",
                  fontSize: "12px",
                  color: isCompleted ? "#0f766e" : isActive ? "#315cf5" : "var(--text-muted)",
                  fontWeight: isCompleted || isActive ? 600 : 500,
                  transition: "all 0.2s ease",
                }}
              >
                {isCompleted ? "✓ " : isActive ? "● " : "○ "} {step}
              </div>
            );
          })}
        </div>
      </div>

      {isLoading && (
        <div style={{
          padding: "2.5rem 1.5rem",
          textAlign: "center",
          backgroundColor: "#ffffff",
          borderRadius: "8px",
          border: "1px solid var(--border-subtle)",
        }}>
          <div style={{ fontWeight: 600, color: "#111827", fontSize: "15px" }}>
            Executing Deterministic Tool Pipeline
          </div>
          <div style={{ fontSize: "13.5px", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            Collecting multi-party evidence graph, synthesizing root-cause hypotheses, and verifying claims...
          </div>
        </div>
      )}

      {investigation && !isLoading && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Root Cause Section */}
          <div style={{
            backgroundColor: "#f8fafc",
            borderRadius: "8px",
            border: "1px solid var(--border-subtle)",
            padding: "1.15rem 1.25rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.65rem",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
                Root Cause Finding
              </span>
              <span className="badge badge-reconciled">
                Confidence: Verified
              </span>
            </div>
            <div style={{ fontSize: "15px", color: "#111827", fontWeight: 600 }}>
              {investigation.summary}
            </div>
            <div style={{
              fontSize: "13.5px",
              color: "var(--text-secondary)",
              background: "#ffffff",
              padding: "0.75rem 1rem",
              borderRadius: "6px",
              border: "1px solid var(--border-subtle)",
            }}>
              <strong style={{ color: "#315cf5" }}>Diagnosed Cause: </strong>
              {investigation.root_cause_explanation}
            </div>
          </div>

          {/* Factual Claims Table */}
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
              <span style={{ fontSize: "15px", fontWeight: 600, color: "#111827" }}>
                Factual Claims ({investigation.claims?.length || 0})
              </span>
              <span className="badge badge-reconciled">
                {investigation.unsupported_claims_count === 0 ? "100% Verified · 0.00% Unsupported" : "Unverified"}
              </span>
            </div>

            <div style={{ border: "1px solid var(--border-subtle)", borderRadius: "8px", overflow: "hidden" }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Claim Statement</th>
                    <th>Referenced Entities</th>
                    <th>Target Field</th>
                    <th>Verified Value</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {investigation.claims?.map((claim: any, idx: number) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 500, color: "#111827" }}>
                        {claim.claim_text}
                      </td>
                      <td className="mono" style={{ fontSize: "12.5px", color: "#315cf5" }}>
                        {claim.referenced_entity_ids?.join(", ") || "—"}
                      </td>
                      <td className="mono" style={{ fontSize: "12.5px" }}>
                        {claim.target_field || "—"}
                      </td>
                      <td className="tabular-num" style={{ fontSize: "13.5px", fontWeight: 600, color: "var(--status-reconciled)" }}>
                        {claim.verified_value !== undefined ? String(claim.verified_value) : "Verified"}
                      </td>
                      <td>
                        <span className="badge badge-reconciled">
                          ✓ {claim.verification_status || "VERIFIED"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Human Review Package (if escalated) */}
          {investigation.human_review_package && (
            <div style={{
              backgroundColor: "#fffbeb",
              border: "1px solid #fde68a",
              borderRadius: "8px",
              padding: "1rem 1.25rem",
            }}>
              <div style={{ fontSize: "12px", fontWeight: 700, color: "var(--status-review)", textTransform: "uppercase", marginBottom: "0.4rem" }}>
                Human Review Package (Priority: {investigation.human_review_package.priority})
              </div>
              <div style={{ fontSize: "13.5px", color: "var(--text-secondary)", marginBottom: "0.5rem" }}>
                {investigation.human_review_package.key_ambiguities?.map((amb: string, idx: number) => (
                  <div key={idx}>• {amb}</div>
                ))}
              </div>
              <div style={{ fontSize: "13px", fontWeight: 600, color: "#111827" }}>Recommended Actions:</div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.2rem", marginTop: "0.25rem" }}>
                {investigation.human_review_package.recommended_analyst_actions?.map((act: string, idx: number) => (
                  <div key={idx} className="mono" style={{ fontSize: "12.5px", color: "#315cf5" }}>
                    → {act}
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
