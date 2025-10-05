from functools import wraps
from cachetools import TTLCache
import hashlib
import json


def cache_response(ttl: int = 300):
    cache = TTLCache(maxsize=1000, ttl=ttl)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Создаем ключ кеша на основе аргументов функции
            key_parts = [func.__name__] + [str(arg) for arg in args] + [f"{k}:{v}" for k, v in kwargs.items()]
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            if cache_key in cache:
                return cache[cache_key]

            result = await func(*args, **kwargs)
            cache[cache_key] = result
            return result

        return wrapper

    return decorator