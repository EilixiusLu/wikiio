"""add site_rating_avg and site_rating_count to pages

Revision ID: 6a8f9c1d2e3a
Revises: 5d3b7e9a1c8f
Create Date: 2026-06-07 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a8f9c1d2e3a'
down_revision: Union[str, Sequence[str], None] = '5d3b7e9a1c8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'pages',
        sa.Column('site_rating_avg', sa.Float(), nullable=True)
    )
    op.add_column(
        'pages',
        sa.Column('site_rating_count', sa.Integer(), server_default='0', nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('pages', 'site_rating_count')
    op.drop_column('pages', 'site_rating_avg')
