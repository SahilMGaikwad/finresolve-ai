"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { DiscrepancyBadge } from "@/components/cases/DiscrepancyBadge";
import { api, CaseSummary } from "@/lib/api";

export default function CaseExplorerPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [filter, setFilter] = useState<"all" | "discrepancies" | "clean">("all");
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const res = await api.listCases(100, 0);
        setCases(res.cases || []);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const filteredCases = cases.filter((c) => {
    if (filter === "discrepancies" && c.discrepancies_count === 0) return false;
    if (filter === "clean" && c.discrepancies_count > 0) return false;
    if (search && !c.case_id.toLowerCase().includes(search.toLowerCase()) && !c.merchant_id.toLowerCase().includes(search.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div>
      <Header
        title="Reconciliation Case Explorer"
        subtitle="Search, filter, and inspect canonical financial cases across ingestion batches"
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Filter Controls Bar */}
        <div style={{ display: "flex", gap: "1rem", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              onClick={() => setFilter("all")}
              className={filter === "all" ? "btn-primary" : "btn-secondary"}
              style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem" }}
            >
              All Cases ({cases.length})
            </button>
            <button
              onClick={() => setFilter("discrepancies")}
              className={filter === "discrepancies" ? "btn-primary" : "btn-secondary"}
              style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem" }}
            >
              Flagged Discrepancies ({cases.filter((c) => c.discrepancies_count > 0).length})
            </button>
            <button
              onClick={() => setFilter("clean")}
              className={filter === "clean" ? "btn-primary" : "btn-secondary"}
              style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem" }}
            >
              Clean Reconciled ({cases.filter((c) => c.discrepancies_count === 0).length})
            </button>
          </div>

          <input
            type="text"
            placeholder="Search by Case ID or Merchant ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "6px",
              padding: "0.4rem 0.85rem",
              color: "#fff",
              fontSize: "0.85rem",
              width: "320px",
            }}
          />
        </div>

        {/* Case Table */}
        <div className="card" style={{ padding: "0" }}>
          <div style={{ overflowX: "auto" }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Merchant ID</th>
                  <th>Difficulty</th>
                  <th>Payments</th>
                  <th>Settlements</th>
                  <th>Discrepancies</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredCases.map((c) => (
                  <tr key={c.case_id}>
                    <td className="mono" style={{ fontWeight: 600, color: "var(--text-accent)" }}>
                      {c.case_id}
                    </td>
                    <td className="mono">{c.merchant_id}</td>
                    <td className="mono">{c.difficulty.toUpperCase()}</td>
                    <td className="mono">{c.payments_count}</td>
                    <td className="mono">{c.settlements_count}</td>
                    <td>
                      {c.discrepancies_count > 0 ? (
                        <span className="badge badge-discrepancy">{c.discrepancies_count} Discrepancies</span>
                      ) : (
                        <span className="badge badge-reconciled">Clean</span>
                      )}
                    </td>
                    <td><DiscrepancyBadge status={c.status} /></td>
                    <td>
                      <Link
                        href={`/cases/${c.case_id}`}
                        className="btn-secondary"
                        style={{ fontSize: "0.75rem", padding: "0.25rem 0.65rem" }}
                      >
                        Inspect Workspace →
                      </Link>
                    </td>
                  </tr>
                ))}
                {isLoading && (
                  <tr><td colSpan={8} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>Loading cases...</td></tr>
                )}
                {!isLoading && filteredCases.length === 0 && (
                  <tr><td colSpan={8} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>No cases match the selected filter</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
