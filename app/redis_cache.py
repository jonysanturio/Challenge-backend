from functools import wraps
from .databases import redis_client
import logging
import json
import redis

log = logging.getLogger("cache")

def to_dict(result):
    if hasattr(result, "__table__"):
        return {c.name: getattr(result, c.name) for c in result.__table__.columns}
    return result

def distributed_cache(key_pattern: str, ttl : int = 30):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key_pattern.format(**kwargs)
            try:
                cache_date = redis_client.get(cache_key)
                if cache_date:
                    return json.loads(cache_date)
                result = func(*args, **kwargs)
                payload = to_dict(result)
                redis_client.setex(cache_key, ttl, json.dumps(payload, default=str))
                return result
            
            except redis.RedisError as e:
                logging.error(f"Redis error: {str(e)}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
