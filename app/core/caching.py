import asyncio

from functools import wraps
from fastapi_cache.decorator import cache

from core.logger import root
from core.config import settings


def ttl_for(key: str) -> int:
    return getattr(settings, f'TTL_{key.upper()}', settings.TTL_DEFAULT)


def logged_cache(expire: int):
    def decorator(func):
        is_coroutine = asyncio.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            root.info(
                f'Cache MISS for async {func.__name__} with args={args} kwargs={kwargs}'
            )

            result = await func(*args, **kwargs)

            root.info(
                f'Cached result for async {func.__name__}'
            )

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            root.info(
                f'Cache MISS for {func.__name__} with args={args} kwargs={kwargs}'
            )

            result = func(*args, **kwargs)

            root.info(
                f'Cached result for {func.__name__}'
            )

            return result

        if is_coroutine:
            return cache(expire=expire)(async_wrapper)

        else:
            return cache(expire=expire)(sync_wrapper)

    return decorator
