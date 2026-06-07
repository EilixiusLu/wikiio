import asyncio
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.config import settings
from app.models.site import Site
from app.models.page import Page
from app.models.revision import Revision
from app.crawler.mediawiki import MediaWikiClient
from app.utils.logger import crawler_logger as logger
from app.utils.cache import cache_delete, cache_clear_pattern


def utcnow():
    """返回不带时区信息的UTC时间（适配数据库TIMESTAMP WITHOUT TIME ZONE）"""
    return datetime.now(timezone.utc).replace(tzinfo=None)

def parse_timestamp(ts: str) -> datetime:
    """把MediaWiki返回的时间字符串转换为不带时区的datetime"""
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.replace(tzinfo=None)  # 去掉时区信息

async def crawl_site_full(site_id: str):
    """对一个维基站点进行全量爬取"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Site).where(Site.site_id == site_id))
        site = result.scalar_one_or_none()
        if not site:
            logger.error(f"站点不存在: {site_id}")
            return

        logger.info(f"开始全量爬取站点: {site.name} ({site.api_url})")
        client = MediaWikiClient(site.api_url, requests_per_second=settings.CRAWL_REQUESTS_PER_SECOND)

        logger.info("正在获取页面列表...")
        all_pages = await client.get_all_pages(namespace=0)
        logger.info(f"共发现 {len(all_pages)} 个页面")

        success = 0
        for i, page_info in enumerate(all_pages):
            title = page_info["title"]
            logger.info(f"[{i+1}/{len(all_pages)}] 正在爬取: {title}")
            try:
                await crawl_single_page(db, site, client, title)
                success += 1
            except Exception as e:
                logger.error(f"爬取页面失败 {title}: {e}")

        site.last_crawled_at = utcnow()
        await db.commit()
        logger.info(f"全量爬取完成！成功: {success}/{len(all_pages)}")

async def crawl_single_page(
    db: AsyncSession,
    site: Site,
    client: MediaWikiClient,
    title: str
):
    """爬取单个页面的内容和历史"""
    page_data = await client.get_page_content(title)
    if not page_data:
        return

    page_id = page_data["pageid"]
    revisions = page_data.get("revisions", [])
    categories = page_data.get("categories", [])

    if not revisions:
        return

    # revisions[0]是最新版本（rvlimit=1获取的），用于获取当前内容
    latest_rev = revisions[0]
    wikitext = latest_rev.get("*", "") or latest_rev.get("content", "") or ""
    last_edited = latest_rev.get("timestamp", None)

    # 获取完整历史的第一条来确定真正的作者
    all_revisions_for_author = await client.get_page_revisions(title)
    if all_revisions_for_author:
        first_rev = all_revisions_for_author[0]  # 最早的版本
        author = first_rev.get("user", "")
        author_id = first_rev.get("userid", None)
    else:
        author = latest_rev.get("user", "")
        author_id = latest_rev.get("userid", None)

    cat_list = [c["title"].replace("Category:", "") for c in categories]
    categories_json = json.dumps(cat_list, ensure_ascii=False)

    word_count = len(wikitext.replace(" ", "").replace("\n", ""))
    slug = title.replace(" ", "_")

    result = await db.execute(
        select(Page).where(
            Page.site_id == site.site_id,
            Page.page_id == page_id
        )
    )
    existing_page = result.scalar_one_or_none()

    if existing_page:
        existing_page.wikitext = wikitext
        existing_page.word_count = word_count
        existing_page.categories = categories_json
        existing_page.last_crawled_at = utcnow()
        if last_edited:
            existing_page.last_edited_at = parse_timestamp(last_edited)
        db_page = existing_page
    else:
        db_page = Page(
            site_id=site.site_id,
            page_id=page_id,
            title=title,
            slug=slug,
            author=author,
            author_id=author_id,
            wikitext=wikitext,
            word_count=word_count,
            categories=categories_json,
            namespace=0,
            last_edited_at=parse_timestamp(last_edited) if last_edited else None,
        )
        db.add(db_page)
        await db.flush()

    for rev in all_revisions_for_author:
        result = await db.execute(
            select(Revision).where(
                Revision.site_id == site.site_id,
                Revision.rev_id == rev["revid"]
            )
        )
        if result.scalar_one_or_none():
            continue

        db_rev = Revision(
            page_id=db_page.id,
            site_id=site.site_id,
            rev_id=rev["revid"],
            parent_rev_id=rev.get("parentid"),
            editor=rev.get("user", ""),
            editor_id=rev.get("userid"),
            comment=rev.get("comment", ""),
            size=rev.get("size", 0),
            timestamp=parse_timestamp(rev["timestamp"]),
        )
        db.add(db_rev)

    await db.commit()

    # --- 原站 RatePage 评分 ---
    if site.has_ratepage:
        try:
            rating = await client.get_page_rating(page_id)
            if rating:
                db_page.site_rating_avg = rating["avg_rating"]
                db_page.site_rating_count = rating["total_votes"]
                await db.commit()
        except Exception as e:
            logger.warning(f"获取原站评分失败 {title}: {e}")

    # --- 缓存失效 ---
    try:
        await cache_delete(f"page:{db_page.id}")
        await cache_delete(f"page:{db_page.id}:site-rating")
        await cache_clear_pattern(f"pages:list:{site.site_id}:*")
        await cache_clear_pattern(f"pages:count:{site.site_id}*")
        await cache_clear_pattern(f"pages:stats:{site.site_id}*")
        await cache_clear_pattern(f"pages:top-authors:{site.site_id}:*")
        await cache_clear_pattern("pages:rankings:*")
        if db_page.author:
            await cache_clear_pattern(f"pages:author:{db_page.author}:*")
        await cache_delete(f"search:categories:{site.site_id}")
    except Exception:
        pass

async def crawl_site_incremental(site_id: str):
    """增量更新：只爬取最近60分钟内发生变动的页面"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Site).where(Site.site_id == site_id))
        site = result.scalar_one_or_none()
        if not site:
            return

        logger.info(f"开始增量更新: {site.name}")
        client = MediaWikiClient(site.api_url, requests_per_second=settings.CRAWL_REQUESTS_PER_SECOND)

        recent = await client.get_recent_changes(minutes=settings.CRAWL_INCREMENTAL_WINDOW_MINUTES)
        logger.info(f"发现 {len(recent)} 个最近变动页面（窗口={settings.CRAWL_INCREMENTAL_WINDOW_MINUTES}分钟）")

        titles = list({rc["title"] for rc in recent})
        for title in titles:
            try:
                await crawl_single_page(db, site, client, title)
                logger.info(f"增量更新完成: {title}")
            except Exception as e:
                logger.error(f"增量更新失败 {title}: {e}")

        site.last_crawled_at = utcnow()
        await db.commit()
        logger.info("增量更新完成")


