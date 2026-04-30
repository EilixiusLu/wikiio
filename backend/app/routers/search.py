from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, text
from app.database import get_db
from app.models.page import Page
from app.models.revision import Revision
from typing import Optional
import json

router = APIRouter(prefix="/search", tags=["搜索"])

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
    """搜索页面，支持标题、作者、分类和Wikitext内容检索"""

    # 构建搜索条件
    search_conditions = [
        Page.title.ilike(f"%{q}%"),
        Page.author.ilike(f"%{q}%"),
    ]

    # 是否同时搜索Wikitext内容
    if search_wikitext:
        search_conditions.append(Page.wikitext.ilike(f"%{q}%"))

    query = select(Page).where(or_(*search_conditions))

    # 按站点筛选
    if site_id:
        query = query.where(Page.site_id == site_id)

    # 按作者筛选
    if author:
        query = query.where(Page.author == author)

    # 按分类筛选
    if category:
        query = query.where(Page.categories.contains(category))

    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 排序：标题匹配优先，其次是作者匹配，最后是Wikitext匹配
    if order_by == "rating":
        query = query.order_by(Page.rating_avg.desc(), Page.last_edited_at.desc())
    elif order_by == "word_count":
        query = query.order_by(Page.word_count.desc())
    else:
        query = query.order_by(Page.last_edited_at.desc())

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    pages = result.scalars().all()

    output = []
    for p in pages:
        # 判断关键词出现在哪里
        match_in = []
        if p.title and q.lower() in p.title.lower():
            match_in.append("标题")
        if p.author and q.lower() in p.author.lower():
            match_in.append("作者")
        if search_wikitext and p.wikitext and q.lower() in p.wikitext.lower():
            match_in.append("正文")
            # 提取关键词在Wikitext里的上下文片段
            wikitext_lower = p.wikitext.lower()
            idx = wikitext_lower.find(q.lower())
            start = max(0, idx - 60)
            end = min(len(p.wikitext), idx + len(q) + 60)
            snippet = p.wikitext[start:end].replace("\n", " ").strip()
            if start > 0:
                snippet = "..." + snippet
            if end < len(p.wikitext):
                snippet = snippet + "..."
        else:
            snippet = None

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
            Page.categories != "[]"
        )
    )
    rows = result.scalars().all()

    cat_count = {}
    for row in rows:
        try:
            cats = json.loads(row)
            for cat in cats:
                cat_count[cat] = cat_count.get(cat, 0) + 1
        except:
            pass

    sorted_cats = sorted(cat_count.items(), key=lambda x: x[1], reverse=True)
    return [{"name": k, "count": v} for k, v in sorted_cats[:50]]