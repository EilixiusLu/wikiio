from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.page import Page
from app.models.revision import Revision
from typing import Optional
import json

router = APIRouter(prefix="/pages", tags=["页面"])

@router.get("/")
async def list_pages(
    site_id: str,
    category: Optional[str] = None,
    author: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    order_by: str = "last_edited_at",
    db: AsyncSession = Depends(get_db)
):
    """获取页面列表，支持按站点、分类、作者筛选"""
    query = select(Page).where(Page.site_id == site_id)

    if author:
        query = query.where(Page.author == author)

    if category:
        query = query.where(Page.categories.contains(category))

    if order_by == "rating":
        query = query.order_by(desc(Page.rating_avg))
    elif order_by == "word_count":
        query = query.order_by(desc(Page.word_count))
    else:
        query = query.order_by(desc(Page.last_edited_at))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    pages = result.scalars().all()

    # 把categories从JSON字符串转成列表
    output = []
    for p in pages:
        item = {
            "id": p.id,
            "site_id": p.site_id,
            "page_id": p.page_id,
            "title": p.title,
            "slug": p.slug,
            "author": p.author,
            "word_count": p.word_count,
            "categories": json.loads(p.categories) if p.categories else [],
            "rating_count": p.rating_count,
            "rating_avg": p.rating_avg,
            "last_edited_at": p.last_edited_at,
        }
        output.append(item)

    return output

@router.get("/count")
async def count_pages(
    site_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取站点页面总数"""
    result = await db.execute(
        select(func.count()).where(Page.site_id == site_id)
    )
    return {"count": result.scalar()}

@router.get("/stats")
async def get_stats(
    site_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取站点数据统计"""

    # 页面总数
    total = await db.execute(
        select(func.count()).where(Page.site_id == site_id)
    )

    # 总字数
    total_words = await db.execute(
        select(func.sum(Page.word_count)).where(Page.site_id == site_id)
    )

    # 作者数量
    author_count = await db.execute(
        select(func.count(Page.author.distinct())).where(Page.site_id == site_id)
    )

    # 编辑版本总数
    rev_count = await db.execute(
        select(func.count()).where(Revision.site_id == site_id)
    )

    return {
        "site_id": site_id,
        "total_pages": total.scalar() or 0,
        "total_words": total_words.scalar() or 0,
        "total_authors": author_count.scalar() or 0,
        "total_revisions": rev_count.scalar() or 0,
    }

@router.get("/top-authors")
async def get_top_authors(
    site_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """获取页面数量最多的作者排名"""
    result = await db.execute(
        select(Page.author, func.count().label("page_count"))
        .where(Page.site_id == site_id)
        .where(Page.author != None)
        .group_by(Page.author)
        .order_by(desc("page_count"))
        .limit(limit)
    )
    rows = result.all()
    return [{"author": r[0], "page_count": r[1]} for r in rows]

@router.get("/{page_id}")
async def get_page(
    page_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个页面详情"""
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=404, detail="页面不存在")

    # 获取最近10条编辑历史
    rev_result = await db.execute(
        select(Revision)
        .where(Revision.page_id == page.id)
        .order_by(desc(Revision.timestamp))
        .limit(10)
    )
    revisions = rev_result.scalars().all()

    return {
        "id": page.id,
        "site_id": page.site_id,
        "page_id": page.page_id,
        "title": page.title,
        "slug": page.slug,
        "author": page.author,
        "word_count": page.word_count,
        "categories": json.loads(page.categories) if page.categories else [],
        "rating_count": page.rating_count,
        "rating_avg": page.rating_avg,
        "last_edited_at": page.last_edited_at,
        "first_crawled_at": page.first_crawled_at,
        "wikitext": page.wikitext or "",
        "recent_revisions": [
            {
                "rev_id": r.rev_id,
                "editor": r.editor,
                "comment": r.comment,
                "size": r.size,
                "timestamp": r.timestamp,
            }
            for r in revisions
        ]
    }