import json
from functools import wraps

import redis

from core.settings import REDIS_HOST, REDIS_PORT

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def cache_decorator():
    """Redis cache decorator.

    :param expiration_time: time in seconds
    :return: Redis cached data.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            cache_key = kwargs.pop("cache_key", None)
            redis_client.delete(cache_key)
            if not cache_key:
                return func(self, request, None, None, *args, **kwargs)

            cached_images = redis_client.lrange(cache_key, 0, -1)
            image_data = None
            if cached_images:
                image_data = json.loads(cached_images[0])
                redis_client.lpop(cache_key)
            return func(self, request, image_data, cache_key, *args, **kwargs)

        return wrapper

    return decorator
