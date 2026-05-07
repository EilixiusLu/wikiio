import logging
import logging.handlers
import os
from pathlib import Path

# 创建日志目录
LOG_DIR = Path(__file__).parent.parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: str, filename: str, level=logging.INFO) -> logging.Logger:
    """创建一个带文件和控制台输出的logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 文件handler：每天轮转，保留30天
    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_DIR / filename,
        when="midnight",
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# 各模块logger
access_logger = setup_logger("wikiio.access", "access.log")
crawler_logger = setup_logger("wikiio.crawler", "crawler.log")
rating_logger = setup_logger("wikiio.rating", "rating.log")
error_logger = setup_logger("wikiio.error", "error.log", level=logging.ERROR)