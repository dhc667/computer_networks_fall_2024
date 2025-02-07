import os
import json


HOST = '127.0.0.1'
PORT = '8000'

def make_request(method, path, headers=None, data=None):
    headerstr = "-h {}" if headers is None else f" -h {headers}"
    datastr = "" if data is None else f" -d {data}"
    response_string = os.popen(f"python3 client_main.py -m {method} -u http://localhost:8080{path} {headerstr} {datastr}").read()
    return json.loads(response_string) # JSON con campos status, body y headers

# def test_get_root():
#     response = make_request("GET", "/")
#     assert response['status'] == 200


