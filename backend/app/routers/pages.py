from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.page import Page
from app.models.revision import Revision
from typing import Optional
from app.models.site import Site
from app.models.user import User
from app.crawler.mediawiki import MediaWikiClient
from app.utils.cache import cached
import json


router = APIRouter(prefix="/pages", tags=["页面"])

@router.get("/")
@cached(ttl=120, key_prefix="pages:list:{site_id}:{author}:{category}:{skip}:{limit}:{order_by}")
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
@cached(ttl=120, key_prefix="pages:count:{site_id}")
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
@cached(ttl=300, key_prefix="pages:stats:{site_id}")
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
@cached(ttl=300, key_prefix="pages:top-authors:{site_id}:{limit}")
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


@router.get("/rankings/by-rating")
@cached(ttl=300, key_prefix="pages:rankings:by-rating:{site_id}:{skip}:{limit}")
async def ranking_by_rating(
    site_id: str,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """按平均评分排名（至少有1人评分）"""
    result = await db.execute(
        select(Page)
        .where(Page.site_id == site_id, Page.rating_count > 0)
        .order_by(Page.rating_avg.desc(), Page.rating_count.desc())
        .offset(skip).limit(limit)
    )
    pages = result.scalars().all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "author": p.author,
            "word_count": p.word_count,
            "rating_avg": p.rating_avg,
            "rating_count": p.rating_count,
            "categories": json.loads(p.categories) if p.categories else [],
            "last_edited_at": p.last_edited_at,
        }
        for p in pages
    ]

@router.get("/rankings/by-author")
@cached(ttl=300, key_prefix="pages:rankings:by-author:{site_id}:{order_by}:{skip}:{limit}")
async def ranking_by_author(
    site_id: str,
    order_by: str = "page_count",
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """作者排名，支持按页面数量或平均评分排序"""
    if order_by == "rating":
        # 按作者所有页面的平均评分排名
        result = await db.execute(
            select(
                Page.author,
                func.count().label("page_count"),
                func.avg(Page.rating_avg).label("avg_rating"),
                func.sum(Page.word_count).label("total_words"),
            )
            .where(Page.site_id == site_id, Page.author != None)
            .group_by(Page.author)
            .order_by(desc("avg_rating"))
            .offset(skip).limit(limit)
        )
    else:
        # 按页面数量排名
        result = await db.execute(
            select(
                Page.author,
                func.count().label("page_count"),
                func.avg(Page.rating_avg).label("avg_rating"),
                func.sum(Page.word_count).label("total_words"),
            )
            .where(Page.site_id == site_id, Page.author != None)
            .group_by(Page.author)
            .order_by(desc("page_count"))
            .offset(skip).limit(limit)
        )

    rows = result.all()
    return [
        {
            "author": r.author,
            "page_count": r.page_count,
            "avg_rating": round(float(r.avg_rating), 2) if r.avg_rating else 0.0,
            "total_words": r.total_words or 0,
        }
        for r in rows
    ]

@router.get("/rankings/by-site-rating")
@cached(ttl=300, key_prefix="pages:rankings:by-site-rating:{site_id}:{skip}:{limit}")
async def ranking_by_site_rating(
    site_id: str,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """按原站 RatePage 评分排名（至少有一票）"""
    result = await db.execute(
        select(Page)
        .where(Page.site_id == site_id, Page.site_rating_count > 0)
        .order_by(Page.site_rating_avg.desc(), Page.site_rating_count.desc())
        .offset(skip).limit(limit)
    )
    pages = result.scalars().all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "author": p.author,
            "word_count": p.word_count,
            "site_rating_avg": p.site_rating_avg,
            "site_rating_count": p.site_rating_count,
            "rating_avg": p.rating_avg,
            "rating_count": p.rating_count,
            "categories": json.loads(p.categories) if p.categories else [],
            "last_edited_at": p.last_edited_at,
        }
        for p in pages
    ]

