"use client";

import { useState } from "react";
import { formatDateTime, formatINR } from "@/lib/formatters";
import { DiscrepancyBadge } from "./DiscrepancyBadge";

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

  const tabs = [
    { id: "payments", label: `Payments (${observed.payments?.length || 0})` },
    { id: "settlements", label: `Settlements (${observed.settlements?.length || 0})` },
    { id: "fees", label: `Fees (${observed.fees?.length || 0})` },
    { id: "refunds", label: `Refunds (${observed.refunds?.length || 0})` },
    { id: "ledger", label: `Double-Entry Ledger (${observed.ledger_entries?.length || 0})` },
  ];

  return (
    <div className="card" style={{ padding: "0" }}>
      {/* Tab Navigation */}
      <div style={{
        display: "flex",
        borderBottom: "1px solid var(--border-subtle)",
        backgroundColor: "var(--bg-secondary)",
        borderTopLeftRadius: "8px",
        borderTopRightRadius: "8px",
      }}>
        {tabs.map((t) => {
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              style={{
                padding: "0.85rem 1.25rem",
                fontSize: "0.85rem",
                fontWeight: isActive ? 600 : 400,
                color: isActive ? "#ffffff" : "var(--text-muted)",
                borderBottom: isActive ? "2px solid #3b82f6" : "2px solid transparent",
                backgroundColor: isActive ? "var(--bg-card)" : "transparent",
              }}
            >
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div style={{ overflowX: "auto" }}>
        {activeTab === "payments" && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Payment ID</th>
                <th>Order ID</th>
                <th>Method</th>
                <th>Status</th>
                <th>Captured At</th>
                <th style={{ textAlign: "right" }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {observed.payments?.map((p) => (
                <tr key={p.payment_id}>
                  <td className="mono" style={{ color: "var(--text-accent)" }}>{p.payment_id}</td>
                  <td className="mono">{p.order_id || "—"}</td>
                  <td>{p.method}</td>
                  <td><DiscrepancyBadge status={p.status} /></td>
                  <td className="mono">{formatDateTime(p.captured_at)}</td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 600, color: "#fff" }}>
                    {formatINR(p.amount?.amount_minor)}
                  </td>
                </tr>
              ))}
              {(!observed.payments || observed.payments.length === 0) && (
                <tr><td colSpan={6} style={{ textAlign: "center", color: "var(--text-muted)" }}>No payment records found</td></tr>
              )}
            </tbody>
          </table>
        )}

        {activeTab === "settlements" && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Settlement ID</th>
                <th>Payment ID</th>
                <th>UTR</th>
                <th>Status</th>
                <th>Settled At</th>
                <th style={{ textAlign: "right" }}>Gross</th>
                <th style={{ textAlign: "right" }}>Fee</th>
                <th style={{ textAlign: "right" }}>Net Amount</th>
              </tr>
            </thead>
            <tbody>
              {observed.settlements?.map((s) => (
                <tr key={s.settlement_id}>
                  <td className="mono" style={{ color: "var(--text-accent)" }}>{s.settlement_id}</td>
                  <td className="mono">{s.payment_id}</td>
                  <td className="mono">{s.utr || "—"}</td>
                  <td><DiscrepancyBadge status={s.status} /></td>
                  <td className="mono">{formatDateTime(s.settled_at)}</td>
                  <td className="mono" style={{ textAlign: "right" }}>{formatINR(s.gross_amount?.amount_minor)}</td>
                  <td className="mono" style={{ textAlign: "right", color: "var(--status-discrepancy)" }}>
                    -{formatINR(s.fee_amount?.amount_minor)}
                  </td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 600, color: "var(--status-reconciled)" }}>
                    {formatINR(s.net_amount?.amount_minor)}
                  </td>
                </tr>
              ))}
              {(!observed.settlements || observed.settlements.length === 0) && (
                <tr><td colSpan={8} style={{ textAlign: "center", color: "var(--text-muted)" }}>No settlement records found</td></tr>
              )}
            </tbody>
          </table>
        )}

        {activeTab === "fees" && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Fee ID</th>
                <th>Fee Type</th>
                <th>Rate (bps)</th>
                <th>Applied At</th>
                <th style={{ textAlign: "right" }}>Fee Amount</th>
              </tr>
            </thead>
            <tbody>
              {observed.fees?.map((f) => (
                <tr key={f.fee_id}>
                  <td className="mono" style={{ color: "var(--text-accent)" }}>{f.fee_id}</td>
                  <td>{f.fee_type?.replace(/_/g, " ").toUpperCase()}</td>
                  <td className="mono">{f.rate_bps} bps</td>
                  <td className="mono">{formatDateTime(f.applied_at)}</td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 600, color: "#fff" }}>
                    {formatINR(f.amount?.amount_minor)}
                  </td>
                </tr>
              ))}
              {(!observed.fees || observed.fees.length === 0) && (
                <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)" }}>No fee records found</td></tr>
              )}
            </tbody>
          </table>
        )}

        {activeTab === "refunds" && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Refund ID</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Processed At</th>
                <th style={{ textAlign: "right" }}>Refund Amount</th>
              </tr>
            </thead>
            <tbody>
              {observed.refunds?.map((r) => (
                <tr key={r.refund_id}>
                  <td className="mono" style={{ color: "var(--text-accent)" }}>{r.refund_id}</td>
                  <td>{r.reason}</td>
                  <td><DiscrepancyBadge status={r.status} /></td>
                  <td className="mono">{formatDateTime(r.processed_at)}</td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 600, color: "var(--status-review)" }}>
                    {formatINR(r.amount?.amount_minor)}
                  </td>
                </tr>
              ))}
              {(!observed.refunds || observed.refunds.length === 0) && (
                <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)" }}>No refund records found</td></tr>
              )}
            </tbody>
          </table>
        )}

        {activeTab === "ledger" && (
          <table className="data-table">
            <thead>
              <tr>
                <th>Entry ID</th>
                <th>Reference ID</th>
                <th>Type</th>
                <th>Posted At</th>
                <th style={{ textAlign: "right" }}>Debit</th>
                <th style={{ textAlign: "right" }}>Credit</th>
                <th style={{ textAlign: "right" }}>Running Balance</th>
              </tr>
            </thead>
            <tbody>
              {observed.ledger_entries?.map((l) => (
                <tr key={l.entry_id}>
                  <td className="mono" style={{ color: "var(--text-accent)" }}>{l.entry_id}</td>
                  <td className="mono">{l.reference_id}</td>
                  <td className="mono"><DiscrepancyBadge status={l.entry_type} /></td>
                  <td className="mono">{formatDateTime(l.posted_at)}</td>
                  <td className="mono" style={{ textAlign: "right", color: l.debit?.amount_minor > 0 ? "#fff" : "var(--text-muted)" }}>
                    {l.debit?.amount_minor > 0 ? formatINR(l.debit?.amount_minor) : "—"}
                  </td>
                  <td className="mono" style={{ textAlign: "right", color: l.credit?.amount_minor > 0 ? "#fff" : "var(--text-muted)" }}>
                    {l.credit?.amount_minor > 0 ? formatINR(l.credit?.amount_minor) : "—"}
                  </td>
                  <td className="mono" style={{ textAlign: "right", fontWeight: 600, color: "var(--status-info)" }}>
                    {formatINR(l.balance_after?.amount_minor)}
                  </td>
                </tr>
              ))}
              {(!observed.ledger_entries || observed.ledger_entries.length === 0) && (
                <tr><td colSpan={7} style={{ textAlign: "center", color: "var(--text-muted)" }}>No ledger entries found</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
