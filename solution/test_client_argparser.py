from client_argparser_builder import parse_args


def test_get_parser_2():

    args = parse_args(["-m", "GET", "-u", "http://example.com"])

    assert args.method == "GET"
    assert args.url == "http://example.com"

def test_get_parser_3():

    args = parse_args(["-m", "GET", "-u", "http://example.com", "-h", "{'key': 'value'}"])

    assert args.method == "GET"
    assert args.url == "http://example.com"
    assert args.headers == "{'key': 'value'}"

def test_get_parser_4():

    args = parse_args(["-m", "GET", "-u", "http://example.com", "-d", "data"])

    assert args.method == "GET"
    assert args.url == "http://example.com"
    assert args.data == "data"

# assert error if method not sent
def test_get_parser_5():

    try:
        args = parse_args(["-u", "http://example.com"])
    except SystemExit:
        assert True
    else:
        assert False

# assert error if url not sent
def test_get_parser_6():
    try:
        args = parse_args(["-m", "GET"])
    except SystemExit:
        assert True
    else:
        assert False


    
