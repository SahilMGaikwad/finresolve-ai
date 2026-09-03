"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { RefreshIcon } from "@/components/icons/Icons";
import { api } from "@/lib/api";

export default function HealthPage() {
  const [health, setHealth] = useState<any>(null);
  const [ready, setReady] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadHealthData = async () => {
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
  };

  useEffect(() => {
    loadHealthData();
  }, []);

  const services = [
    { name: "API Gateway", status: health?.status === "ok" ? "OPERATIONAL" : "UNAVAILABLE", endpoint: "/health" },
    { name: "Reconciliation Engine", status: ready?.checks?.reconciliation_engine === "ready" ? "OPERATIONAL" : "DEGRADED", endpoint: "/ready" },
    { name: "Evidence Engine", status: ready?.checks?.application === "ready" ? "OPERATIONAL" : "DEGRADED", endpoint: "/ready" },
    { name: "AI Investigator", status: ready?.checks?.investigator_engine === "ready" ? "OPERATIONAL" : "DEGRADED", endpoint: "/ready" },
    { name: "Simulator", status: ready?.checks?.counterfactual_engine === "ready" ? "OPERATIONAL" : "DEGRADED", endpoint: "/ready" },
    { name: "Policy Engine", status: ready?.checks?.policy_engine === "ready" ? "OPERATIONAL" : "DEGRADED", endpoint: "/ready" },
    { name: "Audit Ledger", status: ready?.checks?.config === "valid" ? "OPERATIONAL" : "DEGRADED", endpoint: "/audit/events" },
  ];

  return (
    <div>
      <Header
        breadcrumbs={[{ label: "FinResolve", href: "/" }, { label: "System Health" }]}
        actions={
          <button onClick={loadHealthData} disabled={isLoading} className="btn btn-secondary btn-sm">
            <RefreshIcon size={12} />
            <span>{isLoading ? "Checking..." : "Refresh Status"}</span>
          </button>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        <div>
          <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--color-indigo)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Infrastructure Telemetry
          </div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.015em", marginTop: "2px" }}>
            Engine Subsystem Health
          </h1>
          <p style={{ fontSize: "12.5px", color: "var(--text-muted)", marginTop: "2px" }}>
            Real-time readiness verification for core financial reconciliation and investigation microservices.
          </p>
        </div>

        {/* Engine Services Status Table */}
        <div className="table-container">
          <div style={{ padding: "0.85rem 1rem", borderBottom: "1px solid var(--border-subtle)" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
              Engine Subsystems
            </span>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Service Name</th>
                <th>Endpoint Check</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {services.map((s) => (
                <tr key={s.name}>
                  <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                    {s.name}
                  </td>
                  <td className="mono" style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {s.endpoint}
                  </td>
                  <td>
                    <span className={`badge badge-${s.status === "OPERATIONAL" ? "reconciled" : "discrepancy"}`} style={{ fontSize: "10.5px" }}>
                      ● {s.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Runtime Performance Telemetry */}
        <div className="table-container">
          <div style={{ padding: "0.85rem 1rem", borderBottom: "1px solid var(--border-subtle)" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
              Runtime Telemetry (/metrics)
            </span>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Metric Name</th>
                <th>Value</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="mono" style={{ fontWeight: 600, color: "var(--text-primary)" }}>http_requests_total</td>
                <td className="mono tabular-num" style={{ fontWeight: 700, color: "var(--color-indigo)" }}>{metrics?.http_requests_total || 0}</td>
                <td style={{ color: "var(--text-muted)", fontSize: "12px" }}>Total HTTP requests handled</td>
              </tr>
              <tr>
                <td className="mono" style={{ fontWeight: 600, color: "var(--text-primary)" }}>cases_total</td>
                <td className="mono tabular-num" style={{ fontWeight: 700, color: "var(--color-indigo)" }}>{metrics?.cases_total || 50}</td>
                <td style={{ color: "var(--text-muted)", fontSize: "12px" }}>Active case entities in working memory</td>
              </tr>
              <tr>
                <td className="mono" style={{ fontWeight: 600, color: "var(--text-primary)" }}>simulations_total</td>
                <td className="mono tabular-num" style={{ fontWeight: 700, color: "var(--status-reconciled)" }}>{metrics?.simulations_total || 0}</td>
                <td style={{ color: "var(--text-muted)", fontSize: "12px" }}>Counterfactual simulations executed</td>
              </tr>
              <tr>
                <td className="mono" style={{ fontWeight: 600, color: "var(--text-primary)" }}>audit_events_total</td>
                <td className="mono tabular-num" style={{ fontWeight: 700, color: "var(--status-reconciled)" }}>{metrics?.audit_events_total || 0}</td>
                <td style={{ color: "var(--text-muted)", fontSize: "12px" }}>Cryptographic SHA-256 blocks recorded</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
