import json

import grpc
from concurrent import futures
import time
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2
import jwt


class UnaryService(pb2_grpc.UnaryServicer):

    def __init__(self, *args, **kwargs):
        pass

    def HasAccess(self, request, context):

        # get the string from the incoming request
        message = request.token
        print(f'server: {request.token}, {request.roles}')
        if token := request.token:
            key = 'PupsSecret'
            try:
                # print(dir(jwt))
                payload = jwt.decode(token, key, algorithms=["HS256"])
                print(f'PAY! {payload}')
                returned = payload
            except Exception as e:
                print(f'NOT PAY! {e}')
                returned = 'NO RESULT'
        result = json.dumps(returned)
        result = {'has_access': True}

        return pb2.HasAccessResponse(**result)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_UnaryServicer_to_server(UnaryService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    print('i am alive, alive!')
    serve()
