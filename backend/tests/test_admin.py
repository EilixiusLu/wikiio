"""测试管理后台相关 API"""


class TestAdminStats:
    URL = "/api/v1/admin/stats"

    async def test_stats_as_admin(self, client, admin_headers, sample_pages, sample_site):
        """管理员应能获取统计"""
        resp = await client.get(self.URL, headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_pages"] == 3
        assert data["total_sites"] >= 1

    async def test_stats_as_non_admin(self, client, user_headers):
        """普通用户应不能获取统计"""
        resp = await client.get(self.URL, headers=user_headers)
        assert resp.status_code == 403


class TestAdminLogs:
    URL = "/api/v1/admin/logs"

    async def test_valid_log_type(self, client, admin_headers):
        """有效的日志类型"""
        resp = await client.get(
            f"{self.URL}/access",
            params={"lines": 10},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "lines" in data
        assert "total_lines" in data

    async def test_invalid_log_type(self, client, admin_headers):
        """无效的日志类型应返回 400"""
        resp = await client.get(
            f"{self.URL}/invalid_type",
            headers=admin_headers,
        )
        assert resp.status_code == 400

    async def test_logs_as_non_admin(self, client, user_headers):
        """普通用户应不能查看日志"""
        resp = await client.get(
            f"{self.URL}/access",
            headers=user_headers,
        )
        assert resp.status_code == 403


class TestAdminSites:
    URL = "/api/v1/admin/sites"

    async def test_list_all_sites(self, client, admin_headers, sample_site, db_session):
        """管理员应能看到所有状态站点"""
        from app.models.site import Site
        pending = Site(
            name="待审核",
            site_id="pending-site",
            api_url="https://pending.com/api.php",
            base_url="https://pending.com",
            status="pending",
        )
        db_session.add(pending)
        await db_session.commit()

        resp = await client.get(self.URL, headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        site_ids = [s["site_id"] for s in data]
        assert "pending-site" in site_ids
        assert "test-wiki" in site_ids

    async def test_list_as_non_admin(self, client, user_headers):
        """普通用户应不能查看管理站点列表"""
        resp = await client.get(self.URL, headers=user_headers)
        assert resp.status_code == 403


class TestApproveRejectSite:
    APPROVE_URL = "/api/v1/admin/sites"
    REJECT_URL = "/api/v1/admin/sites"

    async def test_approve_site(self, client, admin_headers, db_session):
        """审核通过站点"""
        from app.models.site import Site
        site = Site(
            name="待审站",
            site_id="to-approve",
            api_url="https://pending.com/api.php",
            base_url="https://pending.com",
            status="pending",
        )
        db_session.add(site)
        await db_session.commit()

        resp = await client.post(
            f"{self.APPROVE_URL}/to-approve/approve",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "已审核通过" in resp.json()["message"]

        await db_session.refresh(site)
        assert site.status == "approved"

    async def test_reject_site(self, client, admin_headers, db_session):
        """拒绝站点"""
        from app.models.site import Site
        site = Site(
            name="待拒站",
            site_id="to-reject",
            api_url="https://reject.com/api.php",
            base_url="https://reject.com",
            status="pending",
        )
        db_session.add(site)
        await db_session.commit()

        resp = await client.post(
            f"{self.REJECT_URL}/to-reject/reject",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "已拒绝" in resp.json()["message"]

        await db_session.refresh(site)
        assert site.status == "rejected"

    async def test_approve_nonexistent(self, client, admin_headers):
        """审核不存在的站点应返回 404"""
        resp = await client.post(
            f"{self.APPROVE_URL}/no-such-site/approve",
            headers=admin_headers,
        )
        assert resp.status_code == 404
