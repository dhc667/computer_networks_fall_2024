import json

valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "CONNECT", "TRACE"]

def encode(method, host, port, path, headers, data):
    header_lines = []

    # Validate the method
    if method not in valid_methods:
        raise ValueError(f"Invalid method: {method}")

    if headers:
        try:
            headers = json.loads(headers)
            for key, value in headers.items():
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






