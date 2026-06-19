"""测试认证相关 API"""

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta, timezone


class TestRegister:
    URL = "/api/v1/auth/register"

    @patch("app.routers.auth.send_verification_email", new_callable=AsyncMock)
    async def test_register_success(self, mock_send_email, client):
        """正常注册应返回 201 以及 message + email（不再返回 JWT）"""
        resp = await client.post(self.URL, json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "message" in data
        assert "验证" in data["message"]
        assert data["email"] == "newuser@example.com"
        assert "access_token" not in data
        mock_send_email.assert_called_once()

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
        """正常登录应返回 token（fixture 中 test_user 的 is_email_verified=True）"""
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

    async def test_login_unverified_user_returns_403(self, client, db_session):
        """未验证邮箱的用户登录应返回 403"""
        from app.models.user import User
        from app.utils.security import hash_password

        user = User(
            email="unverified@example.com",
            username="unverifieduser",
            hashed_password=hash_password("testpass123"),
            is_email_verified=False,
        )
        db_session.add(user)
        await db_session.commit()

        resp = await client.post(self.URL, json={
            "email": "unverified@example.com",
            "password": "testpass123",
        })
        assert resp.status_code == 403
        assert "验证" in resp.json()["detail"]

    async def test_login_after_verification_succeeds(self, client, db_session):
        """验证邮箱后可以正常登录"""
        from app.models.user import User
        from app.utils.security import hash_password

        user = User(
            email="verifythenlogin@example.com",
            username="verifythenlogin",
            hashed_password=hash_password("testpass123"),
            is_email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()

        resp = await client.post(self.URL, json={
            "email": "verifythenlogin@example.com",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()


class TestVerifyEmail:
    URL = "/api/v1/auth/verify-email"

    async def test_verify_success(self, client, db_session):
        """用有效 token 通过 POST 验证邮箱"""
        from app.models.user import User
        from sqlalchemy import select

        future = datetime.now(timezone.utc) + timedelta(hours=24)
        user = User(
            email="verify@example.com",
            username="verifyuser",
            hashed_password="hash",
            email_verify_token="valid-token-123",
            email_verify_token_expires_at=future,
            is_email_verified=False,
        )
        db_session.add(user)
        await db_session.commit()

        resp = await client.post(self.URL, params={"token": "valid-token-123"})
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
        resp = await client.post(self.URL, params={"token": "invalid-token"})
        assert resp.status_code == 400
        assert "无效" in resp.json()["detail"]

    async def test_verify_expired_token(self, client, db_session):
        """过期 token 应返回 400"""
        from app.models.user import User

        past = datetime.now(timezone.utc) - timedelta(hours=1)
        user = User(
            email="expired@example.com",
            username="expireduser",
            hashed_password="hash",
            email_verify_token="expired-token",
            email_verify_token_expires_at=past,
            is_email_verified=False,
        )
        db_session.add(user)
        await db_session.commit()

        resp = await client.post(self.URL, params={"token": "expired-token"})
        assert resp.status_code == 400
        assert "过期" in resp.json()["detail"]

    async def test_verify_already_verified(self, client, db_session):
        """已验证的邮箱再次验证应提示无需重复操作"""
        from app.models.user import User

        future = datetime.now(timezone.utc) + timedelta(hours=24)
        user = User(
            email="already@example.com",
            username="alreadyuser",
            hashed_password="hash",
            is_email_verified=True,
            email_verify_token="already-token",
            email_verify_token_expires_at=future,
        )
        db_session.add(user)
        await db_session.commit()

        resp = await client.post(self.URL, params={"token": "already-token"})
        assert resp.status_code == 200
        assert "已" in resp.json()["message"]


class TestResendVerification:
    URL = "/api/v1/auth/resend-verification"

    @patch("app.routers.auth.send_verification_resend_email", new_callable=AsyncMock)
    async def test_resend_verification_success(self, mock_send_email, client, db_session):
        """重发验证邮件正常返回 200"""
        from app.models.user import User

        user = User(
            email="resend@example.com",
            username="resenduser",
            hashed_password="hash",
            is_email_verified=False,
        )
        db_session.add(user)
        await db_session.commit()

        resp = await client.post(self.URL, params={"email": "resend@example.com"})
        assert resp.status_code == 200
        mock_send_email.assert_called_once()

    async def test_resend_verification_nonexistent_email_silent(self, client):
        """重发给不存在邮箱静默返回 200（防用户枚举）"""
        resp = await client.post(self.URL, params={"email": "nobody@example.com"})
        assert resp.status_code == 200
        assert "message" in resp.json()

    async def test_resend_verification_already_verified(self, client, test_user):
        """重发给已验证用户返回 400"""
        resp = await client.post(self.URL, params={"email": "test@example.com"})
        assert resp.status_code == 400
        assert "已" in resp.json()["detail"]
