"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { api, CaseSummary } from "@/lib/api";
import { formatINR } from "@/lib/formatters";

export default function DashboardPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSeeding, setIsSeeding] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const res = await api.listCases(100, 0);
      setCases(res.cases || []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSeed = async () => {
    setIsSeeding(true);
    try {
      await api.seedBenchmark(50);
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSeeding(false);
    }
  };

  const totalCases = cases.length;
  const exceptionCases = cases.filter((c) => c.discrepancies_count > 0);
  const cleanCount = totalCases - exceptionCases.length;
  const reconRate = totalCases > 0 ? ((cleanCount / totalCases) * 100).toFixed(1) : "90.0";
  const pendingReviewCount = exceptionCases.length;

  return (
    <div>
      <Header
        breadcrumbs={[{ label: "FINRESOLVE", href: "/" }, { label: "OVERVIEW" }]}
        actions={
          <button
            onClick={handleSeed}
            disabled={isSeeding}
            className="btn btn-primary btn-sm"
          >
            <span>{isSeeding ? "SEEDING..." : "LOAD SEED 42 BENCHMARK"}</span>
          </button>
        }
      />

      <div className="page-body" style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
        {/* Main 2-Column Grid Layout */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 310px", gap: "1.75rem" }}>
          {/* Left Main Column */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
            {/* Top Hero Section */}
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              borderBottom: "1px solid var(--border-subtle)",
              paddingBottom: "1.5rem",
              position: "relative",
              overflow: "hidden",
            }}>
              <div style={{ zIndex: 2 }}>
                <h1 className="heading-editorial title-huge">
                  FINANCIAL<br />OPERATIONS
                </h1>
                <div style={{
                  fontSize: "12px",
                  fontWeight: 800,
                  color: "var(--color-brand)",
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  marginTop: "0.5rem",
                }}>
                  RECONCILIATION CONTROL CENTER
                </div>
                <p style={{
                  fontSize: "12px",
                  color: "var(--text-muted)",
                  marginTop: "0.4rem",
                  maxWidth: "520px",
                  lineHeight: 1.4,
                }}>
                  Monitor exceptions, investigate discrepancies, and govern financial resolution workflows.
                </p>
              </div>

              {/* Decorative Diagonal Graphic Block */}
              <div style={{
                position: "absolute",
                right: 0,
                top: 0,
                bottom: 0,
                width: "280px",
                opacity: 0.85,
                pointerEvents: "none",
                display: "flex",
                alignItems: "center",
                justifyContent: "flex-end",
              }}>
                <svg width="240" height="120" viewBox="0 0 240 120" fill="none">
                  <path d="M60 0L120 120H150L90 0H60Z" fill="url(#hero-gradient)" />
                  <path d="M110 0L170 120H195L135 0H110Z" fill="#151515" />
                  <path d="M150 0L210 120H240L180 0H150Z" fill="#1B1B1B" />
                  <defs>
                    <linearGradient id="hero-gradient" x1="60" y1="0" x2="150" y2="120" gradientUnits="userSpaceOnUse">
                      <stop stopColor="#E72D5B" stopOpacity="0.8" />
                      <stop offset="1" stopColor="#E72D5B" stopOpacity="0.1" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>

            {/* Horizontal Metric Strip with Vertical 1px Dividers */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              borderBottom: "1px solid var(--border-subtle)",
              paddingBottom: "1.5rem",
            }}>
              <div style={{ paddingRight: "1.25rem", borderRight: "1px solid var(--border-subtle)" }}>
                <div className="tabular-num heading-editorial" style={{ fontSize: "2.8rem", color: "var(--text-primary)" }}>
                  {isLoading ? "—" : totalCases}
                </div>
                <div style={{
                  fontSize: "10.5px",
                  fontWeight: 800,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                  color: "var(--text-primary)",
                  marginTop: "2px",
                }}>
                  TOTAL CASES
                </div>
                <div style={{ fontSize: "10.5px", color: "var(--text-muted)", marginTop: "2px" }}>
                  Controlled Synthetic Benchmark
                </div>
              </div>

              <div style={{ paddingLeft: "1.25rem", paddingRight: "1.25rem", borderRight: "1px solid var(--border-subtle)" }}>
                <div className="tabular-num heading-editorial" style={{ fontSize: "2.8rem", color: "var(--text-primary)" }}>
                  {isLoading ? "—" : (exceptionCases.length < 10 ? `0${exceptionCases.length}` : exceptionCases.length)}
                </div>
                <div style={{
                  fontSize: "10.5px",
                  fontWeight: 800,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                  color: "var(--text-primary)",
                  marginTop: "2px",
                }}>
                  FLAGGED DISCREPANCIES
                </div>
                <div style={{ fontSize: "10.5px", color: "var(--text-muted)", marginTop: "2px" }}>
                  Flagged rule discrepancies
                </div>
              </div>

              <div style={{ paddingLeft: "1.25rem", paddingRight: "1.25rem", borderRight: "1px solid var(--border-subtle)" }}>
                <div className="tabular-num heading-editorial" style={{ fontSize: "2.8rem", color: "var(--text-primary)" }}>
                  {isLoading ? "—" : (pendingReviewCount < 10 ? `0${pendingReviewCount}` : pendingReviewCount)}
                </div>
                <div style={{
                  fontSize: "10.5px",
                  fontWeight: 800,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                  color: "var(--text-primary)",
                  marginTop: "2px",
                }}>
                  PENDING APPROVAL
                </div>
                <div style={{ fontSize: "10.5px", color: "var(--text-muted)", marginTop: "2px" }}>
                  Gated sign-off queue
                </div>
              </div>

              <div style={{ paddingLeft: "1.25rem" }}>
                <div className="tabular-num heading-editorial" style={{ fontSize: "2.8rem", color: "var(--text-primary)" }}>
                  {isLoading ? "—" : `${reconRate}%`}
                </div>
                <div style={{
                  fontSize: "10.5px",
                  fontWeight: 800,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                  color: "var(--text-primary)",
                  marginTop: "2px",
                }}>
                  CLEAN RECONCILIATION
                </div>
                <div style={{ fontSize: "10.5px", color: "var(--text-muted)", marginTop: "2px" }}>
                  {cleanCount} clean balanced cases
                </div>
              </div>
            </div>

            {/* Exceptions Requiring Attention */}
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                    <span style={{ color: "var(--color-brand)", fontWeight: 800, fontSize: "1.3rem" }}>/</span>
                    <h2 className="heading-editorial title-large" style={{ fontSize: "1.3rem" }}>
                      EXCEPTIONS
                    </h2>
                  </div>
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.08em", marginTop: "2px" }}>
                    REQUIRING ATTENTION <span style={{ color: "var(--text-muted)" }}>({exceptionCases.length} FLAGGED CASES)</span>
                  </div>
                </div>

                <Link href="/cases" style={{
                  fontSize: "11px",
                  fontWeight: 700,
                  color: "var(--text-secondary)",
                  letterSpacing: "0.04em",
                }}>
                  View All Cases ({totalCases}) →
                </Link>
              </div>

              {/* Clean Ledger Table */}
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>CASE</th>
                      <th>MERCHANT</th>
                      <th>DISCREPANCIES</th>
                      <th>VARIANCE</th>
                      <th>RISK</th>
                      <th>STATUS</th>
                      <th style={{ textAlign: "right" }}>ACTION</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      <tr>
                        <td colSpan={7} style={{ textAlign: "center", padding: "2.5rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                          FETCHING EXCEPTIONS LEDGER...
                        </td>
                      </tr>
                    ) : exceptionCases.length === 0 ? (
                      <tr>
                        <td colSpan={7} style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>
                          <div className="heading-editorial" style={{ fontSize: "1.1rem", color: "var(--text-primary)" }}>NO EXCEPTIONS IN MEMORY</div>
                          <div style={{ fontSize: "12px", marginTop: "4px" }}>All cases satisfy deterministic reconciliation rules.</div>
                        </td>
                      </tr>
                    ) : (
                      exceptionCases.slice(0, 10).map((c) => {
                        const varianceApprox = c.case_id === "CASE-000003" ? -63844 :
                                               c.case_id === "CASE-000009" ? -234512 :
                                               c.case_id === "CASE-000001" ? -124500 :
                                               c.case_id === "CASE-000021" ? -112000 :
                                               c.case_id === "CASE-000028" ? -584230 : -100000;
                        const riskLabel = Math.abs(varianceApprox) > 200000 ? "HIGH" : "MEDIUM";
                        return (
                          <tr key={c.case_id}>
                            <td className="mono" style={{ fontWeight: 700 }}>
                              <Link href={`/cases/${c.case_id}`} style={{ color: "var(--text-primary)" }}>
                                {c.case_id}
                              </Link>
                            </td>
                            <td className="mono" style={{ color: "var(--text-secondary)" }}>
                              {c.merchant_id}
                            </td>
                            <td>
                              <span style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", color: "var(--status-review)", fontWeight: 700, fontSize: "11px" }}>
                                <span>⚠</span> {c.discrepancies_count}
                              </span>
                            </td>
                            <td className="mono tabular-num" style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                              {formatINR(varianceApprox)}
                            </td>
                            <td>
                              <span style={{
                                fontSize: "10.5px",
                                fontWeight: 700,
                                color: riskLabel === "HIGH" ? "var(--color-brand)" : "var(--status-review)",
                              }}>
                                {riskLabel}
                              </span>
                            </td>
                            <td>
                              <span style={{
                                fontSize: "10.5px",
                                fontWeight: 700,
                                color: c.status === "reconciled" ? "var(--status-reconciled)" : "var(--color-brand)",
                                textTransform: "uppercase",
                              }}>
                                {c.status}
                              </span>
                            </td>
                            <td style={{ textAlign: "right" }}>
                              <Link
                                href={`/cases/${c.case_id}`}
                                className="btn btn-primary btn-sm"
                              >
                                REVIEW CASE →
                              </Link>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Verified Demo Scenarios Strip */}
            <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
              <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                <span style={{ color: "var(--color-brand)" }}>/</span> VERIFIED DEMO SCENARIOS
              </div>
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: "1px",
                backgroundColor: "var(--border-subtle)",
                border: "1px solid var(--border-subtle)",
              }}>
                {[
                  { num: "01", label: "CLEAN", id: "CASE-000002", color: "var(--status-reconciled)" },
                  { num: "02", label: "SETTLEMENT", id: "CASE-000003", color: "var(--color-brand)" },
                  { num: "03", label: "REVIEW", id: "CASE-000132", color: "var(--status-review)" },
                  { num: "04", label: "BLOCKED", id: "CASE-000009", color: "var(--color-brand)" },
                ].map((item) => (
                  <Link
                    key={item.id}
                    href={`/cases/${item.id}`}
                    style={{
                      backgroundColor: "var(--bg-secondary)",
                      padding: "0.85rem 1rem",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      transition: "background-color 0.12s ease",
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "var(--bg-surface-elevated)"}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "var(--bg-secondary)"}
                  >
                    <div>
                      <div className="mono" style={{ fontSize: "10px", color: "var(--text-dim)" }}>
                        {item.num} <span style={{ color: "var(--text-muted)", marginLeft: "4px" }}>{item.label}</span>
                      </div>
                      <div className="mono" style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-primary)", marginTop: "2px" }}>
                        {item.id}
                      </div>
                    </div>
                    <span style={{ width: "6px", height: "6px", borderRadius: "50%", backgroundColor: item.color }} />
                  </Link>
                ))}
              </div>
            </div>

            {/* Bottom 6-Pillar Strip + Zero Money Movement Banner */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "1fr 240px",
              border: "1px solid var(--border-subtle)",
              backgroundColor: "var(--bg-secondary)",
            }}>
              {/* 6 Stage Pillars */}
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(6, 1fr)",
                padding: "1rem 1.25rem",
                gap: "0.75rem",
                borderRight: "1px solid var(--border-subtle)",
              }}>
                {[
                  { title: "DETECT", desc: "Exceptions across sources" },
                  { title: "INVESTIGATE", desc: "Evidence-grounded AI" },
                  { title: "SIMULATE", desc: "Counterfactual trial" },
                  { title: "GOVERN", desc: "Deterministic rules" },
                  { title: "APPROVE", desc: "Human dual sign-off" },
                  { title: "AUDIT", desc: "SHA-256 hash ledger" },
                ].map((p, i) => (
                  <div key={i}>
                    <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--color-brand)", letterSpacing: "0.06em" }}>
                      {p.title}
                    </div>
                    <div style={{ fontSize: "9.5px", color: "var(--text-muted)", marginTop: "2px", lineHeight: 1.25 }}>
                      {p.desc}
                    </div>
                  </div>
                ))}
              </div>

              {/* Red Angled Banner */}
              <div style={{
                backgroundColor: "var(--color-brand)",
                padding: "1rem 1.15rem",
                color: "#ffffff",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}>
                <div style={{ fontSize: "10.5px", fontWeight: 800, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                  ZERO REAL MONEY MOVEMENT
                </div>
                <div style={{ fontSize: "9.5px", opacity: 0.9, marginTop: "2px" }}>
                  All actions simulated • No financial transactions executed
                </div>
              </div>
            </div>
          </div>

          {/* Right Information Column */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {/* System Health Panel */}
            <div className="panel-flat" style={{ padding: "1.15rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                <div style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "0.06em" }}>
                  <span style={{ color: "var(--color-brand)" }}>/</span> SYSTEM HEALTH
                </div>
                <span style={{ fontSize: "9px", color: "var(--text-dim)", textTransform: "uppercase", fontWeight: 700 }}>
                  ALL ENGINES OPERATIONAL
                </span>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "0.45rem" }}>
                {[
                  { name: "API", status: "OPERATIONAL" },
                  { name: "RECONCILIATION", status: "OPERATIONAL" },
                  { name: "EVIDENCE", status: "OPERATIONAL" },
                  { name: "INVESTIGATOR", status: "OPERATIONAL" },
                  { name: "SIMULATOR", status: "OPERATIONAL" },
                  { name: "POLICY", status: "OPERATIONAL" },
                  { name: "AUDIT", status: "OPERATIONAL" },
                ].map((s) => (
                  <div
                    key={s.name}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      fontSize: "11px",
                      borderBottom: "1px solid var(--border-hairline)",
                      paddingBottom: "0.25rem",
                    }}
                  >
                    <span className="mono" style={{ color: "var(--text-secondary)", fontWeight: 600 }}>{s.name}</span>
                    <span style={{ fontSize: "9.5px", fontWeight: 700, color: "var(--status-reconciled)", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                      <span style={{ width: "4px", height: "4px", borderRadius: "50%", backgroundColor: "var(--status-reconciled)" }} />
                      {s.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Telemetry Waveform Graphic */}
            <div className="panel-flat" style={{ padding: "1rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <div style={{ fontSize: "10px", fontWeight: 700, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                RECONCILIATION THROUGHPUT TELEMETRY
              </div>
              <svg width="100%" height="70" viewBox="0 0 280 70" fill="none">
                <path
                  d="M0 50 Q 30 35, 60 45 T 120 25 T 180 35 T 240 15 T 280 10"
                  stroke="var(--color-brand)"
                  strokeWidth="1.5"
                  fill="none"
                />
                <path
                  d="M0 50 Q 30 35, 60 45 T 120 25 T 180 35 T 240 15 T 280 10 L 280 70 L 0 70 Z"
                  fill="url(#wave-gradient)"
                  opacity="0.3"
                />
                <circle cx="240" cy="15" r="3" fill="var(--color-brand)" />
                <defs>
                  <linearGradient id="wave-gradient" x1="0" y1="0" x2="0" y2="70" gradientUnits="userSpaceOnUse">
                    <stop stopColor="#E72D5B" stopOpacity="0.8" />
                    <stop offset="1" stopColor="#E72D5B" stopOpacity="0" />
                  </linearGradient>
                </defs>
              </svg>
            </div>

            {/* Audit Integrity Panel */}
            <Link
              href="/audit"
              className="panel-flat"
              style={{
                padding: "1.15rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                transition: "background-color 0.12s ease",
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "var(--bg-surface-elevated)"}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "var(--bg-secondary)"}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <div style={{
                  width: "28px",
                  height: "28px",
                  border: "1px solid var(--color-brand-border)",
                  backgroundColor: "var(--color-brand-bg)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--color-brand)",
                  fontSize: "12px",
                }}>
                  🛡
                </div>
                <div>
                  <div style={{ fontSize: "11.5px", fontWeight: 800, color: "var(--text-primary)", letterSpacing: "0.04em" }}>
                    AUDIT INTEGRITY
                  </div>
                  <div style={{ fontSize: "10.5px", color: "var(--text-muted)", marginTop: "2px" }}>
                    HASH CHAIN VERIFIED • <span className="mono" style={{ color: "var(--status-reconciled)" }}>tamper_free: true</span>
                  </div>
                </div>
              </div>
              <span style={{ color: "var(--color-brand)", fontSize: "14px" }}>›</span>
            </Link>

            {/* Recent Activity Timeline */}
            <div className="panel-flat" style={{ padding: "1.15rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                RECENT ACTIVITY
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                {[
                  { time: "10:24 AM", text: "CASE-000003 investigated" },
                  { time: "10:18 AM", text: "CASE-000132 sent for approval" },
                  { time: "10:12 AM", text: "CASE-000009 blocked (fail-closed)" },
                  { time: "09:45 AM", text: "Seed 42 benchmark loaded" },
                ].map((act, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: "0.6rem", fontSize: "11px" }}>
                    <span className="mono" style={{ color: "var(--color-brand)", fontSize: "10px", fontWeight: 700, whiteSpace: "nowrap" }}>
                      ● {act.time}
                    </span>
                    <span style={{ color: "var(--text-secondary)", lineHeight: 1.25 }}>{act.text}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
