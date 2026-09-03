"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { DiscrepancyBadge } from "@/components/cases/DiscrepancyBadge";
import { RefreshIcon } from "@/components/icons/Icons";
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
      const res = await api.listCases(50, 0);
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
        breadcrumbs={[{ label: "FINRESOLVE", href: "/" }, { label: "CASES" }]}
        actions={
          cases.length === 0 ? (
            <button onClick={handleSeed} disabled={isSeeding} className="btn btn-primary btn-sm">
              <RefreshIcon size={12} />
              <span>{isSeeding ? "SEEDING..." : "LOAD SEED 42 BENCHMARK"}</span>
            </button>
          ) : undefined
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* Title Bar */}
        <div style={{
          borderBottom: "1px solid var(--border-subtle)",
          paddingBottom: "1.75rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
        }}>
          <div>
            <div style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem" }}>
              MULTI-PARTY LEDGER TRACE
            </div>
            <h1 className="heading-editorial title-huge">
              RECONCILIATION<br />CASES
            </h1>
            <div style={{ fontSize: "12.5px", color: "var(--text-secondary)", marginTop: "0.75rem" }}>
              Canonical multi-party transaction sets loaded in active working memory.
            </div>
          </div>

          <div style={{ textAlign: "right" }}>
            <div className="mono" style={{ fontSize: "10.5px", color: "var(--text-dim)" }}>INDEX COUNT</div>
            <div className="mono" style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-primary)" }}>{cases.length} REGISTERED CASES</div>
          </div>
        </div>

        {/* Filter Toolbar */}
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "1rem",
          background: "var(--bg-surface)",
          padding: "0.75rem 1rem",
          border: "1px solid var(--border-subtle)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
            <button
              onClick={() => setFilter("all")}
              style={{
                padding: "0.3rem 0.75rem",
                fontSize: "11px",
                fontWeight: 700,
                fontFamily: "var(--font-heading)",
                letterSpacing: "0.04em",
                backgroundColor: filter === "all" ? "var(--bg-surface-elevated)" : "transparent",
                color: filter === "all" ? "var(--text-primary)" : "var(--text-muted)",
                border: filter === "all" ? "1px solid var(--border-medium)" : "1px solid transparent",
                borderBottom: filter === "all" ? "2px solid var(--color-brand)" : "2px solid transparent",
              }}
            >
              ALL ({cases.length})
            </button>
            <button
              onClick={() => setFilter("discrepancies")}
              style={{
                padding: "0.3rem 0.75rem",
                fontSize: "11px",
                fontWeight: 700,
                fontFamily: "var(--font-heading)",
                letterSpacing: "0.04em",
                backgroundColor: filter === "discrepancies" ? "var(--bg-surface-elevated)" : "transparent",
                color: filter === "discrepancies" ? "var(--color-brand)" : "var(--text-muted)",
                border: filter === "discrepancies" ? "1px solid var(--border-medium)" : "1px solid transparent",
                borderBottom: filter === "discrepancies" ? "2px solid var(--color-brand)" : "2px solid transparent",
              }}
            >
              FLAGGED DISCREPANCIES ({discrepancyCount})
            </button>
            <button
              onClick={() => setFilter("clean")}
              style={{
                padding: "0.3rem 0.75rem",
                fontSize: "11px",
                fontWeight: 700,
                fontFamily: "var(--font-heading)",
                letterSpacing: "0.04em",
                backgroundColor: filter === "clean" ? "var(--bg-surface-elevated)" : "transparent",
                color: filter === "clean" ? "var(--status-reconciled)" : "var(--text-muted)",
                border: filter === "clean" ? "1px solid var(--border-medium)" : "1px solid transparent",
                borderBottom: filter === "clean" ? "2px solid var(--status-reconciled)" : "2px solid transparent",
              }}
            >
              CLEAN ({cleanCount})
            </button>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <input
              type="text"
              placeholder="SEARCH BY CASE OR MERCHANT..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input mono"
              style={{ width: "260px", textTransform: "uppercase", fontSize: "11px" }}
            />
          </div>
        </div>

        {/* Cases Table */}
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>CASE ID</th>
                <th>MERCHANT</th>
                <th>DIFFICULTY</th>
                <th>DISCREPANCIES</th>
                <th>STATUS</th>
                <th style={{ textAlign: "right" }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "2.5rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                    SCANNING CASE REPOSITORY...
                  </td>
                </tr>
              ) : filteredCases.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "2.5rem", color: "var(--text-muted)" }}>
                    No matching cases found.
                  </td>
                </tr>
              ) : (
                filteredCases.map((c) => (
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
                      <span className="mono" style={{
                        fontSize: "10.5px",
                        textTransform: "uppercase",
                        color: "var(--text-secondary)",
                      }}>
                        {c.difficulty}
                      </span>
                    </td>
                    <td>
                      <DiscrepancyBadge count={c.discrepancies_count} status={c.status} />
                    </td>
                    <td>
                      <span style={{
                        fontSize: "10.5px",
                        fontWeight: 700,
                        textTransform: "uppercase",
                        letterSpacing: "0.04em",
                        color: c.status === "reconciled" ? "var(--status-reconciled)" : "var(--color-brand)",
                      }}>
                        ● {c.status}
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
