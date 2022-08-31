import logging
import os
import sys

from elasticsearch import Elasticsearch

from utils.backoff import backoff

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base)
from core.config import settings

logger = logging.getLogger(__name__)

elastic_host = f'{settings.ELASTIC_URL}'
elastic = Elasticsearch(hosts=[elastic_host])


@backoff(start_sleep_time=1, factor=2, border_sleep_time=6, logger=logger)
def check_es_connection():
    while not elastic.ping():
        logger.info(f'Trying to connect to {elastic_host}...')
        raise ConnectionRefusedError
    logger.info(f'Connected to {elastic_host}')


if __name__ == '__main__':
    check_es_connection()
