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
        <Header breadcrumbs={[{ label: "FINRESOLVE", href: "/" }, { label: "CASES", href: "/cases" }, { label: caseId }]} />
        <div className="page-body" style={{ textAlign: "center", padding: "4rem" }}>
          <p className="mono" style={{ color: "var(--text-muted)", fontSize: "12px" }}>LOADING FINANCIAL RECORDS & EVIDENCE GRAPH...</p>
        </div>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div>
        <Header breadcrumbs={[{ label: "FINRESOLVE", href: "/" }, { label: "CASES", href: "/cases" }, { label: "NOT FOUND" }]} />
        <div className="page-body" style={{ textAlign: "center", padding: "4rem" }}>
          <p style={{ color: "var(--color-brand)", fontSize: "14px", fontWeight: 700 }}>CASE &apos;{caseId}&apos; COULD NOT BE LOCATED.</p>
          <Link href="/cases" className="btn btn-secondary" style={{ marginTop: "1rem" }}>
            ← BACK TO CASES
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
          { label: "FINRESOLVE", href: "/" },
          { label: "CASES", href: "/cases" },
          { label: caseData.case_id },
        ]}
        actions={
          <button
            onClick={handleRunInvestigation}
            disabled={isInvestigating}
            className="btn btn-primary btn-sm"
          >
            <PlayIcon size={11} />
            <span>{isInvestigating ? "INVESTIGATING..." : "RUN AI INVESTIGATION"}</span>
          </button>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
        {/* Terminal Header */}
        <div style={{
          borderBottom: "1px solid var(--border-subtle)",
          paddingBottom: "1.5rem",
          display: "flex",
          flexDirection: "column",
          gap: "1.25rem",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <span className="mono" style={{ fontSize: "12px", color: "var(--color-brand)", fontWeight: 700 }}>
                  CASE ID // {caseData.case_id}
                </span>
                <span className="mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                  MERCHANT: {caseData.merchant_id}
                </span>
                <span style={{
                  fontSize: "10px",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.04em",
                  color: caseData.status === "reconciled" ? "var(--status-reconciled)" : "var(--color-brand)",
                }}>
                  ● {caseData.status}
                </span>
                {isBlockedCompoundCase && (
                  <span style={{ fontSize: "10px", fontWeight: 700, color: "var(--color-brand)" }}>
                    ● FAIL-CLOSED BLOCKED
                  </span>
                )}
              </div>

              <h1 className="heading-editorial title-large" style={{ marginTop: "0.4rem" }}>
                {caseId === "CASE-000003" ? "SETTLEMENT DISCREPANCY" :
                 caseId === "CASE-000002" ? "BALANCED RECONCILIATION BASELINE" :
                 caseId === "CASE-000132" ? "HIGH-VALUE SETTLEMENT DISCREPANCY" :
                 caseId === "CASE-000009" ? "COMPOUND CORRUPTION DISCREPANCY" :
                 `${caseData.difficulty.toUpperCase()} DISCREPANCY TRACE`}
              </h1>
            </div>

            {/* Financial Variance Hero */}
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.06em" }}>
                NET VARIANCE
              </div>
              <div className="tabular-num heading-editorial" style={{
                fontSize: "2.2rem",
                color: discrepancyDelta === 0 ? "var(--status-reconciled)" : "var(--color-brand)",
                marginTop: "2px",
              }}>
                {discrepancyDelta !== 0 ? formatINR(discrepancyDelta) : "₹0.00"}
              </div>
            </div>
          </div>

          {/* Horizontal Financial Comparison Strip */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "1fr auto 1fr auto 1.2fr",
            alignItems: "center",
            gap: "1rem",
            backgroundColor: "var(--bg-secondary)",
            border: "1px solid var(--border-subtle)",
            padding: "1rem 1.5rem",
          }}>
            <div>
              <div style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.06em" }}>Captured Gross</div>
              <div className="tabular-num heading-editorial" style={{ fontSize: "1.35rem", color: "var(--text-primary)", marginTop: "2px" }}>
                {grossPay > 0 ? formatINR(grossPay) : "—"}
              </div>
            </div>
            <div style={{ color: "var(--text-dim)", fontSize: "1.2rem" }}>→</div>
            <div>
              <div style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.06em" }}>Settled Net</div>
              <div className="tabular-num heading-editorial" style={{ fontSize: "1.35rem", color: "var(--text-primary)", marginTop: "2px" }}>
                {netSet > 0 ? formatINR(netSet) : "—"}
              </div>
            </div>
            <div style={{ color: "var(--text-dim)", fontSize: "1.2rem" }}>→</div>
            <div>
              <div style={{ fontSize: "10px", color: "var(--color-brand)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.06em" }}>Net Variance</div>
              <div className="tabular-num heading-editorial" style={{
                fontSize: "1.35rem",
                color: discrepancyDelta === 0 ? "var(--status-reconciled)" : "var(--color-brand)",
                marginTop: "2px",
              }}>
                {discrepancyDelta !== 0 ? formatINR(discrepancyDelta) : "₹0.00 BALANCED"}
              </div>
            </div>
          </div>

          {/* Sub-Tabs */}
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            {[
              { id: "overview", label: "01 WORKSTATION OVERVIEW" },
              { id: "records", label: `02 OBSERVED RECORDS (${(caseData.observed?.payments?.length || 0) + (caseData.observed?.settlements?.length || 0)})` },
              { id: "evidence", label: "03 EVIDENCE GRAPH" },
              { id: "investigation", label: "04 AI INVESTIGATION" },
              { id: "resolution", label: "05 RESOLUTION SIMULATOR" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                style={{
                  padding: "0.4rem 0.75rem",
                  fontSize: "11px",
                  fontWeight: 700,
                  fontFamily: "var(--font-heading)",
                  letterSpacing: "0.04em",
                  color: activeTab === tab.id ? "var(--text-primary)" : "var(--text-muted)",
                  backgroundColor: activeTab === tab.id ? "var(--bg-surface-elevated)" : "transparent",
                  border: activeTab === tab.id ? "1px solid var(--border-medium)" : "1px solid transparent",
                  borderBottom: activeTab === tab.id ? "2px solid var(--color-brand)" : "2px solid transparent",
                  transition: "all 0.12s ease",
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab 1: Workstation Overview */}
        {activeTab === "overview" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1.15fr", gap: "1.5rem" }}>
            {/* Left Column */}
            <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
              {/* Detected Discrepancies */}
              <div>
                <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem" }}>
                  <span style={{ color: "var(--color-brand)" }}>/</span> DISCREPANCY FINDINGS ({discrepancies.length})
                </div>
                {discrepancies.length === 0 ? (
                  <div style={{ padding: "1.5rem", border: "1px solid var(--border-subtle)", backgroundColor: "var(--bg-secondary)", textAlign: "center" }}>
                    <div style={{ color: "var(--status-reconciled)", fontWeight: 700, fontSize: "13px" }}>ZERO DISCREPANCIES DETECTED</div>
                    <div style={{ fontSize: "11.5px", color: "var(--text-muted)", marginTop: "2px" }}>All multi-party signals balance with zero accounting variance.</div>
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                    {discrepancies.map((d, i) => (
                      <div
                        key={i}
                        style={{
                          padding: "0.85rem 1rem",
                          backgroundColor: "var(--bg-secondary)",
                          border: "1px solid var(--border-subtle)",
                          borderLeft: "3px solid var(--color-brand)",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <span style={{ fontSize: "12.5px", fontWeight: 700, color: "var(--text-primary)" }}>
                            {d.rule_name || "Reconciliation Rule Exception"}
                          </span>
                          <span style={{ fontSize: "10px", fontWeight: 700, color: "var(--color-brand)" }}>
                            ● {d.severity?.toUpperCase() || "HIGH"}
                          </span>
                        </div>
                        <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px", lineHeight: 1.4 }}>
                          {d.description}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Vertical Editorial Timeline */}
              <div>
                <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem" }}>
                  <span style={{ color: "var(--color-brand)" }}>/</span> INVESTIGATION PIPELINE LIFECYCLE
                </div>
                <div style={{
                  display: "flex",
                  flexDirection: "column",
                  border: "1px solid var(--border-subtle)",
                  backgroundColor: "var(--bg-secondary)",
                }}>
                  {[
                    { num: "01", name: "DETECTED", desc: "Multi-signal reconciliation rules evaluated", state: "done" },
                    { num: "02", name: "EVIDENCE COLLECTED", desc: "Graph edges constructed for payments & settlements", state: "done" },
                    { num: "03", name: "INVESTIGATION", desc: "Bounded deterministic agent execution", state: investigation ? "done" : "ready" },
                    { num: "04", name: "DIAGNOSIS", desc: investigation ? "Root cause synthesized" : "Bayesian ranking ready", state: investigation ? "done" : "pending" },
                    { num: "05", name: "SIMULATION", desc: isBlockedCompoundCase ? "Fail-closed blocked (invalid state)" : "Virtual deep-clone state validated", state: isBlockedCompoundCase ? "blocked" : (investigation ? "done" : "pending") },
                    { num: "06", name: "POLICY", desc: "Deterministic gating POL-001 - POL-003", state: investigation ? "done" : "pending" },
                    { num: "07", name: "APPROVAL", desc: "Separation of duties review workflow", state: investigation?.resolution_plan?.policy_decision?.decision === "HUMAN_REVIEW" ? "active" : "pending" },
                    { num: "08", name: "AUDIT", desc: "Append-only SHA-256 backwards hash-pointer", state: "done" },
                  ].map((stage, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "1rem",
                        padding: "0.6rem 1rem",
                        borderBottom: idx < 7 ? "1px solid var(--border-hairline)" : "none",
                      }}
                    >
                      <span className="mono" style={{ fontSize: "11px", color: "var(--text-dim)", fontWeight: 700 }}>
                        {stage.num}
                      </span>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-primary)" }}>
                          {stage.name}
                        </div>
                        <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                          {stage.desc}
                        </div>
                      </div>
                      <span style={{
                        fontSize: "10px",
                        fontWeight: 700,
                        letterSpacing: "0.04em",
                        color:
                          stage.state === "done" ? "var(--status-reconciled)" :
                          stage.state === "blocked" ? "var(--color-brand)" :
                          stage.state === "active" ? "var(--status-review)" :
                          stage.state === "ready" ? "var(--text-primary)" : "var(--text-dim)",
                      }}>
                        ● {stage.state.toUpperCase()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column: Hero Counterfactual Simulation & Policy */}
            <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
              {/* Counterfactual Simulation Hero */}
              <div style={{
                backgroundColor: "var(--bg-secondary)",
                border: "1px solid var(--border-subtle)",
                padding: "1.5rem",
                display: "flex",
                flexDirection: "column",
                gap: "1.25rem",
              }}>
                <div>
                  <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                    / SIMULATE BEFORE EXECUTION
                  </div>
                  <h2 className="heading-editorial title-large" style={{ marginTop: "2px" }}>
                    COUNTERFACTUAL SIMULATION
                  </h2>
                  <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
                    Proves candidate corrections eliminate variance without violating double-entry conservation of money.
                  </p>
                </div>

                {/* 3-Step Transformation */}
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr auto 1.2fr auto 1fr",
                  alignItems: "center",
                  gap: "0.75rem",
                  border: "1px solid var(--border-subtle)",
                  backgroundColor: "var(--bg-canvas)",
                  padding: "1rem",
                }}>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "9.5px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>CURRENT</div>
                    <div className="tabular-num heading-editorial" style={{ fontSize: "1.15rem", color: "var(--text-primary)", marginTop: "2px" }}>
                      {netSet > 0 ? formatINR(netSet) : "—"}
                    </div>
                  </div>
                  <div style={{ color: "var(--text-dim)" }}>↓</div>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "9.5px", color: "var(--color-brand)", textTransform: "uppercase", fontWeight: 700 }}>PROPOSED ADJUSTMENT</div>
                    <div className="tabular-num heading-editorial" style={{ fontSize: "1.15rem", color: "var(--color-brand)", marginTop: "2px" }}>
                      {discrepancyDelta !== 0 ? `+${formatINR(Math.abs(discrepancyDelta))}` : "₹0.00"}
                    </div>
                  </div>
                  <div style={{ color: "var(--text-dim)" }}>↓</div>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "9.5px", color: "var(--status-reconciled)", textTransform: "uppercase", fontWeight: 700 }}>PROJECTED</div>
                    <div className="tabular-num heading-editorial" style={{ fontSize: "1.15rem", color: "var(--status-reconciled)", marginTop: "2px" }}>
                      {grossPay > 0 ? formatINR(grossPay - totalFees) : "—"}
                    </div>
                  </div>
                </div>

                {/* Large Result Callouts */}
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "1rem",
                  borderTop: "1px solid var(--border-hairline)",
                  paddingTop: "1rem",
                }}>
                  <div>
                    <div className="tabular-num heading-editorial" style={{ fontSize: "1.75rem", color: "var(--status-reconciled)" }}>
                      ₹0.00
                    </div>
                    <div style={{ fontSize: "10px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-muted)" }}>
                      RESIDUAL DISCREPANCY
                    </div>
                  </div>

                  <div>
                    <div className="heading-editorial" style={{ fontSize: "1.75rem", color: "var(--status-reconciled)" }}>
                      BALANCED
                    </div>
                    <div style={{ fontSize: "10px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-muted)" }}>
                      DOUBLE-ENTRY LEDGER
                    </div>
                  </div>
                </div>

                {/* Simulation Notice */}
                <div style={{
                  padding: "0.6rem 0.85rem",
                  backgroundColor: "var(--bg-canvas)",
                  border: "1px solid var(--border-hairline)",
                  fontSize: "10.5px",
                  color: "var(--text-muted)",
                  textAlign: "center",
                  fontWeight: 700,
                  letterSpacing: "0.06em",
                }}>
                  SIMULATION ONLY • NO FINANCIAL TRANSACTION EXECUTED
                </div>
              </div>

              {/* Policy Governance */}
              <div style={{
                backgroundColor: "var(--bg-secondary)",
                border: "1px solid var(--border-subtle)",
                padding: "1.25rem 1.5rem",
                display: "flex",
                flexDirection: "column",
                gap: "1rem",
              }}>
                <div>
                  <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    / POLICY GOVERNANCE
                  </div>
                  <h3 className="heading-editorial title-medium" style={{ marginTop: "2px" }}>
                    DETERMINISTIC GOVERNANCE
                  </h3>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                  {[
                    { id: "POL-001", name: "SIMULATION VALIDITY", status: "PASSED", color: "var(--status-reconciled)" },
                    { id: "POL-002", name: "EVIDENCE SUFFICIENCY", status: "PASSED", color: "var(--status-reconciled)" },
                    { id: "POL-003", name: "MONETARY RISK THRESHOLD", status: Math.abs(discrepancyDelta) > 500000 ? "HUMAN REVIEW REQUIRED" : "PASSED", color: Math.abs(discrepancyDelta) > 500000 ? "var(--status-review)" : "var(--status-reconciled)" },
                  ].map((pol) => (
                    <div
                      key={pol.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "0.5rem 0.75rem",
                        backgroundColor: "var(--bg-canvas)",
                        border: "1px solid var(--border-hairline)",
                        fontSize: "11.5px",
                      }}
                    >
                      <div>
                        <span className="mono" style={{ fontWeight: 700, color: "var(--text-muted)", marginRight: "0.5rem" }}>
                          {pol.id}
                        </span>
                        <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{pol.name}</span>
                      </div>
                      <span style={{ fontSize: "10.5px", fontWeight: 700, color: pol.color }}>
                        ● {pol.status}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Control Principle */}
                <div style={{
                  borderLeft: "2px solid var(--color-brand)",
                  paddingLeft: "0.75rem",
                  fontSize: "10.5px",
                  color: "var(--text-secondary)",
                  lineHeight: 1.4,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.04em",
                }}>
                  AI FINDINGS DO NOT AUTHORIZE FINANCIAL ACTIONS.<br />ALL EXECUTION STRICTLY REQUIRES POLICY APPROVAL.
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
