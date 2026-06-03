from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.site import Site
from app.routers.users import get_current_user
from app.models.user import User
from app.schemas.site import SiteCreate
from app.crawler.tasks import crawl_site_incremental, crawl_site_full
from app.utils.cache import cached, cache_delete, cache_clear_pattern
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sites", tags=["维基站点"])

@router.get("/")
@cached(ttl=300, key_prefix="sites:list")
async def list_sites(db: AsyncSession = Depends(get_db)):
    """获取所有已接入的维基站点列表"""
    result = await db.execute(
        select(Site).where(Site.status == "approved").order_by(Site.created_at)
    )
    sites = result.scalars().all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "site_id": s.site_id,
            "base_url": s.base_url,
            "description": s.description,
            "language": s.language,
            "platform": s.platform,
            "has_ratepage": s.has_ratepage,
            "rating_enabled": s.rating_enabled,
            "last_crawled_at": s.last_crawled_at,
            "status": s.status,
        }
        for s in sites
    ]

@router.get("/{site_id}")
@cached(ttl=300, key_prefix="sites:{site_id}")
async def get_site(
    site_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取单个站点详情"""
    result = await db.execute(select(Site).where(Site.site_id == site_id))
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="站点不存在")
    return site

@router.post("/", status_code=201)
async def create_site(
    data: SiteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """申请接入一个新维基站点（仅Wikiio管理员）"""
    if current_user.role < 3:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    # 检查site_id是否已存在
    result = await db.execute(select(Site).where(Site.site_id == data.site_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该站点ID已存在")

    # 根据平台自动生成API URL
    if data.platform == "fandom":
        # Fandom: https://xxx.fandom.com/zh/api.php
        api_url = data.base_url.rstrip("/") + "/api.php"
    else:
        # Miraheze: https://xxx.miraheze.org/w/api.php
        api_url = data.base_url.rstrip("/") + "/w/api.php"

    site = Site(
        name=data.name,
        site_id=data.site_id,
        api_url=api_url,
        base_url=data.base_url,
        description=data.description,
        language=data.language,
        platform=data.platform,
        has_ratepage=data.has_ratepage,
        owner_id=current_user.id,
        status="approved",
        crawl_enabled=True,
    )
    db.add(site)
    await db.commit()
    await db.refresh(site)
    # 失效站点列表缓存
    await cache_delete("sites:list")
    return site

@router.post("/{site_id}/crawl")
async def trigger_crawl(
    site_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    full: bool = False,
):
    """手动触发爬取（仅Wikiio管理员）。full=True 全量爬取，否则增量更新。"""
    if current_user.role < 3:
        raise HTTPException(status_code=403, detail="权限不足")

    result = await db.execute(select(Site).where(Site.site_id == site_id))
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="站点不存在")

    crawl_type = "全量爬取" if full else "增量更新"
    task_func = crawl_site_full if full else crawl_site_incremental

    # 优先通过 Celery 异步执行
    try:
        from app.crawler.scheduler import crawl_single_site_task
        crawl_single_site_task.delay(site_id, full=full)
        return {"message": f"已提交{crawl_type}任务: {site.name}（Celery）"}
    except Exception:
        logger.warning(
            "Celery/Redis 不可用，降级为 BackgroundTasks 执行: site=%s", site_id
        )
        background_tasks.add_task(task_func, site_id)
        return {"message": f"已开始{crawl_type}: {site.name}（降级模式）"}

@router.delete("/{site_id}")
async def delete_site(
    site_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除站点（仅Wikiio管理员）"""
    if current_user.role < 3:
        raise HTTPException(status_code=403, detail="权限不足")

    result = await db.execute(select(Site).where(Site.site_id == site_id))
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="站点不存在")

    await db.delete(site)
    await db.commit()
    # 失效站点相关缓存
    await cache_delete(f"sites:{site_id}")
    await cache_delete("sites:list")
    return {"message": f"已删除站点 {site.name}"}