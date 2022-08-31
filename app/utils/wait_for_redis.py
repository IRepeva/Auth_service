import logging
import os
import sys

import redis

from utils.backoff import backoff

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base)
from core.config import settings

logger = logging.getLogger(__name__)

redis = redis.Redis.from_url(url=settings.REDIS_URL)


@backoff(start_sleep_time=1, factor=2, border_sleep_time=6, logger=logger)
def check_redis_connection():
    while not redis.ping():
        logger.info('Trying to connect to redis...')
        raise redis.exceptions.ConnectionError
    logger.info(
        f"Connected to {str(settings.REDIS_URL)}"
    )


if __name__ == '__main__':
    check_redis_connection()
