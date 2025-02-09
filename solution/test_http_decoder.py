from http_request import StandardHTTPMethod
from http_decoder import HTTPDecoder, HTTPDecoderStatus
import random


def test_1():
    source = b'GET / HTTP/1.1\r\nhost: localhost:8080\r\n\r\n'
    decoder = HTTPDecoder(source)
    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == StandardHTTPMethod.GET.value
    assert decoder.path == '/'
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {'host': 'localhost:8080'}
    assert decoder.remainder == b''

def test_2():
    source = b'GET / HTTP/1.1\r\nhost: localhost:8080\r\ncontent-length: 5\r\n\r\nHello'
    decoder = HTTPDecoder(source)
    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == StandardHTTPMethod.GET.value
    assert decoder.path == '/'
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {'host': 'localhost:8080', 'content-length': '5'}
    assert decoder.remainder == b'Hello'

# now for a few error cases
def test_3():
    source = b'GET / HTTP/1.1\r\nhost: localhost:8080\r\ncontent-length: 5\r\n'
    decoder = HTTPDecoder(source)
    assert (decoder.decoder_status != HTTPDecoderStatus.Finished)

def test_4():
    source = b'GET /testing/a/long/path HTTP/1.1\r\nhost: localhost:8080\r\ncontent-length: 5\r\n\r\nHello'
    decoder = HTTPDecoder(source)
    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == StandardHTTPMethod.GET.value
    assert decoder.path == '/testing/a/long/path'
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {'host': 'localhost:8080', 'content-length': '5'}
    assert decoder.remainder == b'Hello'

def test_handles_several_headers():
    source = b'GET / HTTP/1.1\r\nhost: localhost:8080\r\ncontent-length: 5\r\ncontent-type: text/plain\r\n\r\nHello'
    decoder = HTTPDecoder(source)
    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == StandardHTTPMethod.GET.value
    assert decoder.path == '/'
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {'host': 'localhost:8080', 'content-length': '5', 'content-type': 'text/plain'}


def test_does_not_accept_invalid_version():
    source = b'GET / HTTP/1.4\r\nhost: localhost:8080\r\ncontent-length: 5\r\ncontent-type: text/plain\r\n\r\nHello'
    decoder = HTTPDecoder(source)
    assert (decoder.decoder_status == HTTPDecoderStatus.Error)

def test_does_not_accept_invalid_header():
    source = b'GET / HTTP/1.1\r\nhost: localhost:8080\r\ncontent-length: 5\r\ncontent-type: text/plain\r\nContent:\r\n\r\nHello'
    decoder = HTTPDecoder(source)
    assert (decoder.decoder_status == HTTPDecoderStatus.Error)


def test_header_names_case_insensitive():
    source = b'GET / HTTP/1.1\r\nhost: localhost:8080\r\ncontent-length: 5\r\ncontent-type: text/plain\r\n\r\nHello'
    decoder = HTTPDecoder(source)
    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == StandardHTTPMethod.GET.value
    assert decoder.path == '/'
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {'host': 'localhost:8080', 'content-length': '5', 'content-type': 'text/plain'}

def test_throws_error_on_invalid_path():
    source = b'GET /invalid /path HTTP/1.1\r\nhost: localhost:8080\r\ncontent-length: 5\r\ncontent-type: text/plain\r\n\r\nHello'
    decoder = HTTPDecoder(source)
    assert (decoder.decoder_status == HTTPDecoderStatus.Error)


def test_parses_response_correctly():
    source = b'HTTP/1.1 200 OK\r\ncontent-length: 5\r\ncontent-type: text/plain\r\n\r\nHello'
    decoder = HTTPDecoder(source)
    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == None
    assert decoder.path == None
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {'content-length': '5', 'content-type': 'text/plain'}
    assert decoder.remainder == b'Hello'

def test_parses_response_correctly_with_no_body():
    source = b'HTTP/1.1 200 OK\r\ncontent-length: 0\r\ncontent-type: text/plain\r\n\r\n'
    decoder = HTTPDecoder(source)
    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == None
    assert decoder.path == None
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {'content-length': '0', 'content-type': 'text/plain'}
    assert decoder.remainder == b''

def test_parses_response_correctly_with_no_headers():
    source = b'HTTP/1.1 200 OK\r\n\r\n'
    decoder = HTTPDecoder(source)
    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == None
    assert decoder.path == None
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {}
    assert decoder.remainder == b''

def test_parses_different_codes_correctly():
    source = b'HTTP/1.1 404 Not Found\r\ncontent-length: 0\r\ncontent-type: text/plain\r\n\r\n'
    decoder = HTTPDecoder(source)
    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == None
    assert decoder.path == None
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {'content-length': '0', 'content-type': 'text/plain'}
    assert decoder.remainder == b''

def chunk_data(data: bytes, min_chunk_size: int, max_chunk_size: int) -> list[bytes]:
    chunks = []

    i = 0
    adv = 0
    while(adv < len(data)):
        i = random.randint(min_chunk_size, max_chunk_size)
        chunks.append(data[adv:adv+i])
        adv += i

    return chunks

def test_parses_chunked_data():
    source = b'HTTP/1.1 200 OK\r\ncontent-length: 0\r\ncontent-type: text/plain\r\ntransfer-encoding: chunked\r\n\r\nHello There'

    decoder = HTTPDecoder(b"")

    chunks = chunk_data(source, 1, 5)

    for chunk in chunks:
        decoder.add_chunk(chunk)

    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == None
    assert decoder.path == None
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {'content-length': '0', 'content-type': 'text/plain', 'transfer-encoding': 'chunked'}
    assert decoder.remainder == b'Hello There'

def test_parses_chunked_data_with_no_body():
    source = b'HTTP/1.1 200 OK\r\ncontent-length: 0\r\ncontent-type: text/plain\r\ntransfer-encoding: chunked\r\n\r\n'

    decoder = HTTPDecoder(b"")

    chunks = chunk_data(source, 1, 5)

    for chunk in chunks:
        decoder.add_chunk(chunk)

    assert decoder.decoder_status == HTTPDecoderStatus.Finished
    assert decoder.method == None
    assert decoder.path == None
    assert decoder.http_version == 'HTTP/1.1'
    assert decoder.headers == {'content-length': '0', 'content-type': 'text/plain', 'transfer-encoding': 'chunked'}
    assert decoder.remainder == b''

def test_finds_error_early():
    source = b'HTTP/1.3 200 OK\r\ncontent-length: 0\r\ncontent-type: text/plain\r\ntransfer-encoding: chunked\r\n\r\nHello There'

    decoder = HTTPDecoder(b"")

    chunk = source[:10]

    decoder.add_chunk(chunk)

    assert decoder.decoder_status == HTTPDecoderStatus.Error

def test_finds_missing_header_colon_early():
    source = b'HTTP/1.1 200 OK\r\ncontent-length 0\r\ncontent-type: text/plain\r\ntransfer-encoding: chunked\r\n\r\nHello There'

    decoder = HTTPDecoder(b"")

    decoder.add_chunk(source[:b'HTTP/1.1 200 OK\r\ncontent-length 0\r\n'.__len__()])

    assert decoder.decoder_status == HTTPDecoderStatus.Error
