"""测试页面相关 API"""


class TestListPages:
    URL = "/api/v1/pages/"

    async def test_list_by_site(self, client, sample_pages):
        """按站点获取页面列表"""
        resp = await client.get(self.URL, params={"site_id": "test-wiki"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    async def test_list_empty_site(self, client, sample_site):
        """没有页面的站点返回空列表"""
        resp = await client.get(self.URL, params={"site_id": "test-wiki"})
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_filter_author(self, client, sample_pages):
        """按作者筛选"""
        resp = await client.get(
            self.URL,
            params={"site_id": "test-wiki", "author": "作者A"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(p["author"] == "作者A" for p in data)

    async def test_list_order_by_rating(self, client, sample_pages):
        """按评分排序"""
        resp = await client.get(
            self.URL,
            params={"site_id": "test-wiki", "order_by": "rating"},
        )
        assert resp.status_code == 200
        data = resp.json()
        ratings = [p["rating_avg"] for p in data]
        assert ratings == sorted(ratings, reverse=True)

    async def test_list_pagination(self, client, sample_pages):
        """分页参数"""
        resp = await client.get(
            self.URL,
            params={"site_id": "test-wiki", "limit": 2},
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 2

        resp2 = await client.get(
            self.URL,
            params={"site_id": "test-wiki", "skip": 2, "limit": 2},
        )
        assert len(resp2.json()) == 1


class TestCountPages:
    URL = "/api/v1/pages/count"

    async def test_count(self, client, sample_pages):
        resp = await client.get(self.URL, params={"site_id": "test-wiki"})
        assert resp.status_code == 200
        assert resp.json()["count"] == 3

    async def test_count_zero(self, client, sample_site):
        resp = await client.get(self.URL, params={"site_id": "test-wiki"})
        assert resp.json()["count"] == 0


class TestStats:
    URL = "/api/v1/pages/stats"

    async def test_stats(self, client, sample_pages):
        """站点统计应返回正确数字"""
        resp = await client.get(self.URL, params={"site_id": "test-wiki"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_pages"] == 3
        assert data["total_words"] == 46  # 15 + 25 + 6
        assert data["total_authors"] == 2  # 作者A + 作者B
        assert data["total_revisions"] == 0

    async def test_stats_empty(self, client, sample_site):
        resp = await client.get(self.URL, params={"site_id": "test-wiki"})
        assert resp.json()["total_pages"] == 0


class TestGetPage:
    URL = "/api/v1/pages"

    async def test_get_existing(self, client, sample_pages):
        page = sample_pages[0]
        resp = await client.get(f"{self.URL}/{page.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "测试页面一"
        assert data["author"] == "作者A"
        assert data["word_count"] == 15

    async def test_get_nonexistent(self, client):
        resp = await client.get(f"{self.URL}/99999")
        assert resp.status_code == 404


class TestTopAuthors:
    URL = "/api/v1/pages/top-authors"

    async def test_top_authors(self, client, sample_pages):
        resp = await client.get(
            self.URL,
            params={"site_id": "test-wiki"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        # 作者A有2篇排在前面
        assert data[0]["author"] == "作者A"
        assert data[0]["page_count"] == 2

    async def test_top_authors_limit(self, client, sample_pages):
        resp = await client.get(
            self.URL,
            params={"site_id": "test-wiki", "limit": 1},
        )
        assert len(resp.json()) == 1


class TestRankings:
    RATING_URL = "/api/v1/pages/rankings/by-rating"
    AUTHOR_URL = "/api/v1/pages/rankings/by-author"

    async def test_rating_ranking(self, client, sample_pages):
        resp = await client.get(
            self.RATING_URL,
            params={"site_id": "test-wiki"},
        )
        assert resp.status_code == 200
        data = resp.json()
        # 只有2篇有评分（rating_count > 0）
        assert len(data) == 2
        assert data[0]["rating_avg"] >= data[1]["rating_avg"]

    async def test_author_ranking_by_pages(self, client, sample_pages):
        resp = await client.get(
            self.AUTHOR_URL,
            params={"site_id": "test-wiki", "order_by": "page_count"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data[0]["author"] == "作者A"
        assert data[0]["page_count"] == 2

    async def test_author_ranking_by_rating(self, client, sample_pages):
        resp = await client.get(
            self.AUTHOR_URL,
            params={"site_id": "test-wiki", "order_by": "rating"},
        )
        assert resp.status_code == 200
        data = resp.json()
        for item in data:
            assert "avg_rating" in item


class TestAuthorEndpoints:
    BASE = "/api/v1/pages/author"

    async def test_author_pages(self, client, sample_pages):
        resp = await client.get(f"{self.BASE}/作者A")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["pages"]) == 2

    async def test_author_pages_with_site(self, client, sample_pages):
        resp = await client.get(
            f"{self.BASE}/作者A",
            params={"site_id": "test-wiki"},
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    async def test_author_stats(self, client, sample_pages):
        resp = await client.get(f"{self.BASE}/作者A/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["author"] == "作者A"
        assert data["total_pages"] == 2

    async def test_author_nonexistent(self, client):
        resp = await client.get(f"{self.BASE}/不存在的作者")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
