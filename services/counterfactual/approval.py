"""
FinResolve AI — Approval Workflow Manager

Enforces Role-Based Access Control and separation of duties for human-reviewed resolutions.
Proposer user ID is strictly prohibited from approving their own resolution proposal.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from services.audit.logger import global_audit_logger
from services.security.auth import AuthenticatedUser, Role


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalRecord(BaseModel):
    approval_id: str = Field(default_factory=lambda: f"appr_{uuid4().hex[:12]}")
    proposal_id: str
    status: ApprovalStatus
    proposer_id: str
    approver_id: str | None = None
    approver_role: Role | None = None
    comments: str | None = None
    decided_at: datetime | None = None


class ApprovalWorkflowManager:
    """
    Manages proposal review and enforces separation-of-duties rules.
    """

    def __init__(self):
        self._approvals: dict[str, ApprovalRecord] = {}

    def submit_for_review(self, proposal_id: str, proposer: AuthenticatedUser) -> ApprovalRecord:
        """Create a pending approval record for a resolution proposal."""
        record = ApprovalRecord(
            proposal_id=proposal_id,
            status=ApprovalStatus.PENDING,
            proposer_id=proposer.user_id,
        )
        self._approvals[proposal_id] = record

        global_audit_logger.record_event(
            actor=proposer.username,
            actor_role=proposer.role.value,
            operation="PROPOSAL_SUBMITTED_FOR_REVIEW",
            result="SUCCESS",
            reason=f"Proposal {proposal_id} submitted for review",
        )
        return record

    def approve_proposal(
        self,
        proposal_id: str,
        approver: AuthenticatedUser,
        comments: str | None = None,
    ) -> ApprovalRecord:
        """
        Approve a pending resolution proposal.
        Enforces separation of duties and role permissions.
        """
        record = self._approvals.get(proposal_id)
        if not record:
            raise ValueError(f"No approval record found for proposal {proposal_id}")

        if record.status != ApprovalStatus.PENDING:
            raise ValueError(f"Proposal {proposal_id} is already in state {record.status.value}")

        # Separation of duties check
        if record.proposer_id == approver.user_id:
            raise PermissionError("Separation of duties violation: Proposer cannot approve their own proposal!")

        # Role permission check (must be APPROVER or ADMIN)
        if approver.role not in (Role.APPROVER, Role.ADMIN):
            raise PermissionError(f"User role '{approver.role.value}' is not authorized to approve resolutions")

        record.status = ApprovalStatus.APPROVED
        record.approver_id = approver.user_id
        record.approver_role = approver.role
        record.comments = comments
        record.decided_at = datetime.now(timezone.utc)

        global_audit_logger.record_event(
            actor=approver.username,
            actor_role=approver.role.value,
            operation="PROPOSAL_APPROVED",
            result="SUCCESS",
            reason=comments or "Proposal approved by authorized approver",
        )
        return record

    def reject_proposal(
        self,
        proposal_id: str,
        reviewer: AuthenticatedUser,
        reason: str,
    ) -> ApprovalRecord:
        """Reject a resolution proposal."""
        record = self._approvals.get(proposal_id)
        if not record:
            raise ValueError(f"No approval record found for proposal {proposal_id}")

        record.status = ApprovalStatus.REJECTED
        record.approver_id = reviewer.user_id
        record.approver_role = reviewer.role
        record.comments = reason
        record.decided_at = datetime.now(timezone.utc)

        global_audit_logger.record_event(
            actor=reviewer.username,
            actor_role=reviewer.role.value,
            operation="PROPOSAL_REJECTED",
            result="REJECTED",
            reason=reason,
        )
        return record
