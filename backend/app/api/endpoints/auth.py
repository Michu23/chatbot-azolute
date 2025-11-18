from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    create_password_reset_token,
    verify_password_reset_token,
    create_email_verification_token,
    verify_email_verification_token,
)
from app.models.user import User, RefreshToken
from app.schemas.user import UserCreate, UserLogin, PasswordReset, PasswordResetRequest, EmailVerification
from app.schemas.auth import AuthResponse, RefreshTokenRequest
from app.core.config import settings
from app.services.email import send_verification_email, send_password_reset_email

router = APIRouter()


@router.post("/signup", response_model=AuthResponse)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user"""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_verified=False,  # Require email verification
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Send verification email
    verification_token = create_email_verification_token(new_user.email)
    await send_verification_email(new_user.email, verification_token)

    # Create tokens
    access_token = create_access_token(subject=str(new_user.id))
    refresh_token_str = create_refresh_token(subject=str(new_user.id))

    # Store refresh token
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_obj = RefreshToken(
        token=refresh_token_str,
        user_id=new_user.id,
        expires_at=expires_at,
    )
    db.add(refresh_token_obj)
    await db.commit()

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        user=new_user,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login user"""
    # Get user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token_str = create_refresh_token(subject=str(user.id))

    # Store refresh token
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_obj = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=expires_at,
    )
    db.add(refresh_token_obj)
    await db.commit()

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        user=user,
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token"""
    # Verify refresh token exists in database
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token_data.refresh_token)
    )
    refresh_token_obj = result.scalar_one_or_none()

    if not refresh_token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Check if token is expired
    if refresh_token_obj.expires_at < datetime.utcnow():
        await db.delete(refresh_token_obj)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    # Get user
    result = await db.execute(
        select(User).where(User.id == refresh_token_obj.user_id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    access_token = create_access_token(subject=str(user.id))
    new_refresh_token_str = create_refresh_token(subject=str(user.id))

    # Delete old refresh token and create new one
    await db.delete(refresh_token_obj)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token_obj = RefreshToken(
        token=new_refresh_token_str,
        user_id=user.id,
        expires_at=expires_at,
    )
    db.add(new_refresh_token_obj)
    await db.commit()

    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token_str,
        user=user,
    )


@router.post("/verify-email")
async def verify_email(
    verification: EmailVerification,
    db: AsyncSession = Depends(get_db),
):
    """Verify user email"""
    email = verify_email_verification_token(verification.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    # Get user and verify email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_verified = True
    await db.commit()

    return {"message": "Email verified successfully"}


@router.post("/request-password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request password reset"""
    # Get user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if user:
        reset_token = create_password_reset_token(user.email)
        await send_password_reset_email(user.email, reset_token)

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db),
):
    """Reset password"""
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Get user and update password
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.hashed_password = get_password_hash(reset_data.new_password)
    await db.commit()

    return {"message": "Password reset successfully"}
