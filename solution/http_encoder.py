import json


def encode_http_request(method: str, host: str, port: int, path: str, headers: str | None, data: str | None):
    header_lines = []

    if headers:
        headers = headers.replace("\\ ", "")
        try:
            header_dict = json.loads(headers)
            for key, value in header_dict.items():
                header_lines.append(f"{key}: {value}")
        except Exception as e:
            print(f"Invalid headers format: {e}")

    header_str = "\r\n".join(header_lines)
    content_length = f"Content-Length: {len(data)}" if data else ""

    # Create the HTTP request
    http_request = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\n"

    if header_str:
        http_request += f"{header_str}\r\n"
    if content_length:
        http_request += f"{content_length}\r\n"
    if data: 
        http_request += f"\r\n{data}\r\n"
    else:
        http_request += "\r\n"

    return http_request






