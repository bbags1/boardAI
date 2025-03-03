"""Add folder support to documents

Revision ID: add_folder_support
Revises: af6e501b8206
Create Date: 2025-03-02 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_folder_support'
down_revision = 'af6e501b8206'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to documents table
    op.add_column('documents', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('is_folder', sa.Boolean(), server_default='false', nullable=False))
    
    # Add foreign key constraint for parent_id
    op.create_foreign_key('fk_document_parent', 'documents', 'documents', ['parent_id'], ['id'])


def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('fk_document_parent', 'documents', type_='foreignkey')
    
    # Remove columns
    op.drop_column('documents', 'is_folder')
    op.drop_column('documents', 'parent_id') 