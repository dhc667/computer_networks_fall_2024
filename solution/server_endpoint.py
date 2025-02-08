from typing import Callable
from http_request import HTTPRequest 
from http_response import HTTPResponse

class Endpoint:
    def __init__(self, method: str, path: str, handler: Callable[[dict, HTTPRequest], HTTPResponse]) -> None:
        self.method = method
        self.path = path
        self.handler = handler



