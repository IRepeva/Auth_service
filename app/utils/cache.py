import json
from functools import wraps
from typing import List

from aioredis import Redis
from pydantic import BaseModel

from services.base import BaseService


def get_cache_key(kwargs):
    cache_key = ''
    service = BaseService

    for key, value in kwargs.items():
        if isinstance(value, BaseService):
            service = value
            continue
        cache_key += f'-{key}:{value}'
    return service.INDEX + cache_key if service.INDEX else cache_key, service


class Cache:
    CACHE_EXPIRE_IN_SECONDS = 60 * 5

    def __init__(self, *args, **kwargs):
        self.cache_args = args
        self.cache_kwargs = kwargs

    def __call__(self, function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            cache_key, service = get_cache_key(kwargs)

            cache_result = await self._get_from_cache(service.redis, cache_key,
                                                      service.MODEL)
            if cache_result:
                return cache_result

            result = await function(*args, **kwargs)
            await self._set_to_cache(service.redis, cache_key,
                                     result, service.MODEL)
            return result

        return wrapper

    async def _get_from_cache(
            self, redis: Redis, key: str, model: BaseModel
    ) -> BaseModel | List[BaseModel] | None:
        data = await redis.get(key)
        if not data:
            return None
        data = json.loads(data)

        if isinstance(data, list):
            return [model.parse_raw(item) for item in data]

        return model.parse_obj(data)

    async def _set_to_cache(self, redis: Redis, key: str, data, model):
        if isinstance(data, list):
            data = [model.json(item) for item in data]
            return await redis.setex(key, self.CACHE_EXPIRE_IN_SECONDS,
                                     json.dumps(data))

        await redis.setex(key, self.CACHE_EXPIRE_IN_SECONDS, model.json(data))
