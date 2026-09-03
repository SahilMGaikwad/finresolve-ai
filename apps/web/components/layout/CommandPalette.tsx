"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { api, CaseSummary } from "@/lib/api";
import { SearchIcon, CloseIcon } from "@/components/icons/Icons";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setIsLoading(true);
      api.listCases(100, 0)
        .then((res) => setCases(res.cases || []))
        .catch((err) => console.error(err))
        .finally(() => setIsLoading(false));
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery("");
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const q = query.toLowerCase().trim();

  const matchedCases = cases.filter((c) => {
    if (!q) return true;
    return (
      c.case_id.toLowerCase().includes(q) ||
      c.difficulty.toLowerCase().includes(q) ||
      c.status.toLowerCase().includes(q)
    );
  });

  const matchedMerchants = cases.filter((c) => {
    if (!q) return false;
    return c.merchant_id.toLowerCase().includes(q);
  });

  const handleSelectCase = (caseId: string) => {
    onClose();
    router.push(`/cases/${caseId}`);
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(9, 9, 9, 0.85)",
        backdropFilter: "blur(2px)",
        zIndex: 999,
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "center",
        paddingTop: "10vh",
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "620px",
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-subtle)",
          boxShadow: "var(--shadow-lg)",
          display: "flex",
          flexDirection: "column",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          padding: "0.85rem 1.25rem",
          borderBottom: "1px solid var(--border-subtle)",
          backgroundColor: "var(--bg-surface-secondary)",
        }}>
          <SearchIcon size={14} color="var(--color-brand)" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="TYPE TO SEARCH CASES, MERCHANTS, SETTLEMENTS..."
            style={{
              flex: 1,
              backgroundColor: "transparent",
              border: "none",
              outline: "none",
              color: "var(--text-primary)",
              fontSize: "13px",
              fontFamily: "var(--font-heading)",
              textTransform: "uppercase",
              letterSpacing: "0.04em",
              fontWeight: 600,
            }}
          />
          {query && (
            <button onClick={() => setQuery("")} style={{ color: "var(--text-muted)", padding: "2px" }}>
              <CloseIcon size={12} />
            </button>
          )}
          <span style={{
            fontSize: "9.5px",
            fontFamily: "var(--font-mono)",
            border: "1px solid var(--border-subtle)",
            padding: "0.1rem 0.35rem",
            color: "var(--text-muted)",
          }}>ESC</span>
        </div>

        {/* Results Body */}
        <div style={{ maxHeight: "380px", overflowY: "auto", padding: "0.5rem 0" }}>
          {isLoading ? (
            <div style={{ padding: "1.5rem", textAlign: "center", color: "var(--text-muted)", fontSize: "12px", fontFamily: "var(--font-mono)" }}>
              SCANNING INDEX...
            </div>
          ) : matchedCases.length === 0 && matchedMerchants.length === 0 ? (
            <div style={{ padding: "2rem", textAlign: "center", color: "var(--text-muted)", fontSize: "12px" }}>
              NO MATCHES FOR &quot;{query}&quot;
            </div>
          ) : (
            <>
              {/* CASES Group */}
              {matchedCases.length > 0 && (
                <div style={{ marginBottom: "0.5rem" }}>
                  <div style={{
                    fontSize: "9.5px",
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    color: "var(--text-dim)",
                    padding: "0.4rem 1.25rem",
                  }}>
                    Cases ({matchedCases.length})
                  </div>
                  {matchedCases.slice(0, 8).map((c) => (
                    <div
                      key={c.case_id}
                      onClick={() => handleSelectCase(c.case_id)}
                      style={{
                        padding: "0.6rem 1.25rem",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        cursor: "pointer",
                        fontSize: "12.5px",
                        borderBottom: "1px solid var(--border-hairline)",
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "var(--bg-surface-hover)"}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                        <span className="mono" style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                          {c.case_id}
                        </span>
                        <span className="mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                          {c.merchant_id}
                        </span>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                        <span style={{
                          fontSize: "9.5px",
                          fontWeight: 700,
                          letterSpacing: "0.04em",
                          color:
                            c.status === "reconciled" ? "var(--status-reconciled)" : "var(--color-brand)",
                        }}>
                          ● {c.status.toUpperCase()}
                        </span>
                        <span style={{ color: "var(--color-brand)", fontSize: "12px" }}>→</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* MERCHANTS Group */}
              {matchedMerchants.length > 0 && (
                <div>
                  <div style={{
                    fontSize: "9.5px",
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    color: "var(--text-dim)",
                    padding: "0.4rem 1.25rem",
                    borderTop: "1px solid var(--border-subtle)",
                  }}>
                    Merchants ({matchedMerchants.length})
                  </div>
                  {matchedMerchants.slice(0, 4).map((c) => (
                    <div
                      key={`m_${c.case_id}`}
                      onClick={() => handleSelectCase(c.case_id)}
                      style={{
                        padding: "0.6rem 1.25rem",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        cursor: "pointer",
                        fontSize: "12.5px",
                        borderBottom: "1px solid var(--border-hairline)",
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "var(--bg-surface-hover)"}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                    >
                      <span className="mono" style={{ color: "var(--text-secondary)" }}>
                        {c.merchant_id}
                      </span>
                      <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                        OPEN {c.case_id} →
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: "0.5rem 1.25rem",
          backgroundColor: "var(--bg-surface-secondary)",
          borderTop: "1px solid var(--border-subtle)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          fontSize: "10.5px",
          color: "var(--text-muted)",
          fontFamily: "var(--font-mono)",
        }}>
          <span>NAVIGATE [ ↑ ↓ ]</span>
          <span>SELECT [ ENTER ]</span>
        </div>
      </div>
    </div>
  );
}
