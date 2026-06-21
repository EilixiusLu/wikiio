from typing import List, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ENVIRONMENT: str = "development"

    # Resend 邮件配置
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "Wikiio <noreply@ewikiio.verniy.site>"

    # 邮箱验证 token 有效期（秒），默认 24 小时
    EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS: int = 86400

    # 前端基础 URL，用于拼接验证链接
    FRONTEND_BASE_URL: str = "https://wikiio.verniy.site"

    # CORS 允许的来源（支持逗号分隔字符串或 JSON 数组）
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """兼容逗号分隔字符串（Docker Compose 传参）和列表"""
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                import json
                return json.loads(s)
            return [origin.strip() for origin in s.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return [str(v)]

    # Redis 缓存配置
    REDIS_CACHE_TTL_DEFAULT: int = 300       # 默认缓存 TTL（秒）
    REDIS_CACHE_PREFIX: str = "wikiio:"       # 缓存键前缀

    # 爬虫配置
    CRAWL_REQUESTS_PER_SECOND: float = 0.33        # 爬虫请求速率（越低越安全）
    CRAWL_INCREMENTAL_WINDOW_MINUTES: int = 120     # 增量更新窗口（分钟）
    CRAWL_INTER_SITE_DELAY_SECONDS: int = 60        # 站间爬取延迟（秒）
    CRAWL_SCHEDULE_CRON: str = "42 */2 * * *"       # Celery Beat 调度 cron 表达式

settings = Settings()