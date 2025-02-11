import cmd
import subprocess
import json
import os

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
            process_args = ["curl", "-X", "POST", "-d", data, url]
            print(' '.join(process_args))
            result = subprocess.run(process_args, capture_output=True, text=True)
            print(result.stdout)
        except ValueError:
            print("Usage: create <title> <content>")

    def do_fetch_head(self, arg):
        'Get the headers of the response to getting a note by ID: fetch_head <note_id>'
        if not arg:
            print("Usage: fetch_head <note_id>")
            return
        url = f"http://{self.host}:{self.port}/notes/{arg}"
        process_args = ["curl", "--head", url]
        print(' '.join(process_args))
        result = subprocess.run(process_args, capture_output=True, text=True)
        print(result.stdout.replace('\r', ''))

    def do_fetch(self, arg):
        'Fetch a note by ID: fetch <note_id>'
        if not arg:
            print("Usage: fetch <note_id>")
            return
        url = f"http://{self.host}:{self.port}/notes/{arg}"
        process_args = ["curl", "-X", "GET", url]
        print(' '.join(process_args))
        result = subprocess.run(process_args, capture_output=True, text=True)
        try:
            note = json.loads(result.stdout)
            print(json.dumps(note, indent=4))
        except json.JSONDecodeError:
            print(result.stdout)

    def do_delete(self, arg):
        'Delete a note by ID: delete <note_id>'
        url = f"http://{self.host}:{self.port}/notes/{arg}"
        process_args = ["curl", "-X", "DELETE", url]
        print(' '.join(process_args))
        result = subprocess.run(process_args, capture_output=True, text=True)
        print(result.stdout)

    def do_update(self, arg):
        'Update a note by ID: update <note_id> <title> <content>'
        try:
            note_id, title, content = arg.split(' ', 2)
            url = f"http://{self.host}:{self.port}/notes/{note_id}"
            data = json.dumps({"id": note_id, "title": title, "content": content})
            process_args = ["curl", "-X", "PUT", "-d", data, url]
            print(' '.join(process_args))
            result = subprocess.run(process_args, capture_output=True, text=True)
            print(result.stdout)
        except ValueError:
            print("Usage: update <note_id> <title> <content>")

    def do_list_head(self, arg):
        'Get the headers of the note data response: list_head'
        url = f"http://{self.host}:{self.port}/notes"
        process_args = ["curl", "--head", url]
        print(' '.join(process_args))
        result = subprocess.run(process_args, capture_output=True, text=True)
        print(result.stdout.replace('\r', ''))

    def do_list(self, arg):
        'List all notes: list'
        url = f"http://{self.host}:{self.port}/notes"
        process_args = ["curl", "-X", "GET", url]
        print(' '.join(process_args))
        result = subprocess.run(process_args, capture_output=True, text=True)
        try:
            notes = json.loads(result.stdout)
            print(json.dumps(notes, indent=4))
        except json.JSONDecodeError:
            print(result.stdout)

    def do_post_picture(self, arg):
        'Post a picture: post_picture <note_id> <path>'
        try:
            note_id, path = arg.split(' ', 1)
            url = f"http://{self.host}:{self.port}/notes/{note_id}/pictures"
            process_args = ["curl", "-X", "POST", url, "--data-binary", f"@{path}"]
            print(' '.join(process_args))
            result = subprocess.run(process_args, capture_output=True, text=True)
            print(result.stdout)
        except ValueError:
            print("Usage: post_picture <note_id> <path>")

    def do_note_picture_ids_head(self, arg):
        'Get the headers of getting note picture ids response: get_note_picture_ids_head <note_id>'
        if not arg:
            print("Usage: note_picture_ids_head <note_id>")
            return

        url = f"http://{self.host}:{self.port}/notes/{arg}/pictures"
        process_args = ["curl", "--head", url]
        print(' '.join(process_args))
        result = subprocess.run(process_args, capture_output=True, text=True)
        print(result.stdout.replace('\r', ''))

    def do_note_picture_ids(self, arg):
        'Get the IDs of the pictures of a note: note_picture_ids <note_id>'
        if not arg:
            print("Usage: note_picture_ids <note_id>")
            return
        url = f"http://{self.host}:{self.port}/notes/{arg}/pictures"
        process_args = ["curl", "-X", "GET", url]
        print(' '.join(process_args))
        result = subprocess.run(process_args, capture_output=True, text=True)
        try:
            pictures = json.loads(result.stdout)
            print(json.dumps(pictures, indent=4))
        except json.JSONDecodeError:
            print(result.stdout)

    def do_get_picture(self, arg):
        'Get a picture: get_picture <picture_id> <target_file_name.png>'
        try:
            picture_id, target_file = arg.split(' ', 1)
            url = f"http://{self.host}:{self.port}/pictures/{picture_id}"
            process_args = ["curl", "-X", "GET", url, "--output", target_file]
            print(' '.join(process_args))
            result = subprocess.run(process_args, capture_output=True, text=True)
            print(result.stdout)
        except ValueError:
            print("Usage: get_picture <picture_id> <target_file_name.png>")

    def do_get_picture_head(self, arg):
        'Get the headers of getting a picture response: get_picture_head <picture_id>'
        try:
            if not arg:
                raise ValueError
            picture_id = arg
            url = f"http://{self.host}:{self.port}/pictures/{picture_id}"
            process_args = ["curl", "--head", url]
            print(' '.join(process_args))
            result = subprocess.run(process_args, capture_output=True, text=True)
            print(result.stdout.replace('\r', ''))
        except ValueError:
            print("Usage: get_picture_head <picture_id>")

    def do_delete_picture(self, arg):
        'Delete a picture: delete_picture <picture_id>'
        if not arg:
            print("Usage: delete_picture <picture_id>")
        url = f"http://{self.host}:{self.port}/pictures/{arg}"
        process_args = ["curl", "-X", "DELETE", url]
        print(' '.join(process_args))
        result = subprocess.run(process_args, capture_output=True, text=True)
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
