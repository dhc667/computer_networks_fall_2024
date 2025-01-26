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