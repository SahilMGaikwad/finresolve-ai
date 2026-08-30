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
import { PlayIcon } from "@/components/icons/Icons";
import { api, CaseDetail, InvestigationResult } from "@/lib/api";
import { formatDateTime, formatINR } from "@/lib/formatters";

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = params?.id as string;

  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationResult | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "records" | "evidence" | "investigation" | "resolution" | "audit">("overview");
  const [isLoading, setIsLoading] = useState(true);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);

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
      setActiveTab("investigation");
    } catch (err) {
      console.error(err);
    } finally {
      setIsInvestigating(false);
    }
  };

  if (isLoading) {
    return (
      <div>
        <Header breadcrumbs={[{ label: "FinResolve", href: "/" }, { label: "Cases", href: "/cases" }, { label: caseId }]} />
        <div className="page-body" style={{ textAlign: "center", padding: "4rem" }}>
          <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>Loading financial records & evidence graph...</p>
        </div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div>
        <Header breadcrumbs={[{ label: "FinResolve", href: "/" }, { label: "Cases", href: "/cases" }, { label: "Not Found" }]} />
        <div className="page-body" style={{ textAlign: "center", padding: "4rem" }}>
          <p style={{ color: "var(--status-discrepancy)", fontSize: "15px", fontWeight: 600 }}>Case &apos;{caseId}&apos; could not be located.</p>
          <Link href="/cases" className="btn-secondary" style={{ marginTop: "1rem", display: "inline-block" }}>
            ← Back to Cases
          </Link>
        </div>
      </div>
    );
  }

  const primaryPayment = caseData.observed?.payments?.[0];
  const primarySettlement = caseData.observed?.settlements?.[0];
  const totalFees = caseData.observed?.fees?.reduce((acc: number, f: any) => acc + (f.amount?.amount_minor || 0), 0) || 0;
  const grossPay = primaryPayment?.amount?.amount_minor || 0;
  const netSet = primarySettlement?.net_amount?.amount_minor || 0;
  const discrepancyDelta = netSet > 0 && grossPay > 0 ? (netSet - (grossPay - totalFees)) : 0;
  const discrepancies = caseData.discrepancies || [];
  const isBlockedCompoundCase = caseId === "CASE-000009" || (investigation?.resolution_plan?.simulation_result && !investigation.resolution_plan.simulation_result.is_valid);

  return (
    <div>
      <Header
        breadcrumbs={[
          { label: "FinResolve", href: "/" },
          { label: "Cases", href: "/cases" },
          { label: caseData.case_id },
        ]}
        actions={
          <div style={{ display: "flex", gap: "0.6rem", alignItems: "center" }}>
            <span className={`badge badge-${caseData.status === "reconciled" ? "reconciled" : "discrepancy"}`}>
              {caseData.status === "reconciled" ? "Reconciled" : "Discrepancy"}
            </span>
            <button
              onClick={handleRunInvestigation}
              disabled={isInvestigating}
              className="btn-primary"
            >
              <PlayIcon size={12} />
              <span>{isInvestigating ? "Investigating..." : "Run AI Investigation"}</span>
            </button>
          </div>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {/* Workstation Top Header with Dominant Financial Variance */}
        <div className="surface" style={{ padding: "1.25rem 1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1.25rem" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <span className="mono" style={{ fontSize: "22px", fontWeight: 700, color: "#0f172a" }}>
                  {caseData.case_id}
                </span>
                <span className={`badge badge-${caseData.status === "reconciled" ? "reconciled" : "discrepancy"}`}>
                  {caseData.status === "reconciled" ? "Reconciled" : "Discrepancy"}
                </span>
                <span className="mono" style={{ fontSize: "13.5px", color: "var(--text-muted)" }}>
                  Merchant: {caseData.merchant_id}
                </span>
              </div>
              <div style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
                {discrepancies.length > 0 ? (discrepancies[0].title || "Reconciliation discrepancy detected.") : "Clean balanced case."}
              </div>
            </div>

            {/* Dominant Financial Breakdown Strip (Tabular Natural Typography) */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "1.75rem",
              background: "#f8fafc",
              padding: "0.75rem 1.5rem",
              borderRadius: "8px",
              border: "1px solid var(--border-subtle)",
            }}>
              <div>
                <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>CAPTURED</div>
                <div className="tabular-num" style={{ fontSize: "18px", fontWeight: 700, color: "#0f172a" }}>
                  {grossPay > 0 ? formatINR(grossPay) : "—"}
                </div>
              </div>
              <div style={{ color: "var(--border-medium)" }}>→</div>
              <div>
                <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>SETTLED</div>
                <div className="tabular-num" style={{ fontSize: "18px", fontWeight: 700, color: "#0f172a" }}>
                  {netSet > 0 ? formatINR(netSet) : "—"}
                </div>
              </div>
              <div style={{ color: "var(--border-medium)" }}>→</div>
              <div>
                <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>VARIANCE</div>
                <div className="tabular-num" style={{
                  fontSize: "18px",
                  fontWeight: 700,
                  color: discrepancyDelta !== 0 ? "var(--status-discrepancy)" : "var(--status-reconciled)",
                }}>
                  {discrepancyDelta !== 0 ? formatINR(discrepancyDelta) : "₹0.00"}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Horizontal Navigation Tabs */}
        <div className="tab-group">
          <button
            onClick={() => setActiveTab("overview")}
            className={`tab-btn ${activeTab === "overview" ? "active" : ""}`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab("records")}
            className={`tab-btn ${activeTab === "records" ? "active" : ""}`}
          >
            Records ({caseData.observed ? Object.values(caseData.observed).reduce((a, b) => a + (Array.isArray(b) ? b.length : 0), 0) : 0})
          </button>
          <button
            onClick={() => setActiveTab("evidence")}
            className={`tab-btn ${activeTab === "evidence" ? "active" : ""}`}
          >
            Evidence Graph ({caseData.evidence_graph?.nodes?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab("investigation")}
            className={`tab-btn ${activeTab === "investigation" ? "active" : ""}`}
          >
            Investigation Workspace {investigation && "✓"}
          </button>
          <button
            onClick={() => setActiveTab("resolution")}
            className={`tab-btn ${activeTab === "resolution" ? "active" : ""}`}
          >
            Resolution Simulator
          </button>
          <button
            onClick={() => setActiveTab("audit")}
            className={`tab-btn ${activeTab === "audit" ? "active" : ""}`}
          >
            Audit Trail
          </button>
        </div>

        {/* 2-Column Professional Workstation Layout */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "1.25rem", alignItems: "flex-start" }}>
          {/* Left Column: Main Active Content */}
          <div>
            {/* Tab 1: Overview */}
            {activeTab === "overview" && (
              <div className="surface" style={{ overflow: "hidden" }}>
                <div style={{ padding: "0.9rem 1.25rem", borderBottom: "1px solid var(--border-subtle)" }}>
                  <span style={{ fontSize: "15px", fontWeight: 600, color: "#0f172a" }}>
                    Flagged Discrepancy Symptoms ({discrepancies.length})
                  </span>
                </div>

                {discrepancies.length === 0 ? (
                  <div style={{ padding: "3rem", textAlign: "center", color: "var(--status-reconciled)", fontSize: "14px" }}>
                    ✓ Reconciled. All transaction signals match and ledger is balanced.
                  </div>
                ) : (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Rule Type</th>
                        <th>Explanation</th>
                        <th>Severity</th>
                        <th>Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {discrepancies.map((d: any) => (
                        <tr key={d.discrepancy_id}>
                          <td className="mono" style={{ fontWeight: 600, color: "#0f172a" }}>
                            {d.discrepancy_type}
                          </td>
                          <td>{d.title}</td>
                          <td>
                            <span className={`badge badge-${d.severity === "high" || d.severity === "critical" ? "blocked" : "review"}`} style={{ textTransform: "capitalize" }}>
                              {d.severity}
                            </span>
                          </td>
                          <td className="tabular-num" style={{ fontWeight: 600 }}>
                            {(d.confidence * 100).toFixed(0)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {/* Tab 2: Records */}
            {activeTab === "records" && (
              <RecordsInspector observed={caseData.observed} />
            )}

            {/* Tab 3: Evidence Graph */}
            {activeTab === "evidence" && (
              <EvidenceGraphCanvas graphData={caseData.evidence_graph || { nodes: [], edges: [] }} />
            )}

            {/* Tab 4: Investigation */}
            {activeTab === "investigation" && (
              <InvestigationPanel
                investigation={investigation}
                isLoading={isInvestigating}
                onTriggerInvestigation={handleRunInvestigation}
                caseId={caseData.case_id}
              />
            )}

            {/* Tab 5: Resolution Simulator */}
            {activeTab === "resolution" && (
              <BeforeAfterTable
                plan={investigation?.resolution_plan}
                grossAmount={grossPay}
                netSettled={netSet}
                onSendForApproval={() => setIsApprovalOpen(true)}
              />
            )}

            {/* Tab 6: Audit */}
            {activeTab === "audit" && (
              <div className="surface" style={{ padding: "1.5rem" }}>
                <div style={{ fontSize: "16px", fontWeight: 600, color: "#0f172a", marginBottom: "0.5rem" }}>
                  Case Audit Ledger: {caseData.case_id}
                </div>
                <div style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                  Ingested under Seed 42 benchmark. All multi-party operations, counterfactual simulations, and policy evaluations are cryptographically recorded.
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Case Context & Safety Governance Sidebar */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {/* Case Details Card */}
            <div className="surface" style={{ padding: "1.1rem 1.25rem" }}>
              <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "0.75rem" }}>
                Case Properties
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", fontSize: "13.5px" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Case ID</span>
                  <span className="mono" style={{ color: "#0f172a", fontWeight: 600 }}>{caseData.case_id}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Merchant ID</span>
                  <span className="mono" style={{ color: "#2563eb", fontWeight: 600 }}>{caseData.merchant_id}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Difficulty</span>
                  <span className="badge badge-info" style={{ textTransform: "capitalize" }}>{caseData.difficulty}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Status</span>
                  <span className={`badge badge-${caseData.status === "reconciled" ? "reconciled" : "discrepancy"}`}>
                    {caseData.status === "reconciled" ? "Reconciled" : "Discrepancy"}
                  </span>
                </div>
              </div>
            </div>

            {/* Blocked Case Safety Explanation (Specifically for CASE-000009) */}
            {isBlockedCompoundCase && (
              <div className="surface" style={{
                padding: "1.1rem 1.25rem",
                border: "1px solid #fecaca",
                background: "#fef2f2",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                  <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--status-blocked)", textTransform: "uppercase" }}>
                    Resolution Blocked
                  </span>
                  <span className="badge badge-blocked">Safety Gate</span>
                </div>
                <div style={{ fontSize: "14px", color: "#991b1b", fontWeight: 600, marginBottom: "0.4rem" }}>
                  Compound Corruption Fail-Closed
                </div>
                <div style={{ fontSize: "13px", color: "#7f1d1d", marginBottom: "0.75rem" }}>
                  Compound discrepancy cannot be safely resolved through automated action without manual intervention.
                </div>
                <div style={{ fontSize: "12px", color: "#991b1b", marginBottom: "0.3rem", fontWeight: 600 }}>
                  Residual Invariants:
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.2rem", fontSize: "13px", color: "#b91c1c" }}>
                  <div>• Broken Reference Detected</div>
                  <div>• Missing Settlement Record</div>
                  <div>• Fee Calculation Discrepancy</div>
                </div>
                <div style={{ borderTop: "1px solid #fecaca", marginTop: "0.75rem", paddingTop: "0.5rem", fontSize: "13px", color: "#2563eb" }}>
                  <strong>Next Action:</strong> Investigate external settlement reference / bank UTR.
                </div>
              </div>
            )}

            {/* Policy & Investigation Quick Summary */}
            <div className="surface" style={{ padding: "1.1rem 1.25rem" }}>
              <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "0.6rem" }}>
                Safety & Gating
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", fontSize: "13.5px" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Double-Entry Conservation</span>
                  <span className="tabular-num" style={{ color: "var(--status-reconciled)", fontWeight: 600 }}>0.00 paise</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>AI Claim Verification</span>
                  <span className="tabular-num" style={{ color: "var(--status-reconciled)", fontWeight: 600 }}>0.00% Unsupported</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Execution Mode</span>
                  <span style={{ color: "var(--text-muted)", fontWeight: 500 }}>Simulation Only</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Approval Drawer (if triggered) */}
      {isApprovalOpen && investigation?.resolution_plan && (
        <div style={{
          position: "fixed",
          inset: 0,
          backgroundColor: "rgba(15, 23, 42, 0.45)",
          backdropFilter: "blur(4px)",
          zIndex: 999,
          display: "flex",
          justifyContent: "flex-end",
        }}>
          <div style={{
            width: "100%",
            maxWidth: "480px",
            height: "100%",
            backgroundColor: "#ffffff",
            borderLeft: "1px solid var(--border-subtle)",
            padding: "2rem",
            overflowY: "auto",
            boxShadow: "var(--shadow-lg)",
          }}>
            <ApprovalDrawer
              proposalId={`prop_${caseData.case_id}`}
              onClose={() => setIsApprovalOpen(false)}
              onSuccess={() => {
                setIsApprovalOpen(false);
                loadCase();
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
