from client.urlparser import urlparser

def test_1():
    up = urlparser("http://www.google.com")
    assert up.host == "www.google.com"
    assert up.port == 80
    assert up.path == "/"

def test_2():
    up = urlparser("http://www.google.com:8080")
    assert up.host == "www.google.com"
    assert up.port == 8080
    assert up.path == "/"

def test_3():
    up = urlparser("http://www.google.com:8080/")
    assert up.host == "www.google.com"
    assert up.port == 8080
    assert up.path == "/"

def test_4():
    up = urlparser("http://www.google.com:8080/search")
    assert up.host == "www.google.com"
    assert up.port == 8080
    assert up.path == "/search"
