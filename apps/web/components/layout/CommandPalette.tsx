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
        backgroundColor: "rgba(11, 18, 32, 0.45)",
        backdropFilter: "blur(4px)",
        zIndex: 999,
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "center",
        paddingTop: "12vh",
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "600px",
          backgroundColor: "#ffffff",
          border: "1px solid var(--border-subtle)",
          borderRadius: "10px",
          boxShadow: "var(--shadow-lg)",
          overflow: "hidden",
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
          padding: "0.9rem 1.15rem",
          borderBottom: "1px solid var(--border-subtle)",
        }}>
          <SearchIcon size={16} color="var(--text-muted)" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search cases (CASE-000003), merchants (merchant_0003), payments..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              outline: "none",
              color: "#111827",
              fontSize: "14px",
              fontFamily: "inherit",
            }}
          />
          <button
            onClick={onClose}
            style={{ color: "var(--text-muted)", padding: "0.2rem" }}
          >
            <CloseIcon size={14} />
          </button>
        </div>

        {/* Results List */}
        <div style={{ maxHeight: "380px", overflowY: "auto", padding: "0.6rem" }}>
          {isLoading ? (
            <div style={{ padding: "2.5rem", textAlign: "center", color: "var(--text-muted)", fontSize: "13.5px" }}>
              Searching operations store...
            </div>
          ) : matchedCases.length === 0 && matchedMerchants.length === 0 ? (
            <div style={{ padding: "2.5rem", textAlign: "center", color: "var(--text-muted)", fontSize: "13.5px" }}>
              No matching records found for &quot;{query}&quot;.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {/* Category: Cases */}
              {matchedCases.length > 0 && (
                <div>
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", padding: "0.3rem 0.6rem", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                    CASES ({matchedCases.length})
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}>
                    {matchedCases.slice(0, 8).map((c) => (
                      <div
                        key={c.case_id}
                        onClick={() => handleSelectCase(c.case_id)}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          padding: "0.55rem 0.85rem",
                          borderRadius: "6px",
                          cursor: "pointer",
                          transition: "background-color 0.12s ease",
                        }}
                        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "var(--bg-surface-hover)")}
                        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                          <span className="mono" style={{ fontWeight: 600, color: "#111827", fontSize: "13.5px" }}>
                            {c.case_id}
                          </span>
                          <span className="mono" style={{ fontSize: "12.5px", color: "var(--text-muted)" }}>
                            {c.merchant_id}
                          </span>
                        </div>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                          <span className={`badge badge-${c.status === "reconciled" ? "reconciled" : "discrepancy"}`}>
                            {c.status}
                          </span>
                          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                            {c.discrepancies_count} {c.discrepancies_count === 1 ? "issue" : "issues"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Category: Merchants */}
              {matchedMerchants.length > 0 && (
                <div>
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", padding: "0.3rem 0.6rem", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                    MERCHANTS ({matchedMerchants.length})
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}>
                    {matchedMerchants.slice(0, 5).map((c) => (
                      <div
                        key={`m_${c.case_id}`}
                        onClick={() => handleSelectCase(c.case_id)}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          padding: "0.55rem 0.85rem",
                          borderRadius: "6px",
                          cursor: "pointer",
                          transition: "background-color 0.12s ease",
                        }}
                        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "var(--bg-surface-hover)")}
                        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
                      >
                        <span className="mono" style={{ fontWeight: 600, color: "#315cf5", fontSize: "13px" }}>
                          {c.merchant_id}
                        </span>
                        <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                          Linked to {c.case_id}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer info */}
        <div style={{
          padding: "0.65rem 1rem",
          background: "#f8fafc",
          borderTop: "1px solid var(--border-subtle)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "12px",
          color: "var(--text-muted)",
        }}>
          <div>Press <span className="kbd-tag">ESC</span> to close</div>
          <div><span className="kbd-tag">↑↓</span> to navigate <span className="kbd-tag">↵</span> to select</div>
        </div>
      </div>
    </div>
  );
}
