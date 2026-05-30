"""测试认证相关 API"""

import pytest


class TestRegister:
    URL = "/api/v1/auth/register"

    async def test_register_success(self, client):
        """正常注册应返回 201 和用户信息"""
        resp = await client.post(self.URL, json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["is_email_verified"] is False

    async def test_register_duplicate_email(self, client, test_user):
        """重复邮箱应返回 400"""
        resp = await client.post(self.URL, json={
            "email": "test@example.com",
            "username": "another",
            "password": "password123",
        })
        assert resp.status_code == 400
        assert "已被注册" in resp.json()["detail"]

    async def test_register_duplicate_username(self, client, test_user):
        """重复用户名应返回 400"""
        resp = await client.post(self.URL, json={
            "email": "another@example.com",
            "username": "testuser",
            "password": "password123",
        })
        assert resp.status_code == 400
        assert "已被使用" in resp.json()["detail"]

    async def test_register_invalid_data(self, client):
        """无效数据应返回 422"""
        resp = await client.post(self.URL, json={
            "email": "not-an-email",
            "username": "ab",
            "password": "short",
        })
        assert resp.status_code == 422


class TestLogin:
    URL = "/api/v1/auth/login"

    async def test_login_success(self, client, test_user):
        """正常登录应返回 token"""
        resp = await client.post(self.URL, json={
            "email": "test@example.com",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"

    async def test_login_wrong_password(self, client, test_user):
        """错误密码应返回 401"""
        resp = await client.post(self.URL, json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401
        assert "错误" in resp.json()["detail"]

    async def test_login_nonexistent_email(self, client):
        """不存在的邮箱应返回 401"""
        resp = await client.post(self.URL, json={
            "email": "nobody@example.com",
            "password": "password123",
        })
        assert resp.status_code == 401


class TestVerifyEmail:
    URL = "/api/v1/auth/verify-email"

    async def test_verify_success(self, client, db_session):
        """用有效 token 验证邮箱"""
        from app.models.user import User
        from sqlalchemy import select
        user = User(
            email="verify@example.com",
            username="verifyuser",
            hashed_password="hash",
            email_verify_token="valid-token-123",
            is_email_verified=False,
        )
        db_session.add(user)
        await db_session.commit()

        resp = await client.get(f"{self.URL}/valid-token-123")
        assert resp.status_code == 200
        assert "成功" in resp.json()["message"]

        # 重新查询验证数据库已更新
        result = await db_session.execute(
            select(User).where(User.email == "verify@example.com")
        )
        updated = result.scalar_one()
        assert updated.is_email_verified is True
        assert updated.email_verify_token is None

    async def test_verify_invalid_token(self, client):
        """无效 token 应返回 400"""
        resp = await client.get(f"{self.URL}/invalid-token")
        assert resp.status_code == 400

    async def test_verify_already_verified(self, client, db_session):
        """已验证的邮箱再次验证应提示已验证"""
        from app.models.user import User
        user = User(
            email="already@example.com",
            username="alreadyuser",
            hashed_password="hash",
            is_email_verified=True,
            email_verify_token="already-token",
        )
        db_session.add(user)
        await db_session.commit()

        resp = await client.get(f"{self.URL}/already-token")
        assert resp.status_code == 200
        assert "已经验证" in resp.json()["message"]
