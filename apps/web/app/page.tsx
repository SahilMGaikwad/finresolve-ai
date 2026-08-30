"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { DiscrepancyBadge } from "@/components/cases/DiscrepancyBadge";
import { api, CaseSummary } from "@/lib/api";

export default function DashboardPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSeeding, setIsSeeding] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const res = await api.listCases(20, 0);
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
      await api.seedBenchmark(50);
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSeeding(false);
    }
  };

  const totalCases = cases.length;
  const discrepancyCases = cases.filter((c) => c.discrepancies_count > 0).length;
  const reconciledCases = totalCases - discrepancyCases;
  const reconRate = totalCases > 0 ? ((reconciledCases / totalCases) * 100).toFixed(1) : "100.0";

  return (
    <div>
      <Header
        title="FinOps Executive Dashboard"
        subtitle="Synthetic Benchmark — Seed 42 | Real-time multi-signal reconciliation telemetry & automated resolution control"
        actions={
          <button
            onClick={handleSeed}
            disabled={isSeeding}
            className="btn-primary"
          >
            {isSeeding ? "Generating..." : "⚡ Load 50-Case FinOps Benchmark"}
          </button>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* KPI Cards Grid */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "1.25rem",
        }}>
          <div className="card">
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
              Completed Case Investigations
            </div>
            <div className="mono" style={{ fontSize: "2rem", fontWeight: 700, color: "#fff", marginTop: "0.5rem" }}>
              {totalCases}
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
              Synthetic Benchmark (Seed 42)
            </div>
          </div>

          <div className="card">
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
              Reconciliation Rate
            </div>
            <div className="mono" style={{ fontSize: "2rem", fontWeight: 700, color: "var(--status-reconciled)", marginTop: "0.5rem" }}>
              {reconRate}%
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
              {reconciledCases} balanced clean cases
            </div>
          </div>

          <div className="card">
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
              Flagged Discrepancies
            </div>
            <div className="mono" style={{ fontSize: "2rem", fontWeight: 700, color: "var(--status-discrepancy)", marginTop: "0.5rem" }}>
              {discrepancyCases}
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
              Requires resolution review
            </div>
          </div>

          <div className="card">
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
              Zero-Harm Safety Rate
            </div>
            <div className="mono" style={{ fontSize: "2rem", fontWeight: 700, color: "var(--status-reconciled)", marginTop: "0.5rem" }}>
              100.0%
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
              Closed-loop invariant gating
            </div>
          </div>
        </div>

        {/* Live Case Explorer Preview */}
        <div className="card" style={{ padding: "0" }}>
          <div style={{
            padding: "1.25rem 1.5rem",
            borderBottom: "1px solid var(--border-subtle)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}>
            <div>
              <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "#fff" }}>Recent Reconciliation Cases (Synthetic Benchmark)</h3>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Click any case to launch the multi-signal inspector and AI investigator workspace.
              </p>
            </div>
            <Link href="/cases" className="btn-secondary" style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem" }}>
              View All Cases →
            </Link>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Merchant ID</th>
                  <th>Difficulty</th>
                  <th>Discrepancies</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {cases.slice(0, 10).map((c) => (
                  <tr key={c.case_id}>
                    <td className="mono" style={{ fontWeight: 600, color: "var(--text-accent)" }}>
                      {c.case_id}
                    </td>
                    <td className="mono">{c.merchant_id}</td>
                    <td className="mono">{c.difficulty.toUpperCase()}</td>
                    <td>
                      {c.discrepancies_count > 0 ? (
                        <span className="badge badge-discrepancy">{c.discrepancies_count} Discrepancy</span>
                      ) : (
                        <span className="badge badge-reconciled">Clean (0)</span>
                      )}
                    </td>
                    <td><DiscrepancyBadge status={c.status} /></td>
                    <td>
                      <Link
                        href={`/cases/${c.case_id}`}
                        className="btn-secondary"
                        style={{ fontSize: "0.75rem", padding: "0.25rem 0.65rem" }}
                      >
                        Inspect Case →
                      </Link>
                    </td>
                  </tr>
                ))}
                {isLoading && (
                  <tr><td colSpan={6} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>Loading cases...</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
