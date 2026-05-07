from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.rating import Rating
from app.models.page import Page
from app.models.user import User
from app.routers.users import get_current_user
from app.utils.logger import rating_logger

router = APIRouter(prefix="/ratings", tags=["评分"])

@router.get("/page/{page_id}")
async def get_page_rating(
    page_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取页面的评分统计"""
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="页面不存在")

    return {
        "page_id": page_id,
        "rating_avg": page.rating_avg,
        "rating_count": page.rating_count,
    }

@router.get("/page/{page_id}/mine")
async def get_my_rating(
    page_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户对某页面的评分"""
    result = await db.execute(
        select(Rating).where(
            Rating.page_id == page_id,
            Rating.user_id == current_user.id
        )
    )
    rating = result.scalar_one_or_none()
    if not rating:
        return {"score": None}
    return {"score": rating.score}

@router.post("/page/{page_id}")
async def rate_page(
    page_id: int,
    score: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """对页面评分（需要绑定Fandom账户）"""

    # 必须绑定Fandom账户才能评分
    if not current_user.is_fandom_verified:
        raise HTTPException(status_code=403, detail="请先绑定Fandom账户才能评分")

    # 验证分数范围
    if not 1 <= score <= 5:
        raise HTTPException(status_code=400, detail="评分必须在1-5之间")

    # 检查页面是否存在
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="页面不存在")

    # 检查站点是否开放评分
    from app.models.site import Site
    site_result = await db.execute(select(Site).where(Site.site_id == page.site_id))
    site = site_result.scalar_one_or_none()
    if site and not site.rating_enabled:
        raise HTTPException(status_code=403, detail="该站点未开放评分功能")

    # 查找是否已评过分
    result = await db.execute(
        select(Rating).where(
            Rating.page_id == page_id,
            Rating.user_id == current_user.id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # 修改评分
        existing.previous_score = existing.score
        existing.score = score
        existing.updated_count += 1
    else:
        # 新增评分
        new_rating = Rating(
            user_id=current_user.id,
            page_id=page_id,
            site_id=page.site_id,
            score=score,
        )
        db.add(new_rating)

    await db.flush()

    # 重新计算页面平均分和评分人数
    stats = await db.execute(
        select(
            func.count().label("count"),
            func.avg(Rating.score).label("avg")
        ).where(Rating.page_id == page_id)
    )
    row = stats.one()
    page.rating_count = row.count
    page.rating_avg = round(float(row.avg), 2)

    await db.commit()

    rating_logger.info(
        f"user={current_user.id}({current_user.fandom_username}) "
        f"page={page_id}({page.title}) "
        f"score={score} "
        f"site={page.site_id}"
    )

    return {
        "message": "评分成功",
        "score": score,
        "rating_avg": page.rating_avg,
        "rating_count": page.rating_count,
    }

@router.delete("/page/{page_id}")
async def delete_rating(
    page_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除自己的评分"""
    result = await db.execute(
        select(Rating).where(
            Rating.page_id == page_id,
            Rating.user_id == current_user.id
        )
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(status_code=404, detail="你还没有对该页面评分")

    await db.delete(rating)

    # 更新页面评分统计
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    if page:
        stats = await db.execute(
            select(
                func.count().label("count"),
                func.avg(Rating.score).label("avg")
            ).where(Rating.page_id == page_id)
        )
        row = stats.one()
        page.rating_count = row.count or 0
        page.rating_avg = round(float(row.avg), 2) if row.avg else 0.0

    await db.commit()
    return {"message": "已删除评分"}