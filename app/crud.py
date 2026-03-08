# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from app.models import (
    Document, DocumentVersion, DocumentCollection, DocumentComment,
    Asset, User, DocumentRedirect, DocumentTemplate, DocumentAssetAssociation
)
from app.schemas import (
    DocumentCreate, DocumentUpdate, DocumentCollectionCreate,
    DocumentCommentCreate, AssetCreate, DocumentRedirectBase, DocumentTemplateCreate
)
from app.render import render_markdown_to_html


# ====== USER CRUD ======
async def create_user(db: AsyncSession, username: str, email: str, password: str, full_name: str = None, role: str = "viewer"):
    from app.auth import hash_password
    
    # Check if user already exists
    existing_user = await get_user_by_username(db, username)
    if existing_user:
        raise ValueError(f"Username '{username}' already exists")
    
    existing_email = await get_user_by_email(db, email)
    if existing_email:
        raise ValueError(f"Email '{email}' already registered")
    
    # Hash password before storing
    hashed_pw = hash_password(password)
    
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_pw,
        full_name=full_name,
        role=role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


# ====== DOCUMENT COLLECTION CRUD ======
async def create_collection(db: AsyncSession, collection: DocumentCollectionCreate, created_by: int):
    db_collection = DocumentCollection(
        name=collection.name,
        description=collection.description,
        slug=collection.slug,
        created_by=created_by
    )
    db.add(db_collection)
    await db.commit()
    await db.refresh(db_collection)
    return db_collection

async def get_collection(db: AsyncSession, collection_id: int):
    result = await db.execute(select(DocumentCollection).filter(DocumentCollection.id == collection_id))
    return result.scalar_one_or_none()

async def get_collection_by_slug(db: AsyncSession, slug: str):
    result = await db.execute(select(DocumentCollection).filter(DocumentCollection.slug == slug))
    return result.scalar_one_or_none()

async def get_collections(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(DocumentCollection).offset(skip).limit(limit))
    return result.scalars().all()

async def update_collection(db: AsyncSession, collection_id: int, name: str = None, description: str = None):
    db_collection = await db.get(DocumentCollection, collection_id)
    if db_collection:
        if name:
            db_collection.name = name
        if description:
            db_collection.description = description
        await db.commit()
        await db.refresh(db_collection)
    return db_collection

async def delete_collection(db: AsyncSession, collection_id: int):
    db_collection = await db.get(DocumentCollection, collection_id)
    if db_collection:
        await db.delete(db_collection)
        await db.commit()
    return db_collection


# ====== DOCUMENT CRUD ======
async def create_document(db: AsyncSession, document: DocumentCreate, owner_id: int):
    db_document = Document(
        title=document.title,
        slug=document.slug,
        content=document.content,
        html_content=render_markdown_to_html(document.content),
        owner_id=owner_id,
        collection_id=document.collection_id,
        parent_document_id=document.parent_document_id,
        front_matter=document.front_matter or {},
        tags=document.tags or [],
        variables=document.variables or {},
        status=document.status or "draft",
        needs_rerender=False
    )
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    
    # Create initial version
    await create_document_version(db, db_document.id, 1, document.title, document.content, db_document.html_content, owner_id, document.front_matter, document.variables)
    
    return db_document

async def get_document(db: AsyncSession, document_id: int):
    result = await db.execute(select(Document).filter(Document.id == document_id))
    return result.scalar_one_or_none()

async def get_document_by_slug(db: AsyncSession, slug: str):
    result = await db.execute(select(Document).filter(Document.slug == slug))
    return result.scalar_one_or_none()

async def get_documents(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Document).offset(skip).limit(limit))
    return result.scalars().all()

async def get_documents_by_collection(db: AsyncSession, collection_id: int):
    result = await db.execute(select(Document).filter(Document.collection_id == collection_id))
    return result.scalars().all()

async def get_documents_by_owner(db: AsyncSession, owner_id: int):
    result = await db.execute(select(Document).filter(Document.owner_id == owner_id))
    return result.scalars().all()

async def update_document(db: AsyncSession, document_id: int, document: DocumentUpdate, user_id: int):
    db_document = await db.get(Document, document_id)
    if db_document:
        if document.title:
            db_document.title = document.title
        if document.content:
            db_document.content = document.content
            db_document.html_content = render_markdown_to_html(document.content)
            db_document.needs_rerender = False
            db_document.version += 1
            # Create new version record
            await create_document_version(
                db, 
                document_id, 
                db_document.version,
                document.title or db_document.title,
                document.content,
                db_document.html_content,
                user_id,
                document.front_matter or db_document.front_matter,
                document.variables or db_document.variables
            )
        if document.slug:
            db_document.slug = document.slug
        if document.front_matter is not None:
            db_document.front_matter = document.front_matter
        if document.tags is not None:
            db_document.tags = document.tags
        if document.variables is not None:
            db_document.variables = document.variables
        if document.status:
            db_document.status = document.status
        
        await db.commit()
        await db.refresh(db_document)
    return db_document

