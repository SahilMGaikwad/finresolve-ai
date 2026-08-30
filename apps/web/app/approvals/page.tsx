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
          <h1 style={{ fontSize: "24px", fontWeight: 700, color: "#111827", letterSpacing: "-0.02em" }}>
            Resolution Approval Queue
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-muted)", marginTop: "4px" }}>
            Gated proposals requiring human sign-off, threshold validation, and separation-of-duties governance.
          </p>
        </div>

        {/* Governance Policy Notice */}
        <div style={{
          backgroundColor: "#fffbeb",
          border: "1px solid #fde68a",
          borderRadius: "8px",
          padding: "0.85rem 1.15rem",
          fontSize: "13.5px",
          color: "#111827",
        }}>
          <strong style={{ color: "var(--status-review)" }}>Governance Policy: </strong>
          Proposals exceeding ₹5,000 variance or compound errors require sign-off.
          Role-Based Access Control strictly blocks proposal creators from self-approving.
        </div>

        {/* Approvals Table */}
        <div className="surface" style={{ overflow: "hidden" }}>
          <div style={{ padding: "1rem 1.25rem", borderBottom: "1px solid var(--border-subtle)" }}>
            <span style={{ fontSize: "16px", fontWeight: 600, color: "#111827" }}>
              Pending Review & Sign-Off ({cases.length})
            </span>
          </div>

          {isLoading ? (
            <div style={{ padding: "1.5rem" }}>
              <div className="skeleton" style={{ height: "40px", marginBottom: "0.5rem" }} />
              <div className="skeleton" style={{ height: "40px", marginBottom: "0.5rem" }} />
              <div className="skeleton" style={{ height: "40px" }} />
            </div>
          ) : cases.length === 0 ? (
            <div style={{ padding: "3rem 1.5rem", textAlign: "center" }}>
              <div style={{ fontSize: "16px", fontWeight: 600, color: "#111827" }}>No Pending Approvals</div>
              <p style={{ fontSize: "14px", color: "var(--text-muted)", marginTop: "4px" }}>
                Zero proposals currently awaiting human sign-off.
              </p>
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Case ID</th>
                    <th>Merchant</th>
                    <th>Symptoms</th>
                    <th>Difficulty</th>
                    <th>Policy Decision</th>
                    <th>Status</th>
                    <th style={{ textAlign: "right" }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {cases.map((c) => (
                    <tr key={c.case_id}>
                      <td className="mono" style={{ fontWeight: 600 }}>
                        <Link href={`/cases/${c.case_id}`} style={{ color: "#315cf5" }}>
                          {c.case_id}
                        </Link>
                      </td>
                      <td className="mono" style={{ color: "var(--text-secondary)" }}>
                        {c.merchant_id}
                      </td>
                      <td>
                        <DiscrepancyBadge count={c.discrepancies_count} />
                      </td>
                      <td>
                        <span className="badge badge-info" style={{ textTransform: "capitalize" }}>
                          {c.difficulty}
                        </span>
                      </td>
                      <td>
                        <span className="badge badge-review">
                          Human Review
                        </span>
                      </td>
                      <td>
                        <span className={`badge badge-${c.status === "reconciled" ? "reconciled" : "discrepancy"}`}>
                          {c.status === "reconciled" ? "Reconciled" : "Discrepancy"}
                        </span>
                      </td>
                      <td style={{ textAlign: "right" }}>
                        <Link
                          href={`/cases/${c.case_id}`}
                          className="btn-secondary"
                          style={{
                            padding: "0.35rem 0.75rem",
                            fontSize: "13px",
                            whiteSpace: "nowrap",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "0.4rem",
                          }}
                        >
                          Review Case <ArrowRightIcon size={12} />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
