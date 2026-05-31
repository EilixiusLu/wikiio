"""Celery 调度器：定时对所有已启用站点执行增量爬取

启动方式:
    # Worker（执行任务的后台进程）
    celery -A app.crawler.scheduler worker --loglevel=info -P solo

    # Beat（定时触发器，周期性将任务入队）
    celery -A app.crawler.scheduler beat --loglevel=info

    # 或者合并启动（开发环境）
    celery -A app.crawler.scheduler worker --beat --loglevel=info -P solo
"""

import asyncio
import logging
from celery import Celery
from celery.schedules import crontab
from app.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "wikiio",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=False,
    worker_max_tasks_per_child=20,           # 每个 worker 子进程处理 20 个任务后重启，防内存泄漏
    task_acks_late=True,                      # 任务完成后才确认，避免任务丢失
    task_reject_on_worker_lost=True,          # worker 挂掉时重新调度
    task_track_started=True,
    beat_schedule={
        "crawl-all-sites-incremental": {
            "task": "app.crawler.scheduler.crawl_incremental_task",
            "schedule": crontab(
                # 从配置解析 cron 表达式: "minute hour day_of_month month day_of_week"
                minute=settings.CRAWL_SCHEDULE_CRON.split()[0],
                hour=settings.CRAWL_SCHEDULE_CRON.split()[1],
                day_of_month=settings.CRAWL_SCHEDULE_CRON.split()[2],
                month_of_year=settings.CRAWL_SCHEDULE_CRON.split()[3],
                day_of_week=settings.CRAWL_SCHEDULE_CRON.split()[4],
            ),
            "options": {"expires": 3600},       # 任务 1 小时内未执行则过期跳过
        },
    },
)


@celery_app.task(
    name="app.crawler.scheduler.crawl_incremental_task",
    bind=True,
    max_retries=2,
    default_retry_delay=600,  # 失败后 10 分钟重试
    acks_late=True,
)
def crawl_incremental_task(self):
    """
    Celery Beat 定时任务：遍历所有启用爬取的站点，串行执行增量更新。

    每个站点爬取之间有固定延迟（CRAWL_INTER_SITE_DELAY_SECONDS），
    确保不会短时间向同一个 IP 池发送大量请求。
    """
    logger.info("========== 定时增量爬取开始 ==========")
    try:
        from app.crawler.tasks import crawl_all_sites_incremental
        stats = asyncio.run(crawl_all_sites_incremental())
        logger.info(
            f"定时增量爬取完成: 共 {stats['total']} 个站点, "
            f"成功 {stats['success']}, 失败 {stats['failed']}, "
            f"更新页面 {stats['pages']} 篇"
        )
        return stats
    except Exception as exc:
        logger.error(f"定时增量爬取出错: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.crawler.scheduler.crawl_single_site_task",
    bind=True,
    max_retries=1,
    default_retry_delay=900,  # 15 分钟重试
)
def crawl_single_site_task(self, site_id: str, full: bool = False):
    """
    手动触发的单站爬取任务（异步执行，解耦 HTTP 请求超时）。

    Args:
        site_id: 站点标识
        full: True=全量爬取, False=增量更新
    """
    logger.info(f"异步爬取任务启动: site={site_id}, full={full}")
    try:
        from app.crawler.tasks import crawl_site_full, crawl_site_incremental
        if full:
            asyncio.run(crawl_site_full(site_id))
        else:
            asyncio.run(crawl_site_incremental(site_id))
        logger.info(f"异步爬取完成: site={site_id}")
    except Exception as exc:
        logger.error(f"异步爬取失败 site={site_id}: {exc}")
        raise self.retry(exc=exc)
