"""add custom basemaps table

Revision ID: 20250807180304
Revises: fad2e5b46554
Create Date: 2025-08-07 18:03:04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250807180304'
down_revision = 'fad2e5b46554'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create custom_basemaps table
    op.create_table('custom_basemaps',
        sa.Column('id', sa.String(length=12), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('owner_uuid', postgresql.UUID(), nullable=False),
        sa.Column('project_id', sa.String(length=12), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('attribution', sa.Text(), nullable=True),
        sa.Column('min_zoom', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('max_zoom', sa.Integer(), nullable=True, server_default='22'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['user_mundiai_projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on owner_uuid for faster queries
    op.create_index('idx_custom_basemaps_owner', 'custom_basemaps', ['owner_uuid'])
    
    # Create index on project_id for faster queries
    op.create_index('idx_custom_basemaps_project', 'custom_basemaps', ['project_id'])
    
    # Create index on is_public for finding public basemaps
    op.create_index('idx_custom_basemaps_public', 'custom_basemaps', ['is_public'])
    
    # Create index on is_default for finding default basemaps
    op.create_index('idx_custom_basemaps_default', 'custom_basemaps', ['is_default'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_custom_basemaps_default', table_name='custom_basemaps')
    op.drop_index('idx_custom_basemaps_public', table_name='custom_basemaps')
    op.drop_index('idx_custom_basemaps_project', table_name='custom_basemaps')
    op.drop_index('idx_custom_basemaps_owner', table_name='custom_basemaps')
    
    # Drop table
    op.drop_table('custom_basemaps')