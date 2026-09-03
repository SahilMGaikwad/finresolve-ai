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
      backgroundColor: isOpen ? "rgba(9, 9, 9, 0.85)" : "transparent",
      backdropFilter: isOpen ? "blur(2px)" : undefined,
      zIndex: 999,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: isOpen ? "1.5rem" : 0,
    }}>
      <div style={{
        backgroundColor: "var(--bg-surface)",
        border: "1px solid var(--border-subtle)",
        padding: "1.75rem",
        width: "100%",
        maxWidth: "540px",
        display: "flex",
        flexDirection: "column",
        gap: "1.25rem",
        boxShadow: "var(--shadow-lg)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ fontSize: "10.5px", fontWeight: 700, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.1em" }}>
              DUAL SIGN-OFF MANDATE
            </div>
            <h3 className="heading-editorial title-large" style={{ marginTop: "2px" }}>
              HUMAN APPROVAL GATE
            </h3>
            <p style={{ fontSize: "11.5px", color: "var(--text-muted)", marginTop: "2px" }}>
              Enforces Role-Based Access Control and separation of duties. Proposer cannot self-approve.
            </p>
          </div>
          {onClose && (
            <button onClick={onClose} className="btn btn-secondary btn-sm" style={{ padding: "0.2rem 0.5rem" }}>
              ✕
            </button>
          )}
        </div>

        {errorMsg && (
          <div style={{
            padding: "0.75rem 1rem",
            backgroundColor: "var(--status-discrepancy-bg)",
            color: "var(--color-brand)",
            border: "1px solid var(--status-discrepancy-border)",
            fontSize: "11.5px",
          }}>
            <strong>ACCESS DENIED:</strong> {errorMsg}
          </div>
        )}

        {successMsg && (
          <div style={{
            padding: "0.75rem 1rem",
            backgroundColor: "var(--status-reconciled-bg)",
            color: "var(--status-reconciled)",
            border: "1px solid var(--status-reconciled-border)",
            fontSize: "11.5px",
          }}>
            ✓ {successMsg}
          </div>
        )}

        <div>
          <label style={{ display: "block", fontSize: "10.5px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.4rem" }}>
            JUSTIFICATION & AUDIT NOTES
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
            REJECT PROPOSAL
          </button>
          <button
            onClick={handleApprove}
            disabled={isSubmitting}
            className="btn btn-primary btn-sm"
          >
            {isSubmitting ? "SIGNING..." : "SIGN & APPROVE RESOLUTION"}
          </button>
        </div>
      </div>
    </div>
  );
}
