"""测试用户相关 API（个人信息、Fandom/Miraheze 绑定）"""

import pytest


class TestGetMe:
    URL = "/api/v1/users/me"

    async def test_get_me_authenticated(self, client, user_headers):
        """已登录用户应能获取个人信息"""
        resp = await client.get(self.URL, headers=user_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    async def test_get_me_unauthenticated(self, client):
        """未登录应返回 401"""
        resp = await client.get(self.URL)
        assert resp.status_code == 401  # HTTPBearer 无 token 时返回 401


class TestFandomBind:
    START_URL = "/api/v1/users/fandom/bind/start"
    VERIFY_URL = "/api/v1/users/fandom/bind/verify"
    UNBIND_URL = "/api/v1/users/fandom/unbind"

    async def test_bind_start_success(self, client, user_headers, db_session):
        """发起绑定应返回验证码"""
        resp = await client.post(
            f"{self.START_URL}?fandom_username=NewFandomUser",
            headers=user_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "verify_code" in data
        assert "community.fandom.com" in data["target_url"]

    async def test_bind_start_already_bound(self, client, fandom_bound_user):
        """已绑定用户再次发起应返回 400"""
        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(fandom_bound_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            f"{self.START_URL}?fandom_username=AnotherUser",
            headers=headers,
        )
        assert resp.status_code == 400
        assert "已经绑定" in resp.json()["detail"]

    async def test_bind_start_duplicate_username(self, client, user_headers, db_session):
        """Fandom 用户名已被其他用户绑定时应返回 400"""
        from app.models.user import User
        # 创建另一个已绑定此 Fandom 用户名的用户
        other = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hash",
            is_fandom_verified=True,
            fandom_username="TakenUser",
        )
        db_session.add(other)
        await db_session.commit()

        resp = await client.post(
            f"{self.START_URL}?fandom_username=TakenUser",
            headers=user_headers,
        )
        assert resp.status_code == 400
        assert "已被其他用户绑定" in resp.json()["detail"]

    async def test_bind_verify_not_started(self, client, user_headers):
        """未发起绑定时验证应返回 400"""
        resp = await client.post(self.VERIFY_URL, headers=user_headers)
        assert resp.status_code == 400
        assert "请先发起绑定申请" in resp.json()["detail"]

    async def test_bind_verify_already_bound(self, client, fandom_bound_user):
        """已绑定用户再次验证应返回 400"""
        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(fandom_bound_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(self.VERIFY_URL, headers=headers)
        assert resp.status_code == 400
        assert "已经绑定" in resp.json()["detail"]

    async def test_unbind_success(self, client, fandom_bound_user):
        """解绑后应清空绑定信息并允许重新绑定"""
        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(fandom_bound_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # 解绑
        resp = await client.delete(self.UNBIND_URL, headers=headers)
        assert resp.status_code == 200

        # 验证可以重新发起绑定（返回验证码即表示成功）
        resp = await client.post(
            f"{self.START_URL}?fandom_username=RebindUser",
            headers=headers,
        )
        assert resp.status_code == 200
        assert "verify_code" in resp.json()

    async def test_unbind_role_downgrade(self, client, db_session):
        """普通用户解绑后应降为 role=0"""
        from app.utils.security import create_access_token
        from app.models.user import User

        # 创建一个已绑定的普通用户（role=1）
        user = User(
            email="bound@example.com",
            username="bounduser",
            hashed_password="hash",
            is_fandom_verified=True,
            fandom_username="RoleTestUser",
            role=1,
        )
        db_session.add(user)
        await db_session.commit()

        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.delete(self.UNBIND_URL, headers=headers)
        assert resp.status_code == 200

        await db_session.refresh(user)
        assert user.role == 0

    async def test_unbind_admin_keeps_role(self, client, admin_user):
        """管理员解绑后应保持管理员权限"""
        from app.utils.security import create_access_token
        admin, _ = admin_user
        admin.is_fandom_verified = True
        admin.fandom_username = "AdminFandomUser"

        token = create_access_token({"sub": str(admin.id)})
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.delete(self.UNBIND_URL, headers=headers)
        assert resp.status_code == 200

        # role 应保持 3（管理员）
        assert admin.role == 3


class TestMirahezeBind:
    START_URL = "/api/v1/users/miraheze/bind/start"
    VERIFY_URL = "/api/v1/users/miraheze/bind/verify"
    UNBIND_URL = "/api/v1/users/miraheze/unbind"

    async def test_bind_start_success(self, client, user_headers):
        """发起绑定应返回验证码"""
        resp = await client.post(
            f"{self.START_URL}?miraheze_username=MHUser",
            headers=user_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "verify_code" in data
        assert "meta.miraheze.org" in data["target_url"]

    async def test_bind_start_duplicate(self, client, user_headers, db_session):
        """Miraheze 用户名已被其他用户绑定应返回 400"""
        from app.models.user import User
        other = User(
            email="mh-other@example.com",
            username="mh-other",
            hashed_password="hash",
            is_miraheze_verified=True,
            miraheze_username="TakenMHUser",
        )
        db_session.add(other)
        await db_session.commit()

        resp = await client.post(
            f"{self.START_URL}?miraheze_username=TakenMHUser",
            headers=user_headers,
        )
        assert resp.status_code == 400
        assert "已被其他用户绑定" in resp.json()["detail"]

    async def test_bind_verify_not_started(self, client, user_headers):
        """未发起绑定就验证应返回 400"""
        resp = await client.post(self.VERIFY_URL, headers=user_headers)
        assert resp.status_code == 400
        assert "请先发起绑定申请" in resp.json()["detail"]

    async def test_unbind(self, client, db_session):
        """解绑 Miraheze 后应可重新绑定"""
        from app.utils.security import create_access_token
        from app.models.user import User

        user = User(
            email="mh-bound@example.com",
            username="mh-bound",
            hashed_password="hash",
            is_miraheze_verified=True,
            miraheze_username="MHBoundUser",
        )
        db_session.add(user)
        await db_session.commit()

        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # 解绑
        resp = await client.delete(self.UNBIND_URL, headers=headers)
        assert resp.status_code == 200

        # 验证可以重新绑定
        resp = await client.post(
            f"{self.START_URL}?miraheze_username=RebindMH",
            headers=headers,
        )
        assert resp.status_code == 200
