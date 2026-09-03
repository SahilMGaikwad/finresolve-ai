"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { DiscrepancyBadge } from "@/components/cases/DiscrepancyBadge";
import { ArrowRightIcon, RefreshIcon } from "@/components/icons/Icons";
import { api, CaseSummary } from "@/lib/api";

export default function CaseExplorerPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [filter, setFilter] = useState<"all" | "discrepancies" | "clean">("all");
  const [difficultyFilter, setDifficultyFilter] = useState<string>("all");
  const [search, setSearch] = useState("");
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

  const filteredCases = cases.filter((c) => {
    if (filter === "discrepancies" && c.discrepancies_count === 0) return false;
    if (filter === "clean" && c.discrepancies_count > 0) return false;
    if (difficultyFilter !== "all" && c.difficulty !== difficultyFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      return c.case_id.toLowerCase().includes(q) || c.merchant_id.toLowerCase().includes(q);
    }
    return true;
  });

  const discrepancyCount = cases.filter((c) => c.discrepancies_count > 0).length;
  const cleanCount = cases.filter((c) => c.discrepancies_count === 0).length;

  return (
    <div>
      <Header
        breadcrumbs={[{ label: "FinResolve", href: "/" }, { label: "Cases" }]}
        actions={
          cases.length === 0 ? (
            <button onClick={handleSeed} disabled={isSeeding} className="btn btn-primary btn-sm">
              <RefreshIcon size={12} />
              <span>{isSeeding ? "Seeding..." : "Load Seed 42 Benchmark"}</span>
            </button>
          ) : undefined
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {/* Title Bar */}
        <div>
          <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--color-indigo)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Case Explorer
          </div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.015em", marginTop: "2px" }}>
            Reconciliation Cases
          </h1>
          <p style={{ fontSize: "12.5px", color: "var(--text-muted)", marginTop: "2px" }}>
            Canonical multi-party transaction sets loaded in active working memory.
          </p>
        </div>

        {/* Filter Toolbar */}
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "0.75rem",
          background: "var(--bg-surface)",
          padding: "0.6rem 0.85rem",
          borderRadius: "6px",
          border: "1px solid var(--border-subtle)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", flexWrap: "wrap" }}>
            <button
              onClick={() => setFilter("all")}
              style={{
                padding: "0.25rem 0.6rem",
                borderRadius: "4px",
                fontSize: "12px",
                fontWeight: filter === "all" ? 600 : 500,
                backgroundColor: filter === "all" ? "var(--bg-surface-elevated)" : "transparent",
                color: filter === "all" ? "var(--text-primary)" : "var(--text-muted)",
                border: filter === "all" ? "1px solid var(--border-medium)" : "1px solid transparent",
              }}
            >
              All ({cases.length})
            </button>
            <button
              onClick={() => setFilter("discrepancies")}
              style={{
                padding: "0.25rem 0.6rem",
                borderRadius: "4px",
                fontSize: "12px",
                fontWeight: filter === "discrepancies" ? 600 : 500,
                backgroundColor: filter === "discrepancies" ? "var(--status-discrepancy-bg)" : "transparent",
                color: filter === "discrepancies" ? "var(--status-discrepancy)" : "var(--text-muted)",
                border: filter === "discrepancies" ? "1px solid var(--status-discrepancy-border)" : "1px solid transparent",
              }}
            >
              Flagged Discrepancies ({discrepancyCount})
            </button>
            <button
              onClick={() => setFilter("clean")}
              style={{
                padding: "0.25rem 0.6rem",
                borderRadius: "4px",
                fontSize: "12px",
                fontWeight: filter === "clean" ? 600 : 500,
                backgroundColor: filter === "clean" ? "var(--status-reconciled-bg)" : "transparent",
                color: filter === "clean" ? "var(--status-reconciled)" : "var(--text-muted)",
                border: filter === "clean" ? "1px solid var(--status-reconciled-border)" : "1px solid transparent",
              }}
            >
              Clean ({cleanCount})
            </button>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <input
              type="text"
              placeholder="Filter by ID or Merchant..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input"
              style={{ width: "200px" }}
            />
          </div>
        </div>

        {/* Cases Table */}
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
                    Loading cases...
                  </td>
                </tr>
              ) : filteredCases.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
                    No matching cases found.
                  </td>
                </tr>
              ) : (
                filteredCases.map((c) => (
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
                      <span className={`badge badge-${c.status === "reconciled" ? "reconciled" : "discrepancy"}`} style={{ fontSize: "10.5px" }}>
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
  );
}
