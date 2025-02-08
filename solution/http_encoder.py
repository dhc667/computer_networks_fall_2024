import json

def encode_http(start_line: str, headers: dict, body: str | None):
    header_lines = []
    for key, value in headers.items():
        header_lines.append(f"{key}: {value}")

    header_str = "\r\n".join(header_lines)
    content_length = f"Content-Length: {len(body)}" if body else ""

    # Create the HTTP response
    http_response = f"{start_line}\r\n"

    if header_str:
        http_response += f"{header_str}\r\n"
    if content_length:
        http_response += f"{content_length}\r\n"
    if body:
        http_response += f"\r\n{body}\r\n"
    else:
        http_response += "\r\n"

    return http_response

def encode_http_response(version: str, status_code: int, headers: dict, body: str | None):
    #  NOTE: We will provide no description for the status code, we must leave the space at the end however
    status_line = f"{version} {status_code} \r\n"
    return encode_http(status_line, headers, body)

def encode_http_request(version: str, method: str, host: str, port: int, path: str, headers: str | None, body: str | None):
    request_line = f"{method} {path} {version}\r\n"
    
    if headers is None:
        headers = "{}"

    headers = headers.replace("\\ ", " ")

    parsed_headers = json.loads(headers)
    parsed_headers["Host"] = f"{host}:{port}"
    return encode_http(request_line, parsed_headers, body)






