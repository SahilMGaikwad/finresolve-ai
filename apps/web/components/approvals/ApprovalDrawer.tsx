"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { ApprovalsIcon } from "@/components/icons/Icons";

interface ApprovalDrawerProps {
  proposalId?: string;
  proposal?: any;
  onSuccess?: () => void;
  onApproved?: () => void;
  onClose?: () => void;
}

export function ApprovalDrawer({
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

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h3 style={{ fontSize: "1rem", fontWeight: 800, color: "#0f172a", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <ApprovalsIcon size={18} color="#2563eb" /> Human Approval & Sign-Off Gate
          </h3>
          <p style={{ fontSize: "0.74rem", color: "var(--text-muted)", marginTop: "2px" }}>
            Enforces Role-Based Access Control and separation-of-duties. Proposer cannot self-approve.
          </p>
        </div>
        {onClose && (
          <button onClick={onClose} className="btn-secondary" style={{ fontSize: "0.7rem", padding: "0.25rem 0.55rem" }}>
            ✕
          </button>
        )}
      </div>

      {errorMsg && (
        <div style={{
          padding: "0.85rem 1.15rem",
          backgroundColor: "#fef2f2",
          color: "#991b1b",
          border: "1px solid #fecaca",
          borderRadius: "6px",
          fontSize: "0.78rem",
        }}>
          <strong>Access Denied:</strong> {errorMsg}
        </div>
      )}

      {successMsg && (
        <div style={{
          padding: "0.85rem 1.15rem",
          backgroundColor: "#ecfdf5",
          color: "#059669",
          border: "1px solid #a7f3d0",
          borderRadius: "6px",
          fontSize: "0.78rem",
        }}>
          ✓ {successMsg}
        </div>
      )}

      {/* Separation of Duties Box */}
      <div style={{
        background: "#f8fafc",
        border: "1px solid var(--border-subtle)",
        borderRadius: "6px",
        padding: "0.85rem 1rem",
        display: "flex",
        flexDirection: "column",
        gap: "0.4rem",
        fontSize: "0.75rem",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: "var(--text-muted)" }}>Proposal ID:</span>
          <span className="mono" style={{ fontWeight: 700, color: "#0f172a" }}>{targetId}</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: "var(--text-muted)" }}>Proposer Role:</span>
          <span className="mono" style={{ fontWeight: 600, color: "#2563eb" }}>analyst_01 (Analyst)</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: "var(--text-muted)" }}>Approver Role:</span>
          <span className="mono" style={{ fontWeight: 600, color: "#059669" }}>reviewer_01 (Lead)</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", borderTop: "1px solid var(--border-subtle)", paddingTop: "0.4rem" }}>
          <span style={{ color: "var(--text-muted)" }}>Separation of Duties:</span>
          <span className="badge badge-reconciled" style={{ fontSize: "0.62rem" }}>ENFORCED</span>
        </div>
      </div>

      {/* Justification Input */}
      <div>
        <label style={{ display: "block", fontSize: "0.72rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "0.35rem" }}>
          Analyst Sign-Off Notes / Justification:
        </label>
        <textarea
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          placeholder="Document financial rationale for audit ledger (e.g. Verified settlement adjustment against bank credit advice)..."
          rows={4}
          className="input-control"
          style={{ width: "100%", resize: "none" }}
        />
      </div>

      {/* Action Buttons */}
      <div style={{ display: "flex", gap: "0.65rem", marginTop: "0.5rem" }}>
        <button
          onClick={handleApprove}
          disabled={isSubmitting}
          className="btn-primary"
          style={{ flex: 1, padding: "0.55rem" }}
        >
          {isSubmitting ? "Processing..." : "Approve & Sign Resolution"}
        </button>
        <button
          onClick={handleReject}
          disabled={isSubmitting}
          className="btn-danger"
          style={{ padding: "0.55rem 1rem" }}
        >
          Reject
        </button>
      </div>
    </div>
  );
}
