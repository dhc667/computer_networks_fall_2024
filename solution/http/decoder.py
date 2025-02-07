import re
from enum import Enum

from solution.http.response import StatusCode

# NOTE: Re example:
# pattern = re.compile(r'^http://(?P<host>[^:/]+)(?::(?P<port>\d+))?(?P<path>/.*)?$')

class HTTPDecoderStatus(Enum):
    Error = 'Error'
    
    Initial = 'Initial'
    
    ParsingMethod = 'ParsingMethod'
    ParsingVersion = 'ParsingVersion'
    ParsingStatus = 'ParsingStatus'
    ParsingPath = 'ParsingPath'
    ParsingHeaders = 'ParsingHeaders'
    ParsingBody = 'ParsingBody'


class HTTPDecoder():
    source: bytes
    current_index: int
    decoder_status: HTTPDecoderStatus

    http_version: str
    method: str | None
    status: int | None
    headers: dict[str, str]
    body: bytes | None

    def __init__(self, source: bytes) -> None:
        self.source = source
        self.current_index = 0
        self.finished_parsing = False 

    def parse_response_line(self) -> re.Match[str] | None:
        pass

    def parse_request_line(self) -> re.Match[str] | None:
        pass




