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
        height: "48px",
        backgroundColor: "var(--bg-header)",
        borderBottom: "1px solid var(--border-subtle)",
        padding: "0 2rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky",
        top: 0,
        zIndex: 20,
      }}>
        {/* Left: Breadcrumbs */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          {breadcrumbs ? (
            <div style={{ display: "flex", alignItems: "center", gap: "0.45rem", fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700 }}>
              {breadcrumbs.map((b, i) => (
                <span key={i} style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
                  {i > 0 && <span style={{ color: "var(--color-brand)" }}>/</span>}
                  {b.href ? (
                    <a href={b.href} style={{ color: "var(--text-muted)", textDecoration: "none" }}>
                      {b.label}
                    </a>
                  ) : (
                    <span style={{ color: "var(--text-primary)" }}>{b.label}</span>
                  )}
                </span>
              ))}
            </div>
          ) : (
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-primary)" }}>
                {title || "FINRESOLVE"}
              </span>
              {subtitle && (
                <span style={{ fontSize: "11px", color: "var(--text-muted)", borderLeft: "1px solid var(--border-subtle)", paddingLeft: "0.5rem" }}>
                  {subtitle}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Center: Search Field */}
        <div
          onClick={() => setIsCommandOpen(true)}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.6rem",
            backgroundColor: "var(--bg-input)",
            border: "1px solid var(--border-subtle)",
            padding: "0.3rem 0.85rem",
            width: "360px",
            cursor: "pointer",
            color: "var(--text-muted)",
            fontSize: "11.5px",
            borderRadius: "1px",
            transition: "all 0.12s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "var(--border-medium)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--border-subtle)";
          }}
        >
          <SearchIcon size={12} color="var(--text-muted)" />
          <span style={{ flex: 1, letterSpacing: "0.01em" }}>Search cases, merchants, settlements...</span>
          <span style={{
            fontSize: "9px",
            fontFamily: "var(--font-mono)",
            border: "1px solid var(--border-medium)",
            padding: "0.05rem 0.3rem",
            color: "var(--text-muted)",
            borderRadius: "1px",
          }}>⌘K</span>
        </div>

        {/* Right: Operational Status & Action */}
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
            fontSize: "10.5px",
            fontFamily: "var(--font-mono)",
            color: "var(--text-muted)",
          }}>
            <span style={{ display: "flex", alignItems: "center", gap: "0.35rem", color: "var(--color-brand)" }}>
              <span style={{
                width: "4px",
                height: "4px",
                borderRadius: "50%",
                backgroundColor: "var(--color-brand)",
              }} />
              <span style={{ fontWeight: 700 }}>OPERATIONAL</span>
            </span>
            <span style={{ color: "var(--border-subtle)" }}>|</span>
            <span>SEED 42</span>
            <span style={{ color: "var(--border-subtle)" }}>|</span>
            <span style={{ color: "var(--text-dim)" }}>PROD</span>
          </div>

          {actions && <div>{actions}</div>}
        </div>
      </header>

      {/* Command Palette Modal */}
      <CommandPalette isOpen={isCommandOpen} onClose={() => setIsCommandOpen(false)} />
    </>
  );
}
