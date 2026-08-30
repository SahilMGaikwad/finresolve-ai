"use client";

import { formatINR } from "@/lib/formatters";
import { DiscrepancyBadge } from "../cases/DiscrepancyBadge";

interface BeforeAfterTableProps {
  plan?: {
    plan_id: string;
    overall_strategy: string;
    steps: any[];
    simulation_result?: any;
    policy_decision?: any;
  } | null;
}

export function BeforeAfterTable({ plan }: BeforeAfterTableProps) {
  if (!plan) {
    return (
      <div className="card" style={{ textAlign: "center", padding: "2rem" }}>
        <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
          Run an investigation to generate and simulate a counterfactual resolution plan.
        </p>
      </div>
    );
  }

  const sim = plan.simulation_result;
  const policy = plan.policy_decision;
  const delta = sim?.cumulative_delta;

  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#fff" }}>
            Counterfactual Resolution Simulation
          </h3>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            Closed-loop virtual re-reconciliation and zero-sum double-entry ledger delta.
          </p>
        </div>
        {policy && <DiscrepancyBadge status={policy.decision} label={`Policy: ${policy.decision}`} />}
      </div>

      {/* Plan Strategy Banner */}
      <div style={{
        backgroundColor: "var(--bg-secondary)",
        padding: "1rem",
        borderRadius: "6px",
        border: "1px solid var(--border-subtle)",
        fontSize: "0.85rem",
      }}>
        <div style={{ fontWeight: 600, color: "#fff", marginBottom: "0.25rem" }}>Strategy:</div>
        <div style={{ color: "var(--text-accent)" }}>{plan.overall_strategy}</div>
      </div>

      {/* Financial Delta Grid */}
      {delta && (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "1rem",
        }}>
          <div style={{ backgroundColor: "var(--bg-secondary)", padding: "1rem", borderRadius: "6px", border: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Δ Merchant Balance</div>
            <div className="mono" style={{ fontSize: "1.2rem", fontWeight: 700, color: delta.merchant_balance_delta_minor >= 0 ? "var(--status-reconciled)" : "var(--status-discrepancy)", marginTop: "0.25rem" }}>
              {formatINR(delta.merchant_balance_delta_minor)}
            </div>
          </div>

          <div style={{ backgroundColor: "var(--bg-secondary)", padding: "1rem", borderRadius: "6px", border: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Δ Platform Fee</div>
            <div className="mono" style={{ fontSize: "1.2rem", fontWeight: 700, color: "#fff", marginTop: "0.25rem" }}>
              {formatINR(delta.fee_balance_delta_minor)}
            </div>
          </div>

          <div style={{ backgroundColor: "var(--bg-secondary)", padding: "1rem", borderRadius: "6px", border: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Δ GST Tax Liability</div>
            <div className="mono" style={{ fontSize: "1.2rem", fontWeight: 700, color: "#fff", marginTop: "0.25rem" }}>
              {formatINR(delta.tax_balance_delta_minor)}
            </div>
          </div>

          <div style={{ backgroundColor: "var(--bg-secondary)", padding: "1rem", borderRadius: "6px", border: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Conservation Law</div>
            <div className="mono" style={{ fontSize: "1rem", fontWeight: 700, color: delta.is_balanced ? "var(--status-reconciled)" : "var(--status-discrepancy)", marginTop: "0.35rem" }}>
              {delta.is_balanced ? "✓ ZERO-SUM BALANCED" : "⚠️ IMBALANCED"}
            </div>
          </div>
        </div>
      )}

      {/* Plan Steps Table */}
      <div>
        <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "#fff", marginBottom: "0.5rem" }}>
          Sequential Corrective Steps ({plan.steps?.length || 0})
        </h4>
        <table className="data-table">
          <thead>
            <tr>
              <th>Step</th>
              <th>Action Type</th>
              <th>Target Record</th>
              <th>Rationale</th>
            </tr>
          </thead>
          <tbody>
            {plan.steps?.map((step: any) => (
              <tr key={`step-${step.step_number}`}>
                <td className="mono">#{step.step_number}</td>
                <td className="mono" style={{ fontWeight: 600, color: "#fff" }}>
                  {step.action?.action_type?.toUpperCase()}
                </td>
                <td className="mono" style={{ color: "var(--text-accent)" }}>
                  {step.action?.target_record_id}
                </td>
                <td>{step.rationale}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
