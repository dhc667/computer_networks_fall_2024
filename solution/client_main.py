import json
import socket
import sys
from client_urlparser import urlparser
from http_encoder import encode_http_request
from http_decoder import HTTPDecoder
from http_response import HTTPResponse
from client_argparser_builder import parse_args
from http_versions import HTTPVersion

def decode_http_response(data: bytes) -> HTTPResponse:
    decoder = HTTPDecoder(data)
    return HTTPResponse(decoder.http_version, decoder.status, decoder.headers, decoder.body)

args = sys.argv[1:]
args = parse_args(args)
urlparser = urlparser(args.url)

host = urlparser.host
port = urlparser.port
path = urlparser.path

# print(f"Method: {args.m}")
# print(f"Headers: {args.h}")
# print(f"Body: {args.data}")
# print(f"Host: {host}")
# print(f"Port: {port}")
# print(f"Path: {path}")

http_request = encode_http_request(HTTPVersion.HTTP1_1.value, args.method, host, port, path, args.headers, args.data)
# print(f"HTTP Request:\n")
# print(http_request)

def get_all_data(socket: socket.socket, buffer_size: int):
    data = socket.recv(buffer_size)
    answ = b""
    while(len(data) == buffer_size):
        answ += data
        data = socket.recv(buffer_size)
    answ += data

    return answ

# Establish a socket connection
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(bytes(http_request, "utf-8"))
        response = get_all_data(s, 1024)
        s.close()
    response: HTTPResponse = decode_http_response(response)

    print(json.dumps({
        "status": response.status,
        "body": response.body.decode("utf-8"),
        "headers": response.headers
    }))
        

except Exception as e:
    print(f"Socket error: {e}")


