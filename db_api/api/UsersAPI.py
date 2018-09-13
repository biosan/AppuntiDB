###############
### Imports ###
###############
from flask_restful import reqparse, Resource
from passlib.hash import argon2
from db_api.extensions import auth, logger


########################
### Requests Parsers ###
########################
user_parser = reqparse.RequestParser()
user_parser.add_argument('username')
user_parser.add_argument('mail')
user_parser.add_argument('password')

pass_parser = reqparse.RequestParser()
pass_parser.add_argument('new_password')


### Helper
def isAuthorized(DB, uid, username, return_uid=False):
    uid1 = DB.ConversionUtils.toUID(uid)
    uid2 = DB.ConversionUtils.toUID(username)
    logger.critical('uid: {} - uid2: {}'.format(uid1, uid2))
    if (uid1 == uid2):
        if return_uid:
            return uid1
        else:
            return True
    else:
        return False


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
        new_uid = self.DB.add_user(username = args['username'],
                                   mail = args['mail'],
                                   password = args['password'])
        return {'uid': new_uid}, 201


class UserAPI(Resource):
    method_decorators = {'get':    [auth.login_required],
                         'delete': [auth.login_required],
                         'put':    [auth.login_required]}

    def __init__(self, database_class):
        self.DB = database_class

    def get(self, uid):
        if not isAuthorized(self.DB, uid, auth.username()):
            return "NOT AUTHORIZED"
        #abort_if_user_doesnt_exist(uid)
        return self.DB.get_user(uid)

    def put(self, uid):
        if not isAuthorized(self.DB, uid, auth.username()):
            return "NOT AUTHORIZED"
        args = user_parser.parse_args()
        self.DB.update_user(uid, username = args['username'], mail = args['mail'])
        return 201

    def delete(self, uid):
        if not isAuthorized(self.DB, uid, auth.username()):
            return "NOT AUTHORIZED"
        deleted_uid = self.DB.del_user(uid)
        return {'uid': deleted_uid}, 201



class AuthAPI(Resource):
    method_decorators = {'post' : [auth.login_required]}
                        #'get'  : [auth.login_required]}

    def __init__(self, DB):
        self.DB = DB

    def get(self, anyID):
        is_auth = isAuthorized(self.DB, anyID, auth.username(), return_uid=True)
        if is_auth == False:
            return "NOT AUTHORIZED"
        return {'UID':is_auth}

    def post(self, anyID):
        if not isAuthorized(self.DB, anyID, auth.username()):
            return "NOT AUTHORIZED"
        args = pass_parser.parse_args()
        return self.DB.update_user(uid=auth.username, password=args['new_password'])

    def put(self):
        return None

    def delete(self):
        return None
