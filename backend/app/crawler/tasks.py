import asyncio
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.site import Site
from app.models.page import Page
from app.models.revision import Revision
from app.crawler.mediawiki import MediaWikiClient

logger = logging.getLogger(__name__)

def utcnow():
    """返回不带时区信息的UTC时间（适配数据库TIMESTAMP WITHOUT TIME ZONE）"""
    return datetime.utcnow()

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
        client = MediaWikiClient(site.api_url, requests_per_second=0.5)

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

async def crawl_site_incremental(site_id: str):
    """增量更新：只爬取最近60分钟内发生变动的页面"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Site).where(Site.site_id == site_id))
        site = result.scalar_one_or_none()
        if not site:
            return

        logger.info(f"开始增量更新: {site.name}")
        client = MediaWikiClient(site.api_url, requests_per_second=0.5)

        recent = await client.get_recent_changes(minutes=60)
        logger.info(f"发现 {len(recent)} 个最近变动页面")

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