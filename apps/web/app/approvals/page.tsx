"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { DiscrepancyBadge } from "@/components/cases/DiscrepancyBadge";
import { ArrowRightIcon } from "@/components/icons/Icons";
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
        breadcrumbs={[{ label: "FinResolve", href: "/" }, { label: "Approvals" }]}
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        <div>
          <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--color-indigo)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Governance & Compliance
          </div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.015em", marginTop: "2px" }}>
            Resolution Approval Queue
          </h1>
          <p style={{ fontSize: "12.5px", color: "var(--text-muted)", marginTop: "2px" }}>
            Actions requiring authorized financial review and separation-of-duties governance.
          </p>
        </div>

        {/* Governance Policy Notice */}
        <div style={{
          backgroundColor: "var(--status-review-bg)",
          border: "1px solid var(--status-review-border)",
          borderRadius: "6px",
          padding: "0.75rem 1rem",
          fontSize: "12px",
          color: "var(--text-primary)",
        }}>
          <strong style={{ color: "var(--status-review)" }}>Governance Policy: </strong>
          Proposals exceeding ₹5,000 variance or compound errors require sign-off.
          Role-Based Access Control strictly blocks proposal creators from self-approving.
        </div>

        {/* Approvals Table */}
        <div className="table-container">
          <div style={{ padding: "0.85rem 1rem", borderBottom: "1px solid var(--border-subtle)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
              Pending Review & Sign-Off ({cases.length})
            </span>
            <span style={{ fontSize: "11.5px", color: "var(--text-muted)" }}>
              Separation of Duties Enforced
            </span>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Merchant</th>
                <th>Difficulty</th>
                <th>Discrepancies</th>
                <th>Policy Gate</th>
                <th>Status</th>
                <th style={{ textAlign: "right" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
                    Loading approval queue...
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ padding: "2.5rem 1.5rem", textAlign: "center", color: "var(--text-muted)" }}>
                    <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>No Pending Approvals</div>
                    <div style={{ fontSize: "12px", marginTop: "4px" }}>Zero proposals currently awaiting human sign-off.</div>
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.case_id}>
                    <td className="mono" style={{ fontWeight: 600 }}>
                      <Link href={`/cases/${c.case_id}`} style={{ color: "var(--text-primary)" }}>
                        {c.case_id}
                      </Link>
                    </td>
                    <td className="mono" style={{ color: "var(--text-secondary)" }}>
                      {c.merchant_id}
                    </td>
                    <td>
                      <span style={{
                        fontSize: "11px",
                        textTransform: "capitalize",
                        padding: "0.15rem 0.45rem",
                        borderRadius: "3px",
                        backgroundColor: "var(--bg-surface-secondary)",
                        color: "var(--text-secondary)",
                        border: "1px solid var(--border-subtle)",
                      }}>
                        {c.difficulty}
                      </span>
                    </td>
                    <td>
                      <DiscrepancyBadge count={c.discrepancies_count} status={c.status} />
                    </td>
                    <td>
                      <span className="badge badge-review" style={{ fontSize: "10.5px" }}>
                        HUMAN REVIEW REQUIRED
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-discrepancy" style={{ fontSize: "10.5px" }}>
                        PENDING
                      </span>
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <Link
                        href={`/cases/${c.case_id}`}
                        className="btn btn-primary btn-sm"
                        style={{ fontSize: "11.5px", padding: "0.25rem 0.6rem" }}
                      >
                        Review Case →
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
