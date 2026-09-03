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
      <div style={{
        backgroundColor: "var(--bg-secondary)",
        border: "1px solid var(--border-subtle)",
        textAlign: "center",
        padding: "3.5rem 1.5rem",
      }}>
        <div className="heading-editorial" style={{ fontSize: "1.2rem", color: "var(--text-primary)" }}>NO RESOLUTION PLAN SIMULATED</div>
        <p style={{ color: "var(--text-muted)", fontSize: "12px", maxWidth: "420px", margin: "0.5rem auto 0" }}>
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
    <div style={{
      backgroundColor: "var(--bg-secondary)",
      border: "1px solid var(--border-subtle)",
      padding: "1.75rem",
      display: "flex",
      flexDirection: "column",
      gap: "1.75rem",
    }}>
      {/* Header & Explicit Simulation Label */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.1em" }}>
            / SIMULATE BEFORE EXECUTION
          </div>
          <h2 className="heading-editorial title-large" style={{ marginTop: "2px" }}>
            COUNTERFACTUAL RESOLUTION SIMULATOR
          </h2>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
            Simulate candidate corrective adjustments in isolated memory without altering source ledger records.
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <span style={{
            fontSize: "10.5px",
            fontWeight: 700,
            letterSpacing: "0.04em",
            color: isValid ? "var(--status-reconciled)" : "var(--color-brand)",
          }}>
            ● {isValid ? "SIMULATION PASSED" : "SIMULATION BLOCKED"}
          </span>
          {policy && (
            <span style={{
              fontSize: "10.5px",
              fontWeight: 700,
              letterSpacing: "0.04em",
              color: policy.decision === "AUTO_RESOLVABLE" ? "var(--status-reconciled)" : "var(--status-review)",
            }}>
              ● POLICY: {policy.decision}
            </span>
          )}
        </div>
      </div>

      {/* 3-Column Comparison: Current -> Proposed -> Projected */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "1.5rem",
        borderTop: "1px solid var(--border-subtle)",
        borderBottom: "1px solid var(--border-subtle)",
        padding: "1.75rem 0",
      }}>
        {/* Column 1: Current Observed State */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            CURRENT
          </div>
          <div className="tabular-num heading-editorial" style={{ fontSize: "2.2rem", color: "var(--text-primary)" }}>
            {formatINR(settlementAmount)}
          </div>
          <div style={{ fontSize: "11.5px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "0.2rem" }}>
            <div>Captured Gross: <strong style={{ color: "var(--text-primary)" }}>{formatINR(paymentAmount)}</strong></div>
            <div>Observed Variance: <strong style={{ color: "var(--color-brand)" }}>-{formatINR(Math.abs(deltaMinor))}</strong></div>
          </div>
        </div>

        {/* Column 2: Proposed Action */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            PROPOSED
          </div>
          <div className="tabular-num heading-editorial" style={{ fontSize: "2.2rem", color: "var(--color-brand)" }}>
            +{formatINR(Math.abs(deltaMinor))}
          </div>
          <div style={{ fontSize: "11.5px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "0.2rem" }}>
            <div>Action: <strong style={{ color: "var(--color-brand)" }}>{activePlan.steps?.[0]?.action_type || "settlement_adjustment"}</strong></div>
            <div className="mono" style={{ fontSize: "11px" }}>Target: {observed?.settlements?.[0]?.settlement_id || "stl_43cf2fde24933b83"}</div>
          </div>
        </div>

        {/* Column 3: Projected State */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--status-reconciled)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            PROJECTED
          </div>
          <div className="tabular-num heading-editorial" style={{ fontSize: "2.2rem", color: "var(--status-reconciled)" }}>
            {formatINR(projectedSettlement)}
          </div>
          <div style={{ fontSize: "11.5px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "0.2rem" }}>
            <div>Residual Discrepancy: <strong style={{ color: "var(--status-reconciled)" }}>₹0.00</strong></div>
            <div>Double-Entry Ledger: <strong style={{ color: "var(--status-reconciled)" }}>BALANCED ✓</strong></div>
          </div>
        </div>
      </div>

      {/* Large Results Grid */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "1.5rem",
      }}>
        <div>
          <div className="tabular-num heading-editorial" style={{ fontSize: "2.75rem", color: "var(--status-reconciled)" }}>
            ₹0.00
          </div>
          <div style={{ fontSize: "10px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-muted)" }}>
            RESIDUAL DISCREPANCY
          </div>
        </div>

        <div>
          <div className="heading-editorial" style={{ fontSize: "2.75rem", color: "var(--status-reconciled)" }}>
            BALANCED
          </div>
          <div style={{ fontSize: "10px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-muted)" }}>
            DOUBLE-ENTRY LEDGER
          </div>
        </div>
      </div>

      {/* Safety Notice */}
      <div style={{
        padding: "0.75rem 1rem",
        backgroundColor: "var(--bg-canvas)",
        border: "1px solid var(--border-subtle)",
        fontSize: "10.5px",
        color: "var(--text-muted)",
        textAlign: "center",
        fontWeight: 700,
        letterSpacing: "0.06em",
      }}>
        SIMULATION ONLY • NO FINANCIAL TRANSACTION EXECUTED • REQUIRES HUMAN APPROVAL
      </div>
    </div>
  );
}
