"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  OverviewIcon,
  CasesIcon,
  ApprovalsIcon,
  AuditIcon,
  SystemIcon,
} from "@/components/icons/Icons";

export function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { href: "/", label: "Overview", icon: OverviewIcon },
    { href: "/cases", label: "Cases", icon: CasesIcon },
    { href: "/approvals", label: "Approvals", icon: ApprovalsIcon },
    { href: "/audit", label: "Audit", icon: AuditIcon },
    { href: "/health", label: "System Health", icon: SystemIcon },
  ];

  const demoCases = [
    { id: "CASE-000002", label: "Clean", type: "reconciled" },
    { id: "CASE-000003", label: "Settlement", type: "discrepancy" },
    { id: "CASE-000132", label: "Review", type: "review" },
    { id: "CASE-000009", label: "Blocked", type: "blocked" },
  ];

  return (
    <aside style={{
      width: "230px",
      backgroundColor: "var(--bg-sidebar)",
      borderRight: "1px solid var(--border-subtle)",
      display: "flex",
      flexDirection: "column",
      padding: "1.25rem 0.85rem",
      flexShrink: 0,
      userSelect: "none",
    }}>
      {/* FinResolve Distinctive Brand Header */}
      <div style={{
        padding: "0.25rem 0.5rem 1.25rem 0.5rem",
        borderBottom: "1px solid var(--border-subtle)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.65rem" }}>
          {/* Abstract Reconciliation Mark */}
          <div style={{
            width: "30px",
            height: "30px",
            borderRadius: "7px",
            backgroundColor: "#315cf5",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#ffffff",
            boxShadow: "0 2px 6px rgba(49, 92, 245, 0.3)",
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 6h16" />
              <path d="M4 12h10" />
              <path d="m14 18 4-4 4 4" />
            </svg>
          </div>
          <div>
            <div style={{ fontSize: "14.5px", fontWeight: 800, letterSpacing: "-0.02em", color: "#0b1220", lineHeight: 1.1 }}>
              FINRESOLVE
            </div>
            <div style={{ fontSize: "11px", color: "var(--text-muted)", letterSpacing: "0.02em", marginTop: "2px", fontWeight: 500 }}>
              Financial Operations
            </div>
          </div>
        </div>
      </div>

      {/* Main Navigation Items */}
      <div style={{ flex: 1, overflowY: "auto", marginTop: "1.25rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        <nav style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== "/" && pathname.startsWith(item.href) && (item.href !== "/cases" || pathname === "/cases"));
            return (
              <Link
                key={item.href}
                href={item.href}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.65rem",
                  padding: "0.5rem 0.75rem",
                  borderRadius: "6px",
                  fontSize: "13.5px",
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? "#315cf5" : "var(--text-secondary)",
                  backgroundColor: isActive ? "#eff4ff" : "transparent",
                  borderLeft: isActive ? "3px solid #315cf5" : "3px solid transparent",
                  transition: "all 0.15s ease",
                }}
              >
                <Icon size={16} color={isActive ? "#315cf5" : "var(--text-muted)"} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Demo Scenarios Jump */}
        <div>
          <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em", padding: "0 0.5rem 0.45rem" }}>
            Demo Scenarios
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            {demoCases.map((c) => {
              const isCurrent = pathname === `/cases/${c.id}`;
              return (
                <Link
                  key={c.id}
                  href={`/cases/${c.id}`}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "0.45rem 0.65rem",
                    borderRadius: "5px",
                    fontSize: "12.5px",
                    background: isCurrent ? "#eff4ff" : "#ffffff",
                    border: isCurrent ? "1px solid #bfdbfe" : "1px solid var(--border-subtle)",
                    color: isCurrent ? "#315cf5" : "var(--text-secondary)",
                    transition: "all 0.15s ease",
                  }}
                >
                  <span className="mono" style={{ fontWeight: 600 }}>{c.id}</span>
                  <span className={`badge badge-${c.type}`} style={{ fontSize: "11px", padding: "0.1rem 0.35rem" }}>
                    {c.label}
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {/* Analyst Identity Footer */}
      <div style={{
        marginTop: "auto",
        paddingTop: "1rem",
        borderTop: "1px solid var(--border-subtle)",
      }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0.45rem 0.65rem",
          background: "#f8fafc",
          borderRadius: "6px",
          border: "1px solid var(--border-subtle)",
        }}>
          <div>
            <div style={{ fontSize: "12.5px", fontWeight: 600, color: "#0b1220" }}>
              Sahil Gaikwad
            </div>
            <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>
              Senior Analyst · Development
            </div>
          </div>
          <span style={{
            width: "7px",
            height: "7px",
            borderRadius: "50%",
            backgroundColor: "var(--status-reconciled)",
            boxShadow: "0 0 0 2px rgba(20, 184, 166, 0.2)",
          }} />
        </div>
      </div>
    </aside>
  );
}
