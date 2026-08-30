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
          <button onClick={loadAuditData} disabled={isLoading} className="btn-secondary" style={{ fontSize: "0.74rem" }}>
            <RefreshIcon size={12} />
            <span>{isLoading ? "Verifying..." : "Verify Hash Chain"}</span>
          </button>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 800, color: "#0f172a", letterSpacing: "-0.02em" }}>
            Cryptographic Audit Ledger
          </h1>
          <p style={{ fontSize: "0.76rem", color: "var(--text-muted)", marginTop: "2px" }}>
            Append-only event log with SHA-256 backwards hash-pointer verification across all reconciliation and simulation events.
          </p>
        </div>

        {/* Audit Timeline Table */}
        <AuditTimeline events={events} isTamperFree={isTamperFree} />
      </div>
    </div>
  );
}