@router.get("/author/{author_name}")
@cached(ttl=120, key_prefix="pages:author:{author_name}:list:{site_id}:{skip}:{limit}")
async def get_author_pages(
    author_name: str,
    site_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取某作者的所有页面"""
    query = select(Page).where(Page.author == author_name)
    if site_id:
        query = query.where(Page.site_id == site_id)

    # 统计总数
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()

    # 分页查询
    query = query.order_by(desc(Page.rating_avg), desc(Page.last_edited_at))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    pages = result.scalars().all()

    return {
        "total": total,
        "pages": [
            {
                "id": p.id,
                "site_id": p.site_id,
                "title": p.title,
                "word_count": p.word_count,
                "categories": json.loads(p.categories) if p.categories else [],
                "rating_avg": p.rating_avg,
                "rating_count": p.rating_count,
                "last_edited_at": p.last_edited_at,
            }
            for p in pages
        ]
    }

@router.get("/author/{author_name}/stats")
@cached(ttl=300, key_prefix="pages:author:{author_name}:stats")
async def get_author_stats(
    author_name: str,
    db: AsyncSession = Depends(get_db)
):
    """获取某作者的统计数据（跨所有站点）"""
    # 按站点分组统计
    result = await db.execute(
        select(
            Page.site_id,
            func.count().label("page_count"),
            func.sum(Page.word_count).label("total_words"),
            func.avg(Page.rating_avg).label("avg_rating"),
            func.sum(Page.rating_count).label("total_ratings"),
        )
        .where(Page.author == author_name)
        .group_by(Page.site_id)
    )
    rows = result.all()

    # 获取站点名称
    site_ids = [r.site_id for r in rows]
    sites_result = await db.execute(
        select(Site).where(Site.site_id.in_(site_ids))
    )
    sites_map = {s.site_id: s.name for s in sites_result.scalars().all()}

    # 全站汇总
    total_pages = sum(r.page_count for r in rows)
    total_words = sum(r.total_words or 0 for r in rows)
    total_ratings = sum(r.total_ratings or 0 for r in rows)

    return {
        "author": author_name,
        "total_pages": total_pages,
        "total_words": total_words,
        "total_ratings": total_ratings,
        "sites": [
            {
                "site_id": r.site_id,
                "site_name": sites_map.get(r.site_id, r.site_id),
                "page_count": r.page_count,
                "total_words": r.total_words or 0,
                "avg_rating": round(float(r.avg_rating), 2) if r.avg_rating else 0.0,
                "total_ratings": r.total_ratings or 0,
            }
            for r in rows
        ]
    }   
@router.get("/author/{author_name}/profile")
@cached(ttl=600, key_prefix="pages:author:{author_name}:profile")
async def get_author_profile(
    author_name: str,
    db: AsyncSession = Depends(get_db)
):
    """获取作者的Wikiio账户信息（头像等）"""
    result = await db.execute(
        select(User).where(
            User.fandom_username == author_name,
            User.is_fandom_verified == True
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        return {"has_account": False, "avatar_url": None}
    return {
        "has_account": True,
        "avatar_url": user.fandom_avatar_url,
        "username": user.username,
    }

@router.get("/{page_id}")
@cached(ttl=300, key_prefix="page:{page_id}")
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

@router.get("/{page_id}/site-rating")
@cached(ttl=600, key_prefix="page:{page_id}:site-rating")
async def get_site_rating(
    page_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取页面在原站的RatePage评分（仅对启用了RatePage扩展的维基有效）"""
    # 查找页面
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="页面不存在")

    # 查找站点，检查是否启用了RatePage
    site_result = await db.execute(
        select(Site).where(Site.site_id == page.site_id)
    )
    site = site_result.scalar_one_or_none()
    if not site or not site.has_ratepage:
        return {"available": False, "reason": "该站点未启用RatePage扩展"}

    # 调用MediaWiki API获取评分
    client = MediaWikiClient(site.api_url, requests_per_second=2.0)
    rating = await client.get_page_rating(page.page_id)

    if not rating:
        return {"available": False, "reason": "无法获取原站评分"}

    return {
        "available": True,
        "total_votes": rating["total_votes"],
        "total_points": rating["total_points"],
        "avg_rating": rating["avg_rating"],
        "scale": rating.get("scale", 10),
        "distribution": rating.get("distribution"),
    }