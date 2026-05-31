"""搜索 API —— PostgreSQL 全文搜索 + trigram ILIKE 混合检索

- PostgreSQL: tsvector @@ tsquery (全文索引) OR trigram ILIKE (子串)
- SQLite (测试): 回退为纯 ILIKE
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, text
from app.database import get_db
from app.models.page import Page
from typing import Optional
import json

router = APIRouter(prefix="/search", tags=["搜索"])


def _is_postgresql(db: AsyncSession) -> bool:
    """是否为 PostgreSQL 数据库（trigram / tsvector 才可用）"""
    return db.get_bind().dialect.name == "postgresql"


def _build_search_conditions(
    q: str, is_pg: bool, search_wikitext: bool = True
):
    """构建混合搜索条件。is_pg=True 时使用 tsvector@@tsquery + ILIKE；
    is_pg=False（SQLite）时退化纯 ILIKE。

    Returns (condition, ts_rank_expr_or_null)
    """
    # ---------- ILIKE 子串匹配（所有数据库通用，trigram / trigram 索引加速）----------
    ilike_conds = [Page.title.ilike(f"%{q}%"), Page.author.ilike(f"%{q}%")]
    if search_wikitext:
        ilike_conds.append(Page.wikitext.ilike(f"%{q}%"))
    ilike_match = or_(*ilike_conds)

    if not is_pg:
        return ilike_match, None

    # ---------- PostgreSQL-only: 全文搜索 ----------
    search_vector = func.to_tsvector(
        text("'simple'"),
        func.coalesce(Page.title, "") + " " +
        func.coalesce(Page.author, "") + " " +
        func.coalesce(Page.wikitext, ""),
    )
    ts_query = func.plainto_tsquery(text("'simple'"), q)
    ts_match = search_vector.op("@@")(ts_query)
    ts_rank = func.ts_rank(search_vector, ts_query)

    # 混合: 全文匹配 OR 子串匹配
    return or_(ts_match, ilike_match), ts_rank


@router.get("/")
async def search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    site_id: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None,
    search_wikitext: bool = True,
    order_by: str = "last_edited_at",
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """搜索页面: tsquery 全文匹配 + trigram ILIKE 混合检索"""
    is_pg = _is_postgresql(db)
    main_condition, ts_rank_expr = _build_search_conditions(
        q, is_pg, search_wikitext
    )

    query = select(Page).where(main_condition)

    if site_id:
        query = query.where(Page.site_id == site_id)
    if author:
        query = query.where(Page.author == author)
    if category:
        query = query.where(Page.categories.contains(category))

    # 统计
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 排序
    if order_by == "rating":
        query = query.order_by(Page.rating_avg.desc(), Page.last_edited_at.desc())
    elif order_by == "word_count":
        query = query.order_by(Page.word_count.desc())
    elif order_by == "relevance" and is_pg:
        query = query.order_by(ts_rank_expr.desc(), Page.last_edited_at.desc())
    else:
        # 默认：相关度优先（如有全文索引），其次最新编辑
        if ts_rank_expr is not None:
            query = query.order_by(ts_rank_expr.desc(), Page.last_edited_at.desc())
        else:
            query = query.order_by(Page.last_edited_at.desc())

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    pages = result.scalars().all()

    # 组装输出
    q_lower = q.lower()
    output = []
    for p in pages:
        match_in = []
        snippet = None

        if p.title and q_lower in p.title.lower():
            match_in.append("标题")
        if p.author and q_lower in p.author.lower():
            match_in.append("作者")
        if search_wikitext and p.wikitext and q_lower in p.wikitext.lower():
            match_in.append("正文")
            idx = p.wikitext.lower().find(q_lower)
            if idx == -1:
                idx = 0
            start = max(0, idx - 60)
            end = min(len(p.wikitext), idx + len(q) + 60)
            snippet = p.wikitext[start:end].replace("\n", " ").strip()
            if start > 0:
                snippet = "..." + snippet
            if end < len(p.wikitext):
                snippet = snippet + "..."

        output.append({
            "id": p.id,
            "site_id": p.site_id,
            "title": p.title,
            "author": p.author,
            "word_count": p.word_count,
            "categories": json.loads(p.categories) if p.categories else [],
            "rating_avg": p.rating_avg,
            "rating_count": p.rating_count,
            "last_edited_at": p.last_edited_at,
            "match_in": match_in,
            "snippet": snippet,
        })

    return {
        "total": total,
        "results": output,
        "skip": skip,
        "limit": limit,
        "search_wikitext": search_wikitext,
    }


@router.get("/categories")
async def list_categories(
    site_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取站点所有分类列表"""
    result = await db.execute(
        select(Page.categories).where(
            Page.site_id == site_id,
            Page.categories != None,
            Page.categories != "[]",
        )
    )
    rows = result.scalars().all()

    cat_count = {}
    for row in rows:
        try:
            cats = json.loads(row)
            for cat in cats:
                cat_count[cat] = cat_count.get(cat, 0) + 1
        except Exception:
            pass

    sorted_cats = sorted(cat_count.items(), key=lambda x: x[1], reverse=True)
    return [{"name": k, "count": v} for k, v in sorted_cats[:50]]
