from client_argparser_builder import get_parser

def test_get_parser_1():
    parser = get_parser()

    assert parser is not None

def test_get_parser_2():
    parser = get_parser()

    args = parser.parse_args(["-m", "GET", "-u", "http://example.com"])

    assert args.m == "GET"
    assert args.u == "http://example.com"

def test_get_parser_3():
    parser = get_parser()

    args = parser.parse_args(["-m", "GET", "-u", "http://example.com", "-h", "{'key': 'value'}"])

    assert args.m == "GET"
    assert args.u == "http://example.com"
    assert args.h == "{'key': 'value'}"

def test_get_parser_4():
    parser = get_parser()

    args = parser.parse_args(["-m", "GET", "-u", "http://example.com", "-b", "data"])

    assert args.m == "GET"
    assert args.u == "http://example.com"
    assert args.b == "data"

# assert error if method not sent
def test_get_parser_5():
    parser = get_parser()

    try:
        args = parser.parse_args(["-u", "http://example.com"])
    except SystemExit:
        assert True
    else:
        assert False

# assert error if url not sent
def test_get_parser_6():
    parser = get_parser()

    try:
        args = parser.parse_args(["-m", "GET"])
    except SystemExit:
        assert True
    else:
        assert False


    
