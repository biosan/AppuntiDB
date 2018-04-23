###############
### Imports ###
###############
from flask_restful import reqparse, Resource
import werkzeug
import io
from flask import send_file, Response, request
from flask_socketio import send
import json


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
        args = file_parser.parse_args()
        files_bytestring = []
        print(args)
        #f = request.files.getlist("file[]")
        f = args['file']
        print(f)
        for file in f:#.getlist('file'):
            print('File: ', file)
            #files_bytestring.append(bytes(file.readall()))
            files_bytestring.append(bytes(file.read()))
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
        return DB.del_note_files(nid, all=True)

class NotesFilesPageFromAMQP_API(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self, nid, page, userID):
        note_file = self.DB.get_note_file(nid, page=int(page))
        sid = DB.userID_to_SID[userID]
        note_file_json = json.dump({'data':str(note_file)})
        send(note_file_json, json=True, room=sid, namespace='/ws')
        return 200
