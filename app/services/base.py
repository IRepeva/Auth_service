from dataclasses import dataclass
from typing import Any

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError


@dataclass
class ElasticSearchManager:
    model: Any

    async def get_list(self, sort: str | None = None, page: int | None = 1,
                       page_size: int | None = 50, **kwargs):

        from api.v1.utils.query_parser import QueryParser
        try:
            doc = await self.model.elastic.search(
                index=self.model.INDEX,
                body=await QueryParser.parse_params(self.model, **kwargs),
                from_=page_size * (page - 1),
                size=page_size,
                sort=QueryParser.parse_sort(sort) if sort else None
            )
        except NotFoundError:
            return None

        return [self.model.MODEL(**item['_source']) for item in
                doc['hits']['hits']]

    async def get_by_id(self, _id):
        try:
            doc = await self.model.elastic.get(self.model.INDEX, _id)
        except NotFoundError:
            return None
        return self.model.MODEL(**doc['_source'])


class BaseService:
    INDEX = None
    MODEL = None

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_query(self, param, value):
        query = getattr(self, param)(value)
        return query.to_dict() if query else None

    @property
    def es_manager(self):
        return ElasticSearchManager(self)

    async def get_by_id(self, _id):
        return await self.es_manager.get_by_id(_id)

    async def get_list(self, **kwargs):
        return await self.es_manager.get_list(**kwargs)