async def delete_document(db: AsyncSession, document_id: int):
    db_document = await db.get(Document, document_id)
    if db_document:
        await db.delete(db_document)
        await db.commit()
    return db_document

async def bulk_move_documents(db: AsyncSession, document_ids: list, new_collection_id: int):
    """Move multiple documents to a new collection"""
    result = await db.execute(select(Document).filter(Document.id.in_(document_ids)))
    documents = result.scalars().all()
    for doc in documents:
        doc.collection_id = new_collection_id
    await db.commit()
    return documents

async def bulk_delete_documents(db: AsyncSession, document_ids: list):
    """Delete multiple documents"""
    result = await db.execute(select(Document).filter(Document.id.in_(document_ids)))
    documents = result.scalars().all()
    for doc in documents:
        await db.delete(doc)
    await db.commit()
    return documents


# ====== DOCUMENT VERSION CRUD ======
async def create_document_version(db: AsyncSession, document_id: int, version_number: int, title: str, content: str, html_content: str, author_id: int, front_matter: dict = None, variables: dict = None):
    db_version = DocumentVersion(
        document_id=document_id,
        version_number=version_number,
        title=title,
        content=content,
        html_content=html_content,
        author_id=author_id,
        front_matter=front_matter or {},
        variables=variables or {}
    )
    db.add(db_version)
    await db.commit()
    await db.refresh(db_version)
    return db_version

async def get_document_version(db: AsyncSession, version_id: int):
    result = await db.execute(select(DocumentVersion).filter(DocumentVersion.id == version_id))
    return result.scalar_one_or_none()

async def get_document_versions(db: AsyncSession, document_id: int):
    result = await db.execute(
        select(DocumentVersion)
        .filter(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.version_number.desc())
    )
    return result.scalars().all()

async def restore_document_version(db: AsyncSession, document_id: int, version_id: int, user_id: int):
    """Restore a document to a previous version"""
    db_document = await db.get(Document, document_id)
    db_version = await db.get(DocumentVersion, version_id)
    
    if db_document and db_version:
        db_document.content = db_version.content
        db_document.html_content = db_version.html_content
        db_document.front_matter = db_version.front_matter
        db_document.variables = db_version.variables
        db_document.version += 1
        
        # Create new version from restored content
        await create_document_version(
            db,
            document_id,
            db_document.version,
            db_version.title,
            db_version.content,
            db_version.html_content,
            user_id,
            db_version.front_matter,
            db_version.variables
        )
        
        await db.commit()
        await db.refresh(db_document)
    return db_document


