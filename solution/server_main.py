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
        data = b""
        while True:
            chunk = client_socket.recv(8096)
            if not chunk:
                break
            data += chunk
        decoder = HTTPDecoder(data)
        
        if decoder.decoder_status == HTTPDecoderStatus.Error:
            client_socket.close()
            return

        if decoder.type == HTTPType.Response:
            client_socket.close()
            return

        #  NOTE: So my language server doesn't complain about sending optional values to the constructor
        assert decoder.method is not None
        assert decoder.path is not None
        assert decoder.http_version is not None
        assert decoder.headers is not None

        request: HTTPRequest = HTTPRequest(decoder.http_version, decoder.method, decoder.path, decoder.headers, decoder.body)

        method = request.method
        path = request.path
        headers = request.headers
        body = request.body

        print(f"Method: {method}, Path: {path}, Headers: {headers}, Body: {body}")

        response = HTTPResponse(self.http_version, StatusCode.Status404NotFound.value, {}, None)

        for endpoint in self.endpoints:
            if endpoint.method == method:
                try:
                    args = extract_args(endpoint.path, path)
                    response = endpoint.handler(args, request)
                    break
                except ValueError:
                    continue

        self.send_response(client_socket, response)
        client_socket.close()


    def send_response(self, client_socket: socket.socket, response: HTTPResponse):
        data = encode_http_response(response.version, response.status, response.headers, response.body.decode('utf-8'))

        client_socket.sendall(data.encode('utf-8'))



