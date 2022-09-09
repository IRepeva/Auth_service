import sys
from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

sys.path.append('.')
from db.elastic import get_elastic
from db.redis import get_redis
from api.v1.models import Genre
from services.base import BaseService


class GenreService(BaseService):
    INDEX = 'genres'
    MODEL = Genre


@lru_cache
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
