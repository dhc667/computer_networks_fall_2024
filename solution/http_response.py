from enum import Enum

class StatusCode(Enum):
    """Three digit numbers which indicate the status of a response"""
    
    Status200OK = 200
    Status301MovedPermanently = 301
    Status400BadRequest = 400
    Status403Unauthorized = 403
    Status501NotImplemented = 501

class HTTPResponse:
    def __init__(self, version: str, status: int, headers: dict[str, str], body: bytes | None):
        self.version = version
        self.status = status
        self.headers = headers
        self.body = body
