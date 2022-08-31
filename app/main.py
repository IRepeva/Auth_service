import aioredis
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import films, genres, persons
from utils.wait_for_es import check_es_connection
from utils.wait_for_redis import check_redis_connection
from core.config import settings
from core.logger import LOGGING
from db import elastic, redis

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    check_es_connection()
    check_redis_connection()

    pool = aioredis.ConnectionPool.from_url(
        str(settings.REDIS_URL),
        max_connections=20
    )
    redis.redis = aioredis.Redis(connection_pool=pool)
    elastic.es = AsyncElasticsearch(hosts=[f'{settings.ELASTIC_URL}'])


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
        log_config=LOGGING,
        log_level='info'
    )
