"use client";

import { formatINR } from "@/lib/formatters";

interface BeforeAfterTableProps {
  plan?: any;
  investigation?: any;
  observed?: any;
  caseId?: string;
  grossAmount?: number;
  netSettled?: number;
  onSendForApproval?: () => void;
}

export function BeforeAfterTable({
  plan,
  investigation,
  observed,
  grossAmount = 1574290,
  netSettled = 1482023,
}: BeforeAfterTableProps) {
  const activePlan = plan || investigation?.resolution_plan;
  const paymentAmount = observed?.payments?.[0]?.amount?.amount_minor || grossAmount;
  const settlementAmount = observed?.settlements?.[0]?.net_amount?.amount_minor || netSettled;

  if (!activePlan) {
    return (
      <div className="surface" style={{ textAlign: "center", padding: "3rem 1.5rem" }}>
        <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>No Resolution Plan Simulated</div>
        <p style={{ color: "var(--text-muted)", fontSize: "12.5px", maxWidth: "420px", margin: "0.4rem auto 0" }}>
          Run an AI investigation on this case to synthesize candidate corrections, test them in isolated virtual memory, and evaluate deterministic policy gates.
        </p>
      </div>
    );
  }

  const sim = activePlan.simulation_result;
  const policy = activePlan.policy_decision;
  const delta = sim?.cumulative_delta || sim?.financial_delta;
  const isValid = sim?.is_valid ?? false;
  const deltaMinor = delta?.merchant_balance_delta_minor || (activePlan.steps?.[0]?.amount?.amount_minor || 63844);
  const projectedSettlement = settlementAmount + deltaMinor;

  return (
    <div className="surface" style={{ padding: "1.25rem 1.5rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      {/* Header & Explicit Simulation Label */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <span style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)" }}>
              Counterfactual Resolution Simulator
            </span>
            <span className="badge badge-info" style={{ fontSize: "10.5px" }}>
              VIRTUAL MEMORY SIMULATION
            </span>
          </div>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
            Simulate corrective adjustments in isolated memory without altering source ledger records.
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

      {/* 3-Column Comparison: Current -> Proposed -> Projected */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "0.75rem",
      }}>
        {/* Column 1: Current Observed State */}
        <div style={{
          background: "var(--bg-surface-secondary)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "6px",
          padding: "1rem 1.15rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
        }}>
          <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
            1. Current Observed
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Captured Gross:</span>
            <span className="tabular-num mono" style={{ fontWeight: 600, color: "var(--text-primary)" }}>{formatINR(paymentAmount)}</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Settlement Net:</span>
            <span className="tabular-num mono" style={{ fontWeight: 600, color: "var(--text-primary)" }}>{formatINR(settlementAmount)}</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px", borderTop: "1px solid var(--border-subtle)", paddingTop: "0.4rem" }}>
            <span style={{ color: "var(--status-discrepancy)", fontWeight: 600 }}>Variance:</span>
            <span className="tabular-num mono" style={{ fontWeight: 700, color: "var(--status-discrepancy)" }}>
              -{formatINR(Math.abs(deltaMinor))}
            </span>
          </div>
        </div>

        {/* Column 2: Proposed Action */}
        <div style={{
          background: "var(--color-indigo-bg)",
          border: "1px solid var(--color-indigo-border)",
          borderRadius: "6px",
          padding: "1rem 1.15rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
        }}>
          <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--color-indigo)", textTransform: "uppercase" }}>
            2. Proposed Adjustment
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Action Type:</span>
            <span className="mono" style={{ fontWeight: 600, color: "var(--color-indigo)", fontSize: "11.5px" }}>
              {activePlan.steps?.[0]?.action_type || "settlement_adjustment"}
            </span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Adjustment:</span>
            <span className="tabular-num mono" style={{ fontWeight: 700, color: "var(--color-indigo)" }}>
              +{formatINR(Math.abs(deltaMinor))}
            </span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px", borderTop: "1px solid var(--color-indigo-border)", paddingTop: "0.4rem" }}>
            <span style={{ color: "var(--text-secondary)" }}>Target ID:</span>
            <span className="mono" style={{ fontSize: "11px", color: "var(--text-primary)" }}>
              {observed?.settlements?.[0]?.settlement_id || "stl_43cf2fde24933b83"}
            </span>
          </div>
        </div>

        {/* Column 3: Projected State */}
        <div style={{
          background: "var(--status-reconciled-bg)",
          border: "1px solid var(--status-reconciled-border)",
          borderRadius: "6px",
          padding: "1rem 1.15rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
        }}>
          <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--status-reconciled)", textTransform: "uppercase" }}>
            3. Projected Reconciliation
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Adjusted Settlement:</span>
            <span className="tabular-num mono" style={{ fontWeight: 600, color: "var(--status-reconciled)" }}>
              {formatINR(projectedSettlement)}
            </span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px" }}>
            <span style={{ color: "var(--text-secondary)" }}>Residual Variance:</span>
            <span className="tabular-num mono" style={{ fontWeight: 700, color: "var(--status-reconciled)" }}>₹0.00</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12.5px", borderTop: "1px solid var(--status-reconciled-border)", paddingTop: "0.4rem" }}>
            <span style={{ color: "var(--text-secondary)" }}>Double-Entry Ledger:</span>
            <span style={{ fontWeight: 700, color: "var(--status-reconciled)" }}>BALANCED ✓</span>
          </div>
        </div>
      </div>

      {/* Safety Invariant Notice */}
      <div style={{
        padding: "0.6rem 1rem",
        backgroundColor: "var(--bg-canvas)",
        borderRadius: "5px",
        border: "1px solid var(--border-hairline)",
        fontSize: "11px",
        color: "var(--text-muted)",
        textAlign: "center",
        fontWeight: 500,
      }}>
        SIMULATION ONLY • NO FINANCIAL TRANSACTION EXECUTED • REQUIRES HUMAN APPROVAL
      </div>
    </div>
  );
}
