import socket
from urlparser import urlparser
from argparser_builder import get_parser
from http_encoder import encode_http_request


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

http_request = encode_http_request(args.m, host, port, path, args.h, args.b)

# print(f"HTTP Request:\n")
# print(http_request)

# Establish a socket connection
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(bytes(http_request, "utf-8"))
        response = s.recv(4096, socket.MSG_WAITALL)
        s.close() 
    # Print the response
    # print(f"HTTP Response:\n")
    print(response.decode("utf-8"))
except Exception as e:
    print(f"Socket error: {e}")


