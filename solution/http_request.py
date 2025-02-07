from enum import Enum

class Method(Enum):
    GET = 'GET'
    HEAD = 'HEAD'
    
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    CONNECT = 'CONNECT'
    OPTIONS = 'OPTIONS'
    TRACE = 'TRACE'

class HTTPRequest:
    def __init__(self, version: str, method: Method, headers: dict, body: bytes):
        self.version = version
        self.method = method
        self.headers = headers
        self.body = body
