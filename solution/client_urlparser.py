import re

class urlparser:
    def __init__(self, url):
        pattern = re.compile(r'^http://(?P<host>[^:/]+)(?::(?P<port>\d+))?(?P<path>/.*)?$')
        match = pattern.match(url)
        if match:
            self.host = match.group('host')
            self.port = int(match.group('port')) if match.group('port') else 80
            self.path = match.group('path') if match.group('path') else '/'
        else:
            raise ValueError('Invalid URL')

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print('Usage: python urlparser.py <url>')
        sys.exit(1)

    url = sys.argv[1]

    try:
        up = urlparser(url)
        print('Host: %s' % up.host)
        print('Port: %d' % up.port)
        print('Path: %s' % up.path)
    except ValueError as e:
        print(e)
        sys.exit(1)
