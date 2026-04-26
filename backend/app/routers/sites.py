from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.site import Site
from app.routers.users import get_current_user
from app.models.user import User
from app.crawler.tasks import crawl_site_full
import asyncio

router = APIRouter(prefix="/sites", tags=["维基站点"])

@router.get("/")
async def list_sites(db: AsyncSession = Depends(get_db)):
    """获取所有已接入的维基站点列表"""
    result = await db.execute(
        select(Site).where(Site.status == "approved")
    )
    return result.scalars().all()

@router.post("/")
async def create_site(
    name: str,
    site_id: str,
    api_url: str,
    base_url: str,
    description: str = "",
    language: str = "zh",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """申请接入一个新维基站点（需要登录）"""
    # 检查site_id是否已存在
    result = await db.execute(select(Site).where(Site.site_id == site_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该站点ID已存在")

    site = Site(
        name=name,
        site_id=site_id,
        api_url=api_url,
        base_url=base_url,
        description=description,
        language=language,
        owner_id=current_user.id,
        status="pending",
    )
    db.add(site)
    await db.commit()
    await db.refresh(site)
    return site

@router.post("/{site_id}/crawl")
async def trigger_crawl(
    site_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """手动触发一次全量爬取（需要登录，仅Wikiio管理员可用）"""
    if current_user.role < 3:
        raise HTTPException(status_code=403, detail="权限不足")

    result = await db.execute(select(Site).where(Site.site_id == site_id))
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="站点不存在")

    # 在后台异步执行爬取，不阻塞API响应
    background_tasks.add_task(crawl_site_full, site_id)

    return {"message": f"已开始爬取站点 {site.name}，请稍后查看结果"}