"""测试评分相关 API"""


class TestRatePage:
    URL = "/api/v1/ratings/page"

    async def test_rate_success(self, client, sample_pages, fandom_bound_user):
        """已绑定 Fandom 的用户应能评分"""
        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(fandom_bound_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        page_id = sample_pages[0].id
        resp = await client.post(
            f"{self.URL}/{page_id}",
            json={"score": 4},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "评分成功"
        assert data["score"] == 4

    async def test_rate_unbound(self, client, sample_pages, user_headers):
        """未绑定 Fandom 的用户应不能评分"""
        page_id = sample_pages[0].id
        resp = await client.post(
            f"{self.URL}/{page_id}",
            json={"score": 4},
            headers=user_headers,
        )
        assert resp.status_code == 403
        assert "绑定Fandom" in resp.json()["detail"]

    async def test_rate_out_of_range(self, client, sample_pages, fandom_bound_user):
        """超范围的分数应返回 422"""
        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(fandom_bound_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        page_id = sample_pages[0].id
        resp = await client.post(
            f"{self.URL}/{page_id}",
            json={"score": 6},
            headers=headers,
        )
        assert resp.status_code == 422

    async def test_rate_nonexistent_page(self, client, fandom_bound_user):
        """不存在的页面应返回 404"""
        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(fandom_bound_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            f"{self.URL}/99999",
            json={"score": 3},
            headers=headers,
        )
        assert resp.status_code == 404

    async def test_update_rating(self, client, sample_pages, fandom_bound_user, db_session):
        """重复评分应更新而非新建"""
        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(fandom_bound_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        page_id = sample_pages[0].id

        # 第一次评分
        resp1 = await client.post(
            f"{self.URL}/{page_id}",
            json={"score": 2},
            headers=headers,
        )
        assert resp1.status_code == 200

        # 第二次评分（修改）
        resp2 = await client.post(
            f"{self.URL}/{page_id}",
            json={"score": 5},
            headers=headers,
        )
        assert resp2.status_code == 200
        assert resp2.json()["score"] == 5

        # 验证数据库只有一条记录
        from sqlalchemy import select, func
        from app.models.rating import Rating
        result = await db_session.execute(
            select(func.count()).where(
                Rating.page_id == page_id,
                Rating.user_id == fandom_bound_user.id,
            )
        )
        assert result.scalar() == 1


class TestGetRating:
    URL = "/api/v1/ratings/page"

    async def test_get_page_rating(self, client, sample_pages):
        """获取页面评分统计"""
        page_id = sample_pages[0].id
        resp = await client.get(f"{self.URL}/{page_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert "rating_avg" in data
        assert "rating_count" in data

    async def test_get_nonexistent(self, client):
        resp = await client.get(f"{self.URL}/99999")
        assert resp.status_code == 404


class TestGetMyRating:
    URL = "/api/v1/ratings/page"

    async def test_no_rating(self, client, user_headers, sample_pages):
        """未评分时返回 score=None"""
        page_id = sample_pages[0].id
        resp = await client.get(
            f"{self.URL}/{page_id}/mine",
            headers=user_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["score"] is None

    async def test_with_rating(self, client, sample_pages, fandom_bound_user, db_session):
        """已评分时返回评分"""
        from app.utils.security import create_access_token
        from app.models.rating import Rating

        token = create_access_token({"sub": str(fandom_bound_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # 先评个分
        page_id = sample_pages[0].id
        await client.post(
            f"{self.URL}/{page_id}",
            json={"score": 3},
            headers=headers,
        )

        # 查询我的评分
        resp = await client.get(
            f"{self.URL}/{page_id}/mine",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["score"] == 3


class TestDeleteRating:
    URL = "/api/v1/ratings/page"

    async def test_delete_rating(self, client, sample_pages, fandom_bound_user):
        """删除评分"""
        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(fandom_bound_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        page_id = sample_pages[0].id

        # 先评分
        await client.post(
            f"{self.URL}/{page_id}",
            json={"score": 3},
            headers=headers,
        )

        # 删除评分
        resp = await client.delete(f"{self.URL}/{page_id}", headers=headers)
        assert resp.status_code == 200
        assert "已删除" in resp.json()["message"]

    async def test_delete_no_rating(self, client, user_headers, sample_pages):
        """没有评分时删除应返回 404"""
        page_id = sample_pages[0].id
        resp = await client.delete(f"{self.URL}/{page_id}", headers=user_headers)
        assert resp.status_code == 404
