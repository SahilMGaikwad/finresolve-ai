"use client";

import { useState } from "react";
import { SearchIcon } from "@/components/icons/Icons";
import { CommandPalette } from "./CommandPalette";

interface HeaderProps {
  title?: string;
  subtitle?: string;
  breadcrumbs?: { label: string; href?: string }[];
  actions?: React.ReactNode;
}

export function Header({ title, subtitle, breadcrumbs, actions }: HeaderProps) {
  const [isCommandOpen, setIsCommandOpen] = useState(false);

  return (
    <>
      <header style={{
        height: "56px",
        backgroundColor: "var(--bg-header)",
        borderBottom: "1px solid var(--border-subtle)",
        padding: "0 2.25rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky",
        top: 0,
        zIndex: 20,
      }}>
        {/* Left: Breadcrumbs / Title */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          {breadcrumbs ? (
            <div style={{ display: "flex", alignItems: "center", gap: "0.45rem", fontSize: "13.5px" }}>
              {breadcrumbs.map((b, i) => (
                <span key={i} style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
                  {i > 0 && <span style={{ color: "var(--text-dim)" }}>/</span>}
                  {b.href ? (
                    <a href={b.href} style={{ color: "var(--text-secondary)", textDecoration: "none", fontWeight: 500 }}>
                      {b.label}
                    </a>
                  ) : (
                    <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>{b.label}</span>
                  )}
                </span>
              ))}
            </div>
          ) : (
            <div>
              <span style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)" }}>
                {title}
              </span>
              {subtitle && (
                <span style={{ fontSize: "13px", color: "var(--text-muted)", marginLeft: "0.6rem" }}>
                  {subtitle}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Center: Global Search Bar Trigger */}
        <div
          onClick={() => setIsCommandOpen(true)}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.65rem",
            backgroundColor: "#f8fafc",
            border: "1px solid var(--border-subtle)",
            borderRadius: "6px",
            padding: "0.4rem 0.95rem",
            width: "380px",
            cursor: "pointer",
            color: "var(--text-muted)",
            fontSize: "13px",
            transition: "all 0.15s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "var(--border-medium)";
            e.currentTarget.style.backgroundColor = "#ffffff";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--border-subtle)";
            e.currentTarget.style.backgroundColor = "#f8fafc";
          }}
        >
          <SearchIcon size={14} color="var(--text-muted)" />
          <span style={{ flex: 1 }}>Search cases, merchants, payments...</span>
          <span className="kbd-tag">⌘ K</span>
        </div>

        {/* Right: Actions & System Operational Status */}
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "0.45rem",
            padding: "0.25rem 0.65rem",
            background: "#f0fdfa",
            border: "1px solid #99f6e4",
            borderRadius: "5px",
            fontSize: "11.5px",
            color: "#0f766e",
            fontWeight: 600,
          }}>
            <span style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              backgroundColor: "var(--status-reconciled)",
            }} />
            <span>SYSTEM OPERATIONAL · SEED 42</span>
          </div>

          {actions && <div>{actions}</div>}
        </div>
      </header>

      {/* Command Palette Modal */}
      <CommandPalette isOpen={isCommandOpen} onClose={() => setIsCommandOpen(false)} />
    </>
  );
}
