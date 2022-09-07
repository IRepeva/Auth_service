from functools import wraps
from http import HTTPStatus

import jwt
from core.config import settings
from fastapi import HTTPException

from utils.access_validation import is_allowed


def is_authorized(**kwargs):
    request = kwargs['request']
    if token := request.headers.get('Authorization'):
        token = token.split(' ')[1]
        key = settings.JWT_SECRET_KEY
        try:
            payload = jwt.decode(token, key, algorithms=["HS256"])
            return True, payload
        except Exception as e:
            return False, e
    return False, 'No access token in Headers'


def authorized(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user_authorized, _ = is_authorized(**kwargs)
        if user_authorized:
            return await func(*args, **kwargs)

        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=str(_)
        )
    return wrapper


def has_access(*roles, or_=None, and_=None):
    def wrapper(func):
        @wraps(func)
        async def decorator(*args, **kwargs):
            user_authorized, result = is_authorized(**kwargs)
            if user_authorized:
                user_roles = result['sub']['roles']
                if is_allowed(user_roles, or_, and_, roles):
                    return await func(*args, **kwargs)

                result = 'Not enough permissions to access'

            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=str(result)
            )

        return decorator

    return wrapper
