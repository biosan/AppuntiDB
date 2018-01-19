###############
### Imports ###
###############
from flask_restful import reqparse, Resource


########################
### Requests Parsers ###
########################
note_parser = reqparse.RequestParser()
note_parser.add_argument('name')
note_parser.add_argument('owner')
note_parser.add_argument('tags')


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
