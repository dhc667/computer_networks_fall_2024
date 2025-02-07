import os
import json


HOST = '127.0.0.1'
PORT = '8000'

def make_request(method, path, headers=None, data=None):
    headerstr = "-h {}" if headers is None else f" -h {headers}"
    datastr = "" if data is None else f" -d {data}"
    response_string = os.popen(f"sh run.sh -m {method} -u http://localhost:8000{path} {headerstr} {datastr}").read()
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




