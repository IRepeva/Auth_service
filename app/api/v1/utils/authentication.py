import sys
from functools import wraps
from http import HTTPStatus

import jwt
from fastapi import HTTPException

sys.path.extend(['/app/auth_grpc', '.'])
from core.config import settings
from auth_grpc import auth_grpc_pb2_grpc as pb2_grpc
# from auth_grpc import unary_pb2_grpc as pb2_grpc
# from auth_grpc import unary_pb2 as pb2
from auth_grpc import auth_grpc_pb2 as pb2
from utils.access_validation import is_allowed

import grpc


class UnaryClient(object):
    """
    Client for gRPC functionality
    """

    def __init__(self, host='localhost', port=50051):
        # self.host = 'localhost'
        self.host = host
        self.server_port = port

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client and the server
        # self.stub = pb2_grpc.UnaryStub(self.channel)
        self.stub = pb2_grpc.AuthStub(self.channel)

    # def get_url(self, message):
    #     """
    #     Client function to call the rpc for GetServerResponse
    #     """
    #     message = pb2.Message(message=message)
    #     print(f'{message}')
    #     return self.stub.GetServerResponse(message)

    def get_url(self, token, roles):
        """
        Client function to call the rpc for GetServerResponse
        """
        print(f'in get url, token: {token}, roles: {roles}')
        message = pb2.Token(token=token, roles=roles)
        # message = pb2.Message(token=token, roles=roles)
        print(f'{message}, {type(message)}')
        print(f'OOOOOOOOOH: {dir(self.stub)}')
        print(f'OOOOOOOOOH: {self.stub.GetServerResponse(message)}')
        return self.stub.GetServerResponse(message)
        # return self.stub.GetServerResponse(message)


grpc_client = UnaryClient(
    host=settings.GRPC_HOST, port=settings.GRPC_PORT
)


def get_token_from_request(**kwargs):
    if request := kwargs.get('request'):
        if token := request.headers.get('Authorization'):
            try:
                return True, token.split(' ')[1]
            except IndexError:
                return False, 'Wrong token format'
        return False, 'No access token in Headers'
    return False, 'No request object provided for the endpoint'


def is_authorized(**kwargs):
    status, response = get_token_from_request(**kwargs)
    if status:
        key = settings.JWT_SECRET_KEY
        try:
            payload = jwt.decode(response, key, algorithms=["HS256"])
            return True, payload
        except Exception as e:
            return False, e

    return False, response


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
            user_authorized, resp = is_authorized(**kwargs)
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
            print(f'status: {status}, resp: {response}')
            if status:
                result = grpc_client.get_url(token=response, roles=['1'])
                print(f'MYYYYYYYYYYYYYYY {result}, {type(result)}')
                return await func(*args, **kwargs)
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=str(response)
            )

        return decorator

    return wrapper


if __name__ == '__main__':
    client = grpc_client
    print('CLIIIIIIIIIIIIII')
    print(client, 'CLIIIIIIIIIIIIII')
    # result = client.get_url(message="Bearer "
    #                                 "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2MjY0MDUwNywianRpIjoiYTUwN2QzNjAtM2NhMS00ZmVlLWI0ZTUtN2EyNDRiMTkyNDU4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJ1c2VyX2lkIjoiYWQ0YzNmNWYtMjEwMS00ZDYyLTg3NWItMjEwYTJjYmQ0MmQzIiwicm9sZXMiOlsic3VwZXJ1c2VyIl19LCJuYmYiOjE2NjI2NDA1MDcsImV4cCI6MTY2MjY0NDEwN30.Bwu6aIDx59h2gZW3Sx4NGrSDTI5qmtXA095SVoUiUKc")
    # print(f'MYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY {result}, {type(result)}')
