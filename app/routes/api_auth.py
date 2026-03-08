# app/routes/api_auth.py
"""Authentication routes for user login, logout, and token management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, func
from pydantic import BaseModel

from app import crud, schemas
from app.database import get_db
from app.models import User
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    TokenResponse,
    refresh_access_token,
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request body"""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request body"""
    refresh_token: str


# ====== AUTH ENDPOINTS ======

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    
    **Note**: In production, you may want to:
    - Send email verification
    - Restrict registration (admin only)
    - Implement CAPTCHA
    """
    try:
        user = await crud.create_user(
            db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with username and password.
    
    Returns access token and refresh token.
    """
    # Get user by username
    user = await crud.get_user_by_username(db, request.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    # Update last login
    stmt = update(User).where(User.id == user.id).values(
        last_login=func.now()
    )
    await db.execute(stmt)
    await db.commit()
    
    # Create tokens
    access_token, access_expires = create_access_token(user.id)
    refresh_token, _ = create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": access_expires
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a new access token using a valid refresh token.
    
    Refresh tokens are valid for 7 days. Access tokens expire after 30 minutes.
    """
    try:
        new_access_token, expires_in = await refresh_access_token(request.refresh_token, db)
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": expires_in
        }
    except HTTPException as e:
        raise e


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Requires valid access token in Authorization header.
    
    Example:
        Authorization: Bearer <access_token>
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user.
    
    **Note**: JWT tokens cannot be invalidated server-side without 
    a token blacklist. Client should delete the token locally.
    
    In production with a blacklist:
    - Add token to blacklist in Redis/cache
    - Check blacklist on each request
    - Set TTL to match token expiration
    """
    return {
        "message": "Logged out successfully",
        "detail": "Please delete your tokens from client storage"
    }


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for current user.
    
    Verifies old password before allowing change.
    """
    # Verify old password
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # Hash new password
    hashed_new_password = hash_password(new_password)
    
    # Update password
    stmt = update(User).where(User.id == current_user.id).values(
        hashed_password=hashed_new_password
    )
    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/validate-token")
async def validate_token(
    current_user: User = Depends(get_current_user)
):
    """
    Validate current access token.
    
    Returns 200 with user info if valid, 401 if invalid.
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role
    }

@router.post("/seed-admin", status_code=status.HTTP_201_CREATED)
async def seed_admin(db: AsyncSession = Depends(get_db)):
    """
    Create a default admin account for development/testing.
    
    **WARNING**: This endpoint should ONLY be available in development!
    
    Creates:
    - Email: admin@clarity.local
    - Password: admin123
    - Role: admin
    """
    # Check if admin already exists
    existing_admin = await crud.get_user_by_email("admin@clarity.local", db)
    if existing_admin:
        return {
            "message": "Admin account already exists",
            "email": "admin@clarity.local"
        }
    
    # Create admin user
    admin_user = User(
        email="admin@clarity.local",
        username="admin",
        full_name="Admin User",
        password_hash=hash_password("admin123"),
        is_active=True,
        role="admin"
    )
    
    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)
    
    return {
        "message": "Admin account created successfully!",
        "email": "admin@clarity.local",
        "password": "admin123",
        "role": "admin"
    }