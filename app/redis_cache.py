from functools import wraps
from .databases import redis_client
from .import Logger
import json
import redis

def distributed_cache(key_pattern: str, ttl : int = 30):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = key_pattern.format(**kwargs)
            try:
                cache_date = redis_client.get(cache_key)
                if cache_date:
                    Logger.debug(f"Cache en la llave: {cache_key}")
                    return json.loads(cache_date)
                result = await func(*args, **kwargs)
                redis_client.setex(cache_key, ttl, json.dump(result))
                return result
            
            except redis.RedisError as e:
                Logger.error(f"Redis error: {str(e)}")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
