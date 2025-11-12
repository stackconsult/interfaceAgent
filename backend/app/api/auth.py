"""
Authentication endpoints.
"""


from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
    verify_token_type,
)
from app.models import User
from app.services.audit import AuditLogger

router = APIRouter()


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str = None
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Audit log
    await AuditLogger.log_create(
        db=db,
        user_id=user.id,
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )

    return user


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Login and get access token."""
    # Get user
    result = await db.execute(select(User).where(User.username == user_credentials.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        await AuditLogger.log_login(
            db=db,
            user_id=user.id if user else None,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            success=False,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Audit log
    await AuditLogger.log_login(
        db=db,
        user_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_token)
    verify_token_type(payload, "refresh")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
