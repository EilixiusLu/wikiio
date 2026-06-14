import logging
import logging.handlers
import time
from pathlib import Path

# 创建日志目录
LOG_DIR = Path(__file__).parent.parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── 保留策略 ──
DAYS_TO_KEEP = 30  # 普通日志保留天数


def cleanup_old_logs() -> dict:
    """
    启动时清理超过保留期限的旧日志文件。

    TimedRotatingFileHandler 在进程运行时可靠地按天轮转，
    此函数处理以下边缘情况：
    - 服务重启后未及时轮转的残留文件
    - 手动或脚本生成的非标准命名文件
    - 部分旋转遗留的临时文件（如 .tmp、.gz 后缀）
    """
    now = time.time()
    cutoff = now - DAYS_TO_KEEP * 86400

    deleted: list[str] = []
    for f in LOG_DIR.iterdir():
        if not f.is_file():
            continue
        # 仅处理日志文件：.log 结尾 或 轮转后缀 .log.YYYY-MM-DD
        if not (f.suffix == ".log" or ".log." in f.name):
            continue

        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
                deleted.append(f.name)
        except OSError:
            pass

    return {"deleted": len(deleted), "files": deleted}


def setup_logger(name: str, filename: str, level=logging.INFO) -> logging.Logger:
    """创建一个带文件和控制台输出的 logger"""

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 文件 handler：每天午夜轮转，保留 30 天
    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_DIR / filename,
        when="midnight",
        interval=1,
        backupCount=DAYS_TO_KEEP,
        encoding="utf-8",
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# ── 各模块 logger ──
access_logger = setup_logger("wikiio.access", "access.log")
crawler_logger = setup_logger("wikiio.crawler", "crawler.log")
rating_logger = setup_logger("wikiio.rating", "rating.log")
error_logger = setup_logger("wikiio.error", "error.log", level=logging.ERROR)


# ── 启动时执行一次清理 ──
result = cleanup_old_logs()
if result["deleted"]:
    access_logger.info(
        "启动日志清理: 已移除 %d 个过期日志文件 (%s)",
        result["deleted"],
        ", ".join(result["files"][:5]),
    )
