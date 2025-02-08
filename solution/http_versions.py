from __future__ import annotations
from enum import Enum

class HTTPVersion(Enum):
    HTTP1_1 = 'HTTP/1.1'
    HTTP1_0 = 'HTTP/1.0'
    
    @staticmethod
    def from_str(version: str) -> HTTPVersion | None:
        answ = list(filter(lambda m: m.value == version, [m for m in HTTPVersion]))
        if len(answ) != 1: return None
        return answ[0]

