"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { DiscrepancyBadge } from "@/components/cases/DiscrepancyBadge";
import { RecordsInspector } from "@/components/cases/RecordsInspector";
import { EvidenceGraphCanvas } from "@/components/graph/EvidenceGraphCanvas";
import { InvestigationPanel } from "@/components/investigator/InvestigationPanel";
import { BeforeAfterTable } from "@/components/simulator/BeforeAfterTable";
import { ApprovalDrawer } from "@/components/approvals/ApprovalDrawer";
import { api, CaseDetail, InvestigationResult } from "@/lib/api";

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = params?.id as string;

  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationResult | null>(null);
  const [activeView, setActiveView] = useState<"records" | "graph" | "investigation" | "simulation">("records");
  const [isLoading, setIsLoading] = useState(true);
  const [isInvestigating, setIsInvestigating] = useState(false);

  const loadCase = async () => {
    if (!caseId) return;
    setIsLoading(true);
    try {
      const data = await api.getCase(caseId);
      setCaseData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCase();
  }, [caseId]);

  const handleRunInvestigation = async () => {
    if (!caseData) return;
    setIsInvestigating(true);
    try {
      const result = await api.investigateCase(caseId, caseData.observed);
      setInvestigation(result);
      setActiveView("investigation");
    } catch (err) {
      console.error(err);
    } finally {
      setIsInvestigating(false);
    }
  };

  if (isLoading) {
    return (
      <div>
        <Header title={`Case Workspace: ${caseId}`} subtitle="Loading canonical records..." />
        <div className="page-body" style={{ textAlign: "center", padding: "4rem" }}>
          <p style={{ color: "var(--text-muted)" }}>Loading case records & evidence graph...</p>
        </div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div>
        <Header title="Case Not Found" />
        <div className="page-body" style={{ textAlign: "center", padding: "4rem" }}>
          <p style={{ color: "var(--status-discrepancy)" }}>Case '{caseId}' could not be located in repository.</p>
          <Link href="/cases" className="btn-secondary" style={{ marginTop: "1rem", display: "inline-block" }}>
            ← Back to Case Explorer
          </Link>
        </div>
      </div>
    );
  }

  const discrepancies = caseData.discrepancies || [];

  return (
    <div>
      <Header
        title={`Case Workspace: ${caseData.case_id}`}
        subtitle={`Merchant: ${caseData.merchant_id} | Ingestion Level: ${caseData.difficulty?.toUpperCase()}`}
        actions={
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
            <DiscrepancyBadge status={caseData.status} />
            <button
              onClick={handleRunInvestigation}
              disabled={isInvestigating}
              className="btn-primary"
            >
              {isInvestigating ? "Investigating..." : "⚡ Run AI Investigation"}
            </button>
          </div>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Discrepancy Alert Banner */}
        {discrepancies.length > 0 ? (
          <div style={{
            backgroundColor: "var(--status-discrepancy-bg)",
            border: "1px solid var(--status-discrepancy-border)",
            borderRadius: "8px",
            padding: "1rem 1.25rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.5rem",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "1.1rem" }}>⚠️</span>
              <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--status-discrepancy)" }}>
                {discrepancies.length} Deterministic Discrepancies Flagged by Reconciliation Engine
              </h4>
            </div>
            <ul style={{ paddingLeft: "1.5rem", fontSize: "0.85rem", color: "#fff", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
              {discrepancies.map((d: any, idx: number) => (
                <li key={`disc-${idx}`}>
                  <strong className="mono" style={{ color: "var(--status-discrepancy)" }}>
                    {d.discrepancy_type?.replace(/_/g, " ").toUpperCase()}:
                  </strong>{" "}
                  {d.description}
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div style={{
            backgroundColor: "var(--status-reconciled-bg)",
            border: "1px solid var(--status-reconciled-border)",
            borderRadius: "8px",
            padding: "0.85rem 1.25rem",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
          }}>
            <span>✓</span>
            <div style={{ fontSize: "0.85rem", color: "var(--status-reconciled)", fontWeight: 600 }}>
              All observed payments, settlements, fees, and ledger postings are perfectly balanced (0 Discrepancies).
            </div>
          </div>
        )}

        {/* View Switcher Tabs */}
        <div style={{ display: "flex", gap: "0.5rem", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "0.5rem" }}>
          <button
            onClick={() => setActiveView("records")}
            className={activeView === "records" ? "btn-primary" : "btn-secondary"}
            style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem" }}
          >
            📋 Financial Records
          </button>
          <button
            onClick={() => setActiveView("graph")}
            className={activeView === "graph" ? "btn-primary" : "btn-secondary"}
            style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem" }}
          >
            🕸️ Evidence Graph
          </button>
          <button
            onClick={() => setActiveView("investigation")}
            className={activeView === "investigation" ? "btn-primary" : "btn-secondary"}
            style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem" }}
          >
            🤖 AI Investigation {investigation ? "✓" : ""}
          </button>
          <button
            onClick={() => setActiveView("simulation")}
            className={activeView === "simulation" ? "btn-primary" : "btn-secondary"}
            style={{ fontSize: "0.8rem", padding: "0.4rem 0.85rem" }}
          >
            🔮 Resolution Simulator {investigation?.resolution_plan ? "✓" : ""}
          </button>
        </div>

        {/* Active View Section */}
        {activeView === "records" && (
          <RecordsInspector observed={caseData.observed} />
        )}

        {activeView === "graph" && (
          <EvidenceGraphCanvas graphData={caseData.evidence_graph} />
        )}

        {activeView === "investigation" && (
          <InvestigationPanel
            investigation={investigation}
            isLoading={isInvestigating}
            onTriggerInvestigation={handleRunInvestigation}
          />
        )}

        {activeView === "simulation" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            <BeforeAfterTable plan={investigation?.resolution_plan} />

            {investigation?.resolution_plan && (
              <ApprovalDrawer
                proposalId={investigation.resolution_plan.plan_id}
                onSuccess={() => loadCase()}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
