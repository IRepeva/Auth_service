import datetime
import string
from functools import wraps
from secrets import choice as secrets_choice

from flask import request
from flask_rebar import errors

from api.models import LoginHistory
from databases import cache


def get_device_type(user_agent):
    match user_agent:
        case user_agent.is_mobile:
            return LoginHistory.DEVICE_TYPES['mobile']
        case user_agent.is_pc:
            return LoginHistory.DEVICE_TYPES['pc']
        case user_agent.is_tablet:
            return LoginHistory.DEVICE_TYPES['tablet']
    return LoginHistory.DEVICE_TYPES['other']


def generate_random_string(char_num=16):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets_choice(alphabet) for _ in range(char_num))


def generate_fake_email():
    return generate_random_string(8) + '@fake.fake'


def rate_limit(limit=20):
    def rate_limit_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now_minute = datetime.datetime.now().minute

            current_minute_key = f'limit:{request.remote_addr}:{now_minute}'
            current_count = cache.get(current_minute_key)
            if current_count and int(current_count) >= limit:
                raise errors.TooManyRequests()

            pipe = cache.pipeline()
            pipe.incr(current_minute_key, 1)
            pipe.expire(current_minute_key, 60)
            pipe.execute()

            return func(*args, **kwargs)

        return wrapper

    return rate_limit_decorator
