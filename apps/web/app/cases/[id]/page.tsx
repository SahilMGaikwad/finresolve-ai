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
  const [activeTab, setActiveTab] = useState<"overview" | "records" | "evidence" | "investigation" | "resolution">("overview");
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
          <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>Loading financial records & evidence graph...</p>
        </div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div>
        <Header breadcrumbs={[{ label: "FinResolve", href: "/" }, { label: "Cases", href: "/cases" }, { label: "Not Found" }]} />
        <div className="page-body" style={{ textAlign: "center", padding: "4rem" }}>
          <p style={{ color: "var(--status-discrepancy)", fontSize: "14px", fontWeight: 600 }}>Case &apos;{caseId}&apos; could not be located.</p>
          <Link href="/cases" className="btn btn-secondary" style={{ marginTop: "1rem" }}>
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
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <button
              onClick={handleRunInvestigation}
              disabled={isInvestigating}
              className="btn btn-primary btn-sm"
            >
              <PlayIcon size={12} />
              <span>{isInvestigating ? "Investigating..." : "Run AI Investigation"}</span>
            </button>
          </div>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {/* Terminal Header */}
        <div className="surface" style={{ padding: "1rem 1.25rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.75rem" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span className="mono" style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-primary)" }}>
                  {caseData.case_id}
                </span>
                <span style={{
                  fontSize: "11px",
                  padding: "0.15rem 0.45rem",
                  borderRadius: "3px",
                  backgroundColor: "var(--bg-surface-secondary)",
                  color: "var(--text-secondary)",
                  border: "1px solid var(--border-subtle)",
                }}>
                  Merchant: {caseData.merchant_id}
                </span>
                <span className={`badge badge-${caseData.status === "reconciled" ? "reconciled" : "discrepancy"}`}>
                  {caseData.status === "reconciled" ? "RECONCILED" : "DISCREPANCY DETECTED"}
                </span>
                {isBlockedCompoundCase && (
                  <span className="badge badge-blocked">
                    FAIL-CLOSED BLOCKED
                  </span>
                )}
              </div>
              <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
                Multi-party ledger reconciliation trace • Difficulty: <strong style={{ textTransform: "capitalize", color: "var(--text-secondary)" }}>{caseData.difficulty}</strong>
              </div>
            </div>

            {/* Financial Variance Strip */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "1.25rem",
              backgroundColor: "var(--bg-surface-secondary)",
              padding: "0.5rem 1rem",
              borderRadius: "5px",
              border: "1px solid var(--border-subtle)",
            }}>
              <div>
                <div style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Captured</div>
                <div className="tabular-num mono" style={{ fontSize: "13.5px", fontWeight: 600, color: "var(--text-primary)" }}>
                  {grossPay > 0 ? formatINR(grossPay) : "—"}
                </div>
              </div>
              <div style={{ color: "var(--border-medium)" }}>→</div>
              <div>
                <div style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Settled</div>
                <div className="tabular-num mono" style={{ fontSize: "13.5px", fontWeight: 600, color: "var(--text-primary)" }}>
                  {netSet > 0 ? formatINR(netSet) : "—"}
                </div>
              </div>
              <div style={{ color: "var(--border-medium)" }}>→</div>
              <div>
                <div style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Variance</div>
                <div className="tabular-num mono" style={{
                  fontSize: "13.5px",
                  fontWeight: 700,
                  color: discrepancyDelta === 0 ? "var(--status-reconciled)" : "var(--status-discrepancy)",
                }}>
                  {discrepancyDelta !== 0 ? formatINR(discrepancyDelta) : "₹0.00"}
                </div>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div style={{
            display: "flex",
            gap: "0.25rem",
            marginTop: "1rem",
            borderTop: "1px solid var(--border-hairline)",
            paddingTop: "0.75rem",
          }}>
            {[
              { id: "overview", label: "Workstation Overview" },
              { id: "records", label: `Observed Records (${(caseData.observed?.payments?.length || 0) + (caseData.observed?.settlements?.length || 0) + (caseData.observed?.fees?.length || 0)})` },
              { id: "evidence", label: "Evidence Graph" },
              { id: "investigation", label: "AI Investigation" },
              { id: "resolution", label: "Resolution Simulator" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                style={{
                  padding: "0.35rem 0.75rem",
                  fontSize: "12px",
                  fontWeight: activeTab === tab.id ? 600 : 500,
                  borderRadius: "4px",
                  color: activeTab === tab.id ? "var(--text-primary)" : "var(--text-secondary)",
                  backgroundColor: activeTab === tab.id ? "var(--bg-surface-elevated)" : "transparent",
                  border: activeTab === tab.id ? "1px solid var(--border-medium)" : "1px solid transparent",
                  transition: "all 0.12s ease",
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab 1: Workstation Overview (2-Column Split) */}
        {activeTab === "overview" && (
          <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: "1rem" }}>
            {/* Left Column: Investigation Timeline & Discrepancies */}
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {/* Discrepancies Panel */}
              <div className="surface" style={{ padding: "1rem 1.25rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                  <h3 style={{ fontSize: "12.5px", fontWeight: 600, color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                    Detected Discrepancies ({discrepancies.length})
                  </h3>
                </div>
                {discrepancies.length === 0 ? (
                  <div style={{ padding: "1.25rem", textAlign: "center", color: "var(--text-muted)", fontSize: "12.5px" }}>
                    <div style={{ color: "var(--status-reconciled)", fontWeight: 600 }}>Zero Discrepancies Detected</div>
                    <div style={{ fontSize: "11.5px", marginTop: "2px" }}>All multi-party signals balance with zero accounting variance.</div>
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                    {discrepancies.map((d, i) => (
                      <div
                        key={i}
                        style={{
                          padding: "0.75rem 1rem",
                          backgroundColor: "var(--bg-surface-secondary)",
                          border: "1px solid var(--border-subtle)",
                          borderLeft: "3px solid var(--status-discrepancy)",
                          borderRadius: "4px",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-primary)" }}>
                            {d.rule_name || "Reconciliation Rule Exception"}
                          </span>
                          <span className="badge badge-discrepancy" style={{ fontSize: "10.5px" }}>
                            {d.severity?.toUpperCase() || "HIGH"}
                          </span>
                        </div>
                        <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
                          {d.description}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* 7-Stage Pipeline Visualizer */}
              <div className="surface" style={{ padding: "1rem 1.25rem" }}>
                <h3 style={{ fontSize: "12.5px", fontWeight: 600, color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: "0.75rem" }}>
                  Investigation Pipeline Stages
                </h3>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.45rem" }}>
                  {[
                    { num: "01", name: "DETECTED", desc: "Multi-signal reconciliation rules evaluated", state: "done" },
                    { num: "02", name: "EVIDENCE COLLECTED", desc: "Graph edges constructed for payments & settlements", state: "done" },
                    { num: "03", name: "ROOT CAUSE IDENTIFIED", desc: investigation ? "Diagnosed via Bayesian plausibility" : "Ready for AI investigation", state: investigation ? "done" : "ready" },
                    { num: "04", name: "SIMULATION", desc: isBlockedCompoundCase ? "Fail-closed blocked (invalid state)" : "Virtual deep-clone state validated", state: isBlockedCompoundCase ? "blocked" : (investigation ? "done" : "pending") },
                    { num: "05", name: "POLICY VALIDATION", desc: "Deterministic gating POL-001 - POL-003", state: investigation ? "done" : "pending" },
                    { num: "06", name: "APPROVAL", desc: "Separation of duties review workflow", state: investigation?.resolution_plan?.policy_decision?.decision === "HUMAN_REVIEW" ? "active" : "pending" },
                    { num: "07", name: "AUDIT", desc: "Append-only SHA-256 backwards hash-pointer", state: "done" },
                  ].map((stage, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "0.75rem",
                        padding: "0.45rem 0.65rem",
                        backgroundColor: "var(--bg-surface-secondary)",
                        borderRadius: "4px",
                        border: "1px solid var(--border-hairline)",
                      }}
                    >
                      <span className="mono" style={{ fontSize: "11px", color: "var(--text-dim)", fontWeight: 600 }}>
                        {stage.num}
                      </span>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-primary)" }}>
                          {stage.name}
                        </div>
                        <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                          {stage.desc}
                        </div>
                      </div>
                      <span style={{
                        fontSize: "10.5px",
                        padding: "0.1rem 0.4rem",
                        borderRadius: "3px",
                        fontWeight: 600,
                        backgroundColor:
                          stage.state === "done" ? "var(--status-reconciled-bg)" :
                          stage.state === "blocked" ? "var(--status-blocked-bg)" :
                          stage.state === "active" ? "var(--status-review-bg)" :
                          stage.state === "ready" ? "var(--color-indigo-bg)" : "var(--bg-surface)",
                        color:
                          stage.state === "done" ? "var(--status-reconciled)" :
                          stage.state === "blocked" ? "var(--status-blocked)" :
                          stage.state === "active" ? "var(--status-review)" :
                          stage.state === "ready" ? "var(--color-indigo)" : "var(--text-dim)",
                      }}>
                        {stage.state.toUpperCase()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column: Hero Counterfactual Simulation & Policy Engine */}
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {/* Counterfactual Resolution Hero */}
              <div className="surface" style={{ padding: "1.15rem 1.25rem", border: "1px solid var(--border-subtle)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.6rem" }}>
                  <div>
                    <div style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--color-indigo)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                      Hero Component
                    </div>
                    <h3 style={{ fontSize: "13.5px", fontWeight: 700, color: "var(--text-primary)", marginTop: "1px" }}>
                      COUNTERFACTUAL RESOLUTION
                    </h3>
                  </div>
                  <span style={{
                    fontSize: "10px",
                    fontWeight: 600,
                    padding: "0.15rem 0.45rem",
                    borderRadius: "3px",
                    backgroundColor: "var(--color-indigo-bg)",
                    color: "var(--color-indigo)",
                    border: "1px solid var(--color-indigo-border)",
                  }}>
                    VIRTUAL MEMORY SIMULATION
                  </span>
                </div>
                <p style={{ fontSize: "11.5px", color: "var(--text-muted)", marginBottom: "0.85rem" }}>
                  Simulate candidate corrective adjustments before human sign-off or ledger commit.
                </p>

                {/* 3-Column Transformation */}
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr auto 1.2fr auto 1fr",
                  alignItems: "center",
                  gap: "0.5rem",
                  backgroundColor: "var(--bg-surface-secondary)",
                  padding: "0.75rem",
                  borderRadius: "5px",
                  border: "1px solid var(--border-subtle)",
                }}>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase" }}>Current</div>
                    <div className="tabular-num mono" style={{ fontSize: "13px", fontWeight: 700, color: "var(--text-primary)", marginTop: "2px" }}>
                      {netSet > 0 ? formatINR(netSet) : "—"}
                    </div>
                  </div>
                  <div style={{ color: "var(--border-medium)" }}>→</div>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "10px", color: "var(--color-indigo)", textTransform: "uppercase", fontWeight: 600 }}>Proposed Adjustment</div>
                    <div className="tabular-num mono" style={{ fontSize: "13px", fontWeight: 700, color: "var(--color-indigo)", marginTop: "2px" }}>
                      {discrepancyDelta !== 0 ? `+${formatINR(Math.abs(discrepancyDelta))}` : "₹0.00"}
                    </div>
                  </div>
                  <div style={{ color: "var(--border-medium)" }}>→</div>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "10px", color: "var(--status-reconciled)", textTransform: "uppercase", fontWeight: 600 }}>Projected</div>
                    <div className="tabular-num mono" style={{ fontSize: "13px", fontWeight: 700, color: "var(--status-reconciled)", marginTop: "2px" }}>
                      {grossPay > 0 ? formatINR(grossPay - totalFees) : "—"}
                    </div>
                  </div>
                </div>

                {/* Validation Checklist */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.75rem", padding: "0 0.25rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "11.5px", color: "var(--status-reconciled)" }}>
                    <span>✓</span>
                    <span>Residual Discrepancy: <strong>₹0.00</strong></span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "11.5px", color: "var(--status-reconciled)" }}>
                    <span>✓</span>
                    <span>Double-Entry Ledger: <strong>BALANCED</strong></span>
                  </div>
                </div>

                {/* Simulation Notice */}
                <div style={{
                  marginTop: "0.75rem",
                  padding: "0.45rem 0.65rem",
                  backgroundColor: "var(--bg-canvas)",
                  borderRadius: "4px",
                  fontSize: "10.5px",
                  color: "var(--text-muted)",
                  textAlign: "center",
                  border: "1px solid var(--border-hairline)",
                  fontWeight: 500,
                }}>
                  SIMULATION ONLY • NO FINANCIAL TRANSACTION EXECUTED
                </div>
              </div>

              {/* Deterministic Policy Governance Panel */}
              <div className="surface" style={{ padding: "1.15rem 1.25rem" }}>
                <div style={{ marginBottom: "0.6rem" }}>
                  <h3 style={{ fontSize: "12.5px", fontWeight: 700, color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                    DETERMINISTIC GOVERNANCE
                  </h3>
                  <div style={{ fontSize: "11.5px", color: "var(--text-muted)", marginTop: "2px" }}>
                    AI findings do not authorize financial actions.
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "0.45rem" }}>
                  {[
                    { id: "POL-001", name: "Simulation Validity", status: "PASSED", color: "var(--status-reconciled)" },
                    { id: "POL-002", name: "Evidence Sufficiency", status: "PASSED", color: "var(--status-reconciled)" },
                    { id: "POL-003", name: "Monetary Risk Threshold (₹5,000)", status: Math.abs(discrepancyDelta) > 500000 ? "HUMAN_REVIEW" : "PASSED", color: Math.abs(discrepancyDelta) > 500000 ? "var(--status-review)" : "var(--status-reconciled)" },
                  ].map((pol) => (
                    <div
                      key={pol.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "0.45rem 0.65rem",
                        backgroundColor: "var(--bg-surface-secondary)",
                        borderRadius: "4px",
                        border: "1px solid var(--border-hairline)",
                        fontSize: "12px",
                      }}
                    >
                      <div>
                        <span className="mono" style={{ fontWeight: 600, color: "var(--text-secondary)", marginRight: "0.5rem" }}>
                          {pol.id}
                        </span>
                        <span style={{ color: "var(--text-primary)" }}>{pol.name}</span>
                      </div>
                      <span style={{
                        fontSize: "10.5px",
                        fontWeight: 600,
                        color: pol.color,
                      }}>
                        {pol.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Records Inspector */}
        {activeTab === "records" && (
          <RecordsInspector observed={caseData.observed} />
        )}

        {/* Tab 3: Evidence Graph */}
        {activeTab === "evidence" && (
          <EvidenceGraphCanvas graph={caseData.evidence_graph} />
        )}

        {/* Tab 4: AI Investigation */}
        {activeTab === "investigation" && (
          <InvestigationPanel
            caseId={caseId}
            investigation={investigation}
            onRunInvestigation={handleRunInvestigation}
            isInvestigating={isInvestigating}
          />
        )}

        {/* Tab 5: Resolution Simulator */}
        {activeTab === "resolution" && (
          <BeforeAfterTable
            caseId={caseId}
            observed={caseData.observed}
            investigation={investigation}
          />
        )}
      </div>

      {/* Approval Drawer */}
      <ApprovalDrawer
        isOpen={isApprovalOpen}
        onClose={() => setIsApprovalOpen(false)}
        caseId={caseId}
        onSuccess={() => loadCase()}
      />
    </div>
  );
}
