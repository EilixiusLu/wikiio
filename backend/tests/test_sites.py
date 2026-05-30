"""测试站点相关 API"""


class TestListSites:
    URL = "/api/v1/sites/"

    async def test_empty(self, client):
        """未接入任何站点时应返回空列表"""
        resp = await client.get(self.URL)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_with_sites(self, client, sample_site):
        """有已接入站点时应返回列表"""
        resp = await client.get(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["site_id"] == "test-wiki"
        assert data[0]["platform"] == "fandom"

    async def test_pending_site_not_shown(self, client, db_session, sample_site):
        """待审核站点不应出现在列表中"""
        from app.models.site import Site
        pending = Site(
            name="待审核维基",
            site_id="pending-wiki",
            api_url="https://pending.fandom.com/api.php",
            base_url="https://pending.fandom.com",
            status="pending",
        )
        db_session.add(pending)
        await db_session.commit()

        resp = await client.get(self.URL)
        assert len(resp.json()) == 1  # 只有 sample_site


class TestGetSite:
    URL = "/api/v1/sites"

    async def test_get_existing(self, client, sample_site):
        """获取存在的站点"""
        resp = await client.get(f"{self.URL}/{sample_site.site_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "测试维基"
        assert data["base_url"] == "https://test.fandom.com/zh"

    async def test_get_nonexistent(self, client):
        """获取不存在的站点应返回 404"""
        resp = await client.get(f"{self.URL}/no-such-site")
        assert resp.status_code == 404


class TestCreateSite:
    URL = "/api/v1/sites/"

    async def test_create_as_admin(self, client, admin_headers):
        """管理员应能创建站点"""
        resp = await client.post(
            self.URL,
            json={
                "name": "新维基",
                "site_id": "new-wiki",
                "base_url": "https://new.fandom.com/zh",
                "platform": "fandom",
                "language": "zh",
                "description": "测试新建",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["site_id"] == "new-wiki"
        assert data["status"] == "approved"
        assert data["api_url"] == "https://new.fandom.com/zh/api.php"

    async def test_create_as_non_admin(self, client, user_headers):
        """普通用户应不能创建站点"""
        resp = await client.post(
            self.URL,
            json={
                "name": "新维基",
                "site_id": "user-wiki",
                "base_url": "https://user.fandom.com",
            },
            headers=user_headers,
        )
        assert resp.status_code == 403

    async def test_create_duplicate(self, client, admin_headers, sample_site):
        """重复 site_id 应返回 400"""
        resp = await client.post(
            self.URL,
            json={
                "name": "重复维基",
                "site_id": "test-wiki",
                "base_url": "https://test.fandom.com",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 400
        assert "已存在" in resp.json()["detail"]

    async def test_create_miraheze(self, client, admin_headers):
        """Miraheze 站点应生成对应的 API URL"""
        resp = await client.post(
            self.URL,
            json={
                "name": "MH维基",
                "site_id": "mh-wiki",
                "base_url": "https://test.miraheze.org",
                "platform": "miraheze",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["api_url"] == "https://test.miraheze.org/w/api.php"

    async def test_create_unauthenticated(self, client):
        """未登录应返回 401（HTTPBearer 拒绝）"""
        resp = await client.post(
            self.URL,
            json={
                "name": "匿名",
                "site_id": "anon-wiki",
                "base_url": "https://anon.fandom.com",
            },
        )
        assert resp.status_code == 401


class TestDeleteSite:
    URL = "/api/v1/sites"

    async def test_delete_as_admin(self, client, admin_headers, sample_site):
        """管理员应能删除站点"""
        resp = await client.delete(
            f"{self.URL}/{sample_site.site_id}",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "已删除" in resp.json()["message"]

    async def test_delete_as_non_admin(self, client, user_headers, sample_site):
        """普通用户应不能删除站点"""
        resp = await client.delete(
            f"{self.URL}/{sample_site.site_id}",
            headers=user_headers,
        )
        assert resp.status_code == 403

    async def test_delete_nonexistent(self, client, admin_headers):
        """删除不存在的站点应返回 404"""
        resp = await client.delete(
            f"{self.URL}/no-such-site",
            headers=admin_headers,
        )
        assert resp.status_code == 404


class TestTriggerCrawl:
    URL = "/api/v1/sites"

    async def test_trigger_as_admin(self, client, admin_headers, sample_site):
        """管理员应能触发爬取"""
        resp = await client.post(
            f"{self.URL}/{sample_site.site_id}/crawl",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "开始爬取" in resp.json()["message"]

    async def test_trigger_as_non_admin(self, client, user_headers, sample_site):
        """普通用户应不能触发爬取"""
        resp = await client.post(
            f"{self.URL}/{sample_site.site_id}/crawl",
            headers=user_headers,
        )
        assert resp.status_code == 403
