"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { DiscrepancyBadge } from "@/components/cases/DiscrepancyBadge";
import { ArrowRightIcon, RefreshIcon } from "@/components/icons/Icons";
import { api, CaseSummary } from "@/lib/api";

export default function DashboardPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSeeding, setIsSeeding] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const res = await api.listCases(100, 0);
      setCases(res.cases || []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSeed = async () => {
    setIsSeeding(true);
    try {
      await api.seedBenchmark(500);
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSeeding(false);
    }
  };

  const totalCases = cases.length;
  const exceptionCases = cases.filter((c) => c.discrepancies_count > 0);
  const cleanCount = totalCases - exceptionCases.length;
  const reconRate = totalCases > 0 ? ((cleanCount / totalCases) * 100).toFixed(1) : "100.0";
  const pendingReviewCount = exceptionCases.length;

  return (
    <div>
      <Header
        breadcrumbs={[{ label: "FinResolve", href: "/" }, { label: "Overview" }]}
        actions={
          <button
            onClick={handleSeed}
            disabled={isSeeding}
            className="btn-primary"
          >
            <RefreshIcon size={14} />
            <span>{isSeeding ? "Seeding..." : "Load Seed 42 Benchmark"}</span>
          </button>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Title Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div>
            <h1 style={{ fontSize: "24px", fontWeight: 700, color: "#111827", letterSpacing: "-0.02em" }}>
              Financial Reconciliation Overview
            </h1>
            <p style={{ fontSize: "14px", color: "var(--text-muted)", marginTop: "4px" }}>
              Monitor reconciliation exceptions, automated AI investigations, counterfactual simulations, and approval governance.
            </p>
          </div>
        </div>

        {/* 4 Compact White Metric Cards with Staggered Entrance and Hover Lift */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "1rem",
        }}>
          <div className="surface surface-hover animate-fade-in" style={{ padding: "1.15rem 1.35rem" }}>
            <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)" }}>
              Total Cases
            </div>
            {isLoading ? (
              <div className="skeleton" style={{ height: "32px", width: "80px", marginTop: "6px" }} />
            ) : (
              <div className="tabular-num" style={{ fontSize: "26px", fontWeight: 700, color: "#111827", marginTop: "4px" }}>
                {totalCases}
              </div>
            )}
            <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
              Controlled Synthetic Benchmark
            </div>
          </div>

          <div className="surface surface-hover animate-fade-in animate-delay-1" style={{ padding: "1.15rem 1.35rem" }}>
            <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)" }}>
              Exceptions
            </div>
            {isLoading ? (
              <div className="skeleton" style={{ height: "32px", width: "80px", marginTop: "6px" }} />
            ) : (
              <div className="tabular-num" style={{ fontSize: "26px", fontWeight: 700, color: exceptionCases.length > 0 ? "var(--status-discrepancy)" : "#111827", marginTop: "4px" }}>
                {exceptionCases.length}
              </div>
            )}
            <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
              Flagged rule discrepancies
            </div>
          </div>

          <div className="surface surface-hover animate-fade-in animate-delay-2" style={{ padding: "1.15rem 1.35rem" }}>
            <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)" }}>
              Pending Review
            </div>
            {isLoading ? (
              <div className="skeleton" style={{ height: "32px", width: "80px", marginTop: "6px" }} />
            ) : (
              <div className="tabular-num" style={{ fontSize: "26px", fontWeight: 700, color: pendingReviewCount > 0 ? "var(--status-review)" : "#111827", marginTop: "4px" }}>
                {pendingReviewCount}
              </div>
            )}
            <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
              Gated sign-off queue
            </div>
          </div>

          <div className="surface surface-hover animate-fade-in animate-delay-3" style={{ padding: "1.15rem 1.35rem" }}>
            <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)" }}>
              Reconciliation Rate
            </div>
            {isLoading ? (
              <div className="skeleton" style={{ height: "32px", width: "80px", marginTop: "6px" }} />
            ) : (
              <div className="tabular-num" style={{ fontSize: "26px", fontWeight: 700, color: "var(--status-reconciled)", marginTop: "4px" }}>
                {reconRate}%
              </div>
            )}
            <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
              {cleanCount} clean balanced cases
            </div>
          </div>
        </div>

        {/* Demo Cases Fast Access Strip */}
        <div className="animate-fade-in animate-delay-2" style={{
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          background: "#ffffff",
          border: "1px solid var(--border-subtle)",
          borderRadius: "8px",
          padding: "0.6rem 1rem",
          boxShadow: "var(--shadow-card)",
        }}>
          <span style={{ fontWeight: 600, color: "var(--text-muted)", fontSize: "12px" }}>
            Verified Demo Scenarios:
          </span>
          <Link href="/cases/CASE-000002" style={{ color: "#315cf5", padding: "0.25rem 0.65rem", background: "#eff4ff", borderRadius: "5px", border: "1px solid #bfdbfe", fontWeight: 500, fontSize: "13px", transition: "all 0.15s ease" }}>
            <span className="mono">CASE-000002</span> · Clean Baseline
          </Link>
          <Link href="/cases/CASE-000003" style={{ color: "#315cf5", padding: "0.25rem 0.65rem", background: "#eff4ff", borderRadius: "5px", border: "1px solid #bfdbfe", fontWeight: 500, fontSize: "13px", transition: "all 0.15s ease" }}>
            <span className="mono">CASE-000003</span> · Settlement Mismatch & Sim
          </Link>
          <Link href="/cases/CASE-000132" style={{ color: "#315cf5", padding: "0.25rem 0.65rem", background: "#eff4ff", borderRadius: "5px", border: "1px solid #bfdbfe", fontWeight: 500, fontSize: "13px", transition: "all 0.15s ease" }}>
            <span className="mono">CASE-000132</span> · Human Review
          </Link>
          <Link href="/cases/CASE-000009" style={{ color: "#315cf5", padding: "0.25rem 0.65rem", background: "#eff4ff", borderRadius: "5px", border: "1px solid #bfdbfe", fontWeight: 500, fontSize: "13px", transition: "all 0.15s ease" }}>
            <span className="mono">CASE-000009</span> · Compound Blocked
          </Link>
        </div>

        {/* Primary Content: Exceptions Requiring Attention Table */}
        <div className="surface animate-fade-in animate-delay-3" style={{ overflow: "hidden" }}>
          <div style={{
            padding: "1rem 1.25rem",
            borderBottom: "1px solid var(--border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}>
            <div>
              <span style={{ fontSize: "16px", fontWeight: 600, color: "#111827" }}>
                Exceptions Requiring Attention
              </span>
              <span style={{ fontSize: "13px", color: "var(--text-muted)", marginLeft: "0.6rem" }}>
                ({exceptionCases.length} flagged cases)
              </span>
            </div>
            <Link href="/cases" style={{ fontSize: "13.5px", color: "var(--text-accent)", fontWeight: 500 }}>
              View All Cases ({totalCases}) →
            </Link>
          </div>

          {isLoading ? (
            <div style={{ padding: "1.5rem" }}>
              <div className="skeleton" style={{ height: "40px", marginBottom: "0.5rem" }} />
              <div className="skeleton" style={{ height: "40px", marginBottom: "0.5rem" }} />
              <div className="skeleton" style={{ height: "40px" }} />
            </div>
          ) : exceptionCases.length === 0 ? (
            <div style={{ padding: "3rem 1.5rem", textAlign: "center" }}>
              <div style={{ fontSize: "16px", fontWeight: 600, color: "#111827" }}>No Exceptions In Memory</div>
              <p style={{ fontSize: "14px", color: "var(--text-muted)", margin: "0.4rem auto 1.25rem", maxWidth: "420px" }}>
                All reconciled cases currently satisfy the deterministic reconciliation rules.
              </p>
              <button onClick={handleSeed} disabled={isSeeding} className="btn-primary">
                {isSeeding ? "Loading..." : "Load Seed 42 Benchmark"}
              </button>
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Priority</th>
                    <th>Case ID</th>
                    <th>Merchant</th>
                    <th>Issue Summary</th>
                    <th>Records</th>
                    <th>Difficulty</th>
                    <th>Status</th>
                    <th style={{ textAlign: "right" }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {exceptionCases.slice(0, 15).map((c, idx) => (
                    <tr key={c.case_id}>
                      <td>
                        <span className="badge badge-discrepancy">
                          {idx === 0 || c.difficulty === "hard" ? "High" : "Medium"}
                        </span>
                      </td>
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
                      <td style={{ color: "var(--text-secondary)" }}>
                        {c.payments_count} pay / {c.settlements_count} stl
                      </td>
                      <td>
                        <span className="badge badge-info" style={{ textTransform: "capitalize" }}>
                          {c.difficulty}
                        </span>
                      </td>
                      <td>
                        <span className="badge badge-review">
                          Review Required
                        </span>
                      </td>
                      <td style={{ textAlign: "right" }}>
                        <Link
                          href={`/cases/${c.case_id}`}
                          className="btn-secondary"
                          style={{ padding: "0.35rem 0.75rem", fontSize: "13px" }}
                        >
                          Review <ArrowRightIcon size={12} />
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
