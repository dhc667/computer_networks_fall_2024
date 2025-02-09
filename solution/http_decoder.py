import re
from enum import Enum
from http_request import HTTPRequest
from http_response import HTTPResponse
from http_versions import HTTPVersion

# NOTE: Re example:
# pattern = re.compile(r'^http://(?P<host>[^:/]+)(?::(?P<port>\d+))?(?P<path>/.*)?$')

class HTTPDecoderStatus(Enum):
    Error = 'Error'
    Initial = 'Initial'
    Finished = 'Finished'
    ParsingMethod = 'ParsingMethod'
    ParsingPath = 'ParsingPath'
    ParsingVersion = 'ParsingVersion'
    ParsingStatusCode = 'ParsingStatusCode'
    ParsingStatusDesc = 'ParsingStatusDesc'
    ParsingHeader = 'ParsingHeader'


class ParseletStatus(Enum):
    Unknown = 'Unknown'
    Finished = 'Finished'
    Error = 'Error'

class HTTPType(Enum):
    Response = 'Response'
    Request = 'Request'

class HTTPDecoder():
    METHOD_RE = re.compile(r'[A-Za-z]+')
    VERSION_RE = re.compile(r'HTTP/1.[01]')
    PATH_RE = re.compile(r'[^\s]+')
    STATUS_CODE_RE = re.compile(r'\d{3}')
    STATUS_DESC_RE = re.compile(r'[^\r\n]*')
    
    #  NOTE: RFC: Each field line consists of a case-insensitive field name followed by a colon (":"), optional leading whitespace, the field line value, and optional trailing whitespace.
    HEADER_RE = re.compile(r'(?P<key>[^\s]+):[\t ]*(?P<value>[^\r\n]+)[\t ]*')



    def __init__(self, source: bytes) -> None:
        self.source = source.decode('utf-8')
        self.current_index = 0
        self.decoder_status = HTTPDecoderStatus.Initial

        self.http_version: str | None = None
        self.method: str | None = None
        self.status: int | None = None
        self.headers: dict[str, str] = {}
        self.body: bytes | None = None

        self.path: str | None = None

        self.type: HTTPType | None = None
        self.remainder : b""
        self.parse()

    def add_chunk(self, chunk: bytes):
        pass
    
    def parse(self):
        def error_occurred(): return self.decoder_status == HTTPDecoderStatus.Error
        
        self.parse_start_line()
        if error_occurred(): return
        
        if not self.match_CRLF():
            self.set_error_status()
            return


        self.parse_headers()
        if error_occurred(): return

        if not self.match_CRLF():
            self.set_error_status()
            return

        self.body = self.source[self.current_index:].encode('utf-8')

        self.decoder_status = HTTPDecoderStatus.Finished

    #  NOTE: request-line = method SP request-target SP HTTP-version
    #        status-line = HTTP-version SP status-code SP [ reason-phrase ]
    def parse_start_line(self):
        method = self.METHOD_RE.match(self.source, pos=self.current_index)
        if method and self.at_space(method.end()):
            self.current_index = method.end()
            self.parse_request_line(method.group())
            self.type = HTTPType.Request
            return

        version = self.VERSION_RE.match(self.source, pos=self.current_index)
        if version:
            self.current_index = version.end()
            self.parse_status_line(version.group())
            self.type = HTTPType.Response
            return

        self.set_error_status()


    #  NOTE: request-line = method SP request-target SP HTTP-version
    def parse_request_line(self, method: str):
        self.method = method
        if not self.match_SP():
            self.set_error_status()
        
        path = self.PATH_RE.match(self.source, pos=self.current_index)
        if not path:
            self.set_error_status()
            return 

        self.path = path.group()

        self.current_index = path.end()

        if not self.match_SP():
            self.set_error_status()
            return

        version = self.VERSION_RE.match(self.source, pos=self.current_index)
        if not version:
            self.set_error_status()
            return
        
        self.http_version = version.group()

        self.current_index = version.end()


    #  NOTE: status-line = HTTP-version SP status-code SP [ reason-phrase ]
    def parse_status_line(self, version: str):
        self.http_version = version
        
        if not self.match_SP():
            self.set_error_status()
            return

        code = self.STATUS_CODE_RE.match(self.source, pos=self.current_index)
        if not code:
            self.set_error_status()
            return

        self.current_index = code.end()
        self.status = int(code.group())

        if not self.match_SP():
            self.set_error_status()
            return

        status_desc = self.STATUS_DESC_RE.match(self.source, pos=self.current_index)
        if not status_desc:
            self.set_error_status()
            return

        # we ignore status desc

        self.current_index = status_desc.end()
        
    def parse_headers(self):
        def at_CRLF(): return re.match(r'\r\n', self.source[self.current_index:]) != None 
        
        while(not at_CRLF()):
            header = self.HEADER_RE.match(self.source, self.current_index)
            if not header:
                self.set_error_status()
                return
            key = header.group('key').lower()
            value = header.group('value')
            
            self.current_index = header.end()

            self.headers[key] = value

            if not self.match_CRLF():
                self.set_error_status()
                return            


    def at_space(self, i: int | None):
        if i == None: i = self.current_index
        return self.source[i] == ' '
    
    def match(self, regexp: str) -> bool:
        m = re.match(regexp, self.source[self.current_index:])
        if m != None:
            self.current_index += len(m.group())
            return True
        return False
    
    def match_SP(self) -> bool:
        return self.match(' ')

    def match_CRLF(self) -> bool:
        return self.match(r'\r\n')

    def set_error_status(self):
        self.decoder_status = HTTPDecoderStatus.Error

    def curr_char(self):
        return self.source[self.current_index]

    def at_eof(self, i: int | None = None):
        if i == None: i = self.current_index
        return i >= len(self.source)

# def decode_http(source: bytes) -> HTTPRequest | HTTPResponse | None:
#     decoder = HTTPDecoder(source)
#     if decoder.decoder_status == HTTPDecoderStatus.Error: return None
    
#     version_match = list(filter(lambda v: v.value == decoder.http_version, [v for v in HTTPVersion]))
#     if len(version_match) != 1:
#         return None
    

#     if decoder.type == HTTPType.Request:
#         if decoder.method == None: raise RuntimeError()
#         if decoder.body == None: raise RuntimeError()
#         return HTTPRequest(version_match[0], decoder.method, decoder.headers, decoder.body)

#     if decoder.type == HTTPType.Response:
#         if decoder.status == None: raise RuntimeError()
#         if decoder.body == None: raise RuntimeError()
#         return HTTPResponse(version_match[0], decoder.status, decoder.headers, decoder.body)


