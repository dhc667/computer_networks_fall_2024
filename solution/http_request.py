from __future__ import annotations
from enum import Enum

from http_versions import HTTPVersion

class StandardHTTPMethod(Enum):
    GET = 'GET'
    HEAD = 'HEAD'
    
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    CONNECT = 'CONNECT'
    OPTIONS = 'OPTIONS'
    TRACE = 'TRACE'
    
    @staticmethod
    def from_str(method: str) -> StandardHTTPMethod | None:
        answ = list(filter(lambda m: m.value == method, [m for m in StandardHTTPMethod]))
        if len(answ) != 1: return None
        return answ[0]

class HTTPRequest:
    def __init__(self, version: str, method: str, path: str, headers: dict, body: bytes):
        self.version = version
        self.method = method
        self.headers = headers
        self.body = body
        self.path = path
