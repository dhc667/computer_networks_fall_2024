class ClientCommandLineArguments:
    def __init__(self, method: str, url: str, headers: str | None, data: str | None):
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data

def parse_args(args: list[str]):
    
    method = None
    url = None
    headers = None
    data = None

    i = 0
    while i < len(args):
        if args[i] == "-m":
            i, method = parse_until_argument_name(args, i + 1)
        elif args[i] == "-u":
            i, url = parse_until_argument_name(args, i + 1)
        elif args[i] == "-h":
            i, headers = parse_until_argument_name(args, i + 1)
        elif args[i] == "-d":
            i, data = parse_until_argument_name(args, i + 1)
        else:
            raise SystemExit(f"Unknown argument {args[i]}")

    if method == None:
        raise SystemExit("Method not sent")

    if url == None:
        raise SystemExit("URL not sent")

    return ClientCommandLineArguments(method, url, headers, data)

def parse_until_argument_name(args: list[str], i: int):
    answ = ""

    for j in range(i, len(args)):
        if args[j][0] == "-":
            return j, answ.strip()
        answ += args[j] + " "

    return len(args), answ.strip()
