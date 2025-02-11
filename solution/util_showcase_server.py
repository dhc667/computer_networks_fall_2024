from server_main import Server
from server_main import Endpoint
from http_response import HTTPResponse
from http_request import HTTPRequest
from sqlite3 import connect
import json

import sys

if sys.argv.__len__() != 3:
    print("usage: python3 <script_path> <HOST> <PORT>")
    exit(1)

HOST = sys.argv[1]
PORT = int(sys.argv[2])

server = Server(HOST, PORT)

with connect('test.db') as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS Notes (n INTEGER PRIMARY KEY, Title TEXT, Content TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS NotePicture (n INTEGER PRIMARY KEY, NoteId INTEGER, Picture BLOB)')
    conn.execute('CREATE TABLE IF NOT EXISTS CreatedFlag(n INTEGER PRIMARY KEY)')
    conn.commit()

# add some data to the table if created flag is not set
with connect('test.db') as conn:
    cursor = conn.execute('SELECT * FROM CreatedFlag')
    if cursor.fetchone() is None:
        conn.execute('INSERT INTO Notes (Title, Content) VALUES ("First note", "This is the first note")')
        conn.execute('INSERT INTO Notes (Title, Content) VALUES ("Second note", "This is the second note")')
        conn.execute('INSERT INTO Notes (Title, Content) VALUES ("Third note", "This is the third note")')
        conn.execute('INSERT INTO CreatedFlag (n) VALUES (1)')
        conn.commit()
    conn.commit()

def handle_POST_note(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    # the body is application/json, but is in binary format, we need to get it and parse it
    body = json.loads(req.body.decode('iso-8859-1'))
    title = body['title']
    content = body['content']

    with connect('test.db') as conn:
        cursor = conn.execute('INSERT INTO Notes (Title, Content) VALUES (?, ?)', (title, content))
        conn.commit()

    return HTTPResponse(200, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')

def handle_GET_notes(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    with connect('test.db') as conn:
        cursor = conn.execute('SELECT * FROM Notes')
        notes = cursor.fetchall()

    notes_dict = [{'id': note[0], 'title': note[1], 'content': note[2]} for note in notes]
    notes_json = json.dumps(notes_dict).encode('iso-8859-1')

    return HTTPResponse(200, {'Content-Type': 'application/json', 'Content-length': str(len(notes_json))}, notes_json)

def handle_HEAD_notes(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    original_response = handle_GET_notes(args, req)

    return HTTPResponse(original_response.status, original_response.headers, b'')

def handle_DELETE_note(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    note_id = args['id']

    with connect('test.db') as conn:
        if conn.execute('SELECT * FROM Notes WHERE n = ?', (note_id,)).fetchone() is None:
            return HTTPResponse(404, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')

        conn.execute('DELETE FROM Notes WHERE n = ?', (note_id,))
        conn.commit()

    return HTTPResponse(200, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')

def handle_PUT_note(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    note_id = args['id']

    body = json.loads(req.body.decode('iso-8859-1'))
    title = body['title']
    content = body['content']
    body_id = body['id']

    if note_id != body_id:
        return HTTPResponse(400, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')

    with connect('test.db') as conn:
        conn.execute('UPDATE Notes SET Title = ?, Content = ? WHERE n = ?', (title, content, note_id))
        conn.commit()

    return HTTPResponse(200, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')


def handle_GET_note_by_id(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    note_id = args['id']

    with connect('test.db') as conn:
        note = conn.execute('SELECT * FROM Notes WHERE n = ?', (note_id,)).fetchone()

    if note is None:
        return HTTPResponse(404, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')

    note_dict = {'id': note[0], 'title': note[1], 'content': note[2]}
    note_json = json.dumps(note_dict).encode('iso-8859-1')

    return HTTPResponse(200, {'Content-Type': 'application/json', 'Content-length': str(len(note_json))}, note_json)

def handle_HEAD_note_by_id(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    original_response = handle_GET_note_by_id(args, req)

    return HTTPResponse(original_response.status, original_response.headers, b'')

def handle_POST_picture(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    note_id = args['id']
    picture = req.body

    with connect('test.db') as conn:
        conn.execute('INSERT INTO NotePicture (NoteID, Picture) VALUES (?, ?)', (note_id, picture))
        conn.commit()

    return HTTPResponse(200, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')

def handle_GET_note_picture_ids(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    note_id = args['id']
    rows = []

    with connect('test.db') as conn:
        if conn.execute('SELECT * FROM Notes WHERE n = ?', (note_id,)).fetchone() is None:
            return HTTPResponse(404, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')

        cursor = conn.execute('SELECT n FROM NotePicture WHERE NoteId = ?', (note_id,))
        rows = cursor.fetchall()

    pictures = [row[0] for row in rows]

    data = json.dumps(pictures).encode('iso-8859-1')

    return HTTPResponse(200, {'Content-Type': 'application/json', 'Content-length': str(len(data))}, data)

def handle_HEAD_note_pictures(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    original_response = handle_GET_note_picture_ids(args, req)

    return HTTPResponse(original_response.status, original_response.headers, b'')

def handle_GET_picture(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    picture_id = args['id']

    with connect('test.db') as conn:
        picture = conn.execute('SELECT Picture FROM NotePicture WHERE n = ?', (picture_id,)).fetchone()

    if picture is None:
        return HTTPResponse(404, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')

    return HTTPResponse(200, {'Content-Type': 'image/png', 'Content-length': str(len(picture[0]))}, picture[0])

def handle_HEAD_picture(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    original_response = handle_GET_picture(args, req)

    return HTTPResponse(original_response.status, original_response.headers, b'')

def handle_DELETE_picture(args: dict[str, str], req: HTTPRequest) -> HTTPResponse:
    picture_id = args['id']

    with connect('test.db') as conn:
        if conn.execute('SELECT * FROM NotePicture WHERE n = ?', (picture_id,)).fetchone() is None:
            return HTTPResponse(404, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')

        conn.execute('DELETE FROM NotePicture WHERE n = ?', (picture_id,))
        conn.commit()

    return HTTPResponse(200, {'Content-Type': 'text/plain', 'Content-length': str(0)}, b'')

server.add_endpoint(Endpoint('POST', '/notes', handle_POST_note))
server.add_endpoint(Endpoint('GET', '/notes', handle_GET_notes))
server.add_endpoint(Endpoint('HEAD', '/notes', handle_HEAD_notes))
server.add_endpoint(Endpoint('GET', '/notes/:id', handle_GET_note_by_id))
server.add_endpoint(Endpoint('HEAD', '/notes/:id', handle_HEAD_note_by_id))
server.add_endpoint(Endpoint('DELETE', '/notes/:id', handle_DELETE_note))
server.add_endpoint(Endpoint('PUT', '/notes/:id', handle_PUT_note))
server.add_endpoint(Endpoint('POST', '/notes/:id/pictures', handle_POST_picture))
server.add_endpoint(Endpoint('GET', '/notes/:id/pictures', handle_GET_note_picture_ids))
server.add_endpoint(Endpoint('HEAD', '/notes/:id/pictures', handle_HEAD_note_pictures))
server.add_endpoint(Endpoint('GET', '/pictures/:id', handle_GET_picture))
server.add_endpoint(Endpoint('HEAD', '/pictures/:id', handle_HEAD_picture))
server.add_endpoint(Endpoint('DELETE', '/pictures/:id', handle_DELETE_picture))

server.start()
