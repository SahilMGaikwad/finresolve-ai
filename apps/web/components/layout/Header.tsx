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
        height: "52px",
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
        {/* Left: Breadcrumbs / Title */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          {breadcrumbs ? (
            <div style={{ display: "flex", alignItems: "center", gap: "0.45rem", fontSize: "13px" }}>
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
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                {title || "Financial Operations"}
              </span>
              {subtitle && (
                <span style={{ fontSize: "12px", color: "var(--text-muted)", borderLeft: "1px solid var(--border-medium)", paddingLeft: "0.5rem" }}>
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
            gap: "0.6rem",
            backgroundColor: "var(--bg-surface-secondary)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "5px",
            padding: "0.35rem 0.85rem",
            width: "360px",
            cursor: "pointer",
            color: "var(--text-muted)",
            fontSize: "12.5px",
            transition: "all 0.15s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "var(--border-medium)";
            e.currentTarget.style.backgroundColor = "var(--bg-surface-elevated)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--border-subtle)";
            e.currentTarget.style.backgroundColor = "var(--bg-surface-secondary)";
          }}
        >
          <SearchIcon size={13} color="var(--text-muted)" />
          <span style={{ flex: 1 }}>Search cases, merchants, settlements...</span>
          <span style={{
            fontSize: "10px",
            fontFamily: "var(--font-mono)",
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-medium)",
            borderRadius: "3px",
            padding: "0.1rem 0.35rem",
            color: "var(--text-secondary)",
          }}>⌘K</span>
        </div>

        {/* Right: Metadata & Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {/* Metadata Pill */}
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "0.6rem",
            padding: "0.25rem 0.6rem",
            background: "var(--bg-surface-secondary)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "4px",
            fontSize: "11px",
            color: "var(--text-secondary)",
            fontFamily: "var(--font-mono)",
          }}>
            <span style={{ display: "flex", alignItems: "center", gap: "0.35rem", color: "var(--color-teal)" }}>
              <span style={{
                width: "5px",
                height: "5px",
                borderRadius: "50%",
                backgroundColor: "var(--color-teal)",
              }} />
              <span style={{ fontWeight: 600 }}>OPERATIONAL</span>
            </span>
            <span style={{ color: "var(--border-medium)" }}>|</span>
            <span>SEED 42</span>
            <span style={{ color: "var(--border-medium)" }}>|</span>
            <span style={{ color: "var(--text-muted)" }}>PROD</span>
          </div>

          {actions && <div>{actions}</div>}
        </div>
      </header>

      {/* Command Palette Modal */}
      <CommandPalette isOpen={isCommandOpen} onClose={() => setIsCommandOpen(false)} />
    </>
  );
}
