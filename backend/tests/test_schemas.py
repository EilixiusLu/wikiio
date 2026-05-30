"""测试 Pydantic 数据模型验证"""

import pytest
from pydantic import ValidationError
from app.schemas.user import UserRegister, UserLogin, UserResponse
from app.schemas.site import SiteCreate
from app.schemas.rating import RatingCreate


class TestUserRegister:
    def test_valid(self):
        data = UserRegister(email="test@example.com", username="testuser", password="password123")
        assert data.email == "test@example.com"
        assert data.username == "testuser"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserRegister(email="not-an-email", username="testuser", password="password123")

    def test_username_too_short(self):
        with pytest.raises(ValidationError, match="至少3个字符"):
            UserRegister(email="test@example.com", username="ab", password="password123")

    def test_username_too_long(self):
        with pytest.raises(ValidationError, match="最多20个字符"):
            UserRegister(email="test@example.com", username="a" * 21, password="password123")

    def test_username_special_chars(self):
        with pytest.raises(ValidationError, match="只能包含"):
            UserRegister(email="test@example.com", username="user name!", password="password123")

    def test_username_underscore_ok(self):
        data = UserRegister(email="test@example.com", username="user_name", password="password123")
        assert data.username == "user_name"

    def test_username_hyphen_ok(self):
        data = UserRegister(email="test@example.com", username="user-name", password="password123")
        assert data.username == "user-name"

    def test_password_too_short(self):
        with pytest.raises(ValidationError, match="至少8个字符"):
            UserRegister(email="test@example.com", username="testuser", password="1234567")


class TestUserLogin:
    def test_valid(self):
        data = UserLogin(email="test@example.com", password="password123")
        assert data.email == "test@example.com"
        assert data.password == "password123"


class TestUserResponse:
    def test_optional_fields(self):
        data = UserResponse(
            id=1,
            email="test@example.com",
            username="testuser",
            is_email_verified=True,
            role=0,
            created_at="2024-01-01T00:00:00",
        )
        assert data.fandom_username is None
        assert data.miraheze_username is None


class TestSiteCreate:
    def test_valid_fandom(self):
        data = SiteCreate(
            name="测试维基",
            site_id="test-wiki",
            base_url="https://test.fandom.com/zh",
        )
        assert data.platform == "fandom"
        assert data.language == "zh"

    def test_valid_miraheze(self):
        data = SiteCreate(
            name="Miraheze维基",
            site_id="mh-wiki",
            base_url="https://test.miraheze.org",
            platform="miraheze",
        )
        assert data.platform == "miraheze"

    def test_invalid_platform(self):
        with pytest.raises(ValidationError, match="平台类型"):
            SiteCreate(
                name="测试",
                site_id="test",
                base_url="https://test.com",
                platform="wikidot",
            )

    def test_empty_site_id(self):
        with pytest.raises(ValidationError, match="不能为空"):
            SiteCreate(
                name="测试",
                site_id="  ",
                base_url="https://test.com",
            )


class TestRatingCreate:
    def test_valid(self):
        data = RatingCreate(score=3)
        assert data.score == 3

    def test_min_score(self):
        data = RatingCreate(score=1)
        assert data.score == 1

    def test_max_score(self):
        data = RatingCreate(score=5)
        assert data.score == 5

    def test_too_low(self):
        with pytest.raises(ValidationError, match="1-5"):
            RatingCreate(score=0)

    def test_too_high(self):
        with pytest.raises(ValidationError, match="1-5"):
            RatingCreate(score=6)
