from __future__ import annotations
import re
from enum import Enum
from typing import Counter

# NOTE: Re example:
# pattern = re.compile(r'^http://(?P<host>[^:/]+)(?::(?P<port>\d+))?(?P<path>/.*)?$')

class HTTPDecoderStatus(Enum):
    Error = 'Error'
    Finished = 'Finished'
    ParsingStartLine = 'ParsingStartLine'
    ParsingHeaders = 'ParsingHeaders'

class ParseletStatus(Enum):
    Unknown = 'Unknown'
    Accepted = 'Accepted'
    Error = 'Error'

class ParseletResponse:
    def __init__(self, status: ParseletStatus, content: str | None, end: int | None) -> None:
        self.status = status
        self.content = content
        self.end = end

    @staticmethod
    def make_unknown():
        return ParseletResponse(ParseletStatus.Unknown, None, None)

    @staticmethod
    def make_error():
        return ParseletResponse(ParseletStatus.Error, None, None)

    def is_error(self):
        return self.status == ParseletStatus.Error

    def is_unknown(self):
        return self.status == ParseletStatus.Unknown
    

    def is_accepted(self):
        return self.status == ParseletStatus.Accepted

class HTTPType(Enum):
    Response = 'Response'
    Request = 'Request'

class HTTPDecoder():

    def __init__(self, source: bytes) -> None:
        self.source = source.decode('iso-8859-1')
        self.current_index = 0
        self.decoder_status = HTTPDecoderStatus.ParsingStartLine

        self.http_version: str | None = None
        self.method: str | None = None
        self.status: int | None = None
        self.headers: dict[str, str] = {}

        self.path: str | None = None

        self.type: HTTPType | None = None
        self.parse()
    
    #  NOTE: request-line = method SP request-target SP HTTP-version
    #        status-line = HTTP-version SP status-code SP [ reason-phrase ]

    @property
    def remainder(self):
        return self.source[self.current_index:].encode('iso-8859-1')

    def parse(self) -> None:
        parsing_start_line = lambda: self.decoder_status == HTTPDecoderStatus.ParsingStartLine
        parsing_headers = lambda: self.decoder_status == HTTPDecoderStatus.ParsingHeaders

        if parsing_start_line():
            start_line_parselet_response = self.parse_start_line(self.current_index)
            if start_line_parselet_response.is_error():
                self.set_error_status()
                return
            
            if start_line_parselet_response.is_unknown():
                return

            self.decoder_status = HTTPDecoderStatus.ParsingHeaders

        if parsing_headers():
            header_parselet_response = self.parse_headers_no_content(self.current_index)

            if header_parselet_response.is_error():
                self.set_error_status()
                return

            if header_parselet_response.is_unknown():
                return
            
            self.decoder_status = HTTPDecoderStatus.Finished
    
    def parse_start_line(self, i: int) -> ParseletResponse:
        version_parselet_response = self.parse_version(i)
        if version_parselet_response.is_accepted():
            assert version_parselet_response.end != None
            i = version_parselet_response.end

            assert version_parselet_response.content != None
        
            self.type = HTTPType.Response

            response_line_parselet_response = self.parse_response_line_no_content(i, version_parselet_response.content)

            if response_line_parselet_response.is_accepted():
                assert response_line_parselet_response.end != None
                self.current_index = response_line_parselet_response.end

            return response_line_parselet_response

        if version_parselet_response.is_unknown():
            return version_parselet_response

        method_parselet_response = self.parse_method(i)
        if method_parselet_response.is_accepted():
            assert method_parselet_response.end != None
            i = method_parselet_response.end
            assert method_parselet_response.content != None

            self.type = HTTPType.Request

            request_line_parselet_response = self.parse_request_line_no_content(i, method_parselet_response.content)
    
            if request_line_parselet_response.is_accepted():
                assert request_line_parselet_response.end != None
                self.current_index = request_line_parselet_response.end

            return request_line_parselet_response

        return method_parselet_response

    def parse_request_line_no_content(self, i: int, method: str) -> ParseletResponse:
        if self.at_eof(i):
            return ParseletResponse.make_unknown()

        sp_match = self.match_sp(i)
        if not sp_match:
            return ParseletResponse.make_error()

        _, i = sp_match

        path_parselet_response = self.parse_path(i)
        if not path_parselet_response.is_accepted():
            return path_parselet_response

        assert path_parselet_response.end != None
        i = path_parselet_response.end

        if self.at_eof(i):
            return ParseletResponse.make_unknown()

        sp_match = self.match_sp(i)
        if not sp_match:
            return ParseletResponse.make_error()

        _, i = sp_match

        version_parselet_response = self.parse_version(i)
        if not version_parselet_response.is_accepted():
            return version_parselet_response

        assert version_parselet_response.end != None
        i = version_parselet_response.end

        crlf_parselet_response = self.parse_CRLF(i)
        if not crlf_parselet_response.is_accepted():
            return crlf_parselet_response

        assert crlf_parselet_response.end != None
        i = crlf_parselet_response.end

        version = version_parselet_response.content
        assert version != None

        path = path_parselet_response.content
        assert path != None

        self.method = method
        self.path = path
        self.http_version = version
        self.current_index = i

        return ParseletResponse(ParseletStatus.Accepted, None, i)

    def parse_response_line_no_content(self, i: int, version: str) -> ParseletResponse:
        if self.at_eof(i):
            return ParseletResponse.make_unknown()

        sp_match = self.match_sp(i)
        if not sp_match:
            return ParseletResponse.make_error()

        _, i = sp_match

        status_code_parselet_response = self.parse_status_code(i)
        if not status_code_parselet_response.is_accepted():
            return status_code_parselet_response

        assert status_code_parselet_response.end != None
        i = status_code_parselet_response.end

        if self.at_eof(i):
            return ParseletResponse.make_unknown()

        sp_match = self.match_sp(i)
        if not sp_match:
            return ParseletResponse.make_error()

        _, i = sp_match

        reason_phrase_parselet_response = self.parse_reason_phrase(i)
        if not reason_phrase_parselet_response.is_accepted():
            return reason_phrase_parselet_response

        assert reason_phrase_parselet_response.end != None
        i = reason_phrase_parselet_response.end

        crlf_parselet_response = self.parse_CRLF(i)
        if not crlf_parselet_response.is_accepted():
            return crlf_parselet_response

        assert crlf_parselet_response.end != None
        i = crlf_parselet_response.end

        reason_phrase = reason_phrase_parselet_response.content
        assert reason_phrase != None

        status = status_code_parselet_response.content
        assert status != None

        self.http_version = version
        self.status = int(status) 
        self.current_index = i

        return ParseletResponse(ParseletStatus.Accepted, None, i)

    def parse_headers_no_content(self, i: int) -> ParseletResponse:
        while(True):
            crlf_parselet_response = self.parse_CRLF(i)

            if crlf_parselet_response.is_accepted():
                assert crlf_parselet_response.end != None
                i = crlf_parselet_response.end
                self.current_index = i
                return ParseletResponse(ParseletStatus.Accepted, None, i)

            if crlf_parselet_response.is_unknown():
                return crlf_parselet_response

            if self.at_eof(i):
                return ParseletResponse.make_unknown()

            header_pair_parselet_response = self.parse_header_pair_no_content(i)
            if not header_pair_parselet_response.is_accepted():
                return header_pair_parselet_response
            
            assert header_pair_parselet_response.end != None
            i = header_pair_parselet_response.end

            self.current_index = i



    def parse_header_pair_no_content(self, i: int) -> ParseletResponse:
        def jump_OWS(i: int):
            while (not self.at_eof(i)):
                if self.match(r'[\t ]', i):
                    i += 1
                else: break

            return i

        key_parselet_response = self.parse_header_key(i)
        if not key_parselet_response.is_accepted():
            return key_parselet_response

        assert key_parselet_response.end != None
        i = key_parselet_response.end
        
        if self.at_eof(i):
            return ParseletResponse.make_unknown()

        colon_match = self.match(r':', i)
        if not colon_match:
            return ParseletResponse.make_error()
        i += 1

        i = jump_OWS(i)

        value_parselet_response = self.parse_header_value(i)
        if not value_parselet_response.is_accepted():
            return value_parselet_response
        
        assert value_parselet_response.end != None
        i = value_parselet_response.end

        i = jump_OWS(i)

        crlf_parselet_response = self.parse_CRLF(i)
        if not crlf_parselet_response.is_accepted():
            return crlf_parselet_response

        assert crlf_parselet_response.end != None
        i = crlf_parselet_response.end
        
        key = key_parselet_response.content
        value = value_parselet_response.content

        assert key != None
        assert value != None

        self.headers[key.lower()] = value

        return ParseletResponse(ParseletStatus.Accepted, f"{key}: {value}\r\n", i)

    def parse_CRLF(self, i: int) -> ParseletResponse:
        cr = self.match(r'\r', i)
        if not cr:
            return ParseletResponse.make_error()

        _, i = cr

        if self.at_eof(i):
            return ParseletResponse.make_unknown()

        lf = self.match(r'\n', i)
        if not lf:
            return ParseletResponse.make_error()

        _, i = lf

        return ParseletResponse(ParseletStatus.Accepted, '\r\n', i)

    def parse_header_value(self, i: int) -> ParseletResponse:
        value = self.parse_regexp_chars(r'[^\r\n]', i)
        if value.is_accepted():
            assert value.content != None
            value.content = value.content.strip()
            if value.content == '': return ParseletResponse.make_error()
            return value

        return value

    def parse_header_key(self, i: int) -> ParseletResponse:
        return self.parse_regexp_chars(r'[^\s:]', i)

    def parse_reason_phrase(self, i: int) -> ParseletResponse:
        return self.parse_regexp_chars(r'[^\r\n]', i)

    def parse_path(self, i: int) -> ParseletResponse:
        return self.parse_regexp_chars(r'[^\s]', i)

    def parse_method(self, i: int) -> ParseletResponse:
        return self.parse_regexp_chars(r'[A-Za-z]', i)
    
    def parse_regexp_chars(self, valid_char: str, i: int) -> ParseletResponse:
        so_far = ''

        while(True):
            if self.at_eof(i):
                return ParseletResponse.make_unknown()

            match = self.match(valid_char, i)
            if match:
                char, i = match
                so_far += char
            else:
                return ParseletResponse(ParseletStatus.Accepted, so_far, i)
    
    def parse_version(self, i : int) -> ParseletResponse:
        so_far = ''
        http_parselet_response = self.parse_HTTP(i)
        if not http_parselet_response.is_accepted():
            return http_parselet_response

        assert http_parselet_response.end != None
        i = http_parselet_response.end

        assert http_parselet_response.content != None
        so_far = http_parselet_response.content

        if self.at_eof(i): return ParseletResponse.make_unknown()
        
        slash = self.match(r'/', i)
        if not slash:
            return ParseletResponse.make_error()
        
        so_far += '/'
        i += 1

        version_number_parselet_response = self.parse_version_number(i)
        if not version_number_parselet_response.is_accepted():
            return version_number_parselet_response

        version = version_number_parselet_response.content
        assert version != None
        so_far += version

        assert version_number_parselet_response.end != None
        i = version_number_parselet_response.end


        return ParseletResponse(ParseletStatus.Accepted, so_far, i)

    def parse_HTTP(self, i: int) -> ParseletResponse:
        expected = 'HTTP'
        k = 0
        while(k < len(expected)):
            if self.at_eof(i):
                return ParseletResponse.make_unknown()
            
            match = self.match(expected[k], i)
            if match:
                _, i = match
                k += 1
                continue
            return ParseletResponse.make_error()
        
        return ParseletResponse(ParseletStatus.Accepted, expected, i)

    def parse_version_number(self, i: int) -> ParseletResponse:
        if self.at_eof(i): return ParseletResponse.make_unknown()

        major_match = self.match('1', i)
        if major_match:
            _, i = major_match
        else:
            return ParseletResponse.make_error()

        if self.at_eof(i): return ParseletResponse.make_unknown()
        dot_match = self.match(r'\.', i)
        if dot_match:
            _, i = dot_match
        else: return ParseletResponse.make_error()

        if self.at_eof(i): return ParseletResponse.make_unknown()
        minor_match = self.match(r'[10]', i)
        if minor_match:
            minor, i = minor_match
        else: return ParseletResponse.make_error()

        return ParseletResponse(ParseletStatus.Accepted, f"1.{minor}", i)

    def parse_status_code(self, i: int) -> ParseletResponse:
        so_far = ''

        for _ in range(3):
            if self.at_eof(i):
                return ParseletResponse.make_unknown()

            match = self.match(r'\d', i)
            if match:
                char, i = match
                so_far += char
            else:
                return ParseletResponse.make_error()

        return ParseletResponse(ParseletStatus.Accepted, so_far, i)

    def add_chunk(self, chunk: bytes):
        self.source += chunk.decode('iso-8859-1')
        self.parse()
    
    def advance(self):
        if self.current_index < len(self.source): self.current_index += 1

    def match(self, regexp: str, i: int) -> tuple[str, int] | None:
        m = re.match(regexp, self.source[i:])
        if m:
            return (m.group(), i + len(m.group()))
        return None

    def match_alpha(self, i: int) -> tuple[str, int] | None:
        return self.match(r'[A-Za-z]', i)

    def match_sp(self, i: int) -> tuple[str, int] | None:
        return self.match(r' ', i)

    def at_space(self, i: int | None):
        if i == None: i = self.current_index
        return self.source[i] == ' '
    
    def set_error_status(self):
        self.decoder_status = HTTPDecoderStatus.Error

    def curr_char(self):
        return self.source[self.current_index]

    def at_eof(self, i: int | None = None):
        if i == None: i = self.current_index
        return i >= len(self.source)

