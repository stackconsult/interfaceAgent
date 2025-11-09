"""
Admin endpoints for user, role, and permission management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.models import User, Role, Permission
from app.api.deps import get_current_superuser
from app.core.security import get_password_hash
from app.services.audit import AuditLogger

router = APIRouter()


# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    
    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class PermissionCreate(BaseModel):
    resource: str
    action: str


class PermissionResponse(BaseModel):
    id: int
    role_id: int
    resource: str
    action: str
    
    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    role_id: int


# User endpoints
@router.get("/users/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """List all users (superuser only)."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create a new user (superuser only)."""
    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=user_data.is_active,
        is_superuser=user_data.is_superuser,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Audit log
    await AuditLogger.log_create(
        db=db,
        user_id=current_user.id,
        resource_type="user",
        resource_id=user.id,
        details={"username": user.username},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update a user (superuser only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    # Audit log
    await AuditLogger.log_update(
        db=db,
        user_id=current_user.id,
        resource_type="user",
        resource_id=user.id,
        details=update_data,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return user


@router.post("/users/{user_id}/roles", response_model=UserResponse)
async def assign_role_to_user(
    user_id: int,
    role_request: AssignRoleRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Assign a role to a user (superuser only)."""
    # Get user
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Get role
    result = await db.execute(select(Role).where(Role.id == role_request.role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    # Assign role
    if role not in user.roles:
        user.roles.append(role)
        await db.commit()
        await db.refresh(user)
    
    # Audit log
    await AuditLogger.log(
        db=db,
        user_id=current_user.id,
        action="assign_role",
        resource_type="user",
        resource_id=user.id,
        details={"role_id": role.id, "role_name": role.name},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return user


# Role endpoints
@router.get("/roles/", response_model=List[RoleResponse])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """List all roles (superuser only)."""
    result = await db.execute(select(Role).offset(skip).limit(limit))
    roles = result.scalars().all()
    return roles


@router.post("/roles/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create a new role (superuser only)."""
    # Check if role exists
    result = await db.execute(select(Role).where(Role.name == role_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists",
        )
    
    role = Role(
        name=role_data.name,
        description=role_data.description,
    )
    
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    # Audit log
    await AuditLogger.log_create(
        db=db,
        user_id=current_user.id,
        resource_type="role",
        resource_id=role.id,
        details={"name": role.name},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return role


@router.post("/roles/{role_id}/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def add_permission_to_role(
    role_id: int,
    permission_data: PermissionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Add a permission to a role (superuser only)."""
    # Check if role exists
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    # Create permission
    permission = Permission(
        role_id=role_id,
        resource=permission_data.resource,
        action=permission_data.action,
    )
    
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    
    # Audit log
    await AuditLogger.log_create(
        db=db,
        user_id=current_user.id,
        resource_type="permission",
        resource_id=permission.id,
        details={"role_id": role_id, "resource": permission.resource, "action": permission.action},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return permission


@router.get("/roles/{role_id}/permissions", response_model=List[PermissionResponse])
async def list_role_permissions(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """List permissions for a role (superuser only)."""
    result = await db.execute(select(Permission).where(Permission.role_id == role_id))
    permissions = result.scalars().all()
    return permissions
