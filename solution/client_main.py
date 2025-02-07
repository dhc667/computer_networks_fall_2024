import json
import socket
from client_urlparser import urlparser
from client_argparser_builder import get_parser
from http_encoder import encode_http_request
from http_decoder import decode_http
from http_response import HTTPResponse
parser = get_parser()
args = parser.parse_args()
urlparser = urlparser(args.u)

host = urlparser.host
port = urlparser.port
path = urlparser.path

# print(f"Method: {args.m}")
# print(f"Headers: {args.h}")
# print(f"Body: {args.b}")
# print(f"Host: {host}")
# print(f"Port: {port}")
# print(f"Path: {path}")

http_request = encode_http_request(args.m, host, port, path, args.h, args.d)
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

    response: HTTPResponse = decode_http(response)

    print(json.dumps({
        "status": response.status,
        "body": response.body.decode("utf-8"),
        "headers": response.headers
    }))
        

except Exception as e:
    print(f"Socket error: {e}")


