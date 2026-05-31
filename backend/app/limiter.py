"""速率限制器实例（独立模块，避免循环导入）"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute", "1000/hour"],
)
