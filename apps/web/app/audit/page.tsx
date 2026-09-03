"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { AuditTimeline } from "@/components/audit/AuditTimeline";
import { RefreshIcon } from "@/components/icons/Icons";
import { api, AuditEvent } from "@/lib/api";

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [isTamperFree, setIsTamperFree] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState(true);

  const loadAuditData = async () => {
    setIsLoading(true);
    try {
      const res = await api.getAuditEvents();
      setEvents(res.events || []);
      setIsTamperFree(res.is_tamper_free ?? true);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAuditData();
  }, []);

  return (
    <div>
      <Header
        breadcrumbs={[{ label: "FinResolve", href: "/" }, { label: "Audit" }]}
        actions={
          <button onClick={loadAuditData} disabled={isLoading} className="btn btn-secondary btn-sm">
            <RefreshIcon size={12} />
            <span>{isLoading ? "Verifying..." : "Verify Hash Chain"}</span>
          </button>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {/* Title Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div>
            <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--color-indigo)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
              Compliance & Security Console
            </div>
            <h1 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.015em", marginTop: "2px" }}>
              Audit Integrity Ledger
            </h1>
            <p style={{ fontSize: "12.5px", color: "var(--text-muted)", marginTop: "2px" }}>
              Append-only event log with SHA-256 backwards hash-pointer verification across all reconciliation, simulation, and approval events.
            </p>
          </div>

          {/* Status Badge */}
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "0.6rem",
            padding: "0.4rem 0.85rem",
            backgroundColor: isTamperFree ? "var(--status-reconciled-bg)" : "var(--status-discrepancy-bg)",
            border: `1px solid ${isTamperFree ? "var(--status-reconciled-border)" : "var(--status-discrepancy-border)"}`,
            borderRadius: "5px",
            fontSize: "12px",
            color: isTamperFree ? "var(--status-reconciled)" : "var(--status-discrepancy)",
            fontWeight: 600,
          }}>
            <span>●</span>
            <span>{isTamperFree ? "HASH CHAIN VERIFIED (tamper_free: true)" : "TAMPERING DETECTED"}</span>
          </div>
        </div>

        {/* Audit Timeline Table */}
        <AuditTimeline events={events} isTamperFree={isTamperFree} />
      </div>
    </div>
  );
}
