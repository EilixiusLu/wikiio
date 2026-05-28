import httpx
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MediaWikiClient:
    """封装MediaWiki API的所有请求，支持礼貌爬取限速"""

    def __init__(self, api_url: str, requests_per_second: float = 0.5):
        self.api_url = api_url
        self.delay = 1.0 / requests_per_second
        self._last_request_time = 0.0
        self.headers = {
                "User-Agent": "Wikiio/0.1 (Wiki data analysis platform; dec_verniy@hotmail.com; polite crawler)"
        }

    async def _request(self, params: dict) -> Optional[dict]:
        """发送一次API请求，自动限速"""
        now = asyncio.get_event_loop().time()
        wait = self.delay - (now - self._last_request_time)
        if wait > 0:
            await asyncio.sleep(wait)

        params["format"] = "json"
        params["utf8"] = "1"

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
                response = await client.get(self.api_url, params=params)
                response.raise_for_status()
                self._last_request_time = asyncio.get_event_loop().time()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"请求异常: {e}")
            return None

    async def get_site_info(self) -> Optional[dict]:
        """获取维基基本信息"""
        data = await self._request({
            "action": "query",
            "meta": "siteinfo",
            "siprop": "general|statistics",
        })
        if data:
            return data.get("query", {})
        return None

    async def get_all_pages(self, namespace: int = 0, limit: int = 500) -> list:
        """获取维基所有页面列表（分页自动翻页）"""
        pages = []
        apcontinue = None

        while True:
            params = {
                "action": "query",
                "list": "allpages",
                "apnamespace": namespace,
                "aplimit": limit,
                "approp": "ids|title",
            }
            if apcontinue:
                params["apcontinue"] = apcontinue

            data = await self._request(params)
            if not data:
                break

            batch = data.get("query", {}).get("allpages", [])
            pages.extend(batch)
            logger.info(f"已获取 {len(pages)} 个页面...")

            if "continue" in data:
                apcontinue = data["continue"].get("apcontinue")
            else:
                break

        return pages

    async def get_page_content(self, title: str) -> Optional[dict]:
        """获取单个页面的Wikitext内容和基本信息"""
        data = await self._request({
            "action": "query",
            "titles": title,
            "prop": "revisions|categories|info",
            "rvprop": "content|user|userid|timestamp|ids",
            "rvlimit": 1,
            "inprop": "url",
            "cllimit": 500,
        })
        if not data:
            return None

        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()))

        if "missing" in page:
            return None

        return page

    async def get_page_revisions(self, title: str, limit: int = 500) -> list:
        """获取页面的完整编辑历史"""
        revisions = []
        rvcontinue = None

        while True:
            params = {
                "action": "query",
                "titles": title,
                "prop": "revisions",
                "rvprop": "ids|user|userid|timestamp|size|comment",
                "rvlimit": limit,
                "rvdir": "newer",
            }
            if rvcontinue:
                params["rvcontinue"] = rvcontinue

            data = await self._request(params)
            if not data:
                break

            pages = data.get("query", {}).get("pages", {})
            page = next(iter(pages.values()))
            batch = page.get("revisions", [])
            revisions.extend(batch)

            if "continue" in data:
                rvcontinue = data["continue"].get("rvcontinue")
            else:
                break

        return revisions

    async def get_recent_changes(self, minutes: int = 60, namespace: int = 0) -> list:
        """获取最近发生变动的页面（用于增量更新）"""
        from datetime import datetime, timedelta, timezone
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        rcstart = since.strftime("%Y-%m-%dT%H:%M:%SZ")

        data = await self._request({
            "action": "query",
            "list": "recentchanges",
            "rcnamespace": namespace,
            "rcstart": rcstart,
            "rclimit": 500,
            "rcprop": "title|ids|timestamp|user",
            "rctype": "edit|new",
            "rcdir": "newer",
        })
        if not data:
            return []

        return data.get("query", {}).get("recentchanges", [])
    
    async def get_page_rating(self, page_id: int) -> Optional[dict]:
        """通过RatePage扩展API获取页面原站评分"""
        data = await self._request({
            "action": "query",
            "prop": "pagerating",
            "pageids": page_id,
        })
        if not data:
            return None

        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()), None)
        if not page:
            return None

        rating_data = page.get("pagerating", {})
        if not rating_data:
            return None

        return {
            "total_votes": rating_data.get("total_votes", 0),
            "total_points": rating_data.get("total_points", 0),
            "avg_rating": rating_data.get("avg_rating", 0),
        }