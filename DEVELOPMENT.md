# Clarity Development Guide

## Quick Start

### 1. Local Setup (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/clarity"
export SECRET_KEY="your-dev-secret-key"

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be at: http://localhost:8000
Docs at: http://localhost:8000/docs

### 2. Docker Setup

```bash
# Start everything
docker-compose up --build

# Access logs
docker-compose logs -f web

# Run migrations (if needed)
docker-compose exec web alembic upgrade head

# Stop
docker-compose down
```

---

## Adding a New Feature

### Example: Add "reading_time" field to documents

#### Step 1: Update Model

**app/models.py**
```python
class Document(Base):
    __tablename__ = "documents"
    
    # ... existing fields ...
    reading_time = Column(Integer, nullable=True)  # minutes
```

#### Step 2: Create Migration

```bash
alembic revision --autogenerate -m "add reading_time to documents"
```

This generates `alembic/versions/00X_add_reading_time_to_documents.py`:
```python
def upgrade() -> None:
    op.add_column('documents', sa.Column('reading_time', sa.Integer(), nullable=True))

def downgrade() -> None:
    op.drop_column('documents', 'reading_time')
```

#### Step 3: Update Schema

**app/schemas.py**
```python
class DocumentBase(BaseModel):
    # ... existing fields ...
    reading_time: Optional[int] = None

class Document(DocumentBase):
    # ... existing fields ...
    reading_time: Optional[int] = None
```

#### Step 4: Update CRUD

**app/crud.py**
```python
async def update_document(db: AsyncSession, document_id: int, document: DocumentUpdate, user_id: int):
    db_document = await db.get(Document, document_id)
    if db_document:
        # ... existing updates ...
        if document.reading_time is not None:
            db_document.reading_time = document.reading_time
        await db.commit()
        await db.refresh(db_document)
    return db_document
```

#### Step 5: Apply Migration

```bash
alembic upgrade head
```

#### Step 6: Test via Swagger UI

Visit http://localhost:8000/docs and test the endpoints.

---

## Testing

### Simple Endpoint Test

```bash
# Create a document
curl -X POST "http://localhost:8000/api/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Doc",
    "slug": "my-first-doc",
    "content": "# Hello\nThis is content",
    "front_matter": {},
    "tags": [],
    "variables": {},
    "status": "draft"
  }'

# Should return 201 with document object

# Get all documents
curl "http://localhost:8000/api/documents/"

# Get one document
curl "http://localhost:8000/api/documents/1"

# Update document
curl -X PUT "http://localhost:8000/api/documents/1" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Hello\nUpdated content"
  }'

# Delete document
curl -X DELETE "http://localhost:8000/api/documents/1"
```

### Markdown Rendering Test

```bash
# Render markdown to HTML
curl -X POST "http://localhost:8000/api/documents/1/render/" 
```

Returns:
```json
{
  "id": 1,
  "html_content": "<h1>Hello</h1>\n<p>This is content</p>"
}
```

---

## Database Access

### Connect to Database (Docker)

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U clarity_user -d clarity

# List tables
\dt

# Query documents
SELECT id, title, slug, status FROM documents LIMIT 10;

# Exit
\q
```

### View Migrations

```bash
# Current revision
docker-compose exec web alembic current

# Full history
docker-compose exec web alembic history

