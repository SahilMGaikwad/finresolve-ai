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
            <button onClick={handleSeed} disabled={isSeeding} className="btn-primary" style={{ fontSize: "0.74rem" }}>
              <RefreshIcon size={12} />
              <span>{isSeeding ? "Seeding..." : "Load Seed 42 Benchmark"}</span>
            </button>
          ) : undefined
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {/* Title Bar */}
        <div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 800, color: "#0f172a", letterSpacing: "-0.02em" }}>
            Reconciliation Cases
          </h1>
          <p style={{ fontSize: "0.76rem", color: "var(--text-muted)", marginTop: "2px" }}>
            Canonical multi-party transaction sets loaded in working memory.
          </p>
        </div>

        {/* Compact Filter Toolbar */}
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "0.75rem",
          background: "#ffffff",
          padding: "0.65rem 1rem",
          borderRadius: "8px",
          border: "1px solid var(--border-subtle)",
          boxShadow: "var(--shadow-card)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", flexWrap: "wrap" }}>
            <span style={{ fontSize: "0.68rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginRight: "0.2rem" }}>
              Status:
            </span>
            <button
              onClick={() => setFilter("all")}
              className={filter === "all" ? "btn-primary" : "btn-secondary"}
              style={{ fontSize: "0.72rem", padding: "0.25rem 0.55rem" }}
            >
              All ({cases.length})
            </button>
            <button
              onClick={() => setFilter("discrepancies")}
              className={filter === "discrepancies" ? "btn-primary" : "btn-secondary"}
              style={{ fontSize: "0.72rem", padding: "0.25rem 0.55rem" }}
            >
              Flagged ({discrepancyCount})
            </button>
            <button
              onClick={() => setFilter("clean")}
              className={filter === "clean" ? "btn-primary" : "btn-secondary"}
              style={{ fontSize: "0.72rem", padding: "0.25rem 0.55rem" }}
            >
              Clean ({cleanCount})
            </button>

            <div style={{ width: "1px", height: "16px", background: "var(--border-subtle)", margin: "0 0.35rem" }} />

            <span style={{ fontSize: "0.68rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginRight: "0.2rem" }}>
              Difficulty:
            </span>
            {["all", "easy", "medium", "hard"].map((diff) => (
              <button
                key={diff}
                onClick={() => setDifficultyFilter(diff)}
                className={difficultyFilter === diff ? "btn-primary" : "btn-secondary"}
                style={{ fontSize: "0.72rem", padding: "0.25rem 0.55rem", textTransform: "capitalize" }}
              >
                {diff}
              </button>
            ))}
          </div>

          <div>
            <input
              type="text"
              placeholder="Filter by Case ID or Merchant ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-control"
              style={{ width: "260px" }}
            />
          </div>
        </div>

        {/* Dense Cases Table */}
        <div className="surface" style={{ overflow: "hidden" }}>
          {isLoading ? (
            <div style={{ padding: "3rem", textAlign: "center", color: "var(--text-muted)", fontSize: "0.8rem" }}>
              Loading cases...
            </div>
          ) : cases.length === 0 ? (
            <div style={{ padding: "3rem 1.5rem", textAlign: "center" }}>
              <div style={{ fontSize: "0.9rem", fontWeight: 700, color: "#0f172a" }}>No Cases in Memory</div>
              <p style={{ fontSize: "0.76rem", color: "var(--text-muted)", margin: "0.35rem auto 1.25rem", maxWidth: "400px" }}>
                Load the controlled Seed 42 synthetic benchmark to populate cases.
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
                    <th>Case ID</th>
                    <th>Merchant ID</th>
                    <th>Difficulty</th>
                    <th>Records Breakdown</th>
                    <th>Discrepancy Symptoms</th>
                    <th>Reconciliation Status</th>
                    <th style={{ textAlign: "right" }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCases.map((c) => (
                    <tr key={c.case_id}>
                      <td className="mono" style={{ fontWeight: 700 }}>
                        <Link href={`/cases/${c.case_id}`} style={{ color: "#2563eb" }}>
                          {c.case_id}
                        </Link>
                      </td>
                      <td className="mono" style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
                        {c.merchant_id}
                      </td>
                      <td>
                        <span className="badge badge-info" style={{ fontSize: "0.62rem" }}>
                          {c.difficulty}
                        </span>
                      </td>
                      <td className="mono" style={{ fontSize: "0.75rem" }}>
                        {c.payments_count} payments, {c.settlements_count} settlements
                      </td>
                      <td>
                        <DiscrepancyBadge count={c.discrepancies_count} />
                      </td>
                      <td>
                        <span className={`badge badge-${c.status === "reconciled" ? "reconciled" : "discrepancy"}`}>
                          {c.status}
                        </span>
                      </td>
                      <td style={{ textAlign: "right" }}>
                        <Link
                          href={`/cases/${c.case_id}`}
                          className="btn-secondary"
                          style={{ fontSize: "0.74rem", padding: "0.25rem 0.55rem" }}
                        >
                          Workstation <ArrowRightIcon size={11} />
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
