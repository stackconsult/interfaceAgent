"""
User and RBAC models.
"""

from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)


class User(BaseModel):
    """User model for authentication and authorization."""

    __tablename__ = "user"

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")


class Role(BaseModel):
    """Role model for RBAC."""

    __tablename__ = "role"

    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255))

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", back_populates="role")


class Permission(BaseModel):
    """Permission model for fine-grained access control."""

    __tablename__ = "permission"

    role_id = Column(ForeignKey("role.id"), nullable=False)
    resource = Column(String(50), nullable=False)  # e.g., "agent", "pipeline", "audit_log"
    action = Column(String(50), nullable=False)  # e.g., "create", "read", "update", "delete"

    # Relationships
    role = relationship("Role", back_populates="permissions")
