# Clarity - Architecture & API Documentation

## Overview

Clarity is a technical documentation platform built on FastAPI with a focus on features specifically needed by technical writers:

- Document versioning and history
- Collaboration (comments, reviews)
- Advanced content features (variables, conditionals, includes, tabs)
- Asset management
- Document organization via collections and hierarchy
- Templates and blueprints

---

## Database Architecture

### 9 Core Tables

```
users
├── document_collections (one user can create many)
├── documents (one user owns many)
├── document_comments (one user authors many)
└── assets (one user uploads many)

documents
├── document_versions (one doc has many versions)
├── document_comments (one doc has many comments)
├── assets (through junction table)
└── documents (self-referential for hierarchy)

document_collections
├── documents (many docs in one collection)
└── assets (assets can belong to collection)

assets
└── document_asset_association (many-to-many with documents)

document_templates (templates for various doc types)
document_redirects (manage old URLs -> new doc mappings)
```

### Key Fields

**Users**
- id, username, email, hashed_password, full_name, is_active, created_at

**Documents**
- Core: id, title, slug (unique), content, html_content, needs_rerender
- Organization: collection_id (FK), parent_document_id (FK), order
- Metadata: front_matter (JSON), tags (JSON), variables (JSON)
- Ownership: owner_id (FK to users)
- Status: status (draft|review|published), version
- Timestamps: created_at, updated_at, published_at

**DocumentCollection**
- id, name, description, slug (unique), created_by (FK), timestamps

**DocumentVersion**
- Stores snapshots: document_id, version_number, title, content, html_content
- Metadata: front_matter, variables, author_id
- created_at

**DocumentComment**
- document_id, author_id, content, line_number (for inline comments)
- resolved (boolean for tracking review status)
- timestamps

**Asset**
- filename, original_filename, file_path, file_type, mime_type, file_size
- uploaded_by (FK), collection_id (optional)
- timestamps

**DocumentTemplate**
- name, template_type, content_template, front_matter_schema (JSON)
- created_by, created_at

**DocumentRedirect**
- old_slug -> new_document_id (for managing URL changes)

---

## API Endpoints

### 🔐 Users (6 endpoints)

```
POST   /api/users/                    Create user
GET    /api/users/{user_id}           Get user by ID
GET    /api/users/                    List all users
```

### 📚 Collections (6 endpoints)

```
POST   /api/collections/              Create collection
GET    /api/collections/{id}          Get by ID
GET    /api/collections/by-slug/{slug}  Get by slug
GET    /api/collections/              List collections
PUT    /api/collections/{id}          Update collection
DELETE /api/collections/{id}          Delete collection
```

### 📄 Documents (11 endpoints)

```
POST   /api/documents/                Create document
GET    /api/documents/{id}            Get document
GET    /api/documents/by-slug/{slug}  Get by slug
GET    /api/documents/                List documents (with filters)
PUT    /api/documents/{id}            Update document
DELETE /api/documents/{id}            Delete document
POST   /api/documents/bulk-move/      Move multiple docs to collection
POST   /api/documents/bulk-delete/    Delete multiple docs
POST   /api/documents/{id}/render/    Render markdown to HTML
```

Query parameters for listing:
- `skip`, `limit` - pagination
- `collection_id` - filter by collection
- `owner_id` - filter by owner

### 📖 Versions (3 endpoints)

```
GET    /api/documents/{id}/versions/  Get all versions
GET    /api/versions/{version_id}     Get specific version
POST   /api/documents/{id}/versions/{version_id}/restore/  Restore version
```

### 💬 Comments (5 endpoints)

```
POST   /api/documents/{id}/comments/  Create comment
GET    /api/documents/{id}/comments/  Get all comments on doc
GET    /api/comments/{comment_id}     Get specific comment
POST   /api/comments/{id}/resolve/    Mark as resolved
DELETE /api/comments/{id}             Delete comment
```

### 🎨 Assets (4 endpoints)

```
POST   /api/assets/                   Upload asset
GET    /api/assets/{id}               Get asset
GET    /api/assets/                   List assets (can filter by collection)
DELETE /api/assets/{id}               Delete asset
```

### 📋 Templates (4 endpoints)

```
POST   /api/templates/                Create template
GET    /api/templates/{id}            Get template
GET    /api/templates/                List templates (can filter by type)
DELETE /api/templates/{id}            Delete template
```

### 🔄 Redirects (3 endpoints)

