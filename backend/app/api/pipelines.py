"""
Pipeline management endpoints.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import RBACChecker, get_current_user
from app.core.database import get_db
from app.models import (
    Agent,
    ExecutionStatus,
    Pipeline,
    PipelineExecution,
    PipelineStatus,
    PipelineStep,
    User,
)
from app.services.audit import AuditLogger

router = APIRouter()


class PipelineStepCreate(BaseModel):
    agent_id: int
    order: int
    config: dict = {}


class PipelineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    config: dict = {}


class PipelineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PipelineStatus] = None
    config: Optional[dict] = None


class PipelineStepResponse(BaseModel):
    id: int
    agent_id: int
    order: int
    config: dict

    class Config:
        from_attributes = True


class PipelineResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: PipelineStatus
    config: dict
    steps: List[PipelineStepResponse] = []

    class Config:
        from_attributes = True


class PipelineExecuteRequest(BaseModel):
    input_data: dict


class PipelineExecutionResponse(BaseModel):
    id: int
    pipeline_id: int
    status: ExecutionStatus
    input_data: Optional[dict]
    output_data: Optional[dict]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PipelineResponse])
async def list_pipelines(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("pipeline", "read")),
):
    """List all pipelines."""
    result = await db.execute(
        select(Pipeline).options(selectinload(Pipeline.steps)).offset(skip).limit(limit)
    )
    pipelines = result.scalars().all()
    return pipelines


@router.post("/", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline_data: PipelineCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("pipeline", "create")),
):
    """Create a new pipeline."""
    # Check if pipeline with same name exists
    result = await db.execute(select(Pipeline).where(Pipeline.name == pipeline_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline with this name already exists",
        )

    # Create pipeline
    pipeline = Pipeline(
        name=pipeline_data.name,
        description=pipeline_data.description,
        config=pipeline_data.config,
        status=PipelineStatus.DRAFT,
    )

    db.add(pipeline)
    await db.commit()
    await db.refresh(pipeline)

    # Audit log
    await AuditLogger.log_create(
        db=db,
        user_id=current_user.id,
        resource_type="pipeline",
        resource_id=pipeline.id,
        details={"name": pipeline.name},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )

    return pipeline


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("pipeline", "read")),
):
    """Get a pipeline by ID."""
    result = await db.execute(
        select(Pipeline).options(selectinload(Pipeline.steps)).where(Pipeline.id == pipeline_id)
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found",
        )

    return pipeline


@router.put("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: int,
    pipeline_data: PipelineUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("pipeline", "update")),
):
    """Update a pipeline."""
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found",
        )

    # Update fields
    update_data = pipeline_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pipeline, field, value)

    await db.commit()
    await db.refresh(pipeline)

    # Audit log
    await AuditLogger.log_update(
        db=db,
        user_id=current_user.id,
        resource_type="pipeline",
        resource_id=pipeline.id,
        details=update_data,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )

    return pipeline


@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("pipeline", "delete")),
):
    """Delete a pipeline."""
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found",
        )

    # Audit log before deletion
    await AuditLogger.log_delete(
        db=db,
        user_id=current_user.id,
        resource_type="pipeline",
        resource_id=pipeline.id,
        details={"name": pipeline.name},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )

    await db.delete(pipeline)
    await db.commit()

    return None


@router.post(
    "/{pipeline_id}/steps", response_model=PipelineStepResponse, status_code=status.HTTP_201_CREATED
)
async def add_pipeline_step(
    pipeline_id: int,
    step_data: PipelineStepCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("pipeline", "update")),
):
    """Add a step to a pipeline."""
    # Verify pipeline exists
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalar_one_or_none()
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found",
        )

    # Verify agent exists
    result = await db.execute(select(Agent).where(Agent.id == step_data.agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Create step
    step = PipelineStep(
        pipeline_id=pipeline_id,
        agent_id=step_data.agent_id,
        order=step_data.order,
        config=step_data.config,
    )

    db.add(step)
    await db.commit()
    await db.refresh(step)

    return step


@router.post("/{pipeline_id}/execute", response_model=PipelineExecutionResponse)
async def execute_pipeline(
    pipeline_id: int,
    execution_data: PipelineExecuteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("pipeline", "execute")),
):
    """Execute a pipeline."""
    # Get pipeline with steps
    result = await db.execute(
        select(Pipeline).options(selectinload(Pipeline.steps)).where(Pipeline.id == pipeline_id)
    )
    pipeline = result.scalar_one_or_none()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found",
        )

    if pipeline.status != PipelineStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline is not active",
        )

    # Create execution record
    execution = PipelineExecution(
        pipeline_id=pipeline_id,
        status=ExecutionStatus.PENDING,
        input_data=execution_data.input_data,
        started_at=datetime.utcnow(),
    )

    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    # TODO: Execute pipeline steps asynchronously via Celery
    # For now, we'll just mark it as pending

    # Audit log
    await AuditLogger.log(
        db=db,
        user_id=current_user.id,
        action="execute",
        resource_type="pipeline",
        resource_id=pipeline_id,
        details={"execution_id": execution.id},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )

    return execution


@router.get("/{pipeline_id}/executions", response_model=List[PipelineExecutionResponse])
async def list_pipeline_executions(
    pipeline_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("pipeline", "read")),
):
    """List executions for a pipeline."""
    result = await db.execute(
        select(PipelineExecution)
        .where(PipelineExecution.pipeline_id == pipeline_id)
        .offset(skip)
        .limit(limit)
        .order_by(PipelineExecution.created_at.desc())
    )
    executions = result.scalars().all()
    return executions
