from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.database import get_db
from app.models.user import User
from app.models.page import Page
from app.models.rating import Rating
from app.models.site import Site
from app.routers.users import get_current_user
from pathlib import Path
import os

router = APIRouter(prefix="/admin", tags=["后台管理"])

def require_admin(current_user: User = Depends(get_current_user)):
    """要求Wikiio管理员权限"""
    if current_user.role < 3:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

@router.get("/stats")
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取系统整体统计数据"""
    total_users = await db.execute(select(func.count()).select_from(User))
    verified_users = await db.execute(
        select(func.count()).where(User.is_fandom_verified == True)
    )
    total_pages = await db.execute(select(func.count()).select_from(Page))
    total_ratings = await db.execute(select(func.count()).select_from(Rating))
    total_sites = await db.execute(
        select(func.count()).where(Site.status == "approved")
    )

    return {
        "total_users": total_users.scalar(),
        "verified_users": verified_users.scalar(),
        "total_pages": total_pages.scalar(),
        "total_ratings": total_ratings.scalar(),
        "total_sites": total_sites.scalar(),
    }

@router.get("/logs/{log_type}")
async def get_logs(
    log_type: str,
    lines: int = 100,
    current_user: User = Depends(require_admin)
):
    """读取最新的日志内容"""
    allowed = ["access", "crawler", "rating", "error"]
    if log_type not in allowed:
        raise HTTPException(status_code=400, detail="无效的日志类型")

    log_file = Path(__file__).parent.parent.parent.parent / "logs" / f"{log_type}.log"

    if not log_file.exists():
        return {"lines": [], "message": "日志文件不存在或暂无记录"}

    # 读取最后N行
    with open(log_file, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
        last_lines = all_lines[-lines:]

    return {
        "log_type": log_type,
        "total_lines": len(all_lines),
        "lines": [l.rstrip() for l in last_lines]
    }

@router.get("/sites")
async def list_all_sites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取所有站点（包括待审核的）"""
    result = await db.execute(select(Site).order_by(Site.created_at.desc()))
    sites = result.scalars().all()
    return sites

@router.post("/sites/{site_id}/approve")
async def approve_site(
    site_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """审核通过一个站点申请"""
    result = await db.execute(select(Site).where(Site.site_id == site_id))
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="站点不存在")
    site.status = "approved"
    site.crawl_enabled = True
    await db.commit()
    return {"message": f"站点 {site.name} 已审核通过"}

@router.post("/sites/{site_id}/reject")
async def reject_site(
    site_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """拒绝一个站点申请"""
    result = await db.execute(select(Site).where(Site.site_id == site_id))
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="站点不存在")
    site.status = "rejected"
    await db.commit()
    return {"message": f"站点 {site.name} 已拒绝"}