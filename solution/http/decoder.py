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

        http_version = r'HTTP/1.[10]'
        status = r'(?P<status>[0-9]{3})(?P<status_desc>[A-Za-z])'

        match = re.match(http_version + ' ' + status, self.source[self.current_index:])

        return match

    def parse_request_line(self) -> re.Match[str] | None:

        http_version = r'HTTP/1.[10]'
        method = '(' + '|'.join([item.value for item in Method]) + ')'
        request_target = 

def decode_http_request(request: bytes):
    
    header_field = r'(?P<key>):()'

    # NOTE: We only expect a single space character as the separator, we could parse more
    #       but lenient pasing can introduce vulnerabilities
    http_regexp = f'^{http_version} {status}'

    pattern = re.copile()