```
POST   /api/redirects/                Create redirect (old_slug -> new_doc_id)
GET    /api/redirects/{old_slug}      Get redirect
DELETE /api/redirects/{id}            Delete redirect
```

**Total: 50+ endpoints**

---

## Markdown Extensions

### Remarks (Callout Blocks)

```markdown
!! [note] (Remember This)
Content goes here

!! [info] (FYI)
Content goes here

!! [warning] (Careful!)
Content goes here

!! [tip] (Pro Tip)
Content goes here
```

Renders as styled callout boxes.

### Tabs

```markdown
~~~tabs
tab: "Python"
```python
print("Hello")
```

tab: "JavaScript"
```javascript
console.log("Hello")
```

tab: "Go"
```go
fmt.Println("Hello")
```
~~~
```

Renders as clickable tabs for multi-language examples.

### Variables

```markdown
This is for {{product_name}} version {{version_number}}.
```

Variables come from document.variables (JSON field):
```json
{
  "product_name": "Clarity",
  "version_number": "1.0.0"
}
```

### Includes

```markdown
!include(path/to/other/file.md)
```

Includes content from another document (for content reuse).

### Standard Markdown

- Tables (GitHub-flavored)
- Code blocks with syntax highlighting
- Images
- Links
- Lists
- Headers, etc.

---

## Request/Response Examples

### Create Document

**Request**
```json
POST /api/documents/
{
  "title": "Getting Started",
  "slug": "getting-started",
  "content": "# Introduction\nWelcome...",
  "collection_id": 1,
  "front_matter": {
    "author": "John Doe",
    "audience": "developers"
  },
  "tags": ["tutorial", "basics"],
  "variables": {
    "product_name": "Clarity",
    "version": "1.0"
  },
  "status": "draft"
}
```

**Response** (201 Created)
```json
{
  "id": 42,
  "title": "Getting Started",
  "slug": "getting-started",
  "content": "# Introduction\nWelcome...",
  "html_content": "<h1>Introduction</h1>\n<p>Welcome...</p>",
  "owner_id": 3,
  "collection_id": 1,
  "parent_document_id": null,
  "front_matter": {"author": "John Doe", "audience": "developers"},
  "tags": ["tutorial", "basics"],
  "variables": {"product_name": "Clarity", "version": "1.0"},
  "status": "draft",
  "version": 1,
  "created_at": "2026-03-04T10:30:00Z",
  "updated_at": "2026-03-04T10:30:00Z",
  "published_at": null
}
```

### Update Document

**Request**
```json
PUT /api/documents/42
{
  "content": "# Introduction\nUpdated welcome...",
  "status": "review"
}
```

This automatically:
- Re-renders markdown to HTML
- Increments version number
- Creates DocumentVersion record
- Updates timestamps

### Get Document with Versions

**Request**
```
GET /api/documents/42/versions/
```

**Response**
```json
[
  {
    "id": 2,
    "document_id": 42,
    "version_number": 2,
    "title": "Getting Started",
    "created_at": "2026-03-04T11:00:00Z",
    "author_id": 3
  },
  {
    "id": 1,
    "document_id": 42,
    "version_number": 1,
    "title": "Getting Started",
    "created_at": "2026-03-04T10:30:00Z",
    "author_id": 3
  }
]
```

### Add Comment (for review workflow)

**Request**
```json
POST /api/documents/42/comments/
{
  "content": "This section needs more detail about error handling",
  "line_number": 45
}
```

**Response**
```json
{
  "id": 7,
  "document_id": 42,
  "author_id": 3,
  "content": "This section needs more detail about error handling",
  "line_number": 45,
  "resolved": false,
  "created_at": "2026-03-04T11:15:00Z",
  "updated_at": "2026-03-04T11:15:00Z"
}
```

Author can then:
- See all comments: `GET /api/documents/42/comments/`
- Resolve when addressed: `POST /api/comments/7/resolve/`

### Upload Asset

**Request** (multipart/form-data)
```
POST /api/assets/
file: <binary image data>
original_filename: "architecture-diagram.png"
file_type: "image"
mime_type: "image/png"
file_size: 245678
collection_id: 1
```

**Response**
```json
{
  "id": 23,
  "filename": "architecture-diagram_abc123.png",
  "original_filename": "architecture-diagram.png",
  "file_path": "/assets/architecture-diagram_abc123.png",
  "file_type": "image",
  "mime_type": "image/png",
  "file_size": 245678,
  "uploaded_by": 3,
  "collection_id": 1,
  "created_at": "2026-03-04T11:30:00Z",
  "updated_at": "2026-03-04T11:30:00Z"
}
```

