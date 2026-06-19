"""add_email_verify_token_expires_at_to_users

Revision ID: f03c0ab9ac4a
Revises: 6a8f9c1d2e3a
Create Date: 2026-06-20 01:50:46.478185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f03c0ab9ac4a'
down_revision: Union[str, Sequence[str], None] = '6a8f9c1d2e3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('email_verify_token_expires_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('users', 'email_verify_token_expires_at')
