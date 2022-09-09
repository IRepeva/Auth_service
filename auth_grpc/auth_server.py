from concurrent import futures

import grpc

import auth_pb2 as pb2
import auth_pb2_grpc as pb2_grpc
from app.app import app
from app.databases import db, cache
from app.models import User
from core.settings import settings
from utils.access_validation import is_token_valid, is_allowed


class AuthService(pb2_grpc.AuthServicer):

    def __init__(self, *args, **kwargs):
        pass

    def HasAccess(self, request, context):
        token, roles = request.token, request.roles
        if not token:
            result = {'message': 'No access token', 'has_access': False}
            return pb2.HasAccessResponse(**result)

        secret_key = settings.JWT_SECRET_KEY
        status, response = is_token_valid(token, secret_key, cache)

        if not status:
            result = {'message': response, 'has_access': status}
            return pb2.HasAccessResponse(**result)

        if not roles:
            result = {'message': 'success', 'has_access': status}
            return pb2.HasAccessResponse(**result)

        user_id = response['sub']['user_id']
        with app.app_context():
            user = db.session.query(User).filter(User.id == user_id).first()
            user_roles = [role.name for role in user.get_user_roles()]

        if is_allowed(user_roles, or_=None, and_=roles, roles=None):
            result = {'message': 'success', 'has_access': status}
            return pb2.HasAccessResponse(**result)

        result = {
            'message': 'Not enough permissions to access',
            'has_access': False
        }
        return pb2.HasAccessResponse(**result)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_AuthServicer_to_server(AuthService(), server)
    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
