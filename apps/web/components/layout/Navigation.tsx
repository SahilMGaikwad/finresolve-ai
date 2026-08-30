"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { href: "/", label: "Executive Dashboard", icon: "📊" },
    { href: "/cases", label: "Case Explorer", icon: "📂" },
    { href: "/approvals", label: "Approval Queue", icon: "🛡️" },
    { href: "/audit", label: "Audit Timeline", icon: "🔗" },
    { href: "/health", label: "System Health", icon: "⚡" },
  ];

  return (
    <aside style={{
      width: "260px",
      backgroundColor: "var(--bg-secondary)",
      borderRight: "1px solid var(--border-subtle)",
      display: "flex",
      flexDirection: "column",
      padding: "1.5rem 1rem",
    }}>
      {/* Brand Header */}
      <div style={{ padding: "0.5rem 0.75rem 1.5rem 0.75rem", borderBottom: "1px solid var(--border-subtle)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span style={{ fontSize: "1.5rem" }}>⚡</span>
          <div>
            <h1 style={{ fontSize: "1.1rem", fontWeight: 700, letterSpacing: "-0.02em", color: "#fff" }}>
              FinResolve AI
            </h1>
            <p style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Analyst Console
            </p>
          </div>
        </div>
      </div>

      {/* Nav Links */}
      <nav style={{ marginTop: "1.5rem", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                padding: "0.65rem 0.85rem",
                borderRadius: "6px",
                fontSize: "0.875rem",
                fontWeight: isActive ? 600 : 400,
                color: isActive ? "#ffffff" : "var(--text-secondary)",
                backgroundColor: isActive ? "var(--bg-card)" : "transparent",
                border: isActive ? "1px solid var(--border-subtle)" : "1px solid transparent",
                textDecoration: "none",
              }}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer / Role indicator */}
      <div style={{ marginTop: "auto", padding: "1rem 0.75rem", borderTop: "1px solid var(--border-subtle)" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#fff" }}>analyst_01</div>
            <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Role: SENIOR_ANALYST</div>
          </div>
          <span className="badge badge-reconciled" style={{ fontSize: "0.65rem" }}>ONLINE</span>
        </div>
      </div>
    </aside>
  );
}
