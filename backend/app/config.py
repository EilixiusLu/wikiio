from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_SERVER: str = ""
    ENVIRONMENT: str = "development"

    # CORS 允许的来源（逗号分隔，用于 Docker 等环境配置）
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1"

    # 爬虫配置
    CRAWL_REQUESTS_PER_SECOND: float = 0.33        # 爬虫请求速率（越低越安全）
    CRAWL_INCREMENTAL_WINDOW_MINUTES: int = 120     # 增量更新窗口（分钟）
    CRAWL_INTER_SITE_DELAY_SECONDS: int = 60        # 站间爬取延迟（秒）
    CRAWL_SCHEDULE_CRON: str = "42 */2 * * *"       # Celery Beat 调度 cron 表达式

settings = Settings()