"""
FinResolve AI — Append-Only Audit Logging Architecture

Records immutable, cryptographically chained audit records for all critical financial operations.
"""

from __future__ import annotations

import hashlib
import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """Immutable audit record representing an action performed in FinResolve AI."""
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor: str
    actor_role: str
    request_id: str = "unknown"
    case_id: str | None = None
    operation: str
    result: Literal["SUCCESS", "FAILURE", "REJECTED", "DISCREPANCY_DETECTED"]
    reason: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    policy_decision: dict[str, Any] | None = None
    prev_event_hash: str = "GENESIS"
    event_hash: str = ""

    model_config = {"frozen": True}


class AuditLogger:
    """
    Thread-safe append-only audit logger with cryptographic SHA-256 chaining.
    In production, records stream to PostgreSQL immutable append-only tables or AWS QLDB/S3 Glacier.
    """

    def __init__(self):
        self._events: list[AuditEvent] = []
        self._lock = threading.Lock()
        self._last_hash = "GENESIS"

    def _compute_hash(self, event_dict: dict[str, Any], prev_hash: str) -> str:
        payload = dict(event_dict)
        payload.pop("event_hash", None)
        canonical = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(f"{prev_hash}:{canonical}".encode("utf-8")).hexdigest()

    def record_event(
        self,
        actor: str,
        actor_role: str,
        operation: str,
        result: Literal["SUCCESS", "FAILURE", "REJECTED", "DISCREPANCY_DETECTED"],
        request_id: str = "unknown",
        case_id: str | None = None,
        reason: str | None = None,
        evidence_refs: list[str] | None = None,
        policy_decision: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Append an immutable audit event to the cryptographic chain."""
        with self._lock:
            temp_event = AuditEvent(
                actor=actor,
                actor_role=actor_role,
                request_id=request_id,
                case_id=case_id,
                operation=operation,
                result=result,
                reason=reason,
                evidence_refs=evidence_refs or [],
                policy_decision=policy_decision,
                prev_event_hash=self._last_hash,
                event_hash="",
            )

            # Compute hash with current previous hash
            event_hash = self._compute_hash(temp_event.model_dump(), self._last_hash)
            
            # Construct finalized frozen event with hash
            final_event = AuditEvent(
                event_id=temp_event.event_id,
                timestamp=temp_event.timestamp,
                actor=temp_event.actor,
                actor_role=temp_event.actor_role,
                request_id=temp_event.request_id,
                case_id=temp_event.case_id,
                operation=temp_event.operation,
                result=temp_event.result,
                reason=temp_event.reason,
                evidence_refs=temp_event.evidence_refs,
                policy_decision=temp_event.policy_decision,
                prev_event_hash=self._last_hash,
                event_hash=event_hash,
            )

            self._events.append(final_event)
            self._last_hash = event_hash
            return final_event

    def get_events(self, case_id: str | None = None) -> list[AuditEvent]:
        """Retrieve audit history, optionally filtered by case_id."""
        with self._lock:
            if case_id:
                return [e for e in self._events if e.case_id == case_id]
            return list(self._events)

    def verify_integrity(self) -> bool:
        """
        Verify that the audit log has not been tampered with or modified.
        Returns True if the entire cryptographic hash chain is valid.
        """
        with self._lock:
            current_prev = "GENESIS"
            for event in self._events:
                if event.prev_event_hash != current_prev:
                    return False
                expected_hash = self._compute_hash(event.model_dump(), current_prev)
                if event.event_hash != expected_hash:
                    return False
                current_prev = event.event_hash
            return True

    def reset(self) -> None:
        """Reset audit log (useful in unit tests)."""
        with self._lock:
            self._events.clear()
            self._last_hash = "GENESIS"


# Global audit logger instance
global_audit_logger = AuditLogger()
