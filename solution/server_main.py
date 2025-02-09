import socket
import threading
import json
from server_obtainargs import extract_args

from http_decoder import HTTPDecoderStatus, HTTPType, HTTPDecoder
from http_encoder import encode_http_response
from solution.http_request import HTTPRequest
from solution.http_response import HTTPResponse, StatusCode
from solution.http_versions import HTTPVersion
from solution.server_endpoint import Endpoint


class Server:
    def __init__(self, ip, port, listen=4, http_version: str = HTTPVersion.HTTP1_1.value):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(listen)
        self.endpoints: list[Endpoint] = []
        self.http_version = http_version
        print(f"Server started at {self.ip}:{self.port}")

    def add_endpoint(self, endpoint: Endpoint):
        self.endpoints.append(endpoint)

    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        client_socket.settimeout(10)  # Timeout for idle connections
        remainder = b""
        active = True

        while active:
            decoder = HTTPDecoder(remainder)

            # Read until a full HTTP request is decoded or an error occurs
            while decoder.decoder_status not in {HTTPDecoderStatus.Error, HTTPDecoderStatus.Finished}:
                try:
                    chunk = client_socket.recv(8096)
                    if not chunk:
                        active = False  # Client closed connection
                        break
                    decoder.add_chunk(chunk)
                except socket.timeout:
                    print("Timeout reached, closing connection.")
                    active = False
                    break

            if decoder.decoder_status == HTTPDecoderStatus.Error:
                print("Decoder error, closing connection.")
                break

            assert decoder.method is not None
            assert decoder.path is not None
            assert decoder.http_version is not None
            assert decoder.headers is not None

            content_length = int(decoder.headers.get("content-length", 0))
            remainder = decoder.remainder

            if len(remainder) < content_length:
                missing_length = content_length - len(remainder)
                body = remainder

                while missing_length > 0:
                    try:
                        chunk = client_socket.recv(min(8096, missing_length))
                        if not chunk:
                            active = False
                            break
                        body += chunk
                        missing_length -= len(chunk)
                    except socket.timeout:
                        print("Timeout while reading body, closing connection.")
                        active = False
                        break
            else:
                body = remainder[:content_length]

            request = HTTPRequest(decoder.http_version, decoder.method, decoder.path, decoder.headers, body)

            print(f"Method: {request.method}, Path: {request.path}, Headers: {request.headers}, Body: {request.body}")

            response = HTTPResponse(self.http_version, StatusCode.Status404NotFound.value, {}, None)

            for endpoint in self.endpoints:
                if endpoint.method == request.method:
                    try:
                        args = extract_args(endpoint.path, request.path)
                        response = endpoint.handler(args, request)
                        break
                    except ValueError:
                        active=False
                        continue

            self.send_response(client_socket, response)

            remainder = remainder[content_length:] if len(remainder) > content_length else b""

        client_socket.close()

    def send_response(self, client_socket: socket.socket, response: HTTPResponse):
        data = encode_http_response(response.version, response.status, response.headers, response.body.decode('utf-8'))

        client_socket.sendall(data.encode('utf-8'))



