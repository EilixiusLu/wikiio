"""测试安全工具函数：密码哈希、JWT、验证码"""

from datetime import datetime, timedelta
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_random_code,
)


class TestPassword:
    def test_hash_and_verify(self):
        """密码哈希与验证的往返测试"""
        password = "my_secret_pass_123!@#"
        hashed = hash_password(password)
        assert hashed != password  # 哈希结果不应等于原文
        assert verify_password(password, hashed) is True

    def test_wrong_password(self):
        """错误密码应验证失败"""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_different_hashes(self):
        """相同密码每次生成的哈希应不同（bcrypt 加盐）"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWT:
    def test_create_and_decode(self):
        """JWT 创建与解码往返"""
        payload = {"sub": "42", "role": "admin"}
        token = create_access_token(payload)
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "42"
        assert decoded["role"] == "admin"

    def test_expiry(self):
        """JWT 应包含过期时间"""
        payload = {"sub": "1"}
        token = create_access_token(payload)
        decoded = decode_access_token(token)
        assert "exp" in decoded

    def test_custom_expiry(self):
        """自定义过期时间"""
        payload = {"sub": "1"}
        token = create_access_token(payload, expires_delta=timedelta(seconds=1))
        decoded = decode_access_token(token)
        assert decoded is not None

    def test_invalid_token(self):
        """无效 token 应返回 None"""
        assert decode_access_token("this.is.not.a.valid.token") is None
        assert decode_access_token("") is None

    def test_tampered_token(self):
        """篡改过的 token 应解码失败"""
        payload = {"sub": "1"}
        token = create_access_token(payload)
        tampered = token + "x"
        assert decode_access_token(tampered) is None


class TestRandomCode:
    def test_default_length(self):
        """默认长度为 32 字符（URL-safe base64 编码后约 43 字符）"""
        code = generate_random_code()
        assert isinstance(code, str)
        assert len(code) > 32

    def test_custom_length(self):
        """指定熵长度"""
        code = generate_random_code(16)
        assert isinstance(code, str)
        assert len(code) > 16

    def test_url_safe(self):
        """验证码应是 URL 安全的"""
        code = generate_random_code()
        # URL-safe base64 只包含字母、数字、-、_
        for char in code:
            assert char.isalnum() or char in "-_"

    def test_uniqueness(self):
        """连续生成的验证码应不同"""
        codes = {generate_random_code() for _ in range(100)}
        assert len(codes) == 100
