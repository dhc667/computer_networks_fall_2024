from enum import Enum

from http_versions import HTTPVersion

class StatusCode(Enum):
    """Three digit numbers which indicate the status of a response"""
    
    Status200OK = 200
    Status301MovedPermanently = 301
    Status400BadRequest = 400
    Status404NotFound = 404
    Status403Unauthorized = 403
    Status501NotImplemented = 501

class HTTPResponse:
    def __init__(self, version: HTTPVersion, status: int, headers: dict[str, str], body: bytes | None):
        if body == None: body = b""
        self.version = version
        self.status = status
        self.headers = headers
        self.body: bytes = body
