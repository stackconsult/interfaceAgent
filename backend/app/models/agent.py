"""
Agent and Pipeline models.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, JSON, Enum as SQLEnum, Integer, DateTime
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class AgentStatus(str, enum.Enum):
    """Agent status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AgentType(str, enum.Enum):
    """Agent type enumeration."""
    VALIDATOR = "validator"
    ANALYZER = "analyzer"
    ENRICHER = "enricher"
    TRANSFORMER = "transformer"
    CUSTOM = "custom"


class Agent(BaseModel):
    """Agent model for modular agent system."""
    
    __tablename__ = "agent"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    agent_type = Column(SQLEnum(AgentType), nullable=False)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.INACTIVE, nullable=False)
    config = Column(JSON, default={})  # Agent-specific configuration
    version = Column(String(20), default="1.0.0")
    is_plugin = Column(Boolean, default=False)
    plugin_module = Column(String(255))  # Module path for plugin agents
    
    # Relationships
    pipeline_steps = relationship("PipelineStep", back_populates="agent")


class PipelineStatus(str, enum.Enum):
    """Pipeline status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Pipeline(BaseModel):
    """Pipeline model for orchestrating agents."""
    
    __tablename__ = "pipeline"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    status = Column(SQLEnum(PipelineStatus), default=PipelineStatus.DRAFT, nullable=False)
    config = Column(JSON, default={})
    
    # Relationships
    steps = relationship("PipelineStep", back_populates="pipeline", order_by="PipelineStep.order")
    executions = relationship("PipelineExecution", back_populates="pipeline")


class PipelineStep(BaseModel):
    """Pipeline step linking agents to pipelines."""
    
    __tablename__ = "pipeline_step"
    
    pipeline_id = Column(ForeignKey("pipeline.id"), nullable=False)
    agent_id = Column(ForeignKey("agent.id"), nullable=False)
    order = Column(Integer, nullable=False)
    config = Column(JSON, default={})  # Step-specific configuration
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="steps")
    agent = relationship("Agent", back_populates="pipeline_steps")


class ExecutionStatus(str, enum.Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineExecution(BaseModel):
    """Pipeline execution tracking."""
    
    __tablename__ = "pipeline_execution"
    
    pipeline_id = Column(ForeignKey("pipeline.id"), nullable=False)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(String(1000))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="executions")
