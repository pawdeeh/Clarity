# app/auth.py
"""
Authentication module for Clarity.
Handles JWT token creation/validation, password hashing, and user verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import os

from app.database import get_db
from app.models import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer security scheme
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


# ====== Data Models ======

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds until expiry


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: int  # user_id
    exp: datetime
    iat: datetime
    type: str = "access"  # access or refresh


# ====== Password Functions ======

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Args:
        password: Plaintext password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its hashed version.
    
    Args:
        plain_password: Plaintext password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ====== Token Functions ======

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> tuple[str, int]:
    """
    Create a JWT access token.
    
    Args:
        user_id: User ID to encode in token
        expires_delta: Optional custom expiration time
        
    Returns:
        Tuple of (token, expires_in_seconds)
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),  # JWT subject must be a string
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    expires_in = int((expire - datetime.now(timezone.utc)).total_seconds())
    
    return encoded_jwt, expires_in


def create_refresh_token(user_id: int) -> tuple[str, int]:
    """
    Create a JWT refresh token (longer expiration).
    
    Args:
        user_id: User ID to encode in token
        
    Returns:
        Tuple of (token, expires_in_seconds)
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(user_id),  # JWT subject must be a string
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    expires_in = int((expire - datetime.now(timezone.utc)).total_seconds())
    
    return encoded_jwt, expires_in


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Token payload dictionary
        
    Raises:
        JWTError: If token is invalid or expired
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# ====== FastAPI Dependencies ======

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get the currently authenticated user from token.
    
    Use in route handlers: 
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    
    Raises:
        HTTPException: 401 Unauthorized if token is invalid or missing
        HTTPException: 404 Not Found if user not in database
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id: int = int(payload.get("sub"))  # Convert sub from string to int
        token_type: str = payload.get("type", "access")
        
        # Only accept access tokens in this flow
        if token_type != "access":
            raise credentials_exception
            
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Import here to avoid circular imports
    from app import crud
    
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user


def require_role(required_role: str):
    """
    FastAPI dependency to check if user has required role.
    
    Usage:
        admin_check = require_role("admin")
        
        @router.delete("/users/{id}")
        async def delete_user(
            user_id: int,
            current_user: User = Depends(admin_check),
            db: AsyncSession = Depends(get_db)
        ):
            # Only admins can reach here
            pass
    
    Raises:
        HTTPException: 403 Forbidden if user lacks required role
    """
    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        role_hierarchy = {"admin": 3, "editor": 2, "reviewer": 1, "viewer": 0}
        
        if role_hierarchy.get(current_user.role, -1) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires '{required_role}' role"
            )
        return current_user
    
    return check_role


def requires_at_least_role(min_role: str):
    """
    FastAPI dependency similar to require_role but more flexible naming.
    
    Roles (by hierarchy): admin > editor > reviewer > viewer
    """
    return require_role(min_role)


# ====== Token Refresh ======

async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> tuple[str, int]:
    """
    Get a new access token using a valid refresh token.
    
    Args:
        refresh_token: Valid refresh token
        db: Database session
        
    Returns:
        Tuple of (new_access_token, expires_in_seconds)
        
    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(refresh_token)
        user_id: int = int(payload.get("sub"))  # Convert sub from string to int
        token_type: str = payload.get("type")
        
        if token_type != "refresh" or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Verify user still exists and is active
    from app import crud
    user = await crud.get_user(db, user_id)
    
    if not user or not user.is_active:
        raise credentials_exception
    
    return create_access_token(user_id)
