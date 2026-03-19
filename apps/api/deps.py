from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .db import get_db


async def get_request_context(
    x_tenant_id: int | None = Header(default=None, alias="X-Tenant-Id"),
    x_role: str | None = Header(default=None, alias="X-User-Role"),
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> schemas.RequestContext:
    """
    Resolve a minimal request context (tenant, role, optional user) from headers.

    For MVP we accept tenant/role/user via headers.
    """
    # If a concrete user id is provided, derive tenant and role from the user record.
    if x_user_id is not None:
        user = db.get(models.User, x_user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not found or inactive",
            )
        tenant = db.get(models.Tenant, user.tenant_id)
        if tenant is None or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant not found or inactive",
            )
        return schemas.RequestContext(
            tenant_id=tenant.id,
            role=user.role,
            user_id=user.id,
        )

    # Fallback: old behaviour based on X-Tenant-Id and X-User-Role.
    if x_tenant_id is None or x_role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Tenant-Id or X-User-Role header",
        )

    tenant = db.get(models.Tenant, x_tenant_id)
    if tenant is None or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant not found or inactive",
        )

    try:
        role = schemas.UserRole(x_role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role",
        )

    return schemas.RequestContext(tenant_id=tenant.id, role=role, user_id=None)


def require_internal_actor(ctx: schemas.RequestContext = Depends(get_request_context)):
    """
    Require a role allowed to access funder/internal analysis endpoints.
    """
    if ctx.role not in (schemas.UserRole.ADMIN, schemas.UserRole.ANALYST):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Internal analysis requires admin or analyst role",
        )
    return ctx


def require_public_view(ctx: schemas.RequestContext = Depends(get_request_context)):
    """
    Public understanding endpoints accept all roles but still enforce tenant binding.
    """
    return ctx

