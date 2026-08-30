"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { AuditTimeline } from "@/components/audit/AuditTimeline";
import { api, AuditEvent } from "@/lib/api";

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [isTamperFree, setIsTamperFree] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const res = await api.getAuditEvents();
        setEvents(res.events || []);
        setIsTamperFree(res.is_tamper_free);
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
        title="Immutable Audit Ledger & Cryptographic Chain"
        subtitle="Verifiable SHA-256 event chaining ensuring non-repudiation of financial operations"
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {isLoading ? (
          <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
            <p style={{ color: "var(--text-muted)" }}>Verifying SHA-256 cryptographic chain...</p>
          </div>
        ) : (
          <AuditTimeline events={events} isTamperFree={isTamperFree} />
        )}
      </div>
    </div>
  );
}
