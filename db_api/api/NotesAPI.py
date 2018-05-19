###############
### Imports ###
###############
from flask_restful import reqparse, Resource
import werkzeug
import io
from flask import send_file, Response, request
from flask_socketio import send
import json
import sys


########################
### Requests Parsers ###
########################
note_parser = reqparse.RequestParser()
note_parser.add_argument('name')
note_parser.add_argument('owner')
note_parser.add_argument('tags')

file_parser = reqparse.RequestParser()
file_parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', action='append')

################
### Requests ###
################
class NotesAPI(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self):
        return self.DB.all_notes()

    def post(self):
        args = note_parser.parse_args()
        new_nid = self.DB.add_note(args['name'], args['owner'],
                                   args['tags'].split(';'))
        return new_nid


class NoteAPI(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self, nid):
        abort_if_note_doesnt_exist(nid)
        return self.DB.get_note(nid)

    def put(self, nid):
        args = note_parser.parse_args()
        self.DB.update_note(nid, args['name'], args['owner'], args['tags'])
        return nid

    def delete(self, nid):
        return self.DB.del_note(nid)


class NoteFilesAPI(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self, nid):
        #files = (file for file in self.DB.get_note_file(nid, page=None))
        #return Response(files, mimetype='application/octet-stream')
        file = self.DB.get_note_file(nid, page=None)
        return send_file(io.BytesIO(file), mimetype='application/octet-stream')

    def put(self, nid):
        return None

    def post(self, nid):
        #args = file_parser.parse_args()
        #args = request.form
        files_bytestring = []
        f = request.files#.getlist("file[]")
        print(f, file=sys.stderr)
        #f = args['file']
        for name, file in f.items():#.getlist('file'):
            print('name:', name, file=sys.stderr)
            print('file:', file, file=sys.stderr)
            print('Received file:', file.filename, file=sys.stderr)
            files_bytestring.append(bytes(file.read()))
            #files_bytestring.append(bytes(file.readall()))
        self.DB.add_note_files(nid, files_bytestring)
        return 200

    def delete(self, nid):
        return self.DB.del_note_files(nid, all=True)


class NoteFilesPageAPI(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self, nid, page):
        return send_file(io.BytesIO(self.DB.get_note_file(nid, page=int(page))), mimetype='application/octet-stream')

    def put(self, nid):
        return None

    def delete(self, nid):
        return self.DB.del_note_files(nid, all=True)

class NotesFilesPageFromAMQP_API(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self, nid, page, userID):
        note_file = self.DB.get_note_file(nid, page=int(page))
        sid = self.DB.userID_to_SID[userID]
        note_file_json = json.dumps({'data':str(note_file)})
        self.DB.ws_clients[sid].write_message(note_file, binary=True)
        return 200
