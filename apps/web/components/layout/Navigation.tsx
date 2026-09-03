"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  OverviewIcon,
  CasesIcon,
  ApprovalsIcon,
  AuditIcon,
  SystemIcon,
  SearchIcon,
} from "@/components/icons/Icons";

export function Navigation() {
  const pathname = usePathname();

  const primaryNav = [
    { href: "/", label: "Overview", icon: OverviewIcon },
    { href: "/cases", label: "Cases", icon: CasesIcon },
    { href: "/approvals", label: "Approvals", icon: ApprovalsIcon },
    { href: "/audit", label: "Audit", icon: AuditIcon },
  ];

  const operationsNav = [
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
      width: "225px",
      backgroundColor: "var(--bg-sidebar)",
      borderRight: "1px solid var(--border-subtle)",
      display: "flex",
      flexDirection: "column",
      padding: "1rem 0.75rem",
      flexShrink: 0,
      userSelect: "none",
    }}>
      {/* Brand Header */}
      <div style={{
        padding: "0.25rem 0.5rem 1rem 0.5rem",
        borderBottom: "1px solid var(--border-hairline)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.65rem" }}>
          <div style={{
            width: "28px",
            height: "28px",
            borderRadius: "6px",
            backgroundColor: "var(--color-indigo)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#ffffff",
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 6h16" />
              <path d="M4 12h10" />
              <path d="m14 18 4-4 4 4" />
            </svg>
          </div>
          <div>
            <div style={{ fontSize: "13.5px", fontWeight: 700, letterSpacing: "0.02em", color: "var(--text-primary)", lineHeight: 1.1 }}>
              FINRESOLVE <span style={{ color: "var(--color-indigo)", fontSize: "11px", fontWeight: 800 }}>AI</span>
            </div>
            <div style={{ fontSize: "10.5px", color: "var(--text-muted)", letterSpacing: "0.02em", marginTop: "2px", fontWeight: 500 }}>
              Financial Operations
            </div>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <div style={{ flex: 1, overflowY: "auto", marginTop: "1rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        <nav style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}>
          {primaryNav.map((item) => {
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
                  gap: "0.6rem",
                  padding: "0.45rem 0.65rem",
                  borderRadius: "5px",
                  fontSize: "13px",
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                  backgroundColor: isActive ? "var(--bg-surface-elevated)" : "transparent",
                  borderLeft: isActive ? "2px solid var(--color-indigo)" : "2px solid transparent",
                  transition: "all 0.12s ease",
                }}
              >
                <Icon size={15} color={isActive ? "var(--color-indigo)" : "var(--text-muted)"} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Operations Section */}
        <div>
          <div style={{
            fontSize: "10px",
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            color: "var(--text-dim)",
            padding: "0 0.65rem 0.4rem 0.65rem",
          }}>
            Operations
          </div>
          <nav style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}>
            {operationsNav.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.6rem",
                    padding: "0.45rem 0.65rem",
                    borderRadius: "5px",
                    fontSize: "13px",
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                    backgroundColor: isActive ? "var(--bg-surface-elevated)" : "transparent",
                    borderLeft: isActive ? "2px solid var(--color-indigo)" : "2px solid transparent",
                    transition: "all 0.12s ease",
                  }}
                >
                  <Icon size={15} color={isActive ? "var(--color-indigo)" : "var(--text-muted)"} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Demo Scenarios Quick Links */}
        <div>
          <div style={{
            fontSize: "10px",
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            color: "var(--text-dim)",
            padding: "0 0.65rem 0.4rem 0.65rem",
          }}>
            Demo Scenarios
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            {demoCases.map((c) => {
              const isActive = pathname === `/cases/${c.id}`;
              return (
                <Link
                  key={c.id}
                  href={`/cases/${c.id}`}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "0.35rem 0.65rem",
                    borderRadius: "4px",
                    fontSize: "11.5px",
                    backgroundColor: isActive ? "var(--bg-surface-elevated)" : "transparent",
                    border: isActive ? "1px solid var(--border-medium)" : "1px solid transparent",
                    transition: "all 0.12s ease",
                  }}
                >
                  <span className="mono" style={{ color: isActive ? "var(--text-primary)" : "var(--text-secondary)", fontWeight: 500 }}>
                    {c.id}
                  </span>
                  <span style={{
                    fontSize: "10px",
                    padding: "0.1rem 0.35rem",
                    borderRadius: "3px",
                    fontWeight: 500,
                    backgroundColor:
                      c.type === "reconciled" ? "var(--status-reconciled-bg)" :
                      c.type === "review" ? "var(--status-review-bg)" : "var(--status-discrepancy-bg)",
                    color:
                      c.type === "reconciled" ? "var(--status-reconciled)" :
                      c.type === "review" ? "var(--status-review)" : "var(--status-discrepancy)",
                    border: `1px solid ${
                      c.type === "reconciled" ? "var(--status-reconciled-border)" :
                      c.type === "review" ? "var(--status-review-border)" : "var(--status-discrepancy-border)"
                    }`,
                  }}>
                    {c.label}
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {/* User Profile Info Footer */}
      <div style={{
        paddingTop: "0.75rem",
        borderTop: "1px solid var(--border-hairline)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>
        <div>
          <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-primary)" }}>
            Sahil Gaikwad
          </div>
          <div style={{ fontSize: "10.5px", color: "var(--text-muted)" }}>
            Senior Analyst • Production
          </div>
        </div>
        <div style={{
          width: "7px",
          height: "7px",
          borderRadius: "50%",
          backgroundColor: "var(--color-teal)",
        }} />
      </div>
    </aside>
  );
}
