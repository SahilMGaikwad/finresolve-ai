"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { ApprovalsIcon } from "@/components/icons/Icons";

interface ApprovalDrawerProps {
  isOpen?: boolean;
  caseId?: string;
  proposalId?: string;
  proposal?: any;
  onSuccess?: () => void;
  onApproved?: () => void;
  onClose?: () => void;
}

export function ApprovalDrawer({
  isOpen = false,
  proposalId,
  proposal,
  onSuccess,
  onApproved,
  onClose,
}: ApprovalDrawerProps) {
  const targetId = proposalId || proposal?.proposal_id || "prop_01";
  const [comments, setComments] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleApprove = async () => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await api.approveProposal(targetId, comments);
      setSuccessMsg("Resolution approved and signed successfully.");
      if (onSuccess) onSuccess();
      if (onApproved) onApproved();
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
      await api.rejectProposal(targetId, comments);
      setSuccessMsg("Resolution rejected.");
      if (onSuccess) onSuccess();
      if (onApproved) onApproved();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to reject proposal");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen && onClose) return null;

  return (
    <div style={{
      position: isOpen ? "fixed" : "relative",
      inset: isOpen ? 0 : undefined,
      backgroundColor: isOpen ? "rgba(7, 11, 18, 0.75)" : "transparent",
      backdropFilter: isOpen ? "blur(4px)" : undefined,
      zIndex: isOpen ? 999 : undefined,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: isOpen ? "1rem" : 0,
    }}>
      <div style={{
        backgroundColor: "var(--bg-surface)",
        border: "1px solid var(--border-subtle)",
        borderRadius: "6px",
        padding: "1.25rem 1.5rem",
        width: "100%",
        maxWidth: "520px",
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
        boxShadow: "var(--shadow-lg)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h3 style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <ApprovalsIcon size={16} color="var(--color-indigo)" /> Human Approval & Sign-Off Gate
            </h3>
            <p style={{ fontSize: "11.5px", color: "var(--text-muted)", marginTop: "2px" }}>
              Enforces Role-Based Access Control and separation of duties. Proposer cannot self-approve.
            </p>
          </div>
          {onClose && (
            <button onClick={onClose} className="btn btn-secondary btn-sm">
              ✕
            </button>
          )}
        </div>

        {errorMsg && (
          <div style={{
            padding: "0.75rem 1rem",
            backgroundColor: "var(--status-discrepancy-bg)",
            color: "var(--status-discrepancy)",
            border: "1px solid var(--status-discrepancy-border)",
            borderRadius: "5px",
            fontSize: "12px",
          }}>
            <strong>Access Denied:</strong> {errorMsg}
          </div>
        )}

        {successMsg && (
          <div style={{
            padding: "0.75rem 1rem",
            backgroundColor: "var(--status-reconciled-bg)",
            color: "var(--status-reconciled)",
            border: "1px solid var(--status-reconciled-border)",
            borderRadius: "5px",
            fontSize: "12px",
          }}>
            ✓ {successMsg}
          </div>
        )}

        <div>
          <label style={{ display: "block", fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "0.35rem" }}>
            Analyst Review Comments
          </label>
          <textarea
            rows={3}
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            placeholder="Record justification and supporting audit references for this sign-off..."
            className="input"
            style={{ width: "100%", resize: "vertical" }}
          />
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
          <button
            onClick={handleReject}
            disabled={isSubmitting}
            className="btn btn-danger btn-sm"
          >
            Reject Proposal
          </button>
          <button
            onClick={handleApprove}
            disabled={isSubmitting}
            className="btn btn-success btn-sm"
          >
            {isSubmitting ? "Signing..." : "Sign & Approve Resolution"}
          </button>
        </div>
      </div>
    </div>
  );
}
