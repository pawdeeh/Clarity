# Authentication Testing Guide

Quick reference for testing the newly implemented JWT authentication system.

## Setup & Start

```bash
cd /Users/patrickhammond/PycharmProjects/Clarity

# Start the application
docker-compose up --build

# Or locally:
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for interactive testing.

---

## Test Workflow

### 1. Register a New User

**Request**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'
```

**Expected Response** (201 Created)
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "role": "viewer",
  "is_active": true,
  "created_at": "2026-03-04T10:30:00Z"
}
```

### 2. Login

**Request**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

**Expected Response** (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Store both tokens. Access token expires in 30 minutes, refresh token in 7 days.

### 3. Get Current User Info

**Request**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

Replace `<access_token>` with the token from login response.

**Expected Response** (200 OK)
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "role": "viewer",
  "is_active": true,
  "created_at": "2026-03-04T10:30:00Z"
}
```

### 4. Create a Collection (Protected)

**Request**
```bash
curl -X POST "http://localhost:8000/api/collections/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Documentation",
    "description": "Project documentation",
    "slug": "my-docs"
  }'
```

**Expected Response** (200 OK)
```json
{
  "id": 1,
  "name": "My Documentation",
  "description": "Project documentation",
  "slug": "my-docs",
  "created_by": 1,
  "created_at": "2026-03-04T10:30:00Z",
  "updated_at": "2026-03-04T10:30:00Z"
}
```

### 5. Create a Document (Protected)

**Request**
```bash
curl -X POST "http://localhost:8000/api/documents/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started",
    "slug": "getting-started",
    "content": "# Getting Started\n\nWelcome to my docs!",
    "collection_id": 1,
    "front_matter": {"author": "testuser"},
    "tags": ["tutorial"],
    "variables": {},
    "status": "draft"
  }'
```

**Expected Response** (200 OK)
```json
{
  "id": 1,
  "title": "Getting Started",
  "slug": "getting-started",
  "content": "# Getting Started\n\nWelcome to my docs!",
  "html_content": "<h1>Getting Started</h1>\n<p>Welcome to my docs!</p>",
  "owner_id": 1,
  "collection_id": 1,
  "front_matter": {"author": "testuser"},
  "tags": ["tutorial"],
  "status": "draft",
  "version": 1,
  "created_at": "2026-03-04T10:30:00Z",
  "updated_at": "2026-03-04T10:30:00Z",
  "published_at": null
}
```

### 6. Add a Comment (Protected)

**Request**
```bash
curl -X POST "http://localhost:8000/api/documents/1/comments/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This needs more detail in the introduction",
    "line_number": 5
  }'
```

**Expected Response** (200 OK)
```json
{
  "id": 1,
  "document_id": 1,
  "author_id": 1,
  "content": "This needs more detail in the introduction",
  "line_number": 5,
  "resolved": false,
  "created_at": "2026-03-04T10:35:00Z",
  "updated_at": "2026-03-04T10:35:00Z"
}
```

### 7. Refresh Token

When access token expires (30 minutes), use refresh token:

**Request**
```bash
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

**Expected Response** (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 8. Change Password

**Request**
```bash
curl -X POST "http://localhost:8000/api/auth/change-password" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePassword123!",
    "new_password": "NewSecurePassword456!"
  }'
```

**Expected Response** (200 OK)
```json
{
  "message": "Password changed successfully"
}
```

### 9. Validate Token

Check if a token is still valid:

**Request**
```bash
curl -X POST "http://localhost:8000/api/auth/validate-token" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response** (200 OK)
```json
{
  "valid": true,
  "user_id": 1,
  "username": "testuser",
  "role": "viewer"
}
```

### 10. Logout

**Request**
```bash
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response** (200 OK)
```json
{
  "message": "Logged out successfully",
  "detail": "Please delete your tokens from client storage"
}
```

**Note**: JWT tokens cannot be invalidated server-side. Clients should:
1. Delete tokens from local storage
2. Stop using the token
3. Request new token on next login

---

## Error Cases to Test

### Invalid Username/Password

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "WrongPassword"
  }'
```

**Expected Response** (401 Unauthorized)
```json
{
  "detail": "Invalid username or password"
}
```

### Duplicate Username

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "new@example.com",
    "password": "password123"
  }'
```

**Expected Response** (400 Bad Request)
```json
{
  "detail": "Username 'testuser' already exists"
}
```

### Missing Authentication Header

```bash
curl -X POST "http://localhost:8000/api/collections/" \
  -H "Content-Type: application/json" \
  -d '{"name":"test","slug":"test"}'
```

**Expected Response** (403 Forbidden)
```json
{
  "detail": "Not authenticated"
}
```

### Invalid Token

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer invalid_token_here"
```

**Expected Response** (401 Unauthorized)
```json
{
  "detail": "Could not validate credentials"
}
```

### Expired Token

After access token expires (30 minutes), trying to use it:

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <expired_token>"
```

**Expected Response** (401 Unauthorized)
```json
{
  "detail": "Could not validate credentials"
}
```

Use refresh token to get new access token.

### Ownership Check

Create a document as one user, try to edit as another:

```bash
# User 1 creates doc with id=1
# User 2 tries to edit it:

curl -X PUT "http://localhost:8000/api/documents/1" \
  -H "Authorization: Bearer <user2_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "hacked"}'
```

**Expected Response** (403 Forbidden)
```json
{
  "detail": "You can only edit your own documents"
}
```

---

## Testing in Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Select Bearer token
4. Paste access token from login response
5. Click "Authorize"
6. Now test any protected endpoint (collections, documents, etc.)

---

## Roles & Permissions

Current implementation supports 4 roles:
- **admin** - Full system access
- **editor** - Can create/edit documents
- **reviewer** - Can comment and review
- **viewer** - Can only read published documents (default)

Default role for new users: **viewer**

To test role-based features, you would need to:
1. Create or update user with different roles (currently manual via database)
2. Test endpoints that check roles

---

## Important Notes

### Token Structure

Access Token:
```
Header: {
  "alg": "HS256",
  "typ": "JWT"
}
Payload: {
  "sub": 1,          // user_id
  "exp": 1234567890,
  "iat": 1234565090,
  "type": "access"
}
```

Refresh Token:
```
Payload: {
  "sub": 1,
  "exp": 1235567890,
  "iat": 1234565090,
  "type": "refresh"
}
```

### Security in Production

For production use:
1. Set strong `SECRET_KEY` environment variable
2. Use HTTPS only
3. Implement token blacklist for logout
4. Add rate limiting on login endpoint
5. Implement 2FA
6. Use secure cookies (not localStorage)
7. Implement CORS properly
8. Add password requirements validation

### Database

Passwords are hashed with bcrypt before storing:
- Never store plaintext passwords
- Use same password salt for each user (built-in to bcrypt)
- Verification is slow intentionally (security feature)

---

## Quick Checklist

- [ ] Register new user
- [ ] Login and get tokens
- [ ] Use access token for protected endpoints
- [ ] Refresh token when expired
- [ ] Test invalid credentials (401)
- [ ] Test missing auth (403)
- [ ] Test ownership protection (403)
- [ ] Test role-based access (when roles differ)
- [ ] Change password
- [ ] Validate token
- [ ] Logout

---

## Next: Frontend Integration

Once testing is complete, frontend can:
1. Show login form
2. POST to /api/auth/register for signup
3. POST to /api/auth/login for login
4. Store tokens in localStorage/sessionStorage
5. Add Authorization header to all requests
6. Handle token refresh automatically
7. Redirect to login on 401
8. Show errors from API responses

See ROADMAP.md Phase 2 for next steps.
