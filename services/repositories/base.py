"""
FinResolve AI — Database Repository Architecture

Abstract repository base and transaction boundary interfaces.
Decouples domain business logic from specific PostgreSQL / ORM implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Generic, TypeVar

T = TypeVar("T")


class TransactionContext(ABC):
    """Abstract interface for managing database transaction boundaries."""

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        pass


class BaseRepository(ABC, Generic[T]):
    """Abstract generic repository interface for CRUD operations."""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> T | None:
        """Fetch entity by its unique identifier."""
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Persist or update entity."""
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity by ID."""
        pass
