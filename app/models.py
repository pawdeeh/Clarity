# app/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    role = Column(String, default="viewer")  # admin, editor, reviewer, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)

    # Relationships
    documents = relationship("Document", back_populates="owner")
    collections = relationship("DocumentCollection", back_populates="created_by_user")
    comments = relationship("DocumentComment", back_populates="author")
    assets = relationship("Asset", back_populates="uploaded_by_user")


class DocumentCollection(Base):
    __tablename__ = "document_collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String, unique=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    created_by_user = relationship("User", back_populates="collections")
    documents = relationship("Document", back_populates="collection")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    content = Column(Text)
    html_content = Column(Text)  # Stores rendered HTML content
    needs_rerender = Column(Boolean, default=False)
    
    # Hierarchy & Organization
    collection_id = Column(Integer, ForeignKey("document_collections.id"), nullable=True)
    parent_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    order = Column(Integer, default=0)  # For ordering within parent
    
    # Ownership & Collaboration
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Front Matter & Metadata
    front_matter = Column(JSON, default={})  # Store custom properties/metadata
    tags = Column(JSON, default=[])  # Array of tags
    status = Column(String, default="draft")  # draft, review, published
    
    # Versioning & History
    version = Column(Integer, default=1)
    
    # Variables & Conditionals
    variables = Column(JSON, default={})  # Variables for conditional content
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="documents")
    collection = relationship("DocumentCollection", back_populates="documents")
    parent = relationship(
        "Document",
        remote_side=[id],
        back_populates="child_documents",
        foreign_keys=[parent_document_id]
    )
    child_documents = relationship(
        "Document",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    versions = relationship("DocumentVersion", back_populates="document")
    comments = relationship("DocumentComment", back_populates="document")
    assets = relationship("Asset", secondary="document_asset_association", back_populates="documents")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    version_number = Column(Integer)
    title = Column(String)
    content = Column(Text)
    html_content = Column(Text)
    front_matter = Column(JSON, default={})
    variables = Column(JSON, default={})
    created_at = Column(DateTime, server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="versions")


class DocumentComment(Base):
    __tablename__ = "document_comments"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    line_number = Column(Integer, nullable=True)  # For inline comments
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    document = relationship("Document", back_populates="comments")
    author = relationship("User", back_populates="comments")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    original_filename = Column(String)
    file_path = Column(String)  # Path where file is stored
    file_type = Column(String)  # image, video, document, etc.
    file_size = Column(Integer)  # In bytes
    mime_type = Column(String)
    
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    collection_id = Column(Integer, ForeignKey("document_collections.id"), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    uploaded_by_user = relationship("User", back_populates="assets")
    documents = relationship("Document", secondary="document_asset_association", back_populates="assets")


class DocumentAssetAssociation(Base):
    __tablename__ = "document_asset_association"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"))


class DocumentRedirect(Base):
    __tablename__ = "document_redirects"

    id = Column(Integer, primary_key=True, index=True)
    old_slug = Column(String, unique=True, index=True)
    new_document_id = Column(Integer, ForeignKey("documents.id"))
    created_at = Column(DateTime, server_default=func.now())


class DocumentTemplate(Base):
    __tablename__ = "document_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    template_type = Column(String)  # blueprint type: guide, api_reference, faq, tutorial, etc.
    content_template = Column(Text)  # Template markdown content
    front_matter_schema = Column(JSON, default={})  # Define what front matter fields are required
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)