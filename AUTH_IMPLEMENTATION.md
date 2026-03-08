# Authentication & Authorization Foundation

This file documents the authentication system design and provides implementation guidance.

## Current State

- ✅ User model with hashed_password field
- ✅ User CRUD operations
- ✅ User endpoints (basic create/get/list)
- ❌ JWT token authentication
- ❌ Password hashing
- ❌ Role-based access control (RBAC)
- ❌ Permissions system

---

## Design

### Authentication Flow

```
1. User logs in with username + password
2. Backend validates credentials (bcrypt)
3. JWT token issued (access + refresh)
4. Client includes token in Authorization header
5. Backend validates token on each request
6. Route handler executes if authorized
```

### Authorization Model

**Roles:**
- admin - Full system access
- editor - Can create/edit documents, manage collections
- viewer - Can read published documents only
- reviewer - Can view, comment, but not publish

**Permissions:**
- documents.create
- documents.edit
- documents.delete
- documents.publish
- comments.create
- comments.resolve
- assets.upload
- collections.manage
- users.manage (admin only)

### Implementation Steps

#### 1. Update User Model

Add to `app/models.py`:

```python
from enum import Enum as PyEnum

class UserRole(PyEnum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"
    reviewer = "reviewer"

class User(Base):
    __tablename__ = "users"
    
    # ... existing fields ...
    role = Column(String, default="viewer")  # Default to viewer
    is_active = Column(Boolean, default=True)
    
    # Validation
    @validates('role')
    def validate_role(self, key, value):
        valid_roles = [role.value for role in UserRole]
        if value not in valid_roles:
            raise ValueError(f"Invalid role: {value}")
        return value
```

#### 2. Create Authentication Module

New file `app/auth.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int):
    """Create JWT refresh token (7 days)"""
    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user from token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = await crud.get_user(db, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

async def require_role(required_role: str):
    """Dependency to check user role"""
    def check_role(current_user: User = Depends(get_current_user)):
        role_hierarchy = {"admin": 3, "editor": 2, "reviewer": 1, "viewer": 0}
        if role_hierarchy.get(current_user.role, -1) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return check_role
```

#### 3. Add Login Endpoint

Update `app/routes/api_auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.database import get_db
from app.auth import (
    hash_password, verify_password, 
    create_access_token, create_refresh_token,
    get_current_user
)
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with username and password"""
    user = await crud.get_user_by_username(db, request.username)
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Get new access token using refresh token"""
    # Validate refresh token and issue new access token
    pass

@router.get("/me", response_model=schemas.User)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current authenticated user info"""
    return current_user

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """Logout (invalidate token)"""
    # In production, add token to blacklist
    return {"message": "Logged out successfully"}
```

#### 4. Update CRUD for Password Hashing

Modify `app/crud.py`:

```python
from app.auth import hash_password

async def create_user(
    db: AsyncSession, 
    username: str,
    email: str,
    password: str,  # Plain text
    full_name: str = None,
    role: str = "viewer"
):
    # Hash password before storing
    hashed_password = hash_password(password)
    
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,  # Store hashed version
        full_name=full_name,
        role=role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

#### 5. Protect Routes with Authentication

```python
from app.auth import get_current_user, require_role

# Public endpoint (no auth required)
@router.get("/documents/public/")
async def get_published_documents():
    """Anyone can view published documents"""
    pass

# Authenticated endpoint
@router.post("/documents/")
async def create_document(
    document: schemas.DocumentCreate,
    current_user: User = Depends(get_current_user),  # ← Requires login
    db: AsyncSession = Depends(get_db)
):
    """Only authenticated users can create documents"""
    return await crud.create_document(db, document, current_user.id)

# Admin-only endpoint
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role("admin")),  # ← Requires admin role
    db: AsyncSession = Depends(get_db)
):
    """Only admins can delete users"""
    return await crud.delete_user(db, user_id)

# Editor-only
@router.post("/documents/publish/")
async def publish_document(
    document_id: int,
    current_user: User = Depends(require_role("editor")),
    db: AsyncSession = Depends(get_db)
):
    """Only editors can publish"""
    pass
```

#### 6. Create Migration for Auth Fields

Create new migration file or add to existing:

```python
def upgrade():
    op.add_column('users', sa.Column('role', sa.String(), nullable=False, server_default='viewer'))

def downgrade():
    op.drop_column('users', 'role')
```

#### 7. Update Environment Variables

Add to `.env`:

```
SECRET_KEY=your-very-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Testing Authentication

```bash
# Create user
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123",
    "full_name": "Test User"
  }'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'

# Returns: {"access_token": "eyJ...", "refresh_token": "...", "token_type": "bearer"}

# Use token in request
curl -X GET "http://localhost:8000/api/me" \
  -H "Authorization: Bearer eyJ..."

# Get current user info
curl "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer eyJ..."
```

### Document Ownership & Permissions

Documents should respect:
1. Owner can always edit their own documents
2. Admin can edit any document
3. Editors can edit within their collection
4. Viewers can only read published documents

```python
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_document = await crud.get_document(db, document_id)
    
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    is_owner = db_document.owner_id == current_user.id
    is_admin = current_user.role == "admin"
    is_published = db_document.status == "published"
    
    if not (is_owner or is_admin or is_published):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    return db_document
```

### Next Steps for Implementation

1. Create `app/auth.py` with JWT and password utilities
2. Update `app/models.py` with User.role field
3. Create migration for role field
4. Update `app/routes/api_auth.py` with login/logout
5. Update all route handlers to require authentication
6. Add role-based access control to specific endpoints
7. Test all auth flows
8. Document API changes

---

## Security Considerations

- **Password Storage**: Always hash with bcrypt (never plaintext)
- **Token Expiry**: Short-lived access tokens (30min) + refresh tokens
- **CORS**: Restrict to known origins in production
- **HTTPS**: Use only over HTTPS in production
- **Secret Key**: Generate strong random key, don't commit to repo
- **Token Refresh**: Implement token refresh for long sessions
- **Rate Limiting**: Limit login attempts to prevent brute force
- **Token Blacklist**: For logout functionality, maintain blacklist

---

## Database Updates Needed

Add to User model migration:
- `role` column (VARCHAR, default='viewer')
- Consider adding `last_login` timestamp
- Consider `is_active` constraint checking

---

## Testing Plan

- [ ] Test signup/registration
- [ ] Test login with valid credentials
- [ ] Test login with invalid credentials
- [ ] Test token expiry and refresh
- [ ] Test accessing protected routes without token
- [ ] Test role-based access
- [ ] Test document ownership restrictions
- [ ] Test password reset flow (future)
