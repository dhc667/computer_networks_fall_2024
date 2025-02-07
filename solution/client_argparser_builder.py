from argparse import ArgumentParser

def get_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument("-m", type=str, help="HTTP method", required=True)
    parser.add_argument("-u", type=str, help="URL", required=True)
    parser.add_argument("-h", type=str, help="Headers", required=False)
    parser.add_argument("-b", type=str, help="Data", required=False)
    
    return parser
