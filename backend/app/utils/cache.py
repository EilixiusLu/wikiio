import json
import time
from functools import wraps

from fastapi import Response
from fastapi.encoders import jsonable_encoder
from redis.asyncio import ConnectionPool, Redis

from app.config import settings
from app.utils.logger import error_logger

_pool: ConnectionPool | None = None

# ---- 可用性快速检测 ----
# 如果本机没有运行 Redis，每次连接尝试都会阻塞 socket_timeout 秒，
# 导致每个请求额外等待数秒。这里用一个标志位在首次失败后跳过后续尝试。
_redis_available: bool | None = None   # None=未检测, True=可用, False=不可用
_redis_checked_at: float = 0.0
_RECHECK_INTERVAL: float = 60.0        # 不可用后每隔 60s 重试一次


async def _check_redis() -> bool:
    """检测 Redis 是否可用（PING 一次），更新全局标志"""
    global _redis_available, _redis_checked_at
    _redis_checked_at = time.monotonic()
    try:
        r = get_redis()
        await r.ping()
        _redis_available = True
        return True
    except Exception:
        _redis_available = False
        return False


async def _should_skip() -> bool:
    """判断是否应该跳过缓存操作（Redis 不可用时跳过以避免超时）"""
    global _redis_available
    if _redis_available is True:
        return False  # 之前验证过可用，正常使用
    if _redis_available is None:
        # 首次使用，必须检查一次
        return not await _check_redis()
    # _redis_available is False
    elapsed = time.monotonic() - _redis_checked_at
    if elapsed >= _RECHECK_INTERVAL:
        # 间隔到了，重试一次
        return not await _check_redis()
    return True  # 跳过，避免超时


def get_redis() -> Redis:
    """获取 Redis 客户端（惰性连接池，单例）"""
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
            max_connections=10,
        )
    return Redis.from_pool(_pool)


def _prefixed(key: str) -> str:
    """为缓存键添加统一前缀"""
    return f"{settings.REDIS_CACHE_PREFIX}{key}"


async def cache_get(key: str) -> str | None:
    """读取缓存，Redis 不可用或失败返回 None"""
    if await _should_skip():
        return None
    try:
        redis = get_redis()
        val = await redis.get(_prefixed(key))
        return val
    except Exception:
        error_logger.warning(f"Cache get failed for key={key}")
        return None


async def cache_set(key: str, value, ttl: int) -> None:
    """写入缓存，Redis 不可用或失败静默忽略"""
    if await _should_skip():
        return
    try:
        redis = get_redis()
        encoded = json.dumps(jsonable_encoder(value), ensure_ascii=False)
        await redis.setex(_prefixed(key), ttl, encoded)
    except Exception:
        error_logger.warning(f"Cache set failed for key={key}")


async def cache_delete(key: str) -> None:
    """删除单个缓存键，Redis 不可用或失败静默忽略"""
    if await _should_skip():
        return
    try:
        redis = get_redis()
        await redis.delete(_prefixed(key))
    except Exception:
        error_logger.warning(f"Cache delete failed for key={key}")


async def cache_clear_pattern(pattern: str) -> None:
    """按模式删除缓存键（使用 SCAN 非阻塞扫描）"""
    if await _should_skip():
        return
    try:
        redis = get_redis()
        full_pattern = _prefixed(pattern)
        cursor = 0
        while True:
            cursor, keys = await redis.scan(
                cursor=cursor, match=full_pattern, count=100
            )
            if keys:
                await redis.delete(*keys)
            if cursor == 0:
                break
    except Exception:
        error_logger.warning(f"Cache clear pattern failed for pattern={pattern}")


def cached(ttl: int, key_prefix: str):
    """
    端点缓存装饰器。

    用法:
        @router.get("/{page_id}")
        @cached(ttl=300, key_prefix="page:{page_id}")
        async def get_page(page_id: int, ...):
            ...

    参数:
        ttl: 缓存有效期（秒）
        key_prefix: 缓存键模板，用端点函数参数的 .format(**kwargs) 展开
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = key_prefix.format(**kwargs)

            # 尝试读缓存
            cached_val = await cache_get(key)
            if cached_val is not None:
                return Response(content=cached_val, media_type="application/json")

            # 缓存未命中，执行原函数
            result = await func(*args, **kwargs)

            # 异步写入缓存
            await cache_set(key, result, ttl)

            return result
        return wrapper
    return decorator
