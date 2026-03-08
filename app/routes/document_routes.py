# app/routes/document_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.database import get_db
from app.render import render_markdown_to_html
from app.models import User
from app.auth import get_current_user, require_role
from typing import List

router = APIRouter(prefix="/api", tags=["documents"])


# ====== USER ENDPOINTS ======
@router.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user account. No authentication required."""
    try:
        db_user = await crud.create_user(
            db,
            username=user.username,
            email=user.email,
            password=user.password,
            full_name=user.full_name
        )
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get a user by ID"""
    db_user = await crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/users/", response_model=List[schemas.UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all users"""
    return await crud.get_users(db, skip, limit)


# ====== COLLECTION ENDPOINTS ======
@router.post("/collections/", response_model=schemas.DocumentCollection)
async def create_collection(
    collection: schemas.DocumentCollectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new document collection. Requires authentication."""
    return await crud.create_collection(db, collection, current_user.id)

@router.get("/collections/{collection_id}", response_model=schemas.DocumentCollection)
async def get_collection(collection_id: int, db: AsyncSession = Depends(get_db)):
    """Get a collection by ID"""
    db_collection = await crud.get_collection(db, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return db_collection

@router.get("/collections/by-slug/{slug}", response_model=schemas.DocumentCollection)
async def get_collection_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a collection by slug"""
    db_collection = await crud.get_collection_by_slug(db, slug)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return db_collection

@router.get("/collections/", response_model=List[schemas.DocumentCollection])
async def get_collections(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all collections"""
    return await crud.get_collections(db, skip, limit)

@router.put("/collections/{collection_id}", response_model=schemas.DocumentCollection)
async def update_collection(collection_id: int, name: str = None, description: str = None, db: AsyncSession = Depends(get_db)):
    """Update a collection"""
    db_collection = await crud.update_collection(db, collection_id, name, description)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return db_collection

@router.delete("/collections/{collection_id}", response_model=schemas.DocumentCollection)
async def delete_collection(collection_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a collection"""
    db_collection = await crud.delete_collection(db, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return db_collection


# ====== DOCUMENT ENDPOINTS ======
@router.post("/documents/", response_model=schemas.Document)
async def create_document(
    document: schemas.DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new document. Requires authentication."""
    return await crud.create_document(db, document, current_user.id)

@router.get("/documents/{document_id}", response_model=schemas.Document)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Get a document by ID"""
    db_document = await crud.get_document(db, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.get("/documents/by-slug/{slug}", response_model=schemas.Document)
async def get_document_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a document by slug"""
    db_document = await crud.get_document_by_slug(db, slug)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.get("/documents/", response_model=List[schemas.Document])
async def get_documents(skip: int = 0, limit: int = 100, collection_id: int = None, owner_id: int = None, db: AsyncSession = Depends(get_db)):
    """List documents with optional filtering"""
    if collection_id:
        return await crud.get_documents_by_collection(db, collection_id)
    if owner_id:
        return await crud.get_documents_by_owner(db, owner_id)
    return await crud.get_documents(db, skip, limit)

@router.put("/documents/{document_id}", response_model=schemas.Document)
async def update_document(
    document_id: int,
    document: schemas.DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a document. Requires authentication and ownership."""
    db_document = await crud.get_document(db, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check ownership (or admin)
    if db_document.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only edit your own documents")
    
    return await crud.update_document(db, document_id, document, current_user.id)

@router.delete("/documents/{document_id}", response_model=schemas.Document)
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a document"""
    db_document = await crud.delete_document(db, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.post("/documents/bulk-move/")
async def bulk_move_documents(document_ids: List[int], new_collection_id: int, db: AsyncSession = Depends(get_db)):
    """Move multiple documents to a collection"""
    return await crud.bulk_move_documents(db, document_ids, new_collection_id)

@router.post("/documents/bulk-delete/")
async def bulk_delete_documents(document_ids: List[int], db: AsyncSession = Depends(get_db)):
    """Delete multiple documents"""
    return await crud.bulk_delete_documents(db, document_ids)

@router.post("/documents/{document_id}/render/")
async def render_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Render a document's markdown to HTML"""
    db_document = await crud.get_document(db, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": db_document.id,
        "html_content": render_markdown_to_html(db_document.content, db_document.variables)
    }


# ====== DOCUMENT VERSION ENDPOINTS ======
@router.get("/documents/{document_id}/versions/", response_model=List[schemas.DocumentVersion])
async def get_document_versions(document_id: int, db: AsyncSession = Depends(get_db)):
    """Get all versions of a document"""
    return await crud.get_document_versions(db, document_id)

@router.get("/versions/{version_id}", response_model=schemas.DocumentVersion)
async def get_version(version_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific version"""
    db_version = await crud.get_document_version(db, version_id)
    if not db_version:
        raise HTTPException(status_code=404, detail="Version not found")
    return db_version

@router.post("/documents/{document_id}/versions/{version_id}/restore/")
async def restore_version(
    document_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Restore a document to a previous version. Requires authentication and ownership."""
    db_document = await crud.get_document(db, document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check ownership
    if db_document.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only restore your own documents")
    
    db_document = await crud.restore_document_version(db, document_id, version_id, current_user.id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document or version not found")
    return db_document


# ====== COMMENT ENDPOINTS ======
@router.post("/documents/{document_id}/comments/", response_model=schemas.DocumentComment)
async def create_comment(
    document_id: int,
    comment: schemas.DocumentCommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a comment on a document. Requires authentication."""
    return await crud.create_comment(db, document_id, comment, current_user.id)

@router.get("/documents/{document_id}/comments/", response_model=List[schemas.DocumentComment])
async def get_document_comments(document_id: int, db: AsyncSession = Depends(get_db)):
    """Get all comments on a document"""
    return await crud.get_comments_by_document(db, document_id)

@router.get("/comments/{comment_id}", response_model=schemas.DocumentComment)
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    """Get a comment by ID"""
    db_comment = await crud.get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

@router.post("/comments/{comment_id}/resolve/")
async def resolve_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    """Mark a comment as resolved"""
    db_comment = await crud.resolve_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a comment"""
    db_comment = await crud.delete_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


# ====== TEMPLATE ENDPOINTS ======
@router.post("/redirects/", response_model=schemas.DocumentRedirect)
async def create_redirect(old_slug: str, new_document_id: int, db: AsyncSession = Depends(get_db)):
    """Create a redirect from old slug to new document"""
    return await crud.create_redirect(db, old_slug, new_document_id)

@router.get("/redirects/{old_slug}", response_model=schemas.DocumentRedirect)
async def get_redirect(old_slug: str, db: AsyncSession = Depends(get_db)):
    """Get a redirect"""
    db_redirect = await crud.get_redirect(db, old_slug)
    if not db_redirect:
        raise HTTPException(status_code=404, detail="Redirect not found")
    return db_redirect

@router.delete("/redirects/{redirect_id}")
async def delete_redirect(redirect_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a redirect"""
    db_redirect = await crud.delete_redirect(db, redirect_id)
    if not db_redirect:
        raise HTTPException(status_code=404, detail="Redirect not found")
    return db_redirect


# ====== TEMPLATE ENDPOINTS ======
@router.post("/templates/", response_model=schemas.DocumentTemplate)
async def create_template(
    template: schemas.DocumentTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a document template. Requires authentication."""
    return await crud.create_template(db, template, current_user.id)

@router.get("/templates/{template_id}", response_model=schemas.DocumentTemplate)
async def get_template(template_id: int, db: AsyncSession = Depends(get_db)):
    """Get a template by ID"""
    db_template = await crud.get_template(db, template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template

@router.get("/templates/", response_model=List[schemas.DocumentTemplate])
async def get_templates(skip: int = 0, limit: int = 100, template_type: str = None, db: AsyncSession = Depends(get_db)):
    """List templates with optional filtering"""
    if template_type:
        return await crud.get_templates_by_type(db, template_type)
    return await crud.get_templates(db, skip, limit)

@router.delete("/templates/{template_id}")
async def delete_template(template_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a template"""
    db_template = await crud.delete_template(db, template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template