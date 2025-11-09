"""
Audit logging service.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import AuditLog

settings = get_settings()


class AuditLogger:
    """Service for recording audit logs."""

    @staticmethod
    async def log(
        db: AsyncSession,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
    ) -> AuditLog:
        """Create an audit log entry."""
        if not settings.enable_audit_log:
            return None

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
        )

        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)

        return audit_log

    @staticmethod
    async def log_login(
        db: AsyncSession,
        user_id: int,
        ip_address: str,
        user_agent: str,
        success: bool = True,
    ):
        """Log a login attempt."""
        await AuditLogger.log(
            db=db,
            user_id=user_id,
            action="login",
            resource_type="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            status="success" if success else "failure",
        )

    @staticmethod
    async def log_logout(
        db: AsyncSession,
        user_id: int,
        ip_address: str,
        user_agent: str,
    ):
        """Log a logout."""
        await AuditLogger.log(
            db=db,
            user_id=user_id,
            action="logout",
            resource_type="auth",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    async def log_create(
        db: AsyncSession,
        user_id: int,
        resource_type: str,
        resource_id: int,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Log a resource creation."""
        await AuditLogger.log(
            db=db,
            user_id=user_id,
            action="create",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    async def log_update(
        db: AsyncSession,
        user_id: int,
        resource_type: str,
        resource_id: int,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Log a resource update."""
        await AuditLogger.log(
            db=db,
            user_id=user_id,
            action="update",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    async def log_delete(
        db: AsyncSession,
        user_id: int,
        resource_type: str,
        resource_id: int,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Log a resource deletion."""
        await AuditLogger.log(
            db=db,
            user_id=user_id,
            action="delete",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
