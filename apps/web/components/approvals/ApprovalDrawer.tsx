"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface ApprovalDrawerProps {
  proposalId: string;
  onSuccess: () => void;
}

export function ApprovalDrawer({ proposalId, onSuccess }: ApprovalDrawerProps) {
  const [comments, setComments] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleApprove = async () => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await api.approveProposal(proposalId, comments);
      setSuccessMsg("Resolution approved and signed successfully.");
      onSuccess();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to approve proposal");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await api.rejectProposal(proposalId, comments);
      setSuccessMsg("Resolution rejected.");
      onSuccess();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to reject proposal");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#fff" }}>
        Human Approval & Sign-Off Gate
      </h3>
      <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
        Enforces Role-Based Access Control and separation-of-duties. Proposer cannot self-approve.
      </p>

      {errorMsg && (
        <div style={{ padding: "0.75rem", backgroundColor: "var(--status-discrepancy-bg)", color: "var(--status-discrepancy)", borderRadius: "6px", fontSize: "0.8rem" }}>
          {errorMsg}
        </div>
      )}

      {successMsg && (
        <div style={{ padding: "0.75rem", backgroundColor: "var(--status-reconciled-bg)", color: "var(--status-reconciled)", borderRadius: "6px", fontSize: "0.8rem" }}>
          {successMsg}
        </div>
      )}

      <div>
        <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginBottom: "0.35rem" }}>
          Approver Audit Notes & Justification:
        </label>
        <textarea
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          placeholder="e.g. Contract verified against partner bank UTR ledger."
          rows={3}
          style={{
            width: "100%",
            backgroundColor: "var(--bg-input)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "6px",
            padding: "0.75rem",
            color: "#fff",
            fontSize: "0.85rem",
            fontFamily: "var(--font-sans)",
            resize: "vertical",
          }}
        />
      </div>

      <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
        <button
          onClick={handleReject}
          disabled={isSubmitting}
          className="btn-secondary"
          style={{ color: "var(--status-discrepancy)", borderColor: "var(--status-discrepancy-border)" }}
        >
          Reject Proposal
        </button>
        <button
          onClick={handleApprove}
          disabled={isSubmitting}
          className="btn-primary"
          style={{ backgroundColor: "var(--status-reconciled)", borderColor: "var(--status-reconciled)" }}
        >
          {isSubmitting ? "Signing..." : "✓ Approve & Authorize"}
        </button>
      </div>
    </div>
  );
}
