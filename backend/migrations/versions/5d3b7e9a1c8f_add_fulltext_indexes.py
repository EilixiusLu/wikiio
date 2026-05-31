"""add full-text search indexes (pg_trgm + tsvector)

Revision ID: 5d3b7e9a1c8f
Revises: 0c4a2d8e1f3f
Create Date: 2026-06-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d3b7e9a1c8f'
down_revision: Union[str, Sequence[str], None] = '0c4a2d8e1f3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 启用 pg_trgm 扩展（加速 ILIKE / LIKE）
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # 综合搜索向量 GIN 索引（全文搜索主索引）
    op.create_index(
        op.f('idx_pages_search_vector_gin'),
        'pages',
        [sa.literal_column(
            "to_tsvector('simple'::regconfig, "
            "COALESCE(title, '') || ' ' || "
            "COALESCE(author, '') || ' ' || "
            "COALESCE(wikitext, ''))"
        )],
        unique=False,
        postgresql_using='gin',
    )

    # Trigram GIN 索引（加速 ILIKE 子串搜索，尤其对中文有效）
    op.create_index(
        op.f('idx_pages_title_trgm'),
        'pages',
        ['title'],
        unique=False,
        postgresql_using='gin',
        postgresql_ops={'title': 'gin_trgm_ops'},
    )
    op.create_index(
        op.f('idx_pages_author_trgm'),
        'pages',
        ['author'],
        unique=False,
        postgresql_using='gin',
        postgresql_ops={'author': 'gin_trgm_ops'},
    )
    op.create_index(
        op.f('idx_pages_wikitext_trgm'),
        'pages',
        ['wikitext'],
        unique=False,
        postgresql_using='gin',
        postgresql_ops={'wikitext': 'gin_trgm_ops'},
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('idx_pages_wikitext_trgm'), table_name='pages')
    op.drop_index(op.f('idx_pages_author_trgm'), table_name='pages')
    op.drop_index(op.f('idx_pages_title_trgm'), table_name='pages')
    op.drop_index(op.f('idx_pages_search_vector_gin'), table_name='pages')