async def crawl_all_sites_incremental() -> dict:
    """
    遍历所有已启用爬取的站点，串行执行增量更新。

    站点之间有固定延迟以保护源服务器不被封 IP。
    返回执行统计：{total, success, failed, pages}

    注意：此函数由 Celery 调度器或手动触发调用，不经过 FastAPI 请求生命周期。
    """
    stats = {"total": 0, "success": 0, "failed": 0, "pages": 0}

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Site).where(
                Site.crawl_enabled == True,
                Site.status == "approved",
            )
        )
        sites = result.scalars().all()

    stats["total"] = len(sites)
    logger.info(f"批量增量爬取: 发现 {len(sites)} 个待处理站点")

    for i, site in enumerate(sites):
        logger.info(
            f"[{i+1}/{len(sites)}] 站点: {site.name} ({site.site_id})"
        )
        try:
            await crawl_site_incremental(site.site_id)
            stats["success"] += 1
        except Exception as e:
            logger.error(f"增量更新站点 {site.name} 失败: {e}")
            stats["failed"] += 1

        # 站间延迟：避免短时间连续请求同一目标 IP 域
        if i < len(sites) - 1:
            delay = settings.CRAWL_INTER_SITE_DELAY_SECONDS
            logger.info(
                f"等待 {delay}s 后处理下一个站点（保护源服务器）..."
            )
            await asyncio.sleep(delay)

    logger.info(
        f"批量增量爬取完成: success={stats['success']}, "
        f"failed={stats['failed']}, total={stats['total']}"
    )
    return stats