Then reference in document:
```markdown
![Architecture](https://clarity.example.com/assets/architecture-diagram_abc123.png)
```

### Create Template

**Request**
```json
POST /api/templates/
{
  "name": "API Reference",
  "template_type": "api_reference",
  "description": "Template for documenting API endpoints",
  "content_template": "# {{api_name}}\n\n## Overview\n...",
  "front_matter_schema": {
    "api_name": {"type": "string", "required": true},
    "version": {"type": "string", "required": true},
    "status": {"type": "string", "enum": ["alpha", "beta", "stable"]}
  }
}
```

### Create Redirect (when renaming doc)

When you change a document slug from `old-guide` to `new-guide`:

**Request**
```json
POST /api/redirects/
{
  "old_slug": "old-guide",
  "new_document_id": 42
}
```

This preserves old links in search engines/bookmarks.

---

## Authentication (Coming Soon)

Currently: No authentication (assumed protected deployment environment)

Planned:
- JWT tokens
- User login endpoint
- Role-based access control (RBAC)
- Document sharing/permissions

---

## Error Responses

All endpoints follow standard HTTP status codes:

- `200 OK` - Successful GET
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate slug, etc.
- `500 Server Error` - Unexpected error

Error response format:
```json
{
  "detail": "User not found"
}
```

---

## CRUD Operations in Code

All database operations are in `app/crud.py`:

### Why Separate CRUD?
- Single responsibility
- Easy testing
- Reusable across routes
- Transaction management in one place

### Key CRUD Functions

**Document Management**
```python
await crud.create_document(db, document, owner_id)
await crud.update_document(db, doc_id, update, user_id)
await crud.get_document(db, doc_id)
await crud.get_document_by_slug(db, slug)
await crud.get_documents_by_collection(db, collection_id)
await crud.get_documents_by_owner(db, owner_id)
await crud.bulk_move_documents(db, [doc_ids], new_collection_id)
await crud.bulk_delete_documents(db, [doc_ids])
```

**Versioning**
```python
await crud.create_document_version(db, doc_id, version_num, ...)
await crud.get_document_versions(db, doc_id)
await crud.restore_document_version(db, doc_id, version_id, user_id)
```

**Comments**
```python
await crud.create_comment(db, doc_id, comment, author_id)
await crud.get_comments_by_document(db, doc_id)
await crud.resolve_comment(db, comment_id)
```

**Assets**
```python
await crud.create_asset(db, asset, filename, file_path, uploaded_by)
await crud.get_assets_by_collection(db, collection_id)
```

---

## Markdown Rendering

Central in `app/render.py`:

```python
def render_markdown_to_html(
    markdown_content: str,
    variables: dict = None,
    enable_extras: bool = True
) -> str:
```

Features:
- Codeblock syntax highlighting via Pygments
- Tables support
- Custom Remark extension (callouts)
- Custom Tab extension
- Variable substitution via {{var}} syntax
- Include directive for content reuse
- All standard Markdown features

---

## Data Flow

```
Client
   ↓
FastAPI Routes (/api/documents, /api/collections, etc.)
   ↓
CRUD Operations (app/crud.py)
   ↓
SQLAlchemy ORM → Database (PostgreSQL)
   ↓
Models (app/models.py)

Special: On document update, render.py converts Markdown → HTML
```

---

## Scalability Considerations

- **Async/await** throughout for concurrent requests
- **Connection pooling** via sqlalchemy
- **Pagination** for list endpoints (skip/limit params)
- **Indexing** on frequently queried fields (id, slug, title)
- **JSON fields** in PostgreSQL for flexible metadata
- **Soft deletes** (planned) for audit trails

---

## Security Notes

- **Passwords**: Should be hashed with bcrypt (currently not implemented)
- **Authentication**: JWT tokens (planned)
- **Authorization**: RBAC (planned)
- **SQL Injection**: Protected via SQLAlchemy ORM
- **CORS**: Should be configured based on deployment
- **Rate limiting**: Should be added for production

---

## Testing Strategy (Planned)

- Unit tests for CRUD operations
- Integration tests for API endpoints
- Markdown rendering tests
- Database migration tests
- Link validation tests
- Search indexing tests

---

## Development Workflow

1. **Create migration** for schema changes
   ```bash
   alembic revision --autogenerate -m "add description"
   ```

2. **Update models** in `app/models.py`

3. **Update schemas** in `app/schemas.py` (request/response)

