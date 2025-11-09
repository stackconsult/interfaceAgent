"""
Event and Audit Log models.
"""

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Event(BaseModel):
    """Event model for event bus system."""

    __tablename__ = "event"

    event_type = Column(String(100), nullable=False, index=True)
    source = Column(String(100), nullable=False)
    payload = Column(JSON)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    retry_count = Column(Integer, default=0)
    processed_at = Column(DateTime)


class AuditLog(BaseModel):
    """Audit log model for tracking all system actions."""

    __tablename__ = "audit_log"

    user_id = Column(ForeignKey("user.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    status = Column(String(20), nullable=False)  # success, failure

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Anomaly(BaseModel):
    """Anomaly detection model."""

    __tablename__ = "anomaly"

    detection_type = Column(String(50), nullable=False)  # behavior, pattern, threshold
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    description = Column(String(500))
    data = Column(JSON)
    score = Column(Float)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(ForeignKey("user.id"))


class Escalation(BaseModel):
    """Escalation model for handling critical events."""

    __tablename__ = "escalation"

    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    status = Column(String(20), default="open")  # open, in_progress, resolved, closed
    assigned_to = Column(ForeignKey("user.id"))
    created_by = Column(ForeignKey("user.id"), nullable=False)
    related_resource_type = Column(String(50))
    related_resource_id = Column(Integer)
    resolution_notes = Column(String(2000))
    resolved_at = Column(DateTime)


class Plugin(BaseModel):
    """Plugin registry model."""

    __tablename__ = "plugin"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    version = Column(String(20), nullable=False)
    author = Column(String(100))
    module_path = Column(String(255), nullable=False)
    config_schema = Column(JSON)  # JSON schema for plugin configuration
    is_enabled = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    metadata = Column(JSON)
