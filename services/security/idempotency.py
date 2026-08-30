"""
FinResolve AI — Idempotency & Concurrency Framework

Guarantees safe at-most-once execution for financial operations and simulated resolutions.
Detects concurrent duplicate submissions and payload hash mismatches.
"""

from __future__ import annotations

import hashlib
import json
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class IdempotencyRecord(BaseModel):
    """Represents the execution state of an idempotent operation."""
    idempotency_key: str
    request_hash: str
    operation: str
    status: Literal["PROCESSING", "COMPLETED", "FAILED"]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    response_payload: dict[str, Any] | None = None
    error_message: str | None = None


class IdempotencyStore(ABC):
    """Abstract store for managing idempotency locks and cached responses."""

    @abstractmethod
    def acquire(
        self,
        key: str,
        request_data: Any,
        operation: str,
    ) -> tuple[Literal["NEW", "CACHED", "CONFLICT", "IN_FLIGHT"], IdempotencyRecord | None]:
        """Attempt to acquire execution rights for an idempotency key."""
        pass

    @abstractmethod
    def complete(self, key: str, response_payload: dict[str, Any]) -> None:
        """Mark operation as completed and store response payload."""
        pass

    @abstractmethod
    def fail(self, key: str, error_message: str) -> None:
        """Mark operation as failed."""
        pass


class InMemoryIdempotencyStore(IdempotencyStore):
    """
    Thread-safe in-memory idempotency store.
    In production, this interface is backed by PostgreSQL with SELECT FOR UPDATE or Redis.
    """

    def __init__(self):
        self._store: dict[str, IdempotencyRecord] = {}
        self._lock = threading.Lock()

    @staticmethod
    def compute_hash(data: Any) -> str:
        """Compute deterministic SHA-256 hash of request payload."""
        if isinstance(data, (dict, list)):
            canonical_json = json.dumps(data, sort_keys=True, default=str)
        else:
            canonical_json = str(data)
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def acquire(
        self,
        key: str,
        request_data: Any,
        operation: str,
    ) -> tuple[Literal["NEW", "CACHED", "CONFLICT", "IN_FLIGHT"], IdempotencyRecord | None]:
        req_hash = self.compute_hash(request_data)

        with self._lock:
            if key in self._store:
                existing = self._store[key]

                # Check for hash mismatch on identical key (payload conflict)
                if existing.request_hash != req_hash:
                    return "CONFLICT", existing

                # Check if already finished
                if existing.status == "COMPLETED":
                    return "CACHED", existing

                # Currently being processed by another worker/thread
                if existing.status == "PROCESSING":
                    return "IN_FLIGHT", existing

            # First time seeing this key -> acquire lock
            record = IdempotencyRecord(
                idempotency_key=key,
                request_hash=req_hash,
                operation=operation,
                status="PROCESSING",
            )
            self._store[key] = record
            return "NEW", record

    def complete(self, key: str, response_payload: dict[str, Any]) -> None:
        with self._lock:
            if key in self._store:
                record = self._store[key]
                record.status = "COMPLETED"
                record.completed_at = datetime.now(timezone.utc)
                record.response_payload = response_payload

    def fail(self, key: str, error_message: str) -> None:
        with self._lock:
            if key in self._store:
                record = self._store[key]
                record.status = "FAILED"
                record.completed_at = datetime.now(timezone.utc)
                record.error_message = error_message

    def reset(self) -> None:
        """Reset store (useful in unit tests)."""
        with self._lock:
            self._store.clear()
