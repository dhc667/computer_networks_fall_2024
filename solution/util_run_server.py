from server_main import Server
from server_main import Endpoint
from http_response import HTTPResponse
from http_request import HTTPRequest

import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])

server = Server(HOST, PORT)

message = b'Welcome to the server!'
message_length = len(message)
server.add_endpoint(Endpoint(
    'GET',
    '/',
    lambda args, req: HTTPResponse(200, {'Content-Type': 'text/plain', 'Content-length': str(message_length)}, message)
))

server.add_endpoint(Endpoint(
    'POST',
    '/',
    lambda args, req: HTTPResponse(200, {'Content-Type': 'text/plain', 'Content-length': str(23)}, b'POST request successful')
))

server.add_endpoint(Endpoint(
    'HEAD',
    '/',
    lambda args, req: HTTPResponse(200, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')
))

def add_x_y(args: dict, req: HTTPRequest) -> HTTPResponse:
    x = int(args['x'])
    y = int(args['y'])
    answ = x + y
    encoded_answ = str(answ).encode('iso-8859-1')
    return HTTPResponse(200, {'Content-Type': 'text/plain', 'Content-length': str(len(encoded_answ))}, encoded_answ)

server.add_endpoint(Endpoint(
    'GET',
    '/:x/plus/:y',
    add_x_y
))

server.start()
