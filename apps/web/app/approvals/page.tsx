"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { DiscrepancyBadge } from "@/components/cases/DiscrepancyBadge";
import { api, CaseSummary } from "@/lib/api";

export default function ApprovalsPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const res = await api.listCases(100, 0);
      const reviewCases = (res.cases || []).filter((c) => c.discrepancies_count > 0);
      setCases(reviewCases);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div>
      <Header
        breadcrumbs={[{ label: "FINRESOLVE", href: "/" }, { label: "APPROVALS" }]}
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* Title Header */}
        <div style={{
          borderBottom: "1px solid var(--border-subtle)",
          paddingBottom: "1.75rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
        }}>
          <div>
            <div style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem" }}>
              COMPLIANCE & DUAL CONTROL
            </div>
            <h1 className="heading-editorial title-huge">
              APPROVAL<br />QUEUE
            </h1>
            <div style={{ fontSize: "12.5px", color: "var(--text-secondary)", marginTop: "0.75rem" }}>
              Actions requiring authorized financial review, threshold validation, and separation-of-duties sign-off.
            </div>
          </div>

          <div style={{ textAlign: "right" }}>
            <div className="mono" style={{ fontSize: "10.5px", color: "var(--text-dim)" }}>GATE STATUS</div>
            <div style={{ fontSize: "12px", fontWeight: 700, color: "var(--status-review)" }}>● {cases.length} PENDING SIGN-OFF</div>
          </div>
        </div>

        {/* Governance Notice */}
        <div style={{
          borderLeft: "3px solid var(--status-review)",
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-subtle)",
          borderLeftWidth: "3px",
          padding: "1rem 1.25rem",
          fontSize: "12px",
          color: "var(--text-primary)",
        }}>
          <strong style={{ color: "var(--status-review)", textTransform: "uppercase", letterSpacing: "0.04em" }}>Governance Invariant: </strong>
          Proposals exceeding ₹5,000 variance or compound errors require sign-off.
          Role-Based Access Control strictly blocks proposal creators from self-approving.
        </div>

        {/* Approvals Compliance Ledger Table */}
        <div className="table-container">
          <div style={{
            padding: "0.85rem 1.25rem",
            borderBottom: "1px solid var(--border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}>
            <span className="heading-editorial" style={{ fontSize: "12px", color: "var(--text-primary)" }}>
              PENDING RESOLUTION SIGN-OFFS ({cases.length})
            </span>
            <span className="mono" style={{ fontSize: "10.5px", color: "var(--text-muted)" }}>
              DUAL SIGN-OFF MANDATE ENFORCED
            </span>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>CASE</th>
                <th>MERCHANT</th>
                <th>DIFFICULTY</th>
                <th>DISCREPANCIES</th>
                <th>POLICY GATE</th>
                <th>STATUS</th>
                <th style={{ textAlign: "right" }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center", padding: "2.5rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                    LOADING COMPLIANCE QUEUE...
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ padding: "3rem 1.5rem", textAlign: "center", color: "var(--text-muted)" }}>
                    <div className="heading-editorial" style={{ fontSize: "1.2rem", color: "var(--text-primary)" }}>NO PENDING APPROVALS</div>
                    <div style={{ fontSize: "12px", marginTop: "4px" }}>Zero proposals currently awaiting human sign-off.</div>
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.case_id}>
                    <td className="mono" style={{ fontWeight: 700 }}>
                      <Link href={`/cases/${c.case_id}`} style={{ color: "var(--text-primary)" }}>
                        {c.case_id}
                      </Link>
                    </td>
                    <td className="mono" style={{ color: "var(--text-secondary)" }}>
                      {c.merchant_id}
                    </td>
                    <td>
                      <span className="mono" style={{ fontSize: "10.5px", textTransform: "uppercase", color: "var(--text-secondary)" }}>
                        {c.difficulty}
                      </span>
                    </td>
                    <td>
                      <DiscrepancyBadge count={c.discrepancies_count} status={c.status} />
                    </td>
                    <td>
                      <span style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--status-review)" }}>
                        ● HUMAN REVIEW REQUIRED
                      </span>
                    </td>
                    <td>
                      <span style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--color-brand)" }}>
                        ● PENDING SIGN-OFF
                      </span>
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <Link
                        href={`/cases/${c.case_id}`}
                        className="btn btn-primary btn-sm"
                      >
                        REVIEW CASE →
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
