from typing import Callable
from http_request import HTTPRequest, HTTPMethod
from http_response import HTTPResponse

class Endpoint:
    def __init__(self, method: HTTPMethod, path: str, handler: Callable[[dict, HTTPRequest], HTTPResponse]) -> None:
        self.method = method
        self.path = path
        self.handler = handler



