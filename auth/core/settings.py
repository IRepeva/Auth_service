from functools import lru_cache
from logging import config as logging_config

# LOGGING
from core.logger import LOGGING
from pydantic import BaseSettings, Field

logging_config.dictConfig(LOGGING)


BASE_CONFIG = 'core.settings.jwt_settings'
TEST_CONFIG = 'core.settings.test_settings'


class DBSettings(BaseSettings):
    # POSTGRES
    SQLALCHEMY_DATABASE_URI = Field(
        f'postgresql://postgres:123qwe@127.0.0.1:5432/auth',
        env='POSTGRES_URL'
    )

    # REDIS
    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')


class JWTSettings(BaseSettings):
    # JWT
    JWT_SECRET_KEY: str = Field(env='JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES: int = Field(60 * 60, env='JWT_EXP_ACCESS')
    JWT_REFRESH_TOKEN_EXPIRES: int = Field(60 * 60 * 24, env='JWT_EXP_REFRESH')
    JWT_REFRESH_COOKIE_PATH = '/user/'
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_TOKEN_LOCATION = ['headers', 'cookies']


class TestSettings(BaseSettings):
    # POSTGRES
    SQLALCHEMY_DATABASE_URI = Field(
        f'postgresql://postgres:123qwe@127.0.0.1:5432/auth',
        env='POSTGRES_URL'
    )

    # REDIS
    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')

    # JWT
    JWT_SECRET_KEY: str = Field(env='JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES: int = Field(60 * 60, env='JWT_EXP_ACCESS')
    JWT_REFRESH_TOKEN_EXPIRES: int = Field(60 * 60 * 24, env='JWT_EXP_REFRESH')
    JWT_REFRESH_COOKIE_PATH = '/user/'
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_TOKEN_LOCATION = ['headers', 'cookies']


@lru_cache
def get_db_settings() -> DBSettings:
    return DBSettings()


@lru_cache
def get_jwt_settings() -> JWTSettings:
    return JWTSettings()


@lru_cache
def get_test_settings() -> TestSettings:
    return TestSettings()


db_settings = get_db_settings()
jwt_settings = get_jwt_settings()
test_settings = get_test_settings()