4. **Add CRUD functions** in `app/crud.py`

5. **Add routes** in `app/routes/document_routes.py`

6. **Test endpoints** via Swagger UI at `/docs`

7. **Run migration** in target environment
   ```bash
   alembic upgrade head
   ```

---

## Future Features (from original spec)

- [x] Images, code blocks, tables, hyperlinks
- [x] Remarks (note/info/warning/tips)
- [ ] Reuse/includes (90% done)
- [x] Tab groups
- [x] Versioning
- [x] Variables/conditionals (foundation)
- [ ] Concurrent collaboration (WebSocket needed)
- [x] Front matter
- [ ] Bulk drag-and-drop (UI needed)
- [x] Next steps buttons
- [ ] Tabs with dropdown filters
- [ ] Fingerposts
- [ ] Additional info blocks
- [x] Managing redirects
- [ ] External collaboration/reviews (comments foundation ready)
- [x] Revisions/history
- [x] Blueprints/templates
- [x] Asset manager
- [ ] Testing (broken links, etc.)
- [ ] Styleguide checks
- [ ] Frontend functional tests

---

## Files Overview

**Models** (app/models.py) - 9 SQLAlchemy model classes
**Schemas** (app/schemas.py) - 18 Pydantic schemas
**CRUD** (app/crud.py) - 60+ database functions
**Routes** (app/routes/document_routes.py) - 50+ endpoints
**Render** (app/render.py) - Custom Markdown w/ 5+ extensions
**Migrations** (alembic/versions/) - Database versioning

---

## Asset Management Implementation

### Overview
Comprehensive file upload and asset management system with file validation, organized storage, metadata tracking, and document integration. Includes single/bulk uploads, filtering, and document associations.

### Key Features
- File type and size validation with MIME type checking
- Organized date-based storage structure (YYYY/MM/DD)
- Metadata tracking (original filename, type, size, MIME type, uploader)
- Document-asset associations (many-to-many relationships)
- Filtering by type, uploader, or collection
- Storage statistics and usage monitoring
- File download capability
- Cleanup utilities for orphaned files

### Supported File Types
- **Images**: JPEG, PNG, GIF, WebP, SVG
- **Documents**: PDF, Word (.doc/.docx), Text, Markdown, Excel
- **Videos**: MP4, WebM, QuickTime
- **Audio**: MP3, WAV, WebM

### Configuration
- `UPLOAD_DIR`: Base directory for file storage (default: 
---

## Asset Management Implementation

### Overview
Comprehensive file upl# A
# En
### Overview
Comprehensive file  |
Comprehensi--
### Key Features
- File type and size validation with MIME type checking
- Organized date-based storage structure (YYYY/MM/DD)
- Metadata tracking (original filename, type, size, MIME g |
| GET | `/api/assets- File type  asse- Organized date-based storage structure (YYYY/MM/DD)
lo- Metadata tracking (original filename, type, size, t/- Document-asset associations (many-to-many relationships)
- Filtering -d- Filtering by type, uploader, or collection
- Storage stas- Storage statistics and usage monitoring
-EL- File /api/assets/{id}` | Delete asset |
- Cleanup utilities for o- 
### Supported File Types
- **Images*- *- **Images**: JPEG, PNGc - **Documents**: PDF, Word (.doc/.docx u- **Videos**: MP4, WebM, QuickTime
- **Audio**: MP3, WAV, Web##- **Audio**: MP3, WAV, WebM

### e:
### Configuration
- `UPLO in- `UPLOAD_DIR`: um---

## Asset Management Implementati-many document-asset r
#ati
### Overview
Comprehensive file _coComprehensi C# En
### Overview
Compre, ### sComprehensiitComprehensi--
### Kess### Key Feat**- File type and a- Organized date-based storage structure (YYYY/MM/DD)
mp- Metadata tracking (original filename, type, size, 
 tail -20 /Users/patrickhammond/PycharmProjects/Clarity/ARCHITECTURE.md
 python -c "from markdown.blockprocessors import BlockProcessor; print('BlockProcessor found')" 2>&1
 cd /Users/patrickhammond/PycharmProjects/Clarity && python -m uvicorn app.main:app --reload 2>&1 &
sleep 3
ps aux | grep uvicorn | grep -v grep
 python -c "from app.main import app; print('App imported successfully')"
 cd /Users/patrickhammond/PycharmProjects/Clarity && python3 << 'EOF'
try:
    from app.main import app
    print("SUCCESS: App imported without errors")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
