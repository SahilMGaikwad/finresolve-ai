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
  const reconRate = totalCases > 0 ? ((cleanCount / totalCases) * 100).toFixed(1) : "90.0";
  const pendingReviewCount = exceptionCases.length;

  return (
    <div>
      <Header
        breadcrumbs={[{ label: "FinResolve", href: "/" }, { label: "Overview" }]}
        actions={
          <button
            onClick={handleSeed}
            disabled={isSeeding}
            className="btn btn-primary btn-sm"
          >
            <RefreshIcon size={13} />
            <span>{isSeeding ? "Seeding..." : "Load Seed 42 Benchmark"}</span>
          </button>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {/* Title Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div>
            <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--color-indigo)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
              Financial Operations
            </div>
            <h1 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.015em", marginTop: "2px" }}>
              Reconciliation Control Center
            </h1>
            <p style={{ fontSize: "12.5px", color: "var(--text-muted)", marginTop: "2px" }}>
              Monitor exceptions, investigate discrepancies, and govern financial resolution workflows.
            </p>
          </div>
        </div>

        {/* 4 Compact Metric Blocks */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "0.75rem",
        }}>
          <div className="surface" style={{ padding: "1rem 1.15rem" }}>
            <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              Total Cases
            </div>
            <div className="tabular-num" style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-primary)", marginTop: "4px" }}>
              {isLoading ? "..." : totalCases}
            </div>
            <div style={{ fontSize: "11px", color: "var(--text-dim)", marginTop: "2px" }}>
              Controlled Synthetic Benchmark
            </div>
          </div>

          <div className="surface" style={{ padding: "1rem 1.15rem" }}>
            <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              Flagged Discrepancies
            </div>
            <div className="tabular-num" style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--status-discrepancy)", marginTop: "4px" }}>
              {isLoading ? "..." : exceptionCases.length}
            </div>
            <div style={{ fontSize: "11px", color: "var(--text-dim)", marginTop: "2px" }}>
              Flagged rule discrepancies
            </div>
          </div>

          <div className="surface" style={{ padding: "1rem 1.15rem" }}>
            <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              Pending Approval
            </div>
            <div className="tabular-num" style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--status-review)", marginTop: "4px" }}>
              {isLoading ? "..." : pendingReviewCount}
            </div>
            <div style={{ fontSize: "11px", color: "var(--text-dim)", marginTop: "2px" }}>
              Gated sign-off queue
            </div>
          </div>

          <div className="surface" style={{ padding: "1rem 1.15rem" }}>
            <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              Clean Reconciliation
            </div>
            <div className="tabular-num" style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--status-reconciled)", marginTop: "4px" }}>
              {isLoading ? "..." : `${reconRate}%`}
            </div>
            <div style={{ fontSize: "11px", color: "var(--text-dim)", marginTop: "2px" }}>
              {cleanCount} clean balanced cases
            </div>
          </div>
        </div>

        {/* Demo Fast Access Strip */}
        <div style={{
          padding: "0.75rem 1rem",
          backgroundColor: "var(--bg-surface-secondary)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "6px",
          display: "flex",
          alignItems: "center",
          gap: "1rem",
        }}>
          <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
            Verified Demo Scenarios:
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap", flex: 1 }}>
            <Link
              href="/cases/CASE-000002"
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11.5px", padding: "0.25rem 0.55rem" }}
            >
              <span className="mono" style={{ color: "var(--color-teal)" }}>CASE-000002</span>
              <span style={{ color: "var(--text-secondary)" }}>• Clean Baseline</span>
            </Link>
            <Link
              href="/cases/CASE-000003"
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11.5px", padding: "0.25rem 0.55rem" }}
            >
              <span className="mono" style={{ color: "var(--color-indigo)" }}>CASE-000003</span>
              <span style={{ color: "var(--text-secondary)" }}>• Settlement Mismatch & Sim</span>
            </Link>
            <Link
              href="/cases/CASE-000132"
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11.5px", padding: "0.25rem 0.55rem" }}
            >
              <span className="mono" style={{ color: "var(--status-review)" }}>CASE-000132</span>
              <span style={{ color: "var(--text-secondary)" }}>• Human Review</span>
            </Link>
            <Link
              href="/cases/CASE-000009"
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11.5px", padding: "0.25rem 0.55rem" }}
            >
              <span className="mono" style={{ color: "var(--status-blocked)" }}>CASE-000009</span>
              <span style={{ color: "var(--text-secondary)" }}>• Compound Blocked</span>
            </Link>
          </div>
        </div>

        {/* Exceptions Requiring Attention Table */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
            <h2 style={{ fontSize: "13.5px", fontWeight: 600, color: "var(--text-primary)" }}>
              Exceptions Requiring Attention <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>({exceptionCases.length} flagged cases)</span>
            </h2>
            <Link href="/cases" style={{ fontSize: "12px", color: "var(--color-indigo)", fontWeight: 500 }}>
              View All Cases ({totalCases}) →
            </Link>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Merchant</th>
                  <th>Difficulty</th>
                  <th>Discrepancies</th>
                  <th>Status</th>
                  <th style={{ textAlign: "right" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan={6} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
                      Loading exceptions queue...
                    </td>
                  </tr>
                ) : exceptionCases.length === 0 ? (
                  <tr>
                    <td colSpan={6} style={{ textAlign: "center", padding: "2.5rem", color: "var(--text-muted)" }}>
                      <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>No Exceptions In Memory</div>
                      <div style={{ fontSize: "12px", marginTop: "4px" }}>All reconciled cases currently satisfy the deterministic reconciliation rules.</div>
                      <button
                        onClick={handleSeed}
                        className="btn btn-primary btn-sm"
                        style={{ marginTop: "1rem" }}
                      >
                        Load Seed 42 Benchmark
                      </button>
                    </td>
                  </tr>
                ) : (
                  exceptionCases.slice(0, 10).map((c) => (
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
                        <span className={`badge badge-${c.status === "reconciled" ? "reconciled" : "discrepancy"}`}>
                          {c.status.toUpperCase()}
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
    </div>
  );
}
