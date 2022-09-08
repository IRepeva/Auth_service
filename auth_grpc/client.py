import grpc
import unary_pb2_grpc as pb2_grpc
# import auth_pb2_grpc as pb2_grpc
# import auth_pb2 as pb2
import unary_pb2 as pb2


class AuthClient(object):
    """
    Client for gRPC functionality
    """

    def __init__(self):
        self.host = 'grpc'
        self.server_port = 50051

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client and the server
        self.stub = pb2_grpc.UnaryStub(self.channel)
        # self.stub = pb2_grpc.AuthStub(self.channel)

    def get_url(self, message):
        """
        Client function to call the rpc for GetServerResponse
        """
        print(message)
        mess = pb2.Message(token=message, roles=['1', '2'])
        # mess = pb2.Token(token='message')
        print(f'OOOOOOOOOOOOOOOOOOOOOOO {mess}')
        # return self.stub.GetServerResponse(mess)
        return self.stub.HasAccess(mess)


if __name__ == '__main__':
    client = AuthClient()
    result = client.get_url(message="Hello Server you there?")
    print(f'{result}')
