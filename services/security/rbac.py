"""
FinResolve AI — Role-Based Access Control (RBAC)

Deterministic permission mapping and authorization checks.
"""

from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, Header, status

from services.security.auth import (
    AnonymousUser,
    AuthenticatedUser,
    DevBearerAuthProvider,
    Permission,
    Role,
)

ROLE_PERMISSIONS_MAP: dict[Role, set[Permission]] = {
    Role.VIEWER: {
        Permission.CASE_VIEW,
        Permission.EVIDENCE_VIEW,
    },
    Role.ANALYST: {
        Permission.CASE_VIEW,
        Permission.EVIDENCE_VIEW,
        Permission.EVALUATION_RUN,
        Permission.ACTION_PROPOSE,
    },
    Role.APPROVER: {
        Permission.CASE_VIEW,
        Permission.EVIDENCE_VIEW,
        Permission.ACTION_APPROVE,
    },
    Role.ADMIN: {
        Permission.CASE_VIEW,
        Permission.EVIDENCE_VIEW,
        Permission.EVALUATION_RUN,
        Permission.ACTION_PROPOSE,
        Permission.ACTION_APPROVE,
        Permission.ADMIN_ALL,
    },
    Role.SERVICE: {
        Permission.CASE_VIEW,
        Permission.EVIDENCE_VIEW,
        Permission.EVALUATION_RUN,
    },
}


def get_permissions_for_role(role: Role) -> set[Permission]:
    """Retrieve granted permissions for a given role."""
    return set(ROLE_PERMISSIONS_MAP.get(role, set()))


def check_permission(user: AuthenticatedUser, permission: Permission) -> bool:
    """Evaluate whether user possesses the required permission."""
    if not user.is_authenticated:
        return False
    if Permission.ADMIN_ALL in user.permissions:
        return True
    return permission in user.permissions


# Global default auth provider instance
_default_auth_provider = DevBearerAuthProvider(allow_anonymous_when_disabled=True)


def get_current_user(authorization: str | None = Header(None)) -> AuthenticatedUser:
    """FastAPI dependency to extract and authenticate current user from header."""
    try:
        return _default_auth_provider.authenticate_token(authorization)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permission(permission: Permission) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    """FastAPI dependency factory enforcing a specific permission."""
    def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if not user.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not check_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Missing required permission '{permission.value}'",
            )
        return user
    return dependency


def require_role(allowed_roles: list[Role]) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    """FastAPI dependency factory enforcing specified roles."""
    def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if not user.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        if user.role not in allowed_roles and user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: User role '{user.role.value}' not authorized",
            )
        return user
    return dependency
