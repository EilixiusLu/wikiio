from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.database import get_db
from app.models.page import Page
from typing import Optional
import json

router = APIRouter(prefix="/search", tags=["搜索"])

@router.get("/")
async def search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    site_id: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """搜索页面，支持按标题、作者、分类筛选"""

    # 基础查询：标题或作者包含关键词
    query = select(Page).where(
        or_(
            Page.title.ilike(f"%{q}%"),
            Page.author.ilike(f"%{q}%"),
        )
    )

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

    # 分页
    query = query.order_by(Page.last_edited_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    pages = result.scalars().all()

    output = []
    for p in pages:
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
        })

    return {
        "total": total,
        "results": output,
        "skip": skip,
        "limit": limit,
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

    # 统计每个分类出现次数
    cat_count = {}
    for row in rows:
        try:
            cats = json.loads(row)
            for cat in cats:
                cat_count[cat] = cat_count.get(cat, 0) + 1
        except:
            pass

    # 按出现次数排序
    sorted_cats = sorted(cat_count.items(), key=lambda x: x[1], reverse=True)
    return [{"name": k, "count": v} for k, v in sorted_cats[:50]]