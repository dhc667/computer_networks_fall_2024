import socket
from urlparser import urlparser

method = ""
url = ""
headers = ""
data = ""

# Parse the URL
parsed = urlparser(url)
host = parsed.host
port = parsed.port
path = parsed.path

# Prepare the HTTP request
header_lines = []
if headers:
    try:
        import json
        headers = json.loads(headers)
        for key, value in headers.items():
            header_lines.append(f"{key}: {value}")
    except Exception as e:
        print(f"Invalid headers format: {e}")

header_str = "\\r\\n".join(header_lines)
content_length = f"Content-Length: {len(data)}" if data else ""

# Create the HTTP request
http_request = ""


# Establish a socket connection
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(http_request.encode())
        response = s.recv(4096)

    # Print the response
    print(response.decode())
except Exception as e:
    print(f"Socket error: {e}")


print(header_lines)