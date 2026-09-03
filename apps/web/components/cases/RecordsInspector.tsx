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
    { id: "payments", label: `01 PAYMENTS (${observed.payments?.length || 0})` },
    { id: "settlements", label: `02 SETTLEMENTS (${observed.settlements?.length || 0})` },
    { id: "fees", label: `03 FEES (${observed.fees?.length || 0})` },
    { id: "refunds", label: `04 REFUNDS (${observed.refunds?.length || 0})` },
    { id: "ledger", label: `05 GENERAL LEDGER (${observed.ledger_entries?.length || 0})` },
  ];

  return (
    <div className="table-container">
      {/* Sub-Tabs */}
      <div style={{
        display: "flex",
        borderBottom: "1px solid var(--border-subtle)",
        backgroundColor: "var(--bg-surface-secondary)",
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
                padding: "0.6rem 1.15rem",
                fontSize: "11px",
                fontFamily: "var(--font-heading)",
                fontWeight: 700,
                letterSpacing: "0.04em",
                color: isActive ? "var(--text-primary)" : "var(--text-muted)",
                borderBottom: isActive ? "2px solid var(--color-brand)" : "2px solid transparent",
                backgroundColor: isActive ? "var(--bg-surface)" : "transparent",
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
                <th>PAYMENT ID</th>
                <th>ORDER REF</th>
                <th>AMOUNT</th>
                <th>METHOD</th>
                <th>STATUS</th>
                <th>CAPTURED AT</th>
                <th style={{ textAlign: "right" }}>RAW</th>
              </tr>
            </thead>
            <tbody>
              {observed.payments?.map((p: any) => (
                <tr key={p.payment_id}>
                  <td className="mono" style={{ fontWeight: 700, color: "var(--text-primary)" }}>{p.payment_id}</td>
                  <td className="mono" style={{ color: "var(--text-secondary)" }}>{p.order_id}</td>
                  <td className="mono tabular-num" style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                    {formatINR(p.amount?.amount_minor || 0)}
                  </td>
                  <td>
                    <span className="mono" style={{ fontSize: "10.5px", color: "var(--text-secondary)" }}>{p.method}</span>
                  </td>
                  <td>
                    <span style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--status-reconciled)" }}>● {p.status}</span>
                  </td>
                  <td className="mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                    {formatDateTime(p.captured_at)}
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      onClick={() => setSelectedRawRecord(p)}
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: "10px", padding: "0.15rem 0.4rem" }}
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
                <th>SETTLEMENT ID</th>
                <th>PAYMENT REF</th>
                <th>GROSS</th>
                <th>FEE</th>
                <th>NET SETTLED</th>
                <th>UTR REFERENCE</th>
                <th>STATUS</th>
                <th style={{ textAlign: "right" }}>RAW</th>
              </tr>
            </thead>
            <tbody>
              {observed.settlements?.map((s: any) => (
                <tr key={s.settlement_id}>
                  <td className="mono" style={{ fontWeight: 700, color: "var(--text-primary)" }}>{s.settlement_id}</td>
                  <td className="mono" style={{ color: "var(--text-secondary)" }}>{s.payment_id}</td>
                  <td className="mono tabular-num">{formatINR(s.gross_amount?.amount_minor || 0)}</td>
                  <td className="mono tabular-num" style={{ color: "var(--color-brand)" }}>
                    -{formatINR(s.fee_amount?.amount_minor || 0)}
                  </td>
                  <td className="mono tabular-num" style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                    {formatINR(s.net_amount?.amount_minor || 0)}
                  </td>
                  <td className="mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>{s.utr || "—"}</td>
                  <td>
                    <span style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--status-reconciled)" }}>● {s.status}</span>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      onClick={() => setSelectedRawRecord(s)}
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: "10px", padding: "0.15rem 0.4rem" }}
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
                <th>FEE ID</th>
                <th>SETTLEMENT REF</th>
                <th>FEE TYPE</th>
                <th>RATE (BPS)</th>
                <th>AMOUNT</th>
                <th>APPLIED AT</th>
                <th style={{ textAlign: "right" }}>RAW</th>
              </tr>
            </thead>
            <tbody>
              {observed.fees?.map((f: any) => (
                <tr key={f.fee_id}>
                  <td className="mono" style={{ fontWeight: 700, color: "var(--text-primary)" }}>{f.fee_id}</td>
                  <td className="mono" style={{ color: "var(--text-secondary)" }}>{f.settlement_id}</td>
                  <td style={{ textTransform: "uppercase", fontSize: "11px", fontWeight: 600 }}>{f.fee_type}</td>
                  <td className="mono tabular-num">{f.rate_bps} bps</td>
                  <td className="mono tabular-num" style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                    {formatINR(f.amount?.amount_minor || 0)}
                  </td>
                  <td className="mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>{formatDateTime(f.applied_at)}</td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      onClick={() => setSelectedRawRecord(f)}
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: "10px", padding: "0.15rem 0.4rem" }}
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
                <th>REFUND ID</th>
                <th>PAYMENT REF</th>
                <th>AMOUNT</th>
                <th>STATUS</th>
                <th>INITIATED AT</th>
              </tr>
            </thead>
            <tbody>
              {observed.refunds?.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)", padding: "2rem" }}>
                    No refunds associated with this case.
                  </td>
                </tr>
              ) : (
                observed.refunds?.map((r: any) => (
                  <tr key={r.refund_id}>
                    <td className="mono" style={{ fontWeight: 700, color: "var(--text-primary)" }}>{r.refund_id}</td>
                    <td className="mono" style={{ color: "var(--text-secondary)" }}>{r.payment_id}</td>
                    <td className="mono tabular-num" style={{ fontWeight: 700, color: "var(--color-brand)" }}>
                      -{formatINR(r.amount?.amount_minor || 0)}
                    </td>
                    <td>
                      <span className="mono" style={{ fontSize: "10.5px" }}>{r.status}</span>
                    </td>
                    <td className="mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>{formatDateTime(r.initiated_at)}</td>
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
                <th>ENTRY ID</th>
                <th>REFERENCE ID</th>
                <th>TYPE</th>
                <th>DEBIT</th>
                <th>CREDIT</th>
                <th>BALANCE AFTER</th>
                <th>POSTED AT</th>
              </tr>
            </thead>
            <tbody>
              {observed.ledger_entries?.map((l: any) => (
                <tr key={l.entry_id}>
                  <td className="mono" style={{ fontWeight: 700, color: "var(--text-primary)" }}>{l.entry_id}</td>
                  <td className="mono" style={{ color: "var(--text-secondary)" }}>{l.reference_id}</td>
                  <td>
                    <span className="mono" style={{ fontSize: "10.5px", textTransform: "uppercase" }}>
                      {l.entry_type}
                    </span>
                  </td>
                  <td className="mono tabular-num" style={{ color: l.debit?.amount_minor > 0 ? "var(--color-brand)" : "var(--text-muted)" }}>
                    {l.debit?.amount_minor > 0 ? formatINR(l.debit.amount_minor) : "—"}
                  </td>
                  <td className="mono tabular-num" style={{ color: l.credit?.amount_minor > 0 ? "var(--status-reconciled)" : "var(--text-muted)" }}>
                    {l.credit?.amount_minor > 0 ? formatINR(l.credit.amount_minor) : "—"}
                  </td>
                  <td className="mono tabular-num" style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                    {formatINR(l.balance_after?.amount_minor || 0)}
                  </td>
                  <td className="mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>{formatDateTime(l.posted_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Raw Record Modal */}
      {selectedRawRecord && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "rgba(9, 9, 9, 0.85)",
            backdropFilter: "blur(2px)",
            zIndex: 999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "1.5rem",
          }}
          onClick={() => setSelectedRawRecord(null)}
        >
          <div
            style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-subtle)",
              padding: "1.5rem",
              width: "100%",
              maxWidth: "600px",
              maxHeight: "80vh",
              display: "flex",
              flexDirection: "column",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <span className="heading-editorial" style={{ fontSize: "12px", color: "var(--text-primary)" }}>
                RAW FINANCIAL RECORD PAYLOAD
              </span>
              <button
                onClick={() => setSelectedRawRecord(null)}
                className="btn btn-secondary btn-sm"
              >
                CLOSE
              </button>
            </div>
            <pre style={{
              flex: 1,
              overflowY: "auto",
              backgroundColor: "var(--bg-canvas)",
              padding: "1rem",
              fontSize: "11px",
              fontFamily: "var(--font-mono)",
              color: "var(--text-secondary)",
              border: "1px solid var(--border-hairline)",
            }}>
              {JSON.stringify(selectedRawRecord, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
