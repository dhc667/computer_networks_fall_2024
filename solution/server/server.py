import socket
import threading
import json
from obtainargs import extract_args
from enum import Enum

class Request:
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body

class ResponseStatus(Enum):
    OK = 200
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

class Server:
    def __init__(self, ip, port, listen=4):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(listen)
        self.endpoints = []
        print(f"Server started at {self.ip}:{self.port}")

    def add_endpoint(self, method, path, func):
        self.endpoints.append((method, path, func))

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
        decoded_data = self.decoder(data)
        method, path, headers, body = self.parse_request(decoded_data)

        print(f"Method: {method}, Path: {path}, Headers: {headers}, Body: {body}")

        response_status = ResponseStatus.NOT_FOUND
        response_body = "Not Found"

        for endpoint_method, endpoint_path, endpoint_func in self.endpoints:
            if endpoint_method == method:
                try:
                    args = extract_args(endpoint_path, path)
                    req = Request(headers, body)
                    response_status, response_body = endpoint_func(args, req)
                    break
                except ValueError:
                    continue

        self.send_response(client_socket, response_status, response_body)
        client_socket.close()




    # Dummy code to test the server
    def decoder(self, data):
        return data.decode('utf-8')
    # Dummy code to test the server
    def parse_request(self, data):
        lines = data.split("\r\n")
        method, path, _ = lines[0].split(" ")
        headers = {}
        body = ""
        i = 1
        while lines[i] != "":
            key, value = lines[i].split(": ")
            headers[key] = value
            i += 1
        if "Content-Length" in headers:
            body = json.loads(lines[i + 1])
        return method, path, headers, body
    # Dummy code to test the server
    def send_response(self, client_socket, status, body):
        response_line = f"HTTP/1.1 {status.value} {status.name.replace('_', ' ')}\r\n"
        headers = "Content-Type: application/json\r\n"
        body = json.dumps(body)
        response = response_line + headers + "\r\n" + body
        client_socket.sendall(response.encode('utf-8'))



if __name__ == "__main__":
    server = Server("127.0.0.1", 8080)
    server.start()
    
    def hello_world(args, req):
        return ResponseStatus.OK, {"message": "Hello, World!"}

    def echo(args, req):
        return ResponseStatus.OK, {"you_sent": req.body}

    server.add_endpoint("GET", "/hello", hello_world)
    server.add_endpoint("POST", "/echo", echo)
