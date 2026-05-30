"""fix is_miraheze_verified to be NOT NULL with default false

Revision ID: 0c4a2d8e1f3f
Revises: 36369c50179e
Create Date: 2026-05-30 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c4a2d8e1f3f'
down_revision: Union[str, Sequence[str], None] = '36369c50179e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 将已有 NULL 值更新为 false
    op.execute(
        "UPDATE users SET is_miraheze_verified = false "
        "WHERE is_miraheze_verified IS NULL"
    )
    # 设为 NOT NULL 并加 server_default
    op.alter_column(
        'users', 'is_miraheze_verified',
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("0"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'users', 'is_miraheze_verified',
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
    )
