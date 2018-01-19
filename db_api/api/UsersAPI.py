###############
### Imports ###
###############
from flask_restful import reqparse, Resource


########################
### Requests Parsers ###
########################
user_parser = reqparse.RequestParser()
user_parser.add_argument('username')
user_parser.add_argument('mail')


################
### Requests ###
################
class UsersAPI(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self):
        return self.DB.all_users()

    def post(self):
        args = user_parser.parse_args()
        new_uid = self.DB.add_user(username = args['username'], mail = args['mail'])
        return {'uid': new_uid}, 201


class UserAPI(Resource):
    def __init__(self, database_class):
        self.DB = database_class

    def get(self, uid):
        #abort_if_user_doesnt_exist(uid)
        return self.DB.get_user(uid)

    def put(self, uid):
        args = user_parser.parse_args()
        self.DB.update_user(uid, username = args['username'], mail = args['mail'])
        return 201

    def delete(self, uid):
        deleted_uid = self.DB.del_user(uid)
        return {'uid': deleted_uid}, 201


class Password(Resource):
    def get(self):
        return None

    def post(self):
        return None

    def put(self):
        return None

    def delete(self):
        return None
