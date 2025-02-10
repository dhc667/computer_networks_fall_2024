from server_main import Server
from server_main import Endpoint
from http_response import HTTPResponse
from http_request import HTTPRequest
from time import sleep

import sys

if sys.argv.__len__() != 3:
    print("usage: python3 <script_path> <HOST> <PORT>")
    exit(1)

HOST = sys.argv[1]
PORT = int(sys.argv[2])

server = Server(HOST, PORT)

message = b'Welcome to the server!'
message_length = len(message)
server.add_endpoint(Endpoint(
    'GET',
    '/',
    lambda args, req: HTTPResponse(200, {'Content-Type': 'text/plain', 'Content-length': str(message_length)}, message)))

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

def fib_handle(args: dict[str, str], _: HTTPRequest) -> HTTPResponse:
    fib = lambda x: 1 if x <= 1 else fib(x - 1) + fib(x - 2)

    n = int(args['n'])
    answ = fib(n)

    encoded_answ = str(answ).encode('iso-8859-1')

    return HTTPResponse(
        200,
        {
            "Content-type": "text/plain",
            "Content-length": str(encoded_answ.__len__())
        },
        encoded_answ
    )

server.add_endpoint(Endpoint(
    'GET',
    '/fib/:n',
    fib_handle
))

def wait_handle(args: dict[str, str], _: HTTPRequest) ->  HTTPResponse:
    time = int(args['time'])
    
    sleep(time)

    answ = f"Slept {time} seconds!\n"
    encoded = answ.encode('iso-8859-1')

    return HTTPResponse(
        200, 
        {
            'Content-type': 'text/plain',
            'Content-length': str(len(encoded))
        },
        encoded
    )

server.add_endpoint(Endpoint(
    'GET',
    '/sleep/:time',
    wait_handle
))

def receive_png_handler(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    content_length = int(req.headers['content-length'])
    body = req.body

    with open('./our_tests/received/png1.png', 'wb') as f:
        f.write(body)

    answ = b'File received'

    return HTTPResponse(
        200,
        {
            'Content-type': 'text/plain',
            'Content-length': str(len(answ))        
        },
        answ
    )

server.add_endpoint(Endpoint(
    'POST',
    '/receive_png',
    receive_png_handler
))

server.start()