# Show upcoming migrations
docker-compose exec web alembic upgrade --sql head
```

---

## Code Organization

### Models Should Handle:
- Table structure
- Relationships
- Column types and constraints

### Schemas Should Handle:
- Request/response validation
- Optional vs required fields
- Data serialization

### CRUD Should Handle:
- Database queries
- Transaction management
- Complex operations

### Routes Should Handle:
- HTTP endpoints
- Query parameters
- Error responses
- Status codes

### Don't Mix These!

---

## Common Tasks

### Add a New API Endpoint

In `app/routes/document_routes.py`:

```python
@router.get("/documents/stats/", response_model=dict)
async def get_document_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics about all documents"""
    result = await db.execute(select(func.count(Document.id)))
    total = result.scalar()
    
    result = await db.execute(select(func.count(Document.id)).where(Document.status == 'published'))
    published = result.scalar()
    
    return {
        "total": total,
        "published": published,
        "draft": total - published
    }
```

Then test: `curl http://localhost:8000/api/documents/stats/`

### Query with Filters

```python
# In CRUD or routes
result = await db.execute(
    select(Document)
    .filter(Document.collection_id == collection_id)
    .filter(Document.status == "published")
    .order_by(Document.created_at.desc())
)
docs = result.scalars().all()
```

### Bulk Operations

```python
# Update multiple documents
docs = await crud.bulk_move_documents(db, [1, 2, 3], new_collection_id=5)

# Delete multiple documents
docs = await crud.bulk_delete_documents(db, [1, 2, 3])
```

### Create Version on Update

Already handled in `crud.create_document()` and `crud.update_document()`:
- Creates initial version on document creation
- Creates new version on document update
- Increments version number automatically

---

## Debugging

### Enable SQL Logging

In `app/database.py`:

```python
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    future=True,
    echo=True  # This logs all SQL queries
)
```

### Check API Documentation

While server running: http://localhost:8000/docs

Click endpoint → Try it out → Execute

### View Request/Response

In Swagger UI, scroll to "Response body" after executing a request.

### Print Debugging in Routes

```python
@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    print(f"Fetching document {document_id}")
    db_document = await crud.get_document(db, document_id)
    print(f"Found: {db_document}")
    return db_document
```

---

## Markdown Extensions Testing

### Remarks

```python
content = """
!! [warning] (Important!)
This is a warning message.
"""

html = render_markdown_to_html(content)
print(html)
# Should contain: <div class='remark remark-warning'>
```

### Variables

```python
content = "Hello {{name}}, you are using {{product}}"

html = render_markdown_to_html(
    content,
    variables={"name": "John", "product": "Clarity"}
)
print(html)
# Should contain: Hello John, you are using Clarity
```

### Tabs

```python
content = """
~~~tabs
tab: "Python"
```python
print("Hello")
```
~~~
"""

html = render_markdown_to_html(content)
print(html)
# Should contain: <div class='tab-group'>
```

---

## Environment Variables

Create `.env` in project root:

```
DATABASE_URL=postgresql+asyncpg://clarity_user:clarity_password@db:5432/clarity
SECRET_KEY=dev-secret-key-do-not-use-in-production
DEBUG=True
LOG_LEVEL=INFO
```

For local development without Docker:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/clarity_dev
```

---

## Deployment Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Generate strong `SECRET_KEY`
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Test all endpoints
- [ ] Set up CORS properly
- [ ] Configure authentication (coming soon)
- [ ] Set up monitoring/logging
- [ ] Backup database

---

## Getting Help

### View API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Check Code
- Models: `app/models.py`
- API Endpoints: `app/routes/document_routes.py`
- Database Ops: `app/crud.py`
- Architecture: `ARCHITECTURE.md`

### Run Alembic Help
```bash
alembic --help
```

### View SQLAlchemy Docs
https://docs.sqlalchemy.org/

### View FastAPI Docs
https://fastapi.tiangolo.com/

---

## Know Issues / TODOs

- [ ] Authentication not yet implemented
- [ ] Password hashing not implemented
- [ ] CORS not configured
- [ ] File upload handling (basic structure only)
- [ ] Search/full-text indexing not implemented
- [ ] WebSocket for real-time collaboration
- [ ] Rate limiting
- [ ] Input validation for large documents
- [ ] Concurrent edit conflict resolution

---

## Contributing Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes following structure above
3. Test via Swagger UI
4. Run migrations if needed
5. Commit: `git commit -m "Add your feature"`
6. Push: `git push origin feature/your-feature`
7. Create pull request

---

## Performance Tips

- Use pagination on list endpoints
- Index frequently queried fields (already done for id, slug, title)
- Use bulk operations for large updates
- Cache rendered HTML (markdown rendering can be expensive)
- Consider read replicas for high-traffic environments

---

## Next Steps

- Implement JWT authentication
- Add user permissions/roles
- Build frontend UI (React/Vue)
- Add search indexing (Elasticsearch)
- Set up CI/CD pipeline
- Add comprehensive tests
- Set up monitoring (Sentry, etc.)
