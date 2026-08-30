"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { DiscrepancyBadge } from "@/components/cases/DiscrepancyBadge";
import { api, CaseSummary } from "@/lib/api";

export default function ApprovalsPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const res = await api.listCases(100, 0);
        // Cases with discrepancies that require human review
        const reviewCases = (res.cases || []).filter((c) => c.discrepancies_count > 0);
        setCases(reviewCases);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div>
      <Header
        title="Human Resolution Approval Queue"
        subtitle="High-risk proposals, separation-of-duties enforcement, and sign-off governance"
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Info Banner */}
        <div style={{
          backgroundColor: "var(--status-review-bg)",
          border: "1px solid var(--status-review-border)",
          borderRadius: "8px",
          padding: "1rem 1.25rem",
          fontSize: "0.85rem",
          color: "#fff",
        }}>
          <strong style={{ color: "var(--status-review)" }}>FinOps Governance Rule:</strong> All resolution proposals with monetary adjustments exceeding ₹5,000 or compound discrepancies require human sign-off by an authorized approver before ledger mutation.
        </div>

        {/* Approvals Table */}
        <div className="card" style={{ padding: "0" }}>
          <div style={{ overflowX: "auto" }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Merchant</th>
                  <th>Flagged Discrepancies</th>
                  <th>Risk Tier</th>
                  <th>Policy Gate</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr key={c.case_id}>
                    <td className="mono" style={{ fontWeight: 600, color: "var(--text-accent)" }}>
                      {c.case_id}
                    </td>
                    <td className="mono">{c.merchant_id}</td>
                    <td>
                      <span className="badge badge-discrepancy">{c.discrepancies_count} Discrepancies</span>
                    </td>
                    <td><span className="badge badge-review">MEDIUM / HIGH</span></td>
                    <td><DiscrepancyBadge status="HUMAN_REVIEW_REQUIRED" /></td>
                    <td>
                      <Link
                        href={`/cases/${c.case_id}`}
                        className="btn-primary"
                        style={{ fontSize: "0.75rem", padding: "0.25rem 0.65rem" }}
                      >
                        Review & Sign Off →
                      </Link>
                    </td>
                  </tr>
                ))}
                {isLoading && (
                  <tr><td colSpan={6} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>Loading approval queue...</td></tr>
                )}
                {!isLoading && cases.length === 0 && (
                  <tr><td colSpan={6} style={{ textAlign: "center", padding: "2rem", color: "var(--status-reconciled)" }}>✓ Zero pending resolution proposals awaiting review</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
