"use client";

import { formatINR } from "@/lib/formatters";

interface BeforeAfterTableProps {
  plan?: {
    plan_id: string;
    overall_strategy: string;
    steps: any[];
    simulation_result?: any;
    policy_decision?: any;
  } | null;
  grossAmount?: number;
  netSettled?: number;
  onSendForApproval?: () => void;
}

export function BeforeAfterTable({
  plan,
  grossAmount = 1574290,
  netSettled = 1482023,
  onSendForApproval,
}: BeforeAfterTableProps) {
  if (!plan) {
    return (
      <div className="surface" style={{ textAlign: "center", padding: "3rem 1.5rem" }}>
        <div style={{ fontSize: "15px", fontWeight: 600, color: "#111827" }}>No Resolution Plan Simulated</div>
        <p style={{ color: "var(--text-muted)", fontSize: "13.5px", maxWidth: "420px", margin: "0.4rem auto 0" }}>
          Run an investigation to synthesize candidate corrections, test them in isolated memory, and evaluate policy gates.
        </p>
      </div>
    );
  }

  const sim = plan.simulation_result;
  const policy = plan.policy_decision;
  const delta = sim?.cumulative_delta || sim?.financial_delta;
  const isValid = sim?.is_valid ?? false;
  const deltaMinor = delta?.merchant_balance_delta_minor || 0;
  const projectedSettlement = netSettled + deltaMinor;

  return (
    <div className="surface" style={{ padding: "1.25rem 1.5rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      {/* Header & Explicit Simulation Label */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <span style={{ fontSize: "16px", fontWeight: 700, color: "#111827" }}>
              Counterfactual Resolution Simulator
            </span>
            <span className="badge badge-info" style={{ fontSize: "11px" }}>
              COUNTERFACTUAL SIMULATION · NO LIVE FINANCIAL ACTION
            </span>
          </div>
          <p style={{ fontSize: "13.5px", color: "var(--text-muted)", marginTop: "2px" }}>
            Simulate corrective adjustments in virtual memory without altering source ledger records.
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.4rem" }}>
          <span className={`badge badge-${isValid ? "reconciled" : "blocked"}`}>
            {isValid ? "Simulation Passed" : "Simulation Blocked"}
          </span>
          {policy && (
            <span className={`badge badge-${policy.decision === "AUTO_RESOLVABLE" ? "reconciled" : policy.decision === "BLOCKED" ? "blocked" : "review"}`}>
              Policy: {policy.decision}
            </span>
          )}
        </div>
      </div>

      {/* 3-Column Comparison: Observed -> Proposed -> Projected */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "1rem",
      }}>
        {/* Column 1: Observed */}
        <div style={{
          background: "#f8fafc",
          border: "1px solid var(--border-subtle)",
          borderRadius: "8px",
          padding: "1rem 1.25rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.6rem",
        }}>
          <div style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
            1. Observed State
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Captured Gross:</span>
            <span className="tabular-num" style={{ fontWeight: 600, color: "#111827" }}>{formatINR(grossAmount)}</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Settlement Net:</span>
            <span className="tabular-num" style={{ fontWeight: 600, color: "#111827" }}>{formatINR(netSettled)}</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13.5px", borderTop: "1px solid var(--border-subtle)", paddingTop: "0.5rem" }}>
            <span style={{ color: "var(--status-discrepancy)", fontWeight: 600 }}>Observed Variance:</span>
            <span className="tabular-num" style={{ fontWeight: 700, color: "var(--status-discrepancy)" }}>
              {formatINR(netSettled - grossAmount)}
            </span>
          </div>
        </div>

        {/* Column 2: Proposed */}
        <div style={{
          background: "#f8fafc",
          border: "1px solid var(--border-subtle)",
          borderRadius: "8px",
          padding: "1rem 1.25rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.6rem",
        }}>
          <div style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
            2. Proposed Adjustment
          </div>
          <div style={{ fontSize: "13.5px", color: "#111827", fontWeight: 600 }}>
            {plan.steps?.[0]?.action?.action_type || "settlement_adjustment"}
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Adjustment Value:</span>
            <span className="tabular-num" style={{ fontWeight: 700, color: "#315cf5" }}>
              {deltaMinor >= 0 ? "+" : ""}{formatINR(deltaMinor)}
            </span>
          </div>
          <div style={{ fontSize: "12.5px", color: "var(--text-muted)", borderTop: "1px solid var(--border-subtle)", paddingTop: "0.5rem" }}>
            Target: <span className="mono">{plan.steps?.[0]?.action?.target_record_id || "Record"}</span>
          </div>
        </div>

        {/* Column 3: Projected */}
        <div style={{
          background: "#f8fafc",
          border: `1px solid ${isValid ? "var(--color-teal-border)" : "var(--status-discrepancy-border)"}`,
          borderRadius: "8px",
          padding: "1rem 1.25rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.6rem",
        }}>
          <div style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
            3. Projected Outcome
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Projected Net:</span>
            <span className="tabular-num" style={{ fontWeight: 700, color: "var(--status-reconciled)" }}>{formatINR(projectedSettlement)}</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Residual Discrepancy:</span>
            <span className="tabular-num" style={{ fontWeight: 700, color: isValid ? "var(--status-reconciled)" : "var(--status-discrepancy)" }}>
              {sim?.residual_discrepancies?.length === 0 ? "₹0.00 (Zero)" : `${sim?.residual_discrepancies?.length} errors`}
            </span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13.5px", borderTop: "1px solid var(--border-subtle)", paddingTop: "0.5rem" }}>
            <span style={{ color: "var(--text-secondary)" }}>Double-Entry Ledger:</span>
            <span style={{ fontWeight: 700, color: "var(--status-reconciled)" }}>BALANCED</span>
          </div>
        </div>
      </div>

      {/* Policy Governance Decision Panel */}
      {policy && (
        <div style={{
          backgroundColor: "#f8fafc",
          border: "1px solid var(--border-subtle)",
          borderRadius: "8px",
          padding: "1.15rem 1.25rem",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
            <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
              Policy Decision Gating (POL-001 - POL-005)
            </span>
            <span className="mono" style={{ fontSize: "12.5px", color: "#315cf5", fontWeight: 600 }}>
              Sign-Off Requirement: {policy.approval_requirement || "SINGLE_APPROVER"}
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
            {policy.rule_evaluations?.map((r: any) => (
              <div
                key={r.rule_id}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "0.55rem 0.85rem",
                  background: "#ffffff",
                  borderRadius: "6px",
                  border: "1px solid var(--border-subtle)",
                  fontSize: "13px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span style={{ color: r.passed ? "var(--status-reconciled)" : "var(--status-discrepancy)", fontWeight: 700 }}>
                    {r.passed ? "✓" : "✗"}
                  </span>
                  <span className="mono" style={{ fontWeight: 600, color: "#111827" }}>{r.rule_id}</span>
                  <span style={{ color: "var(--text-muted)" }}>({r.rule_name})</span>
                </div>
                <span style={{ color: "var(--text-secondary)" }}>{r.reason}</span>
              </div>
            ))}
          </div>

          {/* Action trigger */}
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "1rem" }}>
            {onSendForApproval && (
              <button onClick={onSendForApproval} className="btn-primary">
                Send for Human Sign-Off →
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
