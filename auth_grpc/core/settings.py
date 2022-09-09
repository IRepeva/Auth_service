from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # JWT
    JWT_SECRET_KEY: str = Field(env='JWT_SECRET_KEY')

    # gRPC
    GRPC_PORT: int = Field(50051, env='GRPC_PORT')

    # REDIS
    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')

    # POSTGRES
    POSTGRES_URL = Field(
        f'postgresql://postgres:123qwe@127.0.0.1:5432/auth',
        env='POSTGRES_URL'
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
