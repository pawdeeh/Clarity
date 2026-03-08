# schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ====== User Schemas ======
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = "viewer"

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None  # If updating password

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    """User response (excludes sensitive fields)"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ====== Document Collection Schemas ======
class DocumentCollectionBase(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str

class DocumentCollectionCreate(DocumentCollectionBase):
    pass

class DocumentCollection(DocumentCollectionBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====== Document Schemas ======
class DocumentBase(BaseModel):
    title: str
    content: str
    slug: str
    collection_id: Optional[int] = None
    parent_document_id: Optional[int] = None
    front_matter: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    variables: Optional[Dict[str, Any]] = {}
    status: Optional[str] = "draft"

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    front_matter: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    variables: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class Document(DocumentBase):
    id: int
    owner_id: int
    html_content: str
    version: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    asset_ids: Optional[List[int]] = []  # IDs of linked assets

    class Config:
        from_attributes = True


# ====== Document Version Schemas ======
class DocumentVersionBase(BaseModel):
    version_number: int
    title: str
    content: str
    front_matter: Optional[Dict[str, Any]] = {}
    variables: Optional[Dict[str, Any]] = {}

class DocumentVersion(DocumentVersionBase):
    id: int
    document_id: int
    html_content: str
    author_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ====== Document Comment Schemas ======
class DocumentCommentBase(BaseModel):
    content: str
    line_number: Optional[int] = None

class DocumentCommentCreate(DocumentCommentBase):
    pass

class DocumentComment(DocumentCommentBase):
    id: int
    document_id: int
    author_id: int
    resolved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====== Asset Schemas ======
class AssetBase(BaseModel):
    original_filename: str
    file_type: str
    mime_type: str

class AssetCreate(AssetBase):
    file_size: int

class Asset(AssetBase):
    id: int
    filename: str
    file_path: str
    file_size: int
    uploaded_by: int
    collection_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====== Document Redirect Schemas ======
class DocumentRedirectBase(BaseModel):
    old_slug: str
    new_document_id: int

class DocumentRedirect(DocumentRedirectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ====== Document Template Schemas ======
class DocumentTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: str
    content_template: str
    front_matter_schema: Optional[Dict[str, Any]] = {}

class DocumentTemplateCreate(DocumentTemplateBase):
    pass

class DocumentTemplate(DocumentTemplateBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ====== Document Asset Association Schemas ======
class DocumentAssetAssociation(BaseModel):
    id: int
    document_id: int
    asset_id: int

    class Config:
        from_attributes = True


# ====== Enhanced Asset Schemas ======
class AssetResponse(BaseModel):
    """Asset with detailed information"""
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    mime_type: str
    uploaded_by: int
    collection_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    """Asset list with pagination"""
    items: List['AssetResponse']
    total: int
    skip: int
    limit: int


# ====== Asset Statistics Schemas ======
class AssetStats(BaseModel):
    """Asset statistics"""
    total_assets: int
    total_storage_bytes: int
    total_storage_mb: float
    assets_by_type: Dict[str, int]