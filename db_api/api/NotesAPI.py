###############
### Imports ###
###############
from flask import send_file, Response, request
from flask_restful import reqparse, Resource
from db_api.extensions import logger, auth
import werkzeug
import json
import io


########################
### Requests Parsers ###
########################
note_parser = reqparse.RequestParser()
note_parser.add_argument('name')
note_parser.add_argument('owner')
note_parser.add_argument('tags', action='append')
### TODO: Add to global config
categories = ['teacher', 'university', 'subject', 'year']
for c in categories:
    note_parser.add_argument(c)

file_parser = reqparse.RequestParser()
file_parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', action='append')


### Helper
def isAuthorized(DB, nid, username, return_uid=False):
    uid = DB.ConversionUtils.toUID(username)
    if (DB.get_note(nid)['owner'] == uid):
            if return_uid:
                return uid
            else:
                return True
    else:
        return False


################
### Requests ###
################
class NotesAPI(Resource):
    method_decorators = {'post': [auth.login_required]}

    def __init__(self, DB):
        self.DB = DB

    def get(self):
        return self.DB.all_notes()

    def post(self):
        args = note_parser.parse_args()
        category_tags = [(c, args[c]) for c in categories]
        category_tags = list(filter(lambda x: x[1] != None, category_tags))
        logger.debug('NotesAPI.post - category_tags: {}'.format(category_tags))
        new_nid = self.DB.add_note(args['name'], args['owner'],
                                   args['tags'], category_tags)
        return {'nid':new_nid}


class NoteAPI(Resource):
    method_decorators = {'put': [auth.login_required]}

    def __init__(self, DB):
        self.DB = DB

    def get(self, nid):
        return self.DB.get_note(nid)

    def put(self, nid):
        args = note_parser.parse_args()
        if not isAuthorized(self.DB, nid, auth.username()):
            return "NOT AUTHORIZED"
        self.DB.update_note(nid, args['name'], args['owner'], args['tags'])
        return nid

    def delete(self, nid):
        if not isAuthorized(self.DB, nid, auth.username()):
            return "NOT AUTHORIZED"
        self.DB.del_note(nid)
        return {'nid':nid}


class NoteFilesAPI(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self, nid):
        #files = (file for file in self.DB.get_note_file(nid, page=None))
        #return Response(files, mimetype='application/octet-stream')
        file = self.DB.get_note_file(nid, page=None)
        return send_file(io.BytesIO(file), mimetype='application/octet-stream')

    def put(self, nid):
        if not isAuthorized(self.DB, nid, auth.username()):
            return "NOT AUTHORIZED"
        files_bytestring = []
        f = request.files
        ###LOGGING###print(f, file=sys.stderr)
        for name, file in f.items():#.getlist('file'):
            ###LOGGING###print('name:', name, file=sys.stderr)
            ###LOGGING###print('file:', file, file=sys.stderr)
            ###LOGGING###print('Received file:', file.filename, file=sys.stderr)
            files_bytestring.append(bytes(file.read()))
        self.DB.append_note_files(nid, files_bytestring)
        return 200

    def post(self, nid):
        if not isAuthorized(self.DB, nid, auth.username()):
            return "NOT AUTHORIZED"
        files_bytestring = []
        f = request.files
        ###LOGGING###print(f, file=sys.stderr)
        for name, file in f.items():#.getlist('file'):
            ###LOGGING###print('name:', name, file=sys.stderr)
            ###LOGGING###print('file:', file, file=sys.stderr)
            ###LOGGING###print('Received file:', file.filename, file=sys.stderr)
            files_bytestring.append(bytes(file.read()))
        self.DB.add_note_files(nid, files_bytestring)
        return 200

    def delete(self, nid):
        return self.DB.del_note_files(nid, all=True)


class NoteFilesPageAPI(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self, nid, page):
        file = self.DB.get_note_file(nid, page=int(page))
        return send_file(io.BytesIO(file), mimetype='application/octet-stream')

    def put(self, nid):
        return None

    def delete(self, nid, page):
        if not isAuthorized(self.DB, nid, auth.username()):
            return "NOT AUTHORIZED"
        return self.DB.del_note_files(nid, pages=page)


class NotesFilesPageFromAMQP_API(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self, nid, page, userID):
        note_file = self.DB.get_note_file(nid, page=int(page))
        sid = self.DB.userID_to_SID[userID]
        self.DB.ws_clients[sid].write_message(note_file, binary=True)
        return 200