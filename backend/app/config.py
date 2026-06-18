from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_SERVER: str = ""
    ENVIRONMENT: str = "development"

    # CORS 允许的来源（环境变量用逗号分隔，如 "https://wikiio.verniy.site,http://localhost:5173"）
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Redis 缓存配置
    REDIS_CACHE_TTL_DEFAULT: int = 300       # 默认缓存 TTL（秒）
    REDIS_CACHE_PREFIX: str = "wikiio:"       # 缓存键前缀

    # 爬虫配置
    CRAWL_REQUESTS_PER_SECOND: float = 0.33        # 爬虫请求速率（越低越安全）
    CRAWL_INCREMENTAL_WINDOW_MINUTES: int = 120     # 增量更新窗口（分钟）
    CRAWL_INTER_SITE_DELAY_SECONDS: int = 60        # 站间爬取延迟（秒）
    CRAWL_SCHEDULE_CRON: str = "42 */2 * * *"       # Celery Beat 调度 cron 表达式

settings = Settings()