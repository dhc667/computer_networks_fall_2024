import pytest
import subprocess


HOST = '127.0.0.1'
PORT = 8001

def make_curl_request(method: str, url: str, headers: dict[str, str], body: bytes, include_headers: bool = False):
    headers_str = " ".join([f"-H '{k}: {v}'" for k, v in headers.items()])
    body_str = f"-d '{body.decode('iso-8859-1')}'" if body else ""
    include_headers_str = "-i" if include_headers else ""
    return subprocess.run(f"curl -X {method} {url} {headers_str} {body_str} {include_headers_str}", shell=True, capture_output=True)

def send_file_through_curl(method: str, url: str, headers: dict[str, str], file_path: str):
    headers_str = " ".join([f"-H '{k}: {v}'" for k, v in headers.items()])
    return subprocess.run(f"curl -X {method} {url} {headers_str} --data-binary @{file_path}", shell=True, capture_output=True)

def test_get_root():
    response = make_curl_request("GET", f"http://{HOST}:{PORT}/", {}, b"")
    assert response.returncode == 0
    assert response.stdout == b"Welcome to the server!"

def test_sum():
    response = make_curl_request("GET", f"http://{HOST}:{PORT}/3/plus/4", {"Content-Type": "application/json"}, b"")
    assert response.returncode == 0
    assert response.stdout == b"7"

def test_fibonacci():
    fib_dp = [1, 1]
    for i in range(2, 11):
        fib_dp.append(fib_dp[i - 1] + fib_dp[i - 2])

    response = make_curl_request("GET", f"http://{HOST}:{PORT}/fib/10", {"Content-Type": "application/json"}, b"")
    assert response.returncode == 0
    assert response.stdout == str(fib_dp[10]).encode('iso-8859-1')

def test_not_found():
    response = make_curl_request("GET", f"http://{HOST}:{PORT}/not_found", {}, b"", True)
    assert response.returncode == 0
    assert response.stdout == b"HTTP/1.1 404 \r\n\r\n"


def test_post_png():
    response = send_file_through_curl("POST", f"http://{HOST}:{PORT}/receive_png", {"Content-Type": "image/png"}, "our_tests/to_send/png1.png")
    assert response.stdout == b"File received"

    with open("./our_tests/to_send/png1.png", "rb") as f:
        expected = f.read()

    with open("./our_tests/received/png1.png", "rb") as f:
        received = f.read()

    assert expected == received
