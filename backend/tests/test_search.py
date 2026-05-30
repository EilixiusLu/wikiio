"""测试搜索相关 API"""


class TestSearch:
    URL = "/api/v1/search/"

    async def test_search_by_title(self, client, sample_pages):
        """搜索标题"""
        resp = await client.get(self.URL, params={"q": "测试页面一"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert any(r["title"] == "测试页面一" for r in data["results"])

    async def test_search_by_author(self, client, sample_pages):
        """搜索作者"""
        resp = await client.get(self.URL, params={"q": "作者B"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert all("作者B" in r["author"] for r in data["results"])

    async def test_search_by_wikitext(self, client, sample_pages):
        """搜索正文"""
        resp = await client.get(
            self.URL,
            params={"q": "第一篇测试页面", "search_wikitext": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        # 匹配结果应有 snippet
        assert any(r.get("snippet") for r in data["results"])

    async def test_search_no_results(self, client, sample_pages):
        """无匹配返回 total=0"""
        resp = await client.get(
            self.URL,
            params={"q": "不存在的关键词xyz"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert len(data["results"]) == 0

    async def test_search_with_site_filter(self, client, sample_pages, db_session):
        """按站点筛选"""
        from app.models.site import Site
        from app.models.page import Page

        # 创建另一个站点和页面
        other_site = Site(
            name="其他维基",
            site_id="other-wiki",
            api_url="https://other.fandom.com/api.php",
            base_url="https://other.fandom.com",
            status="approved",
        )
        db_session.add(other_site)
        await db_session.flush()

        other_page = Page(
            site_id="other-wiki",
            page_id=2001,
            title="测试页面一",
            slug="测试页面一",
            author="作者C",
            wikitext="其他站点的内容",
            word_count=5,
            namespace=0,
        )
        db_session.add(other_page)
        await db_session.commit()

        # 不加 site 筛选应找到 2 条
        resp = await client.get(self.URL, params={"q": "测试页面一"})
        assert resp.json()["total"] == 2

        # 按 site 筛选
        resp = await client.get(
            self.URL,
            params={"q": "测试页面一", "site_id": "other-wiki"},
        )
        assert resp.json()["total"] == 1

    async def test_search_without_wikitext(self, client, sample_pages):
        """关闭正文搜索时，只匹配标题和作者"""
        resp = await client.get(
            self.URL,
            params={"q": "正文内容", "search_wikitext": False},
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    async def test_search_pagination(self, client, sample_pages):
        """分页 — 只有2页匹配"测试"（测试页面一/二），skip=2 后无更多结果"""
        resp = await client.get(
            self.URL,
            params={"q": "测试", "limit": 2},
        )
        assert resp.status_code == 200
        assert len(resp.json()["results"]) == 2

        resp2 = await client.get(
            self.URL,
            params={"q": "测试", "skip": 2, "limit": 2},
        )
        assert len(resp2.json()["results"]) == 0

    async def test_search_order_by_rating(self, client, sample_pages):
        """按评分排序"""
        resp = await client.get(
            self.URL,
            params={"q": "测试", "order_by": "rating"},
        )
        assert resp.status_code == 200
        results = resp.json()["results"]
        if len(results) > 1:
            ratings = [r["rating_avg"] for r in results]
            assert ratings == sorted(ratings, reverse=True)

    async def test_search_empty_query(self, client):
        """空搜索关键词应返回 422"""
        resp = await client.get(self.URL, params={"q": ""})
        assert resp.status_code == 422


class TestCategories:
    URL = "/api/v1/search/categories"

    async def test_list_categories(self, client, sample_pages):
        """获取分类列表 — 样本数据有5个分类（故事/原创/文档/指南/翻译）"""
        resp = await client.get(self.URL, params={"site_id": "test-wiki"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 5  # 故事、原创、文档、指南、翻译
        # 应该按数量降序排列
        assert data[0]["count"] >= data[1]["count"]

    async def test_categories_empty_site(self, client, sample_site):
        """没有页面的站点返回空列表"""
        resp = await client.get(self.URL, params={"site_id": "test-wiki"})
        assert resp.status_code == 200
        assert resp.json() == []
