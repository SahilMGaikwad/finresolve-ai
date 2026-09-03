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
        breadcrumbs={[{ label: "FINRESOLVE", href: "/" }, { label: "AUDIT" }]}
        actions={
          <button onClick={loadAuditData} disabled={isLoading} className="btn btn-secondary btn-sm">
            <RefreshIcon size={12} />
            <span>{isLoading ? "VERIFYING..." : "VERIFY HASH CHAIN"}</span>
          </button>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* Title Header */}
        <div style={{
          borderBottom: "1px solid var(--border-subtle)",
          paddingBottom: "1.75rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
        }}>
          <div>
            <div style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem" }}>
              CRYPTOGRAPHIC PROOF ARCHIVE
            </div>
            <h1 className="heading-editorial title-huge">
              AUDIT<br />INTEGRITY
            </h1>
            <div style={{ fontSize: "12.5px", color: "var(--text-secondary)", marginTop: "0.75rem" }}>
              Append-only cryptographic ledger with SHA-256 backwards hash-pointer verification.
            </div>
          </div>

          <div style={{ textAlign: "right" }}>
            <div style={{
              fontSize: "11px",
              fontWeight: 700,
              color: isTamperFree ? "var(--status-reconciled)" : "var(--color-brand)",
              letterSpacing: "0.06em",
            }}>
              ● {isTamperFree ? "HASH CHAIN VERIFIED (tamper_free: true)" : "CHAIN TAMPERED"}
            </div>
            <div className="mono" style={{ fontSize: "10.5px", color: "var(--text-dim)", marginTop: "4px" }}>
              GENESIS → LATEST BLOCK
            </div>
          </div>
        </div>

        {/* Audit Timeline Table */}
        <AuditTimeline events={events} isTamperFree={isTamperFree} />
      </div>
    </div>
  );
}
