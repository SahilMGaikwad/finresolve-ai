"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function Navigation() {
  const pathname = usePathname();

  const primaryNav = [
    { href: "/", label: "Overview", num: "01" },
    { href: "/cases", label: "Cases", num: "02" },
    { href: "/approvals", label: "Approvals", num: "03" },
    { href: "/audit", label: "Audit", num: "04" },
  ];

  const operationsNav = [
    { href: "/health", label: "System Health", num: "05" },
  ];

  const demoCases = [
    { id: "CASE-000002", color: "#10B981" },
    { id: "CASE-000003", color: "#E72D5B" },
    { id: "CASE-000132", color: "#D9A441" },
    { id: "CASE-000009", color: "#E72D5B" },
  ];

  return (
    <aside style={{
      width: "220px",
      backgroundColor: "var(--bg-sidebar)",
      borderRight: "1px solid var(--border-subtle)",
      display: "flex",
      flexDirection: "column",
      padding: "1.25rem 0.85rem",
      flexShrink: 0,
      userSelect: "none",
    }}>
      {/* Brand Header */}
      <div style={{
        padding: "0 0.5rem 1.25rem 0.5rem",
        borderBottom: "1px solid var(--border-hairline)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          {/* Geometric Brand Icon */}
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M4 4H20V8H10V11H18V15H10V20H4V4Z" fill="var(--color-brand)" />
          </svg>
          <div style={{
            fontFamily: "var(--font-heading)",
            fontSize: "13.5px",
            fontWeight: 800,
            letterSpacing: "0.02em",
            color: "var(--text-primary)",
            lineHeight: 1,
          }}>
            FINRESOLVE <span style={{ color: "var(--color-brand)", fontSize: "11px" }}>AI</span>
          </div>
        </div>
      </div>

      {/* Nav List */}
      <div style={{ flex: 1, overflowY: "auto", marginTop: "1.25rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Primary Nav */}
        <nav style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          {primaryNav.map((item) => {
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
                  gap: "0.75rem",
                  padding: "0.5rem 0.65rem",
                  fontSize: "12.5px",
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                  background: isActive
                    ? "linear-gradient(90deg, rgba(231, 45, 91, 0.2) 0%, rgba(231, 45, 91, 0) 100%)"
                    : "transparent",
                  borderLeft: isActive ? "2px solid var(--color-brand)" : "2px solid transparent",
                  transition: "all 0.12s ease",
                }}
              >
                <span className="mono" style={{ fontSize: "11px", color: isActive ? "var(--color-brand)" : "var(--text-dim)", fontWeight: 700 }}>
                  {item.num}
                </span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Operations */}
        <div>
          <div style={{
            fontSize: "9.5px",
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "var(--text-dim)",
            padding: "0 0.65rem 0.4rem 0.65rem",
            borderBottom: "1px solid var(--border-hairline)",
            marginBottom: "0.4rem",
          }}>
            OPERATIONS
          </div>
          <nav style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            {operationsNav.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.75rem",
                    padding: "0.5rem 0.65rem",
                    fontSize: "12.5px",
                    fontWeight: isActive ? 700 : 500,
                    color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                    background: isActive
                      ? "linear-gradient(90deg, rgba(231, 45, 91, 0.2) 0%, rgba(231, 45, 91, 0) 100%)"
                      : "transparent",
                    borderLeft: isActive ? "2px solid var(--color-brand)" : "2px solid transparent",
                    transition: "all 0.12s ease",
                  }}
                >
                  <span className="mono" style={{ fontSize: "11px", color: isActive ? "var(--color-brand)" : "var(--text-dim)", fontWeight: 700 }}>
                    {item.num}
                  </span>
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Demo Scenarios */}
        <div>
          <div style={{
            fontSize: "9.5px",
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "var(--text-dim)",
            padding: "0 0.65rem 0.4rem 0.65rem",
            borderBottom: "1px solid var(--border-hairline)",
            marginBottom: "0.4rem",
          }}>
            DEMO SCENARIOS
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
                    fontSize: "11px",
                    color: isActive ? "var(--text-primary)" : "var(--text-muted)",
                    background: isActive ? "var(--bg-surface-elevated)" : "transparent",
                    borderLeft: isActive ? "2px solid var(--color-brand)" : "2px solid transparent",
                    transition: "all 0.12s ease",
                  }}
                >
                  <span className="mono" style={{ fontWeight: isActive ? 700 : 500 }}>
                    {c.id}
                  </span>
                  <span style={{
                    width: "5px",
                    height: "5px",
                    borderRadius: "50%",
                    backgroundColor: c.color,
                  }} />
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {/* Footer Profile */}
      <div style={{
        paddingTop: "1rem",
        borderTop: "1px solid var(--border-hairline)",
        paddingLeft: "0.65rem",
        paddingRight: "0.65rem",
      }}>
        <div style={{ fontSize: "11.5px", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "0.02em" }}>
          SAHIL GAIKWAD
        </div>
        <div style={{ fontSize: "10.5px", color: "var(--text-muted)", marginTop: "1px" }}>
          Senior Analyst
        </div>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "0.35rem",
          fontSize: "9.5px",
          fontFamily: "var(--font-mono)",
          color: "var(--color-brand)",
          fontWeight: 700,
          marginTop: "6px",
        }}>
          <span style={{ width: "4px", height: "4px", borderRadius: "50%", backgroundColor: "var(--color-brand)" }} />
          <span>PRODUCTION</span>
        </div>
      </div>
    </aside>
  );
}
