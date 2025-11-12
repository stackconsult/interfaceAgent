"""
Audit log endpoints.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RBACChecker
from app.core.database import get_db
from app.models import AuditLog, User

router = APIRouter()


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[int]
    details: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AuditLogResponse])
async def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("audit_log", "read")),
):
    """List audit logs with optional filters."""
    query = select(AuditLog)

    # Apply filters
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if status:
        query = query.where(AuditLog.status == status)

    # Order by creation date descending
    query = query.order_by(AuditLog.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()
    return logs


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("audit_log", "read")),
):
    """Get a specific audit log entry."""
    result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return log


@router.get("/actions/list")
async def list_actions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("audit_log", "read")),
):
    """List all unique actions recorded in audit logs."""
    from sqlalchemy import distinct

    result = await db.execute(select(distinct(AuditLog.action)))
    actions = [row[0] for row in result.all()]
    return {"actions": actions}


@router.get("/resource-types/list")
async def list_resource_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("audit_log", "read")),
):
    """List all unique resource types recorded in audit logs."""
    from sqlalchemy import distinct

    result = await db.execute(select(distinct(AuditLog.resource_type)))
    resource_types = [row[0] for row in result.all()]
    return {"resource_types": resource_types}
