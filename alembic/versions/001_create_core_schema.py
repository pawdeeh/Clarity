"""Create core schema with users, collections, documents, and related tables

Revision ID: 001
Revises: 
Create Date: 2026-03-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create Document Collections table
    op.create_table(
        'document_collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_document_collections_id'), 'document_collections', ['id'], unique=False)
    op.create_index(op.f('ix_document_collections_name'), 'document_collections', ['name'], unique=False)
    op.create_index(op.f('ix_document_collections_slug'), 'document_collections', ['slug'], unique=True)

    # Create Documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=False),
        sa.Column('needs_rerender', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('collection_id', sa.Integer(), nullable=True),
        sa.Column('parent_document_id', sa.Integer(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('front_matter', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['collection_id'], ['document_collections.id']),
        sa.ForeignKeyConstraint(['parent_document_id'], ['documents.id']),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_title'), 'documents', ['title'], unique=False)
    op.create_index(op.f('ix_documents_slug'), 'documents', ['slug'], unique=True)

    # Create Document Versions table
    op.create_table(
        'document_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=False),
        sa.Column('front_matter', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id']),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_versions_id'), 'document_versions', ['id'], unique=False)

    # Create Document Comments table
    op.create_table(
        'document_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['author_id'], ['users.id']),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_comments_id'), 'document_comments', ['id'], unique=False)

    # Create Assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('collection_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['collection_id'], ['document_collections.id']),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assets_id'), 'assets', ['id'], unique=False)
    op.create_index(op.f('ix_assets_filename'), 'assets', ['filename'], unique=False)

    # Create Document-Asset Association table
    op.create_table(
        'document_asset_association',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id']),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create Document Redirects table
    op.create_table(
        'document_redirects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('old_slug', sa.String(), nullable=False),
        sa.Column('new_document_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['new_document_id'], ['documents.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('old_slug')
    )
    op.create_index(op.f('ix_document_redirects_id'), 'document_redirects', ['id'], unique=False)
    op.create_index(op.f('ix_document_redirects_old_slug'), 'document_redirects', ['old_slug'], unique=True)

    # Create Document Templates table
    op.create_table(
        'document_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_type', sa.String(), nullable=False),
        sa.Column('content_template', sa.Text(), nullable=False),
        sa.Column('front_matter_schema', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_templates_id'), 'document_templates', ['id'], unique=False)
    op.create_index(op.f('ix_document_templates_name'), 'document_templates', ['name'], unique=False)


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_index(op.f('ix_document_templates_name'), table_name='document_templates')
    op.drop_index(op.f('ix_document_templates_id'), table_name='document_templates')
    op.drop_table('document_templates')

    op.drop_index(op.f('ix_document_redirects_old_slug'), table_name='document_redirects')
    op.drop_index(op.f('ix_document_redirects_id'), table_name='document_redirects')
    op.drop_table('document_redirects')

    op.drop_table('document_asset_association')

    op.drop_index(op.f('ix_assets_filename'), table_name='assets')
    op.drop_index(op.f('ix_assets_id'), table_name='assets')
    op.drop_table('assets')

    op.drop_index(op.f('ix_document_comments_id'), table_name='document_comments')
    op.drop_table('document_comments')

    op.drop_index(op.f('ix_document_versions_id'), table_name='document_versions')
    op.drop_table('document_versions')

    op.drop_index(op.f('ix_documents_slug'), table_name='documents')
    op.drop_index(op.f('ix_documents_title'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')

    op.drop_index(op.f('ix_document_collections_slug'), table_name='document_collections')
    op.drop_index(op.f('ix_document_collections_name'), table_name='document_collections')
    op.drop_index(op.f('ix_document_collections_id'), table_name='document_collections')
    op.drop_table('document_collections')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
