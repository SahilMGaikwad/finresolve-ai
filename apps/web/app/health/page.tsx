"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { api } from "@/lib/api";

export default function HealthPage() {
  const [health, setHealth] = useState<any>(null);
  const [ready, setReady] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const [h, r, m] = await Promise.all([
          api.getHealth().catch(() => ({ status: "offline" })),
          api.getReady().catch(() => ({ status: "unavailable" })),
          api.getMetrics().catch(() => ({})),
        ]);
        setHealth(h);
        setReady(r);
        setMetrics(m);
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
        title="System Telemetry & Engine Health"
        subtitle="Live subsystem readiness, throughput counters, and reconciliation performance metrics"
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Core Subsystem Readiness Grid */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "#fff" }}>
              Core Engine Subsystem Readiness (/ready)
            </h3>
            <span className={ready?.status === "ready" ? "badge badge-reconciled" : "badge badge-discrepancy"}>
              {ready?.status === "ready" ? "ALL SYSTEMS OPERATIONAL" : "DEGRADED"}
            </span>
          </div>

          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1rem",
          }}>
            {ready?.checks && Object.entries(ready.checks).map(([key, val]: [string, any]) => (
              <div
                key={key}
                style={{
                  backgroundColor: "var(--bg-secondary)",
                  padding: "0.85rem 1rem",
                  borderRadius: "6px",
                  border: "1px solid var(--border-subtle)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                  {key.replace(/_/g, " ").toUpperCase()}
                </span>
                <span className="mono" style={{ fontSize: "0.75rem", fontWeight: 600, color: val === "ready" || val === "valid" ? "var(--status-reconciled)" : "var(--status-discrepancy)" }}>
                  {String(val).toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Global Observability Counters */}
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "#fff", marginBottom: "1rem" }}>
            Engine Throughput & Latency Snapshot (/metrics)
          </h3>

          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "1rem",
          }}>
            <div style={{ backgroundColor: "var(--bg-secondary)", padding: "1rem", borderRadius: "6px", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Health Checks Total</div>
              <div className="mono" style={{ fontSize: "1.5rem", fontWeight: 700, color: "#fff", marginTop: "0.25rem" }}>
                {metrics?.counters?.health_checks_total || 0}
              </div>
            </div>

            <div style={{ backgroundColor: "var(--bg-secondary)", padding: "1rem", borderRadius: "6px", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Resolution Proposals</div>
              <div className="mono" style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-accent)", marginTop: "0.25rem" }}>
                {metrics?.counters?.resolution_requests_total || 0}
              </div>
            </div>

            <div style={{ backgroundColor: "var(--bg-secondary)", padding: "1rem", borderRadius: "6px", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>AI Investigations</div>
              <div className="mono" style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--status-info)", marginTop: "0.25rem" }}>
                {metrics?.counters?.investigation_requests_total || 0}
              </div>
            </div>

            <div style={{ backgroundColor: "var(--bg-secondary)", padding: "1rem", borderRadius: "6px", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Application Environment</div>
              <div className="mono" style={{ fontSize: "1.2rem", fontWeight: 700, color: "#fff", marginTop: "0.25rem" }}>
                {health?.environment?.toUpperCase() || "DEVELOPMENT"} (v{health?.version || "0.6.0"})
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
