"""
FinResolve AI — Reconciliation Case Repository

Repository interface and thread-safe implementation for storing and querying cases.
Enforces identifier validation to protect against SQL/NoSQL injection.
"""

from __future__ import annotations

import re
import threading
from abc import ABC, abstractmethod
from typing import Any

from data.schemas.case import ReconciliationCase
from services.repositories.base import BaseRepository

# Strict alphanumeric identifier pattern (letters, numbers, hyphens, underscores)
SAFE_ID_REGEX = re.compile(r"^[a-zA-Z0-9_\-]+$")


def validate_identifier(ident: str, field_name: str = "identifier") -> str:
    """Ensure identifier does not contain SQL injection or control characters."""
    if not ident or not SAFE_ID_REGEX.match(ident):
        raise ValueError(f"Invalid {field_name}: '{ident}'. Identifiers must be alphanumeric with dashes/underscores.")
    return ident


class CaseRepository(BaseRepository[ReconciliationCase]):
    """Abstract repository for ReconciliationCase entities."""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> ReconciliationCase | None:
        pass

    @abstractmethod
    async def save(self, entity: ReconciliationCase) -> ReconciliationCase:
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        pass

    @abstractmethod
    async def list_by_merchant(self, merchant_id: str, limit: int = 50, offset: int = 0) -> list[ReconciliationCase]:
        pass


class InMemoryCaseRepository(CaseRepository):
    """
    Thread-safe in-memory case repository.
    In production, this interface is backed by PostgreSQL with SQLAlchemy/asyncpg.
    """

    def __init__(self):
        self._cases: dict[str, ReconciliationCase] = {}
        self._lock = threading.Lock()

    async def get_by_id(self, entity_id: str) -> ReconciliationCase | None:
        valid_id = validate_identifier(entity_id, "case_id")
        with self._lock:
            return self._cases.get(valid_id)

    async def save(self, entity: ReconciliationCase) -> ReconciliationCase:
        valid_id = validate_identifier(entity.case_id, "case_id")
        with self._lock:
            self._cases[valid_id] = entity
            return entity

    async def delete(self, entity_id: str) -> bool:
        valid_id = validate_identifier(entity_id, "case_id")
        with self._lock:
            return self._cases.pop(valid_id, None) is not None

    async def list_by_merchant(self, merchant_id: str, limit: int = 50, offset: int = 0) -> list[ReconciliationCase]:
        valid_merchant = validate_identifier(merchant_id, "merchant_id")
        with self._lock:
            filtered = [c for c in self._cases.values() if c.merchant_id == valid_merchant]
            return filtered[offset : offset + limit]

    def reset(self) -> None:
        """Reset repository store (useful in tests)."""
        with self._lock:
            self._cases.clear()
