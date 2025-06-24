"""Add custom basemaps table

Revision ID: custom_basemaps_001
Revises: 395e7734f751
Create Date: 2025-06-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'custom_basemaps_001'
down_revision = '395e7734f751'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create custom_basemaps table
    op.create_table('custom_basemaps',
        sa.Column('id', sa.String(length=12), nullable=False),
        sa.Column('owner_uuid', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('tile_url_template', sa.Text(), nullable=False),
        sa.Column('tile_format', sa.String(), nullable=True),
        sa.Column('min_zoom', sa.Integer(), nullable=True),
        sa.Column('max_zoom', sa.Integer(), nullable=True),
        sa.Column('tile_size', sa.Integer(), nullable=True),
        sa.Column('attribution', sa.Text(), nullable=True),
        sa.Column('bounds', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('center', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('default_zoom', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('current_timestamp'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('current_timestamp'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on owner_uuid for faster queries
    op.create_index('idx_custom_basemaps_owner', 'custom_basemaps', ['owner_uuid'])
    
    # Create index on is_public for finding public basemaps
    op.create_index('idx_custom_basemaps_public', 'custom_basemaps', ['is_public'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_custom_basemaps_public', table_name='custom_basemaps')
    op.drop_index('idx_custom_basemaps_owner', table_name='custom_basemaps')
    
    # Drop table
    op.drop_table('custom_basemaps')