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
    { name: "API Gateway", status: health?.status === "ok" ? "HEALTHY" : "UNAVAILABLE", endpoint: "/health" },
    { name: "Reconciliation Engine", status: ready?.checks?.reconciliation_engine === "ready" ? "HEALTHY" : "DEGRADED", endpoint: "/ready" },
    { name: "Counterfactual Simulator", status: ready?.checks?.counterfactual_engine === "ready" ? "HEALTHY" : "DEGRADED", endpoint: "/ready" },
    { name: "Policy Engine", status: ready?.checks?.policy_engine === "ready" ? "HEALTHY" : "DEGRADED", endpoint: "/ready" },
    { name: "AI Investigator", status: ready?.checks?.investigator_engine === "ready" ? "HEALTHY" : "DEGRADED", endpoint: "/ready" },
    { name: "Cryptographic Audit Logger", status: ready?.checks?.config === "valid" ? "HEALTHY" : "DEGRADED", endpoint: "/audit/events" },
  ];

  return (
    <div>
      <Header
        breadcrumbs={[{ label: "FinResolve", href: "/" }, { label: "System Health" }]}
        actions={
          <button onClick={loadHealthData} disabled={isLoading} className="btn-secondary" style={{ fontSize: "0.74rem" }}>
            <RefreshIcon size={12} />
            <span>{isLoading ? "Checking..." : "Refresh Status"}</span>
          </button>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        <div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 800, color: "#0f172a", letterSpacing: "-0.02em" }}>
            System Subsystem Health
          </h1>
          <p style={{ fontSize: "0.76rem", color: "var(--text-muted)", marginTop: "2px" }}>
            Real-time readiness verification for core financial reconciliation and investigation microservices.
          </p>
        </div>

        {/* Services Table */}
        <div className="surface" style={{ overflow: "hidden" }}>
          <div style={{ padding: "0.75rem 1.15rem", borderBottom: "1px solid var(--border-subtle)" }}>
            <span style={{ fontSize: "0.88rem", fontWeight: 800, color: "#0f172a" }}>
              Engine Services Status
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
                  <td style={{ fontWeight: 700, color: "#0f172a" }}>
                    {s.name}
                  </td>
                  <td className="mono" style={{ fontSize: "0.74rem", color: "var(--text-muted)" }}>
                    {s.endpoint}
                  </td>
                  <td>
                    <span className={`badge badge-${s.status === "HEALTHY" ? "reconciled" : "discrepancy"}`}>
                      {s.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Runtime Performance Telemetry Table */}
        <div className="surface" style={{ overflow: "hidden" }}>
          <div style={{ padding: "0.75rem 1.15rem", borderBottom: "1px solid var(--border-subtle)" }}>
            <span style={{ fontSize: "0.88rem", fontWeight: 800, color: "#0f172a" }}>
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
                <td className="mono" style={{ fontWeight: 700, color: "#0f172a" }}>http_requests_total</td>
                <td className="mono" style={{ fontWeight: 800, color: "#2563eb" }}>{metrics?.http_requests_total || 0}</td>
                <td style={{ color: "var(--text-muted)", fontSize: "0.74rem" }}>Total HTTP requests handled</td>
              </tr>
              <tr>
                <td className="mono" style={{ fontWeight: 700, color: "#0f172a" }}>cases_total</td>
                <td className="mono" style={{ fontWeight: 800, color: "#2563eb" }}>{metrics?.cases_total || 0}</td>
                <td style={{ color: "var(--text-muted)", fontSize: "0.74rem" }}>Active case entities in working memory</td>
              </tr>
              <tr>
                <td className="mono" style={{ fontWeight: 700, color: "#0f172a" }}>simulations_total</td>
                <td className="mono" style={{ fontWeight: 800, color: "#059669" }}>{metrics?.simulations_total || 0}</td>
                <td style={{ color: "var(--text-muted)", fontSize: "0.74rem" }}>Counterfactual simulations executed</td>
              </tr>
              <tr>
                <td className="mono" style={{ fontWeight: 700, color: "#0f172a" }}>audit_events_total</td>
                <td className="mono" style={{ fontWeight: 800, color: "#059669" }}>{metrics?.audit_events_total || 0}</td>
                <td style={{ color: "var(--text-muted)", fontSize: "0.74rem" }}>Cryptographic SHA-256 blocks recorded</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
