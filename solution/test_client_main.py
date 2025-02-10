import os
import json

HOST = '127.0.0.1'
PORT = '8000'

def make_request(method, path, host='localhost', port=PORT, headers=None, data=None):
    headerstr = "-h {}" if headers is None else f" -h {headers}"
    datastr = "" if data is None else f" -d {data}"
    response_string = os.popen(f"python3 solution/client_main.py -m {method} -u http://{host}{':' + port if port else ''}{path} {headerstr} {datastr}").read()
    print(response_string)   
    return json.loads(response_string) # JSON con campos status, body y headers

def test_get_root():
    response = make_request("GET", "/")
    assert response['status'] == 200

def test_post_root():
    response = make_request("POST", "/", data="Hello, server!")
    assert response['status'] == 501


def test_head_root():
    response = make_request("HEAD", "/")
    assert response['status'] == 200

def test_malformed_json_body():
    response = make_request(
        "GET",
        "/secure",
        headers='{\\"Authorization\\":\\ \\"Bearer\\ 12345\\",\\ \\"Content-Type\\":\\ \\"application/json\\"}',
        data='{"key":}'
    )

    assert response['status'] == 404

def test_unimplemented_method():
    response = make_request("PATCH", "/")
    assert response['status'] == 501

def get_cubadebate():
    response = make_request("GET", "/", host="www.cubadebate.cu", port="")
    assert response['status'] == 200
