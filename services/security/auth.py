"""
FinResolve AI — Authentication Architecture

Defines abstract AuthProvider interfaces and authentication models.
Distinguishes authenticated vs unauthenticated contexts with safe development defaults.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Role(str, Enum):
    """System roles for Role-Based Access Control."""
    VIEWER = "VIEWER"
    ANALYST = "ANALYST"
    APPROVER = "APPROVER"
    ADMIN = "ADMIN"
    SERVICE = "SERVICE"


class Permission(str, Enum):
    """Granular permissions for FinResolve operations."""
    CASE_VIEW = "case:view"
    EVIDENCE_VIEW = "evidence:view"
    EVALUATION_RUN = "evaluation:run"
    ACTION_PROPOSE = "action:propose"
    ACTION_APPROVE = "action:approve"
    ADMIN_ALL = "admin:all"


class AuthenticatedUser(BaseModel):
    """Model representing an authenticated principal."""
    user_id: str
    username: str
    role: Role
    permissions: set[Permission] = Field(default_factory=set)
    is_authenticated: bool = True

    model_config = {"frozen": True}


class AnonymousUser(AuthenticatedUser):
    """Model representing an unauthenticated guest principal."""
    def __init__(self):
        super().__init__(
            user_id="anonymous",
            username="anonymous",
            role=Role.VIEWER,
            permissions=set(),
            is_authenticated=False,
        )


class AuthProvider(ABC):
    """Abstract interface for authenticating credentials into an AuthenticatedUser."""

    @abstractmethod
    def authenticate_token(self, token: str | None) -> AuthenticatedUser:
        """Authenticate a token (e.g. Bearer JWT or API Key)."""
        pass


class DevBearerAuthProvider(AuthProvider):
    """
    Development-mode auth provider supporting static test tokens and basic JWT-like structures.
    In production, this interface is replaced by an OIDC / OAuth2 / IdP provider.
    """

    # Static token mappings for development and testing
    STATIC_TOKENS: dict[str, tuple[str, str, Role]] = {
        "dev-token-viewer": ("usr_viewer_01", "viewer_user", Role.VIEWER),
        "dev-token-analyst": ("usr_analyst_01", "analyst_user", Role.ANALYST),
        "dev-token-approver": ("usr_approver_01", "approver_user", Role.APPROVER),
        "dev-token-admin": ("usr_admin_01", "admin_user", Role.ADMIN),
        "dev-token-service": ("svc_recon_01", "reconciliation_service", Role.SERVICE),
    }

    def __init__(self, secret_key: str = "dev-secret", allow_anonymous_when_disabled: bool = True):
        self.secret_key = secret_key
        self.allow_anonymous = allow_anonymous_when_disabled

    def authenticate_token(self, token: str | None) -> AuthenticatedUser:
        from services.security.rbac import get_permissions_for_role

        if not token:
            if self.allow_anonymous:
                return AnonymousUser()
            raise PermissionError("Missing authentication credentials")

        # Strip Bearer prefix if present
        clean_token = token.replace("Bearer ", "").strip()

        if clean_token in self.STATIC_TOKENS:
            user_id, username, role = self.STATIC_TOKENS[clean_token]
            perms = get_permissions_for_role(role)
            return AuthenticatedUser(
                user_id=user_id,
                username=username,
                role=role,
                permissions=perms,
                is_authenticated=True,
            )

        raise PermissionError("Invalid authentication token")
