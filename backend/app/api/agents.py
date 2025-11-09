"""
Agent management endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.models import Agent, AgentType, AgentStatus, User
from app.api.deps import get_current_user, RBACChecker
from app.services.audit import AuditLogger
from app.agents.registry import agent_registry

router = APIRouter()


class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    agent_type: AgentType
    config: dict = {}
    version: str = "1.0.0"


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AgentStatus] = None
    config: Optional[dict] = None


class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    agent_type: AgentType
    status: AgentStatus
    config: dict
    version: str
    is_plugin: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("agent", "read")),
):
    """List all agents."""
    result = await db.execute(select(Agent).offset(skip).limit(limit))
    agents = result.scalars().all()
    return agents


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("agent", "create")),
):
    """Create a new agent."""
    # Check if agent with same name exists
    result = await db.execute(select(Agent).where(Agent.name == agent_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent with this name already exists",
        )
    
    # Create agent
    agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
        agent_type=agent_data.agent_type,
        config=agent_data.config,
        version=agent_data.version,
        status=AgentStatus.INACTIVE,
    )
    
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    
    # Audit log
    await AuditLogger.log_create(
        db=db,
        user_id=current_user.id,
        resource_type="agent",
        resource_id=agent.id,
        details={"name": agent.name, "type": agent.agent_type.value},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return agent


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("agent", "read")),
):
    """Get an agent by ID."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("agent", "update")),
):
    """Update an agent."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Update fields
    update_data = agent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    await db.commit()
    await db.refresh(agent)
    
    # Audit log
    await AuditLogger.log_update(
        db=db,
        user_id=current_user.id,
        resource_type="agent",
        resource_id=agent.id,
        details=update_data,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("agent", "delete")),
):
    """Delete an agent."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Audit log before deletion
    await AuditLogger.log_delete(
        db=db,
        user_id=current_user.id,
        resource_type="agent",
        resource_id=agent.id,
        details={"name": agent.name},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    await db.delete(agent)
    await db.commit()
    
    return None


@router.post("/{agent_id}/activate", response_model=AgentResponse)
async def activate_agent(
    agent_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("agent", "update")),
):
    """Activate an agent."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    agent.status = AgentStatus.ACTIVE
    await db.commit()
    await db.refresh(agent)
    
    # Audit log
    await AuditLogger.log_update(
        db=db,
        user_id=current_user.id,
        resource_type="agent",
        resource_id=agent.id,
        details={"action": "activate"},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return agent


@router.post("/{agent_id}/deactivate", response_model=AgentResponse)
async def deactivate_agent(
    agent_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RBACChecker("agent", "update")),
):
    """Deactivate an agent."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    agent.status = AgentStatus.INACTIVE
    await db.commit()
    await db.refresh(agent)
    
    # Audit log
    await AuditLogger.log_update(
        db=db,
        user_id=current_user.id,
        resource_type="agent",
        resource_id=agent.id,
        details={"action": "deactivate"},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return agent


@router.get("/registry/list")
async def list_available_agents(
    current_user: User = Depends(get_current_user),
):
    """List all available agent types from registry."""
    return {
        "agents": agent_registry.list_agents(),
    }
