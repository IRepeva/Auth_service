import sys
from functools import wraps
from http import HTTPStatus

from fastapi import HTTPException
from utils.wait_for_redis import redis

sys.path.extend(['/app/auth_grpc', '.'])
from core.config import settings
from auth_grpc import auth_pb2_grpc as pb2_grpc
from auth_grpc import auth_pb2 as pb2
from utils.access_validation import (
    is_allowed, is_authorized, get_token_from_request
)

import grpc


class AuthClient(object):
    """
    Client for gRPC functionality
    """

    def __init__(self, host='localhost', port=50051):
        self.host = host
        self.server_port = port

        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        self.stub = pb2_grpc.AuthStub(self.channel)

    def get_auth_response(self, token, roles):
        message = pb2.Message(token=token, roles=roles)
        return self.stub.HasAccess(message)


grpc_client = AuthClient(
    host=settings.GRPC_HOST, port=settings.GRPC_PORT
)


def authorized(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user_authorized, _ = is_authorized(
            secret_key=settings.JWT_SECRET_KEY,
            cache=redis, **kwargs
        )
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
            user_authorized, resp = is_authorized(
                secret_key=settings.JWT_SECRET_KEY,
                cache=redis, **kwargs
            )
            if user_authorized:
                user_roles = resp['sub']['roles']
                if is_allowed(user_roles, or_, and_, roles):
                    return await func(*args, **kwargs)

                resp = 'Not enough permissions to access'

            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=str(resp)
            )

        return decorator

    return wrapper


def strict_verification(*roles, or_=None, and_=None):
    def wrapper(func):
        @wraps(func)
        async def decorator(*args, **kwargs):
            status, response = get_token_from_request(**kwargs)
            if status:
                response = grpc_client.get_auth_response(
                    token=response, roles=roles
                )
                if response.has_access:
                    return await func(*args, **kwargs)

                response = response.message
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=str(response)
            )

        return decorator

    return wrapper