# ====== DOCUMENT COMMENT CRUD ======
async def create_comment(db: AsyncSession, document_id: int, comment: DocumentCommentCreate, author_id: int):
    db_comment = DocumentComment(
        document_id=document_id,
        author_id=author_id,
        content=comment.content,
        line_number=comment.line_number
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

async def get_comment(db: AsyncSession, comment_id: int):
    result = await db.execute(select(DocumentComment).filter(DocumentComment.id == comment_id))
    return result.scalar_one_or_none()

async def get_comments_by_document(db: AsyncSession, document_id: int):
    result = await db.execute(
        select(DocumentComment)
        .filter(DocumentComment.document_id == document_id)
        .order_by(DocumentComment.created_at.desc())
    )
    return result.scalars().all()

async def resolve_comment(db: AsyncSession, comment_id: int):
    db_comment = await db.get(DocumentComment, comment_id)
    if db_comment:
        db_comment.resolved = True
        await db.commit()
        await db.refresh(db_comment)
    return db_comment

async def delete_comment(db: AsyncSession, comment_id: int):
    db_comment = await db.get(DocumentComment, comment_id)
    if db_comment:
        await db.delete(db_comment)
        await db.commit()
    return db_comment


# ====== ASSET CRUD ======
# ====== ASSET CRUD ======
async def create_asset(
    db: AsyncSession,
    filename: str,
    original_filename: str,
    file_path: str,
    file_type: str,
    file_size: int,
    mime_type: str,
    uploaded_by: int,
    collection_id: int = None
):
    """Create a new asset record in the database."""
    db_asset = Asset(
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        mime_type=mime_type,
        uploaded_by=uploaded_by,
        collection_id=collection_id
    )
    db.add(db_asset)
    await db.commit()
    await db.refresh(db_asset)
    return db_asset

async def get_asset(db: AsyncSession, asset_id: int):
    """Get a single asset by ID."""
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    return result.scalar_one_or_none()

async def get_assets(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all assets with pagination."""
    result = await db.execute(select(Asset).offset(skip).limit(limit))
    return result.scalars().all()

async def get_assets_by_collection(db: AsyncSession, collection_id: int, skip: int = 0, limit: int = 100):
    """Get all assets in a collection."""
    result = await db.execute(
        select(Asset)
        .filter(Asset.collection_id == collection_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_assets_by_uploader(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    """Get all assets uploaded by a specific user."""
    result = await db.execute(
        select(Asset)
        .filter(Asset.uploaded_by == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_assets_by_type(db: AsyncSession, file_type: str, skip: int = 0, limit: int = 100):
    """Get all assets of a specific type (image, video, document, audio, other)."""
    result = await db.execute(
        select(Asset)
        .filter(Asset.file_type == file_type)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_assets_by_document(db: AsyncSession, document_id: int):
    """Get all assets linked to a specific document."""
    result = await db.execute(
        select(Asset)
        .join(DocumentAssetAssociation)
        .filter(DocumentAssetAssociation.document_id == document_id)
    )
    return result.scalars().all()

async def delete_asset(db: AsyncSession, asset_id: int):
    """Delete an asset and all its associations."""
    db_asset = await db.get(Asset, asset_id)
    if db_asset:
        # Delete all associations
        result = await db.execute(
            select(DocumentAssetAssociation)
            .filter(DocumentAssetAssociation.asset_id == asset_id)
        )
        for assoc in result.scalars():
            await db.delete(assoc)
        
        # Delete the asset
        await db.delete(db_asset)
        await db.commit()
    return db_asset

async def link_asset_to_document(db: AsyncSession, asset_id: int, document_id: int):
    """Link an asset to a document."""
    # Check if already linked
    result = await db.execute(
        select(DocumentAssetAssociation)
        .filter(
            and_(
                DocumentAssetAssociation.asset_id == asset_id,
                DocumentAssetAssociation.document_id == document_id
            )
        )
    )
    if result.scalar_one_or_none():
        return {"message": "Asset already linked to this document"}
    
    # Create new association
    assoc = DocumentAssetAssociation(asset_id=asset_id, document_id=document_id)
    db.add(assoc)
    await db.commit()
    await db.refresh(assoc)
    return {"message": "Asset linked successfully", "association_id": assoc.id}

async def unlink_asset_from_document(db: AsyncSession, asset_id: int, document_id: int):
    """Unlink an asset from a document."""
    result = await db.execute(
        select(DocumentAssetAssociation)
        .filter(
            and_(
                DocumentAssetAssociation.asset_id == asset_id,
                DocumentAssetAssociation.document_id == document_id
            )
        )
    )
    assoc = result.scalar_one_or_none()
    if assoc:
        await db.delete(assoc)
        await db.commit()
    return {"message": "Asset unlinked successfully"}

async def get_asset_stats(db: AsyncSession):
    """Get aggregate statistics about assets."""
    from sqlalchemy import func
    
    # Total assets
    total_result = await db.execute(select(func.count(Asset.id)))
    total_count = total_result.scalar() or 0
    
    # Total storage used
    size_result = await db.execute(select(func.sum(Asset.file_size)))
    total_size = size_result.scalar() or 0
    
    # Count by type
    type_result = await db.execute(
        select(Asset.file_type, func.count(Asset.id))
        .group_by(Asset.file_type)
    )
    by_type = {row[0]: row[1] for row in type_result.all()}
    
    return {
        "total_assets": total_count,
        "total_storage_bytes": total_size,
        "total_storage_mb": round(total_size / (1024 * 1024), 2),
        "assets_by_type": by_type
    }


# ====== DOCUMENT REDIRECT CRUD ======
async def create_redirect(db: AsyncSession, old_slug: str, new_document_id: int):
    db_redirect = DocumentRedirect(old_slug=old_slug, new_document_id=new_document_id)
    db.add(db_redirect)
    await db.commit()
    await db.refresh(db_redirect)
    return db_redirect

async def get_redirect(db: AsyncSession, old_slug: str):
    result = await db.execute(select(DocumentRedirect).filter(DocumentRedirect.old_slug == old_slug))
    return result.scalar_one_or_none()

async def delete_redirect(db: AsyncSession, redirect_id: int):
    db_redirect = await db.get(DocumentRedirect, redirect_id)
    if db_redirect:
        await db.delete(db_redirect)
        await db.commit()
    return db_redirect


# ====== DOCUMENT TEMPLATE CRUD ======
async def create_template(db: AsyncSession, template: DocumentTemplateCreate, created_by: int):
    db_template = DocumentTemplate(
        name=template.name,
        description=template.description,
        template_type=template.template_type,
        content_template=template.content_template,
        front_matter_schema=template.front_matter_schema or {},
        created_by=created_by
    )
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template

async def get_template(db: AsyncSession, template_id: int):
    result = await db.execute(select(DocumentTemplate).filter(DocumentTemplate.id == template_id))
    return result.scalar_one_or_none()

async def get_templates(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(DocumentTemplate).offset(skip).limit(limit))
    return result.scalars().all()

async def get_templates_by_type(db: AsyncSession, template_type: str):
    result = await db.execute(select(DocumentTemplate).filter(DocumentTemplate.template_type == template_type))
    return result.scalars().all()

async def delete_template(db: AsyncSession, template_id: int):
    db_template = await db.get(DocumentTemplate, template_id)
    if db_template:
        await db.delete(db_template)
        await db.commit()
    return db_template