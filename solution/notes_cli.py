import cmd
import subprocess
import json

class NotesCLI(cmd.Cmd):
    intro = 'Welcome to the Notes CLI. Type help or ? to list commands.\n'
    prompt = '(notes) '

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

    def do_create(self, arg):
        'Create a new note: create <title> <content>'
        try:
            title, content = arg.split(' ', 1)
            url = f"http://{self.host}:{self.port}/notes"
            data = json.dumps({"title": title, "content": content})
            result = subprocess.run(["curl", "-X", "POST", "-d", data, url], capture_output=True, text=True)
            print(result.stdout)
        except ValueError:
            print("Usage: create <title> <content>")

    def do_fetch(self, arg):
        'Fetch a note by ID: fetch <note_id>'
        url = f"http://{self.host}:{self.port}/notes/{arg}"
        result = subprocess.run(["curl", "-X", "GET", url], capture_output=True, text=True)
        try:
            note = json.loads(result.stdout)
            print(json.dumps(note, indent=4))
        except json.JSONDecodeError:
            print(result.stdout)

    def do_delete(self, arg):
        'Delete a note by ID: delete <note_id>'
        url = f"http://{self.host}:{self.port}/notes/{arg}"
        result = subprocess.run(["curl", "-X", "DELETE", url], capture_output=True, text=True)
        print(result.stdout)

    def do_update(self, arg):
        'Update a note by ID: update <note_id> <title> <content>'
        try:
            note_id, title, content = arg.split(' ', 2)
            url = f"http://{self.host}:{self.port}/notes/{note_id}"
            data = json.dumps({"id": note_id, "title": title, "content": content})
            result = subprocess.run(["curl", "-X", "PUT", "-d", data, url], capture_output=True, text=True)
            print(result.stdout)
        except ValueError:
            print("Usage: update <note_id> <title> <content>")

    def do_list(self, arg):
        'List all notes: list'
        url = f"http://{self.host}:{self.port}/notes"
        result = subprocess.run(["curl", "-X", "GET", url], capture_output=True, text=True)
        try:
            notes = json.loads(result.stdout)
            print(json.dumps(notes, indent=4))
        except json.JSONDecodeError:
            print(result.stdout)

    def do_exit(self, arg):
        'Exit the CLI: exit'
        print('Goodbye!')
        return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Notes CLI")
    parser.add_argument("host", help="Server host")
    parser.add_argument("port", help="Server port")
    args = parser.parse_args()

    cli = NotesCLI(args.host, args.port)
    cli.cmdloop()

if __name__ == "__main__":
    main()
