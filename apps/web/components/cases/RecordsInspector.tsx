"use client";

import { useState } from "react";
import { formatDateTime, formatINR } from "@/lib/formatters";

interface RecordsInspectorProps {
  observed: {
    payments: any[];
    settlements: any[];
    fees: any[];
    refunds: any[];
    ledger_entries: any[];
    orders?: any[];
  };
}

export function RecordsInspector({ observed }: RecordsInspectorProps) {
  const [activeTab, setActiveTab] = useState<"payments" | "settlements" | "fees" | "refunds" | "ledger">("payments");
  const [selectedRawRecord, setSelectedRawRecord] = useState<any | null>(null);

  const tabs = [
    { id: "payments", label: `Payments (${observed.payments?.length || 0})` },
    { id: "settlements", label: `Settlements (${observed.settlements?.length || 0})` },
    { id: "fees", label: `Fees (${observed.fees?.length || 0})` },
    { id: "refunds", label: `Refunds (${observed.refunds?.length || 0})` },
    { id: "ledger", label: `General Ledger (${observed.ledger_entries?.length || 0})` },
  ];

  return (
    <div className="surface" style={{ overflow: "hidden" }}>
      {/* Sub-Tabs */}
      <div style={{
        display: "flex",
        borderBottom: "1px solid var(--border-subtle)",
        backgroundColor: "#f8fafc",
        overflowX: "auto",
      }}>
        {tabs.map((t) => {
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => {
                setActiveTab(t.id as any);
                setSelectedRawRecord(null);
              }}
              style={{
                padding: "0.65rem 1.15rem",
                fontSize: "0.78rem",
                fontWeight: isActive ? 700 : 500,
                color: isActive ? "#2563eb" : "var(--text-muted)",
                borderBottom: isActive ? "2px solid #2563eb" : "2px solid transparent",
                backgroundColor: isActive ? "#ffffff" : "transparent",
                whiteSpace: "nowrap",
                transition: "all 0.12s ease",
              }}
            >
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Main Table */}
      <div style={{ overflowX: "auto" }}>
        {activeTab === "payments" && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Payment ID</th>
                <th>Order Ref</th>
                <th>Amount</th>
                <th>Method</th>
                <th>Status</th>
                <th>Captured At</th>
                <th style={{ textAlign: "right" }}>Raw</th>
              </tr>
            </thead>
            <tbody>
              {observed.payments?.map((p: any) => (
                <tr key={p.payment_id}>
                  <td className="mono" style={{ fontWeight: 700, color: "#0f172a" }}>{p.payment_id}</td>
                  <td className="mono" style={{ color: "var(--text-secondary)" }}>{p.order_id}</td>
                  <td className="mono" style={{ fontWeight: 800, color: "#0f172a" }}>
                    {formatINR(p.amount?.amount_minor || 0)}
                  </td>
                  <td>
                    <span className="badge badge-info" style={{ fontSize: "0.62rem" }}>{p.method}</span>
                  </td>
                  <td>
                    <span className="badge badge-reconciled" style={{ fontSize: "0.62rem" }}>{p.status}</span>
                  </td>
                  <td className="mono" style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                    {formatDateTime(p.captured_at)}
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      onClick={() => setSelectedRawRecord(p)}
                      className="btn-secondary"
                      style={{ fontSize: "0.65rem", padding: "0.15rem 0.4rem" }}
                    >
                      JSON
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {activeTab === "settlements" && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Settlement ID</th>
                <th>Payment Ref</th>
                <th>Gross</th>
                <th>Fee</th>
                <th>Net Settled</th>
                <th>Status</th>
                <th>UTR Reference</th>
                <th style={{ textAlign: "right" }}>Raw</th>
              </tr>
            </thead>
            <tbody>
              {observed.settlements?.map((s: any) => (
                <tr key={s.settlement_id}>
                  <td className="mono" style={{ fontWeight: 700, color: "#0f172a" }}>{s.settlement_id}</td>
                  <td className="mono" style={{ color: "var(--text-secondary)" }}>{s.payment_id}</td>
                  <td className="mono">{formatINR(s.gross_amount?.amount_minor || 0)}</td>
                  <td className="mono" style={{ color: "var(--status-discrepancy)" }}>
                    -{formatINR(s.fee_amount?.amount_minor || 0)}
                  </td>
                  <td className="mono" style={{ fontWeight: 800, color: "var(--status-reconciled)" }}>
                    {formatINR(s.net_amount?.amount_minor || 0)}
                  </td>
                  <td>
                    <span className="badge badge-reconciled" style={{ fontSize: "0.62rem" }}>{s.status}</span>
                  </td>
                  <td className="mono" style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{s.utr}</td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      onClick={() => setSelectedRawRecord(s)}
                      className="btn-secondary"
                      style={{ fontSize: "0.65rem", padding: "0.15rem 0.4rem" }}
                    >
                      JSON
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {activeTab === "fees" && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Fee ID</th>
                <th>Type</th>
                <th>Payment Ref</th>
                <th>Fee Rate</th>
                <th>Fee Amount</th>
                <th>Applied Timestamp</th>
                <th style={{ textAlign: "right" }}>Raw</th>
              </tr>
            </thead>
            <tbody>
              {observed.fees?.map((f: any) => (
                <tr key={f.fee_id}>
                  <td className="mono" style={{ fontWeight: 700, color: "#0f172a" }}>{f.fee_id}</td>
                  <td>
                    <span className="badge badge-info" style={{ fontSize: "0.62rem" }}>{f.fee_type}</span>
                  </td>
                  <td className="mono" style={{ color: "var(--text-secondary)" }}>{f.payment_id}</td>
                  <td className="mono">{(f.rate_bps / 100).toFixed(2)}% ({f.rate_bps} bps)</td>
                  <td className="mono" style={{ fontWeight: 800, color: "#0f172a" }}>
                    {formatINR(f.amount?.amount_minor || 0)}
                  </td>
                  <td className="mono" style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                    {formatDateTime(f.applied_at)}
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      onClick={() => setSelectedRawRecord(f)}
                      className="btn-secondary"
                      style={{ fontSize: "0.65rem", padding: "0.15rem 0.4rem" }}
                    >
                      JSON
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {activeTab === "refunds" && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Refund ID</th>
                <th>Payment Ref</th>
                <th>Refund Amount</th>
                <th>Reason</th>
                <th>Status</th>
                <th style={{ textAlign: "right" }}>Raw</th>
              </tr>
            </thead>
            <tbody>
              {(!observed.refunds || observed.refunds.length === 0) ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
                    No refund entries for this case.
                  </td>
                </tr>
              ) : (
                observed.refunds.map((r: any) => (
                  <tr key={r.refund_id}>
                    <td className="mono" style={{ fontWeight: 700, color: "#0f172a" }}>{r.refund_id}</td>
                    <td className="mono">{r.payment_id}</td>
                    <td className="mono" style={{ color: "var(--status-discrepancy)", fontWeight: 800 }}>
                      -{formatINR(r.amount?.amount_minor || 0)}
                    </td>
                    <td>{r.reason || "Customer Return"}</td>
                    <td>
                      <span className="badge badge-review" style={{ fontSize: "0.62rem" }}>{r.status}</span>
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <button
                        onClick={() => setSelectedRawRecord(r)}
                        className="btn-secondary"
                        style={{ fontSize: "0.65rem", padding: "0.15rem 0.4rem" }}
                      >
                        JSON
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}

        {activeTab === "ledger" && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Entry ID</th>
                <th>Reference ID</th>
                <th>Account Type</th>
                <th>Debit (Dr)</th>
                <th>Credit (Cr)</th>
                <th>Balance</th>
                <th style={{ textAlign: "right" }}>Raw</th>
              </tr>
            </thead>
            <tbody>
              {observed.ledger_entries?.map((l: any) => (
                <tr key={l.entry_id}>
                  <td className="mono" style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                    {formatDateTime(l.posted_at)}
                  </td>
                  <td className="mono" style={{ fontWeight: 700, color: "#0f172a" }}>{l.entry_id}</td>
                  <td className="mono" style={{ color: "var(--text-secondary)" }}>{l.reference_id}</td>
                  <td>
                    <span className={`badge badge-${l.entry_type === "credit" ? "reconciled" : "info"}`} style={{ fontSize: "0.62rem" }}>
                      {l.entry_type}
                    </span>
                  </td>
                  <td className="mono" style={{ color: l.debit?.amount_minor > 0 ? "var(--status-discrepancy)" : "var(--text-muted)" }}>
                    {l.debit?.amount_minor > 0 ? formatINR(l.debit.amount_minor) : "—"}
                  </td>
                  <td className="mono" style={{ color: l.credit?.amount_minor > 0 ? "var(--status-reconciled)" : "var(--text-muted)", fontWeight: 700 }}>
                    {l.credit?.amount_minor > 0 ? formatINR(l.credit.amount_minor) : "—"}
                  </td>
                  <td className="mono" style={{ fontWeight: 800, color: "#0f172a" }}>
                    {formatINR(l.balance_after?.amount_minor || 0)}
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      onClick={() => setSelectedRawRecord(l)}
                      className="btn-secondary"
                      style={{ fontSize: "0.65rem", padding: "0.15rem 0.4rem" }}
                    >
                      JSON
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Raw Record JSON Drawer */}
      {selectedRawRecord && (
        <div style={{
          padding: "0.85rem 1.15rem",
          background: "#f8fafc",
          borderTop: "1px solid var(--border-subtle)",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
            <span className="mono" style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700 }}>
              RECORD JSON PAYLOAD
            </span>
            <button
              onClick={() => setSelectedRawRecord(null)}
              className="btn-secondary"
              style={{ fontSize: "0.65rem", padding: "0.15rem 0.35rem" }}
            >
              Close
            </button>
          </div>
          <pre className="mono" style={{
            background: "#ffffff",
            padding: "0.75rem",
            borderRadius: "6px",
            fontSize: "0.72rem",
            color: "var(--text-primary)",
            overflowX: "auto",
            border: "1px solid var(--border-subtle)",
          }}>
            {JSON.stringify(selectedRawRecord, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
