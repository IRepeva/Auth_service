from functools import lru_cache
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING

# LOGGING
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # PROJECT
    PROJECT_NAME = Field('movies', env='PROJECT_NAME')

    # ELASTICSEARCH
    ELASTIC_URL: str = Field('http://127.0.0.1:9200', env='ES_URL')

    # REDIS
    REDIS_URL: str = Field('redis://127.0.0.1:6379', env='REDIS_URL')


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
