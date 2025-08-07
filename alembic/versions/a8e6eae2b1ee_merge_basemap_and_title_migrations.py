"""merge basemap and title migrations

Revision ID: a8e6eae2b1ee
Revises: 158ce8e20754, 20250807180304
Create Date: 2025-08-07 16:01:04.320833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8e6eae2b1ee'
down_revision: Union[str, None] = ('158ce8e20754', '20250807180304')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass