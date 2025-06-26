"""add_soft_deleted_at_to_remaining_tables

Revision ID: 468ded7b8d7b
Revises: 978c47f3de28
Create Date: 2025-06-26 12:16:59.537034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '468ded7b8d7b'
down_revision: Union[str, None] = '978c47f3de28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add soft_deleted_at columns to tables that need them
    op.add_column('map_layers', sa.Column('soft_deleted_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('layer_styles', sa.Column('soft_deleted_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('map_layer_styles', sa.Column('soft_deleted_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('custom_basemaps', sa.Column('soft_deleted_at', sa.TIMESTAMP(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove soft_deleted_at columns
    op.drop_column('custom_basemaps', 'soft_deleted_at')
    op.drop_column('map_layer_styles', 'soft_deleted_at')
    op.drop_column('layer_styles', 'soft_deleted_at')
    op.drop_column('map_layers', 'soft_deleted_at')